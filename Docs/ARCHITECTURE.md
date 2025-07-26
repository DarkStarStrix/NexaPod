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

## Installation & Setup

### Quick Start (Docker Compose)
```bash
# Clone and change directory
git clone https://github.com/your-org/nexapod.git
cd nexapod

# Build and start all services
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

## Onboarding & First Contribution

1. Generate or ensure you have an Ed25519 private key:
   ```bash
   python Client/nexapod_client.py join
   ```
   - This will generate `~/.nexapod/client_ed25519.key` and register your node with the coordinator.
2. Start the client runner:
   ```bash
   python Client/nexapod_client.py run
   ```
3. Monitor your node metrics:
   - Prometheus scrape at http://<client-host>:9000/metrics
4. Submit your first job as a researcher:
   ```bash
   curl -X POST http://<coordinator-host>:8000/jobs \
     -H "Content-Type: application/json" \
     -d '{"job_id":"job_001","docker_image":"python:3.9","requirements":{"ram_gb":1.0}}'
   ```
5. Observe assignment, execution, and quorum finalization in logs and dashboard.
````
