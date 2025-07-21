# ...existing code...
from qiskit import Aer, execute, QuantumCircuit

def main():
    qc = QuantumCircuit(2,2)
    # ...build circuit...
    job = execute(qc, Aer.get_backend('qasm_simulator'))
    print(job.result().get_counts())

if __name__=="__main__":
    main()

