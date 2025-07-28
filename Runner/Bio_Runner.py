"""
Runner module for protein secondary structure prediction.
"""
import os
import json
import argparse
import logging
import torch
from Bio import SeqIO
from safetensors.torch import load_file
from comms import CoordinatorClient
from Infrastruture.database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_model(model_path: str) -> torch.nn.Module:
    """Load and return the protein secondary structure model."""
    class ProteinSecStructNet(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.cnn = torch.nn.Conv1d(21, 128, kernel_size=3, padding=1)
            self.bilstm = torch.nn.LSTM(128, 64, bidirectional=True, batch_first=True)
            self.classifier = torch.nn.Linear(128, 3)

        def forward(self, x):
            x = self.cnn(x)
            x = x.permute(0,2,1)
            x, _ = self.bilstm(x)
            return self.classifier(x)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    state_dict = load_file(os.path.expanduser(model_path))
    model = ProteinSecStructNet()
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model

AA_VOCAB = "ACDEFGHIKLMNPQRSTVWY"
AA_TO_IDX = {aa: i for i, aa in enumerate(AA_VOCAB)}

def one_hot_encode(seq: str) -> torch.Tensor:
    """One-hot encode an amino acid sequence."""
    arr = torch.zeros(len(seq), len(AA_VOCAB))
    for i, aa in enumerate(seq):
        idx = AA_TO_IDX.get(aa)
        if idx is not None:
            arr[i, idx] = 1.0
    return arr

def predict_secstruct(model: torch.nn.Module, seq: str) -> str:
    """Predict secondary structure for a single sequence."""
    device = next(model.parameters()).device
    x = one_hot_encode(seq).unsqueeze(0).permute(0,2,1).to(device)
    with torch.no_grad():
        out = model(x)
        pred = torch.argmax(out, dim=-1).squeeze(0).cpu().tolist()
    idx_to_ss = {0: "H", 1: "E", 2: "C"}
    return "".join(idx_to_ss[i] for i in pred)

def process_fasta(model: torch.nn.Module, fasta_path: str) -> list:
    """Read FASTA file and predict secondary structures."""
    results = []
    for rec in SeqIO.parse(fasta_path, "fasta"):
        ss = predict_secstruct(model, str(rec.seq))
        results.append({
            "id": rec.id,
            "sequence": str(rec.seq),
            "predicted_secondary_structure": ss
        })
    return results

def save_results_to_db(results: list, db_path: str):
    """Persist prediction results to the local database."""
    db = Database(db_path)
    for r in results:
        db.store_job({"id": r["id"], "type": "secstruct"}, r)

def submit_results(results: list, client: CoordinatorClient):
    """Submit prediction results back to the coordinator."""
    for r in results:
        client.submit_result(r)

def main():
    """Entry point for runner: poll for jobs and perform inference."""
    parser = argparse.ArgumentParser(description="Protein SecStruct Runner")
    parser.add_argument('--coordinator-url', required=True)
    parser.add_argument('--db-path', default='nexapod.db')
    parser.add_argument('--model-path', required=True)
    parser.add_argument('--input-fasta', required=True)
    args = parser.parse_args()

    client = CoordinatorClient({'coordinator_url': args.coordinator_url})
    model = load_model(args.model_path)

    while True:
        job = client.poll_job()
        if not job:
            continue
        results = process_fasta(model, args.input_fasta)
        save_results_to_db(results, args.db_path)
        submit_results(results, client)

if __name__ == "__main__":
    main()
