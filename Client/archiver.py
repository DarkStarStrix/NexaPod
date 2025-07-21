import tarfile, hashlib
from database import Database

def archive_and_sign(job_id: str, output_dir: str):
    tar_path = f"{job_id}.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(output_dir, arcname="outputs")
    checksum = hashlib.sha256(open(tar_path,'rb').read()).hexdigest()
    # record in ledger
    db = Database()
    db.record_archive(job_id, tar_path, checksum)
    return tar_path, checksum

