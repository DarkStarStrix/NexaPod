<!-- Tags: #DistributedComputing, #ScientificComputing, #HeterogeneousResources, #ScalableArchitecture, #Innovation, #OpenSource -->

# NEXAPod: Distributed Compute Fabric for Scientific Problems

[![CI/CD Pipeline](https://github.com/DarkStarStrix/NexaPod/actions/workflows/ci.yml/badge.svg)](https://github.com/DarkStarStrix/NexaPod/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*NEXAPod seamlessly unites diverse computing resources—from consumer GPUs to high-end clusters—to tackle large-scale scientific challenges.*

---

## 1. Mission

**NEXAPod** is a distributed computing system designed to coordinate heterogeneous compute resources—ranging from consumer GPUs to high-performance clusters—to solve large-scale scientific problems. It is, in essence, **Folding@home for the AI era.**

---

## 2. Frequently Asked Questions (FAQ)

**What is NexaPod?**  
NexaPod is a modern take on distributed scientific computing. It allows anyone to contribute their computer's idle processing power to help solve complex scientific problems, starting with molecular science and protein structure prediction.

**What was the inspiration for NexaPod?**  
NexaPod is a synthesis of three ideas:
1.  **Decentralized Compute at Scale (e.g., Prime Intellect):** Inspired by the vision of training large AI models on a decentralized network of nodes.
2.  **Mesh Networking (e.g., Meshtastic):** Built on the concept of a resilient, decentralized network of peers.
3.  **Scientific Mission (e.g., Folding@home):** Focused on applying this compute power to solve real-world scientific challenges.

**Is this project affiliated with Prime Intellect?**  
No. NexaPod is an independent, open-source project. While inspired by the ambitious goals of projects like Prime Intellect, it is not formally associated with them. NexaPod's focus is on scientific computing and inference, not general-purpose LLM training.

**How is NexaPod different from Folding@home?**  
NexaPod aims to be a modern successor. Key differences include:
-   **AI-Native:** Designed for modern machine learning inference tasks.
-   **Heterogeneous Compute:** Built from the ground up to support diverse hardware (CPU, GPU).
-   **Job Agnostic:** The architecture can be adapted to any scientific problem, not just a single one.
-   **Modern Tooling:** Uses containers, modern CI/CD, and robust orchestration for security and scalability.

---

## 3. Project Roadmap

### **Phase 1: Alpha (Launched)**
-   **Goal:** Ship a working proof-of-concept. Test the core system and validate that the distributed mesh works in the wild.
-   **Actions:** Launched the first public alpha running a *secondary structure prediction* job. Onboarding technical users to gather feedback, observe bugs, and fix obvious blockers.

### **Phase 2: Beta (Next 2–4 Weeks)**
-   **Goal:** Iterate on user feedback, harden the system, and expand the network.
-   **Actions:** Bugfixes and infrastructure upgrades (better logging, validation, robust VPS). Refine onboarding and documentation. Begin groundwork for ZK proofs, incentives, and improved scheduling.

### **Phase 3: Full Launch (Post-Beta, ~1–2 Months Out)**
-   **Goal:** A production-grade, incentivized scientific compute mesh ready to tackle a "grand challenge" problem.
-   **Actions:** Implement **ZK proofs** for trustless validation. Roll out more robust job scheduling. Launch **incentive mechanisms** (token/reputation). Target a large-scale challenge like **DreamMS** (inference on 201 million molecular datapoints).

---

## 4. CI/CD (Build & Publish)

This project uses a GitHub Actions workflow for continuous integration. The pipeline is defined in `.github/workflows/ci.yml` and consists of two main stages for every push to the `main` branch:

1.  **Test:** Runs automated tests to ensure code quality and integration.
2.  **Build & Push:** Builds the `server` and `client` Docker images and pushes them to GitHub Container Registry (GHCR). This makes the latest client available for public download and the server image ready for manual deployment.

Deployment to a production or staging server is currently a manual process. The Dockerfiles are optimized to use build caching, ensuring that only changed layers are rebuilt, which significantly speeds up the pipeline.

---

## 5. Getting Started

There are two main ways to run the project:

### For Contributors (Joining the Public Mesh)
To contribute your compute power to the public network, please follow the official guide:
-   **[Docs/ONBOARDING.md](Docs/ONBOARDING.md)**

This uses the `nexapod` CLI to securely download and run the client.

### For Developers (Running Locally with Docker Compose)
To run the entire stack (server, client, monitoring) locally using the pre-built images from the registry:
1.  **Prerequisites:** Docker and Docker Compose.
2.  **Log in to GHCR (first time only):**
    ```bash
    # Use a Personal Access Token (classic) with read:packages scope.
    echo "YOUR_PAT_TOKEN" | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
    ```
3.  **Pull the latest images:**
    ```bash
    docker-compose pull
    ```
4.  **Launch Services:**
    ```bash
    docker-compose up -d
    ```
This will start the server, a local client, Prometheus, and Grafana. To stop the services, run `docker-compose down`.

#### Monitoring Dashboard (Local)
Once the services are running, you can access the monitoring stack:
-   **Prometheus:** `http://localhost:9090` (View metrics and service discovery)
-   **Grafana:** `http://localhost:3000` (Create dashboards; default user/pass: `admin`/`admin`)

---

## 6. Project Structure

```
nexapod/
├── client/           # Worker node agent code
├── server/           # Coordinator server (API, scheduler)
├── Infrastructure/   # Dockerfiles and Kubernetes manifests
├── docs/             # Architecture, API, and Onboarding documentation
├── scripts/          # Utility scripts
├── tests/            # Unit and integration tests
├── .github/          # CI/CD workflows
├── nexapod           # The user-facing CLI tool
└── docker-compose.yaml # Local development setup
```

---

## 7. Core Components & Tech Stack

| Layer                | Component                | Tech / Libs                                           |
|----------------------|--------------------------|-------------------------------------------------------|
| **Comms**            | HTTP API                 | FastAPI (server) + requests (client)                  |
| **Profiling**        | Hardware detection       | `psutil`, `nvidia-ml-py`, `subprocess` (`nvidia-smi`) |
| **Execution**        | Container runtime        | Docker (`nexapod` CLI)                                |
| **Scheduling**       | Job queue & matching     | In-memory queue (Alpha)                               |
| **Data storage**     | Metadata & logs          | SQLite (Alpha) → Postgres                             |
| **Security**         | Cryptographic signatures | `cryptography` (Ed25519)                              |
| **Orchestration**    | Single-node MVP          | Python scripts + Docker                               |
|                      | Multi-node (v2)          | Kubernetes (k8s) manifests                            |
| **Monitoring**       | Metrics & logs           | Prometheus / Grafana                                  |
| **Testing**          | Unit & integration tests | pytest                                                |

---

## 8. Contributing

PRs and issues are welcome! See **[Docs/CONTRIBUTING.md](Docs/CONTRIBUTING.md)** for detailed guidelines.

---

## 9. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
