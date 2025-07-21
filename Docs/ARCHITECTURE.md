# NEXAPod Architecture

## Overview

NEXAPod is a distributed compute fabric for scientific workloads. It coordinates jobs between a central server and many client nodes, using cryptographically signed logs and a credit system for fair compute allocation.

## System Architecture

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        NEXAPod System                           │
├─────────────────────────────────────────────────────────────────┤
│  Frontend Layer                                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Dashboard     │  │ Contributor Wall│  │   API Client    │ │
│  │   (Streamlit)   │  │     (HTML)      │  │   (REST/CLI)    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  API Layer                                                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    REST API (Flask)                        │ │
│  │  /register  │  /submit-job  │  /status  │  /credits        │ │
│  └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  Core Engine                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │  Scheduler  │  │  Validator  │  │   Security  │  │ Ledger  │ │
│  │   Queue     │  │   Engine    │  │   Manager   │  │ System  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Node DB       │  │    Job DB       │  │   Credit DB     │ │
│  │   (SQLite)      │  │   (SQLite)      │  │   (SQLite)      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  Execution Layer                                               │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                Container Runtime (Docker)                   │ │
│  │  Input Fetcher │ Job Executor │ Output Archiver │ Logger   │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Detailed Dataflow

```
1. Node Registration Flow
   Client Node → [Hardware Profile] → API → Database
                                     ↓
   Client Node ← [Node ID + Status] ← API ← Scheduler

2. Job Submission Flow
   Researcher → [Job Descriptor] → API → Job Queue
                                         ↓
   Node Pool ← [Job Assignment] ← Scheduler ← Job Matcher

3. Job Execution Flow
   Node → [Pull Image] → Docker → [Execute] → [Results]
    ↓                                            ↓
   [Log Job] ← [Sign Result] ← [Validate] ← [Hash Check]

4. Result Verification Flow
   Node A → [Result Hash A] → Validator ← [Result Hash B] ← Node B
                                ↓
   Database ← [Store Result] ← [Compare Hashes] → [Update Reputation]

5. Credit Distribution Flow
   Verified Result → Credit Calculator → Ledger → [Update Balances]
                                         ↓
   Dashboard ← [Display Credits] ← API ← Database
```

### Node State Machine

```
[Unregistered] → register() → [Registered]
      ↓                           ↓
[Verification] ← verify() ← [Pending Verification]
      ↓                           ↓
[Available] → assign_job() → [Busy]
      ↑                           ↓
[Complete] ← submit_result() ← [Executing]
      ↓
[Reputation Update] → [Available]
```

## Component Details

### 1. Scheduler Architecture

```python
class Scheduler:
    - job_queue: Queue[JobDescriptor]
    - node_pool: Dict[str, Node]
    - busy_nodes: Set[str]
    
    Methods:
    - match_nodes(job) → List[Node]
    - assign_job(job, nodes) → JobAssignment
    - handle_result(result) → ValidationResult
```

### 2. Security Architecture

```
Ed25519 Keypairs:
├── Node Identity Keys (per node)
├── Job Signing Keys (per job)
└── Coordinator Master Key

Validation Chain:
Job → Sign(NodeKey) → Verify(CoordinatorKey) → Store(Database)
```

### 3. Database Schema

```sql
-- Nodes table
CREATE TABLE nodes (
    id TEXT PRIMARY KEY,
    tier TEXT,
    profile TEXT,
    reputation REAL DEFAULT 1.0,
    last_seen TIMESTAMP,
    status TEXT DEFAULT 'available'
);

-- Jobs table  
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    descriptor TEXT,
    status TEXT,
    assigned_nodes TEXT,
    result TEXT,
    created_at TIMESTAMP
);

-- Ledger table (append-only)
CREATE TABLE ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT,
    node_id TEXT,
    job_id TEXT,
    credits REAL,
    signature TEXT,
    timestamp TIMESTAMP
);
```

## Scalability Considerations

### Horizontal Scaling

```
Single Coordinator (MVP):
API Server ← → Database ← → N Compute Nodes

Multi-Coordinator (v2):
Load Balancer → Multiple API Servers → Shared Database → N Compute Nodes

P2P Mesh (v3):
Coordinator Nodes ← → P2P Network ← → Compute Nodes
```

### Performance Bottlenecks

1. **Database**: SQLite → PostgreSQL for concurrent access
2. **Job Queue**: In-memory → Redis/RabbitMQ for persistence
3. **File Transfer**: HTTP → IPFS/BitTorrent for large datasets
4. **Validation**: Serial → Parallel hash verification

## Security Model

### Threat Model

| Threat           | Mitigation                                |
|------------------|-------------------------------------------|
| Malicious Nodes  | Redundant execution + hash comparison     |
| Result Tampering | Ed25519 signatures + immutable ledger     |
| Sybil Attacks    | Reputation requirements + stake bonding   |
| DoS Attacks      | Rate limiting + resource quotas           |
| Data Leaks       | Container isolation + encrypted transport |

### Trust Boundaries

```
Trusted:
- Coordinator infrastructure
- Cryptographic primitives
- Container runtime isolation

Semi-Trusted:
- Registered nodes (reputation-based)
- Job submitters (with validation)

Untrusted:
- Network transport
- External data sources
- Unregistered nodes
```

## Technology Stack

| Component      | Technology             | Purpose            |
|----------------|------------------------|--------------------|
| **API Server** | Flask/FastAPI          | REST endpoints     |
| **Database**   | SQLite → PostgreSQL    | Data persistence   |
| **Queue**      | Python Queue → Redis   | Job scheduling     |
| **Containers** | Docker                 | Job isolation      |
| **Crypto**     | Ed25519 (cryptography) | Digital signatures |
| **P2P**        | libp2p (future)        | Mesh networking    |
| **Frontend**   | Streamlit + HTML       | User interfaces    |
| **Monitoring** | Prometheus (future)    | System metrics     |

## Deployment Patterns

### Development Setup
```bash
# Single machine, all components
python -m nexapod.api &
streamlit run dashboard.py &
python client/worker.py
```

### Production Setup
```bash
# Containerized deployment
docker-compose up coordinator
docker-compose scale worker=10
```

### Kubernetes Setup
```yaml
# Multi-pod deployment with persistent storage
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nexapod-coordinator
# ... see k8s/ directory for full manifests
```

## Future Architecture Evolution

### Phase 2: Field Agnostic
- Pluggable job descriptors
- Generic container runtime
- S3/IPFS integration

### Phase 3: P2P Mesh  
- Coordinator federation
- Direct node-to-node communication
- Blockchain integration

### Phase 4: Incentive Layer
- Token economics
- Marketplace mechanisms
- Governance protocols

---

*For implementation details, see [PROTOCOL.md](PROTOCOL.md) and [API.md](API.md).*
*For complete system documentation, see [Doc.md](Doc.md).*
