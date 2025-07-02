# NEXAPod Architecture

## Overview

NEXAPod is a distributed compute fabric for scientific workloads. It coordinates jobs between a central server and many client nodes, using cryptographically signed logs and a credit system for fair compute allocation.

### Dataflow

1. Node registers with server (hardware profile, keypair)
2. Node requests work; server assigns job
3. Node runs job in Docker, signs result
4. Node submits result; server verifies, stores, and credits
5. Credits and logs are published for transparency

---

## Layer Diagram

```
[Client Node] --register--> [Coordinator API]
[Client Node] <--job------- [Scheduler]
[Client Node] --result----> [DB + Reputation]
[Client Node] <--credits--- [Ledger]
```

---

## Data Model

- NodeProfile: CPU, RAM, GPU, OS, key
- JobDescriptor: job_id, image, requirements, input_uri, etc.
- JobResult: job_id, node_id, output, status, timestamp, sha256, signature
- Credits: node_id, job_id, credits, signature

---

## Security

- All logs/results are signed with Ed25519
- Credits are only issued for valid, verified results
- Hashes (SHA256) ensure result integrity

---

## Extensibility

- Add new job types by extending JobDescriptor schema
- Add new node tiers by updating scheduler logic
- Swap SQLite for Postgres for scale
- Add gRPC endpoints for high-throughput clusters

