# NEXAPod Protocol Specification

## Overview

The NEXAPod protocol defines the communication patterns, message formats, and cryptographic requirements for distributed scientific computing. This document specifies the wire format, security model, and state transitions.

## Protocol Version

**Current Version**: `1.0`  
**Compatibility**: Forward-compatible with versioned message schemas

## Message Types

### 1. NodeProfile

**Purpose**: Hardware capability advertisement during registration

```json
{
  "schema_version": "1.0",
  "node_id": "node_12345", 
  "tier": "CONSUMER_GPU",
  "cpu": {
    "model": "Intel Core i7-12700K",
    "cores": 12,
    "threads": 20,
    "frequency_ghz": 3.6
  },
  "memory": {
    "total_gb": 32,
    "available_gb": 28
  },
  "gpu": [
    {
      "model": "NVIDIA RTX 3080",
      "memory_gb": 10,
      "compute_capability": "8.6"
    }
  ],
  "storage": {
    "available_gb": 500
  },
  "os": {
    "name": "Linux",
    "version": "Ubuntu 22.04",
    "kernel": "5.15.0"
  },
  "network": {
    "bandwidth_mbps": 1000,
    "latency_ms": 15
  },
  "timestamp": 1640995200,
  "signature": "ed25519_signature_hex"
}
```

### 2. JobDescriptor

**Purpose**: Scientific workload specification

```json
{
  "schema_version": "1.0",
  "job_id": "fold_protein_001",
  "type": "protein_folding",
  "submitter": "researcher_alice",
  "title": "SARS-CoV-2 Spike Protein Folding",
  "description": "Molecular dynamics simulation of spike protein conformations",
  
  "execution": {
    "docker_image": "nexapod/alphafold:2.3.0",
    "command": ["python", "/app/fold.py", "--input", "/data/input.fasta"],
    "timeout_seconds": 3600,
    "estimated_flops": 1.2e12
  },
  
  "requirements": {
    "min_tier": "CONSUMER_GPU", 
    "min_memory_gb": 8,
    "min_storage_gb": 5,
    "gpu_required": true,
    "special_hardware": []
  },
  
  "data": {
    "input_uri": "s3://nexapod-inputs/fold_protein_001/",
    "input_files": ["sequence.fasta", "params.json"],
    "output_path": "/results/",
    "expected_outputs": ["structure.pdb", "confidence.json"]
  },
  
  "validation": {
    "result_checker": "protein_structure_validator",
    "tolerance": 0.01,
    "redundancy_factor": 2
  },
  
  "incentives": {
    "credit_rate": 1.0,
    "bonus_criteria": "completion_time < 1800s",
    "penalty_criteria": "validation_failure"
  },
  
  "metadata": {
    "priority": "normal",
    "deadline": 1640998800,
    "tags": ["structural_biology", "covid19", "alphafold"]
  },
  
  "timestamp": 1640995200,
  "signature": "submitter_ed25519_signature"
}
```

### 3. JobResult

**Purpose**: Execution outcome with cryptographic proof

```json
{
  "schema_version": "1.0",
  "job_id": "fold_protein_001",
  "node_id": "node_12345",
  
  "execution": {
    "status": "completed",
    "exit_code": 0,
    "start_time": 1640995800,
    "end_time": 1640997400,
    "duration_seconds": 1600
  },
  
  "resources": {
    "cpu_time_seconds": 19200,
    "memory_peak_gb": 6.8,
    "gpu_time_seconds": 1600,
    "network_io_gb": 0.5,
    "storage_io_gb": 2.1
  },
  
  "outputs": {
    "files": ["structure.pdb", "confidence.json", "trajectory.dcd"],
    "stdout": "Folding completed successfully...",
    "stderr": "",
    "metrics": {
      "confidence_score": 0.92,
      "rmsd": 2.1,
      "energy": -1250.5
    }
  },
  
  "validation": {
    "result_hash": "sha256_of_output_files",
    "intermediate_hashes": ["hash1", "hash2", "hash3"],
    "self_check_passed": true,
    "validator_output": "VALID"
  },
  
  "node_info": {
    "hardware_utilization": {
      "cpu_percent": 85,
      "memory_percent": 21,
      "gpu_percent": 95
    },
    "environment": {
      "docker_version": "20.10.21",
      "nvidia_driver": "520.61.05"
    }
  },
  
  "timestamp": 1640997400,
  "signature": "node_ed25519_signature"
}
```

### 4. CreditTransaction

**Purpose**: Compute reward accounting

```json
{
  "schema_version": "1.0",
  "transaction_id": "tx_789abc",
  "job_id": "fold_protein_001",
  "node_id": "node_12345",
  
  "credits": {
    "base_amount": 12.5,
    "bonus_amount": 2.0,
    "penalty_amount": 0.0,
    "total_amount": 14.5
  },
  
  "calculation": {
    "flops_completed": 1.2e12,
    "time_factor": 1.0,
    "quality_factor": 1.16,
    "reputation_multiplier": 1.0
  },
  
  "verification": {
    "verified_by": "coordinator_001",
    "verification_time": 1640997600,
    "consensus_nodes": ["node_12345", "node_67890"]
  },
  
  "timestamp": 1640997600,
  "signature": "coordinator_ed25519_signature"
}
```

## Communication Patterns

### 1. Node Lifecycle

```
State: UNREGISTERED
├── send(NodeProfile) → receive(RegistrationResponse)
└── State: REGISTERED

State: REGISTERED  
├── poll(JobRequest) → receive(JobDescriptor | NoJob)
├── State: ASSIGNED (if job received)
└── heartbeat() → receive(KeepAlive)

State: ASSIGNED
├── execute(Job) → State: EXECUTING
└── cancel() → State: REGISTERED

State: EXECUTING
├── progress_update() → receive(Continue | Abort)
├── complete() → send(JobResult) → State: COMPLETED
└── error() → send(ErrorReport) → State: REGISTERED

State: COMPLETED
├── receive(CreditTransaction) → State: CREDITED
└── timeout() → State: REGISTERED
```

### 2. Job Lifecycle

```
SUBMITTED → QUEUED → ASSIGNED → EXECUTING → VALIDATING → COMPLETED
    ↓          ↓         ↓          ↓           ↓           ↓
  [API]    [Queue]   [Node]    [Docker]   [Validator]  [Ledger]
```

### 3. Message Flow Diagrams

#### Job Submission Flow
```
Researcher → API: POST /submit-job (JobDescriptor)
API → Queue: enqueue(JobDescriptor)  
API → Researcher: {job_id, status: "queued"}

Scheduler → Queue: dequeue() → JobDescriptor
Scheduler → NodePool: find_nodes(requirements)
Scheduler → Node: assign_job(JobDescriptor)
Node → Scheduler: job_accepted | job_rejected
```

#### Result Verification Flow
```
Node A → Coordinator: JobResult A
Node B → Coordinator: JobResult B
Coordinator → Validator: compare(Result A, Result B)
Validator → Coordinator: ValidationResult
Coordinator → Ledger: record_credits(if valid)
Coordinator → Reputation: update_scores()
```

## Security Protocols

### 1. Cryptographic Requirements

**Signature Algorithm**: Ed25519  
**Hash Algorithm**: SHA-256  
**Key Length**: 256 bits  
**Message Authentication**: HMAC-SHA256

### 2. Key Management

```python
# Node Key Generation
private_key = Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# Message Signing
message_bytes = json.dumps(message, sort_keys=True).encode()
signature = private_key.sign(message_bytes)

# Signature Verification  
try:
    public_key.verify(signature, message_bytes)
    return True
except InvalidSignature:
    return False
```

### 3. Trust Model

**Root of Trust**: Coordinator public key (pre-distributed)  
**Node Trust**: Reputation-based with Ed25519 identity  
**Message Integrity**: All messages signed and timestamped  
**Replay Protection**: Monotonic timestamps + nonce

### 4. Threat Mitigation

| Attack Vector     | Mitigation Strategy             |
|-------------------|---------------------------------|
| Message Tampering | Ed25519 signatures              |
| Replay Attacks    | Timestamp validation + nonces   |
| Impersonation     | Public key verification         |
| Result Forgery    | Redundant execution + consensus |
| Denial of Service | Rate limiting + reputation      |

## Protocol Extensions

### 1. Field-Specific Extensions

**Quantum Computing Jobs**:
```json
"quantum_requirements": {
  "qubits": 20,
  "gate_fidelity": 0.999,
  "coherence_time_us": 100
}
```

**Machine Learning Jobs**:
```json
"ml_requirements": {
  "framework": "tensorflow",
  "model_size_gb": 5.2,
  "batch_size": 256
}
```

### 2. P2P Extensions (Future)

```json
"p2p_routing": {
  "peer_id": "libp2p_peer_id",
  "multiaddrs": ["/ip4/192.168.1.100/tcp/4001"],
  "protocols": ["nexapod/1.0.0", "nexapod/mesh/1.0.0"]
}
```

## Error Handling

### 1. Error Response Format

```json
{
  "error": {
    "code": "INVALID_JOB_DESCRIPTOR",
    "message": "Missing required field: docker_image",
    "details": {
      "field": "execution.docker_image",
      "expected_type": "string"
    },
    "timestamp": 1640995200
  }
}
```

### 2. Standard Error Codes

| Code                     | Description                       |
|--------------------------|-----------------------------------|
| `INVALID_SIGNATURE`      | Cryptographic verification failed |
| `INSUFFICIENT_RESOURCES` | Node cannot meet job requirements |
| `JOB_TIMEOUT`            | Execution exceeded time limit     |
| `VALIDATION_FAILED`      | Result validation check failed    |
| `NETWORK_ERROR`          | Communication failure             |

## Implementation Guidelines

### 1. Message Serialization

- **Format**: JSON (UTF-8 encoded)
- **Required Fields**: Must be present and non-null
- **Optional Fields**: May be omitted or null
- **Field Ordering**: Canonical ordering for signature generation

### 2. Transport Layer

- **Protocol**: HTTPS for MVP, gRPC for v2+
- **Authentication**: Bearer tokens + Ed25519 signatures  
- **Compression**: gzip for large payloads
- **Timeouts**: 30s for API calls, 24h for job execution

### 3. Versioning Strategy

- **Schema Version**: Embedded in every message
- **Backward Compatibility**: Maintained for N-1 versions
- **Deprecation**: 6-month notice for breaking changes

---

*This protocol specification is implemented in the NEXAPod codebase.*  
*For API endpoints, see [API.md](API.md).*  
*For system architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).*  
*For complete documentation, see [Doc.md](Doc.md).*
