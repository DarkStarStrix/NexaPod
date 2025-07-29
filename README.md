# NEXAPod

*A Distributed Compute Fabric for Scientific Problems*

---

## 1. Mission

**NEXAPod** is a distributed computing system designed to coordinate heterogeneous compute resources—ranging from consumer GPUs to high-performance clusters—to solve large-scale scientific problems.

---

## 2. Project Layout

```
NexaPod/
├── README.md
├── requirements.txt
├── setup.py           # (Optional) Make the project pip installable
├── nexapod/           # Core package
│   ├── __init__.py
│   ├── descriptor.py
│   ├── runner.py
│   ├── input_fetch.py
│   ├── archiver.py
│   ├── output_validator.py
│   ├── perf_estimator.py
│   ├── security.py
│   └── ... other modules ...
├── examples/          # Example scientific workloads
│   ├── __init__.py
│   ├── surrogate_material.py
│   ├── weather_ensemble.py
│   └── quantum_sim.py
├── scripts/           # Utility scripts (e.g. local test harness)
│   └── ...
└── tests/             # Unit and integration tests
    └── ...
```

---

## 3. Installation

```bash
pip install -r requirements.txt
```

Optionally, run:

```bash
pip install -e .
```

---

## 4. Running

- API Server: `python -m nexapod.api`
- Scheduler: `python scripts/start_scheduler.py`
- Dashboard: `streamlit run scripts/dashboard_app.py`

---

## 5. Developer Quickstart & Repo Structure

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

## 6. Core Components & Tech Stack

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

## 7. Implementation Tips & Notes

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

## 8. Example Job Descriptor

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

## 9. Quickstart

1. `pip install -r requirements.txt`
2. `docker-compose up` (MVP)
3. `python client/nexapod_client.py join`
4. `python server/app.py`

---

---

## 10. Contributing

PRs and issues welcome! See [docs/CONTRIBUTING.md](Docs/CONTRIBUTING.md) for guidelines.

---

## 11. License

MIT License. See [LICENSE](LICENSE).
