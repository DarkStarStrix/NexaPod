# NEXAPod

*A Distributed Compute Fabric for Scientific Problems*

---

## 1. Mission

**NEXAPod** is a distributed computing system designed to coordinate heterogeneous compute resources—ranging from consumer GPUs to high-performance clusters—to solve large-scale **scientific problems**. It draws inspiration from Folding@Home, BOINC, and Mesh networking, but introduces:

- A standardized, cryptographically secure compute protocol
- Tiered compute orchestration
- Domain-agnostic support (proteins, materials, quantum, weather, etc.)
- Fair credit-based contribution accounting

---

## 2. System Overview

NEXAPod is composed of four core **subsystems**, each with specific responsibilities:

```
 ┌────────────────────┐        ┌────────────────────┐
 │   CLIENT NODES     │ <──┐──▶│   COORDINATOR API  │
 │  (Desktops, Rigs)  │    │   │  (Job Control, DB) │
 └────────────────────┘    │   └────────────────────┘
           ▲               │             ▲
           │               ▼             │
 ┌────────────────────┐    ┌────────────────────┐
 │  EXECUTOR + LOGGER │    │  SCHEDULER / MATCH │
 │  (Docker Runner)   │    │ (Tier-Aware Logic) │
 └────────────────────┘    └────────────────────┘
           ▲                                 ▲
           │                                 │
           └─────── Result Upload ───────────┘
                         ↓
              ┌────────────────────┐
              │  PUBLIC LEDGER     │
              │  (Credits, Outputs)│
              └────────────────────┘
```

---

## 3. Developer Quickstart & Repo Structure

### Suggested Layout

```
nexapod/  
├── client/                   # Node-agent (worker) code  
│   ├── nexapod_client.py     # CLI entrypoint  
│   ├── profiles.py           # Hardware introspection (psutil, nvidia-smi)  
│   ├── comms.py              # HTTP/gRPC client + message schemas  
│   ├── executor.py           # Pulls Docker images & runs tasks  
│   ├── logger.py             # Signs & ships JSON logs  
│   └── config.yaml           # Node config (keys, tiers, endpoints)  
│  
├── server/                   # Master controller (API + scheduler)  
│   ├── app.py                # FastAPI (or Flask) server  
│   ├── scheduler.py          # Job queue, warm/cold pools, tier matching  
│   ├── db.py                 # SQLite (MVP) or SQLAlchemy models  
│   ├── reputation.py         # Credits ledger & issuance logic  
│   └── config.yaml           # Server settings (port, DB path, auth keys)  
│  
├── proto/                    # (Optional) Protobuf/gRPC definitions  
│   ├── nexapod.proto  
│   └── generate.sh           # Stub-generation script  
│  
├── infra/                    # Kubernetes manifests & Dockerfiles  
│   ├── Dockerfile.client  
│   ├── Dockerfile.server  
│   ├── k8s/                   # k8s Deployment, Service, ConfigMap yamls  
│   └── scripts/               # bootstrap scripts (e.g. certs, keys)  
│  
├── docs/                     # Design docs & API reference  
│   ├── ARCHITECTURE.md       # Layer diagram + dataflow  
│   ├── API.md                # REST/gRPC endpoints  
│   ├── PROTOCOL.md           # JSON schemas + message types  
│   └── MVP_ROADMAP.md        # Milestones & tasks  
│  
├── examples/                 # Example workloads & manifests  
│   ├── fold_job.json         # Sample protein-folding job descriptor  
│   └── mpi_train.py          # Minimal distributed-training script  
│  
├── scripts/                  # Utility scripts (e.g. local test harness)  
│   └── run_local.sh  
│  
├── tests/                    # Unit & integration tests  
│   ├── test_comms.py  
│   ├── test_scheduler.py  
│   └── test_security.py  
│  
├── .gitignore  
├── LICENSE                   # Apache-2.0 or MIT  
├── README.md                 # Project overview & quickstart  
└── requirements.txt          # Python deps (FastAPI, psutil, docker, cryptography…)  
```

---

## 4. Core Components & Tech Stack

| Layer                | Component                | Tech / Libs                                           |
|----------------------|--------------------------|-------------------------------------------------------|
| **Comms**            | HTTP API                 | FastAPI (server) + requests or `grpcio` (client)      |
|                      | WebSocket / gRPC (v2)    | Protobuf + gRPC                                       |
| **Profiling**        | Hardware detection       | `psutil`, `nvidia-ml-py`, `subprocess` (`nvidia-smi`) |
| **Execution**        | Container runtime        | Docker SDK for Python (`docker-py`)                   |
|                      | Resource sandboxing      | Docker run-time flags (cpu-shares, mem limits)        |
| **Scheduling**       | Job queue & matching     | In-process queue (MVP), later Redis / RabbitMQ        |
| **Data storage**     | Metadata & logs          | SQLite (MVP) → Postgres                               |
| **Security**         | Cryptographic signatures | `cryptography` (Ed25519)                              |
|                      | Hashing                  | `hashlib` (SHA256)                                    |
| **Orchestration**    | Single-node MVP          | Python scripts + Docker                               |
|                      | Multi-node (v2)          | Kubernetes (k8s) manifests + Helm charts              |
| **Credits & ledger** | Credit accounting        | JSON ledger → blockchain smart contracts (v2)         |
| **Monitoring**       | Metrics & logs           | OpenTelemetry / Prometheus / Grafana                  |
| **Testing**          | Unit & integration tests | pytest, tox                                           |

---

## 5. Implementation Tips & Notes

1. **Start Simple**
   - Launch server and a single client on localhost.
   - Use HTTP+JSON for MVP before adding gRPC.
2. **Define Clear Schemas**
   - Keep your JSON message definitions in `docs/PROTOCOL.md`.
   - Use `pydantic` models for request/response validation.
3. **Docker-first**
   - Build small, minimal containers for both client and server.
   - Use multi-stage builds to keep images lean (only Python runtime & code).
4. **Key Management**
   - Auto-generate an Ed25519 keypair in `scripts/bootstrap_keys.sh`.
   - Store private keys encrypted on disk (e.g. via OS keyring) in v1.
5. **Job Descriptor**
   - Standardize fields: `job_id`, `image`, `requirements`, `input_uri`, `tolerance`, `credit_rate`.
   - Version your descriptor schema (add a `schema_version` field).
6. **Warm vs Cold Pools**
   - Track node state in server’s DB.
   - Clients poll for work only when “warm.” Cold clients run health-check jobs.
7. **Verification & Redundancy**
   - For MVP, assign 10% of jobs redundantly.
   - Compare result hashes; flag mismatches for manual review.
8. **Credit Calculation**
   - Base credits on `duration × flops_estimate`.
   - Maintain a per-node cumulative ledger in the DB.
9. **Logging**
   - Emit structured logs (JSON) to STDOUT.
   - Optionally integrate OpenTelemetry for traceability.
10. **Testing**
    - Write mocks for client-server interactions.
    - Simulate flaky nodes by randomly failing jobs in tests.
11. **Documentation & Onboarding**
    - Keep `README.md` updated with quick-start:
      1. `pip install -r requirements.txt`
      2. `docker-compose up` (MVP)
      3. `python client/nexapod_client.py join`
      4. `python server/app.py`
12. **Roadmap to v2**
    - Swap SQLite for Postgres + Redis.
    - Migrate HTTP to gRPC+Protobuf.
    - Introduce a blockchain ledger for credit/token distribution.
    - Container-native orchestration on k8s with Helm charts.

---

## 6. Example Job Descriptor

```json
{
  "schema_version": "1.0",
  "job_id": "fold_ensemble_v1",
  "type": "protein_folding",
  "input_files": ["input1.fasta", "params.json"],
  "docker_image": "nexapod/folding:latest",
  "estimated_flops": 1.2e12,
  "tier": 1,
  "requirements": {"gpu": true, "ram_gb": 8},
  "input_uri": "s3://nexapod-inputs/fold_ensemble_v1/",
  "tolerance": 0.01,
  "credit_rate": 1.0
}
```

---

## 7. Quickstart

1. `pip install -r requirements.txt`
2. `docker-compose up` (MVP)
3. `python client/nexapod_client.py join`
4. `python server/app.py`

---

# NEXAPod Roadmap (v0.1 → v1.0+)

## Phase 0 – MVP (Bootstrap Stage)

> *Goal: Prove the architecture works, run a full job cycle end-to-end.*

**Deliverables:**

* [x] Simple Dockerized client  
* [x] Coordinator API (master node)  
* [x] Job dispatched → container pulled → task run  
* [x] Basic compute logging (JSON + `nvidia-smi`)  
* [x] Results collected + stored locally  
* [x] Warm/cold compute pool logic (static)  
* [x] Credits issued based on job log  
* [x] K8s coordination for spawning compute nodes  

**Outcome:**  
Functional single-problem compute mesh (e.g. protein folding)

---

## Phase 1 – System Refinement (MVP++)

> *Goal: Support multi-job pipelines, real compute tiers, and hardened node tracking.*

**Tasks:**

* [ ] Tier system implementation (e.g. CPU, consumer GPU, HPC)  
* [ ] Automatic node profiling at registration  
* [ ] Job queue + node-matching scheduler  
* [ ] RESTful API endpoints:  
  * `POST /register`  
  * `POST /submit-job`  
  * `GET /status`  
* [ ] Signature + hash validator for all job logs  
* [ ] SQLite DB backend for nodes, jobs, logs  
* [ ] Spot redundancy (same job on two nodes → compare hashes)  
* [ ] Contributor wall (HTML/JSON UI)  
* [ ] Live job dashboard (Streamlit/Flask)  

**Outcome:**  
Multi-node support, reliable job lifecycle, contribution visibility

---

## Phase 2 – Field Agnostic Generalization

> *Goal: Accept any scientific workload (weather, materials, quantum, etc.).*

**Tasks:**

* [ ] Generalize job descriptor schema (compute estimates, input/output contracts)  
* [ ] Container runner sandbox with volume-mounted inputs/outputs  
* [ ] Examples for diverse workloads:  
  * Surrogate material modeling  
  * Weather ensemble forecasting  
  * Quantum simulation (Qiskit jobs)  
* [ ] Output validation framework (user-defined result checker)  
* [ ] Inputs from public S3/IPFS  
* [ ] Outputs to signed archive (tarball, checksum + ledger)  
* [ ] Performance estimation tooling (approx FLOPs/job)  

**Outcome:**  
NEXAPod becomes a protocol for any large-scale scientific task

---

## Phase 3 – Distributed Mesh & Security Hardening

> *Goal: Decentralize trust, build toward long-term scale and resilience.*

**Tasks:**

* [ ] Ed25519 keypair issuance per node  
* [ ] Fully signed log + metadata trail (compute proofs)  
* [ ] Meshtastic or libp2p-based comms prototype  
* [ ] Job replication (P2P share → fallback runner)  
* [ ] ZK (zero-knowledge) proof research for trustless execution (optional)  
* [ ] Rate limits / abuse protection (bad node mitigation)  
* [ ] Hardened result ledger (append-only credit/event log)  

**Outcome:**  
A resilient mesh network with verifiable, trustless compute

---

## Phase 4 – Incentivization & Reputation Layer

> *Goal: Reward real compute with tokens, open up programmable incentives.*

**Tasks:**

* [ ] Nexa Credits ↔ ERC-20 or CSV export  
* [ ] Leaderboard of top contributors  
* [ ] Job sponsors / bounties (in credits or tokens)  
* [ ] Per-node reputation tracking (uptime, accuracy, honesty)  
* [ ] Compute bank dashboard (buy, sell, contribute compute)  

**Outcome:**  
Credits become real currency for open scientific progress

---

## Phase 5 – Public Launch + Onboarding Portal

> *Goal: Bring in contributors, researchers, and developers.*

**Tasks:**

* [ ] Public onboarding UI for new contributors (get container, register node)  
* [ ] Documentation: dev setup, protocol, client API  
* [ ] Example scientific problems (protein folding, quantum sim, etc.)  
* [ ] Open job submission portal  
* [ ] First “NEXAPod Challenge” — distributed benchmark task  
* [ ] Scientific publishing pipeline (result → PDB / arXiv-ready outputs)  

**Outcome:**  
Open scientific mesh computing community, powered by NEXAPod

---

## Timeline Snapshot

| Phase   | Est. Duration | Milestone                       |
|---------|---------------|---------------------------------|
| Phase 0 | ✅ Done        | MVP working end-to-end          |
| Phase 1 | ~2 weeks      | Job queue, DB, credit ledger    |
| Phase 2 | ~3 weeks      | Multi-field job support         |
| Phase 3 | ~4 weeks      | Security, trust, p2p prototype  |
| Phase 4 | ~2–3 weeks    | Credits/token system, dashboard |
| Phase 5 | ongoing       | Public launch + scaling         |

---

## 8. Contributing

PRs and issues welcome! See [docs/CONTRIBUTING.md](Docs/CONTRIBUTING.md) for guidelines.

---

## 9. License

MIT License. See [LICENSE](LICENSE).
