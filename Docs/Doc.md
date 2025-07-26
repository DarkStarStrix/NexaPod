# NexaPod: Comprehensive Technical Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [System Workflow](#system-workflow)
5. [Development Phases](#development-phases)
6. [API Reference](#api-reference)
7. [Security Model](#security-model)
8. [Installation & Setup](#installation--setup)
9. [Testing](#testing)
10. [Contributing](#contributing)

---

## Project Overview

**NexaPod** is a decentralized, field-agnostic compute mesh designed to coordinate heterogeneous computational resources for large-scale scientific problems. The system enables researchers to submit computational jobs that are distributed across a network of volunteer nodes, ranging from consumer GPUs to high-performance computing clusters.

### Mission Statement
*Democratize access to computational resources for scientific research by creating a permissionless, trustless, and incentivized distributed computing platform.*

### Key Features
- **Field Agnostic**: Supports any scientific workload (weather modeling, quantum simulation, materials science, etc.)
- **Decentralized**: No single point of failure, peer-to-peer communication
- **Trustless**: Cryptographic verification and redundant execution
- **Incentivized**: Token-based reward system for compute contributors
- **Scalable**: Automatic node profiling and intelligent job scheduling

---

## Architecture

For detailed architecture documentation, see **[ARCHITECTURE.md](ARCHITECTURE.md)**.

### High-Level System Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Job Submitter │    │   Coordinator   │    │  Compute Nodes  │
│                 │    │                 │    │                 │
│ • Scientists    │◄──►│ • Job Queue     │◄──►│ • CPU Nodes     │
│ • Researchers   │    │ • Scheduler     │    │ • GPU Nodes     │
│ • Institutions  │    │ • Validator     │    │ • HPC Clusters  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Dashboard     │
                    │                 │
                    │ • Live Status   │
                    │ • Contributor   │
                    │   Wall          │
                    │ • Network Graph │
                    └─────────────────┘
```

### Technology Stack Summary

| Layer             | Component        | Technology          |
|-------------------|------------------|---------------------|
| **Frontend**      | Dashboard        | Streamlit           |
| **Frontend**      | Contributor Wall | HTML/CSS/JS         |
| **API**           | REST Endpoints   | Flask               |
| **Core**          | Job Scheduler    | Python + Threading  |
| **Data**          | Database         | SQLite → PostgreSQL |
| **Security**      | Cryptography     | Ed25519 + SHA-256   |
| **Execution**     | Containers       | Docker              |
| **Communication** | Mesh Network     | libp2p (planned)    |

---

## Core Components

### 1. Tier System (`nexapod/tier.py`)
Classifies compute nodes based on their capabilities:

```python
class Tier(Enum):
    CPU = 'CPU'              # Basic CPU nodes
    CONSUMER_GPU = 'Consumer GPU'  # Gaming/workstation GPUs
    HPC = 'HPC'              # High-performance clusters
```

### 2. Node Management (`nexapod/node.py`)
Handles node registration and profiling:
- **Automatic Profiling**: Detects OS, CPU, memory, and GPU capabilities
- **Registration**: Stores node metadata in the database
- **Status Tracking**: Monitors node availability and health

### 3. Job Scheduler (`nexapod/scheduler.py`)
Core scheduling engine with the following features:
- **Job Queue**: FIFO queue for incoming computational tasks
- **Node Matching**: Intelligent assignment based on job requirements
- **Redundancy**: Executes jobs on multiple nodes for verification
- **Conflict Prevention**: Tracks busy nodes to prevent resource conflicts

#### Scheduling Algorithm
```
1. Job arrives in queue
2. Find 2+ available nodes matching job requirements
3. Verify nodes are trusted and not busy
4. Execute job on selected nodes in parallel
5. Compare results via hash validation
6. Accept result if hashes match, else flag discrepancy
7. Mark nodes as available and log result
```

### 4. Database Layer (`nexapod/database.py`)
SQLite-based persistence with three main tables:
- **Nodes**: Store node profiles, tiers, and status
- **Jobs**: Track job metadata and results
- **Logs**: Append-only audit trail for all operations

### 5. Validation System (`nexapod/validator.py`)
Ensures job integrity through:
- **HMAC Signatures**: Cryptographic verification of job logs
- **Hash Comparison**: Validates identical results from redundant execution
- **Result Verification**: User-defined checkers for output validation

### 6. Container Runtime (`nexapod/runner.py`)
Secure job execution environment:
- **Docker Integration**: Runs jobs in isolated containers
- **Volume Mounting**: Manages input/output file systems
- **Resource Limits**: Enforces CPU/memory constraints
- **Result Collection**: Captures job outputs and logs

### 7. API Layer (`nexapod/api.py`)
RESTful endpoints for system interaction. For complete API documentation, see **[API.md](API.md)**.

| Endpoint             | Method | Purpose                   |
|----------------------|--------|---------------------------|
| `/register`          | POST   | Register new compute node |
| `/submit-job`        | POST   | Submit computational job  |
| `/status`            | GET    | Query system status       |
| `/jobs/{id}`         | GET    | Get job details           |
| `/nodes`             | GET    | List registered nodes     |
| `/credits/{node_id}` | GET    | Get credit balance        |

### 8. Dashboard (`dashboard.py`)
Real-time system monitoring:
- **Network Visualization**: Interactive graph of connected nodes
- **Job Status**: Live tracking of submitted jobs
- **Contributor Metrics**: Performance statistics and leaderboards
- **Resource Utilization**: System-wide compute usage

---

## System Workflow

For detailed protocol specifications, see **[PROTOCOL.md](PROTOCOL.md)**.

### Node Registration Flow
```
1. Node starts up and profiles hardware
2. Generates Ed25519 keypair for identity
3. Sends registration request to coordinator
4. Coordinator validates and stores node metadata
5. Node begins polling for available jobs
```

### Job Submission Flow
```
1. Researcher submits job via API or dashboard
2. Job enters scheduler queue with resource requirements
3. Scheduler finds 2+ matching available nodes
4. Job descriptor and input data distributed to nodes
5. Nodes execute job in parallel using containers
6. Results collected and hash-verified
7. Successful result stored and credited to contributors
```

### Validation Flow
```
1. Job completes on multiple nodes
2. Each node signs result with private key
3. Coordinator verifies signatures and compares hashes
4. If hashes match: accept result, update reputation
5. If hashes differ: flag nodes, require additional execution
6. Result archived with cryptographic proof
```

---

## Development Phases

### Phase 1: Core Infrastructure ✅
- [x] Basic node registration and profiling
- [x] Job queue and scheduler
- [x] SQLite database backend
- [x] REST API endpoints
- [x] Hash validation and redundancy
- [x] Live dashboard with network visualization

### Phase 2: Field Agnostic Generalization ✅
- [x] Generalized job descriptor schema
- [x] Container-based execution sandbox
- [x] Support for diverse workloads (weather, materials, quantum)
- [x] Output validation framework
- [x] Input fetching from S3/IPFS
- [x] Signed result archives

### Phase 3: Distributed Mesh & Security ✅
- [x] Ed25519 keypair per node
- [x] Fully signed log trails
- [x] P2P communication (libp2p prototype)
- [x] Job replication and fallback
- [x] Zero-knowledge proof research
- [x] Abuse protection and rate limiting

### Phase 4: Incentivization & Reputation ✅
- [x] Nexa Credits token system
- [x] Job bounties and sponsorship
- [x] Reputation tracking
- [x] Compute marketplace dashboard

### Phase 5: Public Launch (In Progress)
- [ ] Public onboarding UI
- [ ] Documentation portal
- [ ] Scientific problem examples
- [ ] Community challenge programs
- [ ] Research publication pipeline

---

## API Reference

For complete API documentation with examples, see **[API.md](API.md)**.

### Quick Reference

#### Node Registration
```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"id": "node_001", "tier": "CPU", "profile": {...}}'
```

#### Job Submission
```bash
curl -X POST http://localhost:5000/submit-job \
  -H "Content-Type: application/json" \
  -d '{"id": "job_001", "docker_image": "tensorflow/tensorflow:latest"}'
```

#### System Status
```bash
curl http://localhost:5000/status
```

### Python SDK Example
```python
from nexapod_client import NexaPodClient

client = NexaPodClient("http://localhost:5000")
response = client.submit_job({
    "id": "my_job",
    "docker_image": "python:3.9",
    "requirements": {"min_memory_gb": 4}
})
```

---

## Security Model

For detailed security architecture, see **[ARCHITECTURE.md](ARCHITECTURE.md#security-model)**.

### Cryptographic Foundation
- **Ed25519 Signatures**: Each node has a unique keypair for identity
- **HMAC Validation**: All job logs are cryptographically signed
- **Hash Verification**: Results validated through SHA-256 comparison
- **Append-Only Ledger**: Immutable audit trail of all operations

### Trust Mechanisms
1. **Redundant Execution**: Jobs run on multiple nodes
2. **Consensus Validation**: Results accepted only with matching hashes
3. **Reputation System**: Track node reliability over time
4. **Rate Limiting**: Prevent spam and abuse

### Threat Mitigation
- **Byzantine Nodes**: Detected through result comparison
- **Sybil Attacks**: Mitigated by reputation requirements
- **Data Integrity**: Ensured through cryptographic proofs
- **Availability**: Maintained through mesh redundancy

---

## Installation & Setup

Add detailed K8s and Docker Compose onboarding, plus CLI steps.

### Quick Start (Docker Compose)
```bash
# Clone and change directory
git clone https://github.com/your-org/nexapod.git
cd nexapod

# Build and start all services (server, client, Prometheus, Grafana)
docker-compose up --build -d
```

### Quick Start (Kubernetes)
```bash
# Apply all manifests
kubectl apply -f Infrastruture/k8s/

# Verify deployments
kubectl rollout status deployment/nexapod-server
kubectl rollout status deployment/nexapod-client
```

### Register Your Node (Onboarding)
1. Ensure you have a private key (generated on first join).
2. Run the join command on your node machine:
   ```bash
   python Client/nexapod_client.py join
   ```
3. You should see "Node registered with coordinator." and your `node_id` saved in config.

### Start Polling for Jobs
```bash
python Client/nexapod_client.py run
```
The client will expose metrics on port 9000 (`/metrics`).

### Access Dashboard & Monitoring
- **Streamlit Dashboard**: `streamlit run Client/dashboard.py`
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (add Prometheus data source)

---

## Onboarding & First Contribution

Follow these steps to get started as a compute contributor:

1. Fork the NexaPod repository and clone your fork:
   ```bash
git clone https://github.com/<your-username>/nexapod.git
cd nexapod
   ```
2. Install prerequisites:
   ```bash
pip install -r requirements.txt
docker-compose --version
kubectl version --client
   ```
3. Build and deploy the system with Docker Compose or Kubernetes (see above).
4. Register your compute node:
   ```bash
python Client/nexapod_client.py join
``` 
   - This generates your Ed25519 key if needed and registers you as a node.
5. Start your runner:
   ```bash
python Client/nexapod_client.py run
```
6. Monitor your node:
   - Check client logs and metrics on http://localhost:9000/metrics
   - View overall system status in dashboard and Grafana.
7. Submit your first job (as a researcher):
   ```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"job_id":"job_001","docker_image":"python:3.9","requirements":{"ram_gb":1.0}}'
```
8. Observe job assignment and execution in logs, then result finalization via quorum on the server.

Congratulations, you are now part of the NexaPod compute mesh!

---

## Testing

### Running Tests
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Full system test
pytest tests/test_client.py::test_integration
```

### Test Client
The robust test client (`tests/test_client.py`) validates:
- Node registration and profiling
- Job submission and execution
- Result validation and logging
- Complete system integration

### Expected Test Flow
1. Start mock coordinator server
2. Register test node (expect 200 OK)
3. Submit test job (expect 200 OK)
4. Poll for status (expect 200 OK)
5. Validate result logging
6. Verify system integrity

### Continuous Integration
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
```

---

## Contributing

### Development Workflow
1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Implement changes with tests
4. Submit pull request
5. Code review and merge

### Code Standards
- **Python 3.8+** with type hints
- **Black** code formatting
- **Pytest** for testing
- **Docstrings** for all public APIs
- **Type annotations** for function signatures

### Documentation Standards
- Update relevant documentation files
- Include examples in docstrings
- Cross-reference related documentation
- Test all code examples

### Pull Request Template
```markdown
## Description
Brief description of changes

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Documentation
- [ ] Updated relevant docs
- [ ] Added examples
- [ ] Updated API reference

## Breaking Changes
- [ ] None
- [ ] Migration guide provided
```

---

## Related Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Detailed system architecture and component diagrams
- **[PROTOCOL.md](PROTOCOL.md)**: Message formats and communication protocols
- **[API.md](API.md)**: Complete REST API reference with examples
- **[README.md](../README.md)**: Project overview and quick start guide

---

## Troubleshooting

### Common Issues

**Docker Connection Error**:
```bash
# Check Docker daemon
sudo systemctl status docker

# Test Docker access
docker ps
```

**Node Registration Fails**:
```python
# Check network connectivity
import requests
response = requests.get("http://localhost:5000/status")
print(response.status_code)
```

**Job Execution Timeout**:
- Increase timeout in job descriptor
- Check node resource availability
- Monitor Docker container logs

### Getting Help

1. Check the [documentation](#related-documentation)
2. Search existing [GitHub issues](https://github.com/your-org/nexapod/issues)
3. Join the [Discord community](https://discord.gg/nexapod)
4. Email support: support@nexapod.org

---

*This documentation represents the current state and future roadmap of NexaPod. For the latest updates, see the project repository.*

**Last Updated**: 2024-01-01  
**Version**: 1.0.0  
**Authors**: NexaPod Development Team
