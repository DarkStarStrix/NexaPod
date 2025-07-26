# Onboarding & First Contribution

Welcome to NexaPod! This guide walks you through the steps to join the compute mesh as a contributor and submit your first job.

## Prerequisites

- Python 3.8+ and pip
- Docker & Docker Compose (for local dev)
- kubectl and access to a Kubernetes cluster (for production)
- Git and a GitHub account

## 1. Fork & Clone Repository

```bash
# Fork https://github.com/your-org/nexapod to your GitHub account
git clone https://github.com/<your-username>/nexapod.git
cd nexapod
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
docker-compose --version
kubectl version --client
```

## 3. Build & Deploy NexaPod

### a) Docker Compose (Local Dev)
```bash
# Build and start server, client, Prometheus, Grafana
docker-compose up --build -d
```  
Services:
- **nexapod-server** – API, scheduler, DB  
- **nexapod-client** – runner polling for jobs  
- **prometheus** – metrics collection  
- **grafana**  – dashboards

### b) Kubernetes (Production/Staging)
```bash
# Apply core manifests
kubectl apply -f Infrastruture/k8s/
# Apply Prometheus scrape config (namespace: monitoring)
kubectl apply -f Infrastruture/k8s/prometheus-scrape-nexapod.yaml
# Verify deployments
kubectl rollout status deployment/nexapod-server
kubectl rollout status deployment/nexapod-client
```

## 4. Register Your Compute Node

On the node machine where you want to run jobs:

```bash
python Client/nexapod_client.py join
```
- Generates (or loads) your Ed25519 key at `~/.nexapod/client_ed25519.key`  
- Sign and register your hardware profile with the coordinator  
- Updates `Client/config.yaml` with your `node_id`

## 5. Start the Runner

```bash
python Client/nexapod_client.py run
```
- Polls the server for jobs  
- Executes **Docker** containers for each job  
- Signs, logs, and submit results back to the coordinator

## 6. Monitor Your Node

- **Client metrics**: http://<client-host>:9000/metrics  
- **Server metrics**: http://<server-host>:8000/metrics  
- **Streamlit dashboard**: `streamlit run Client/dashboard.py`  
- **Prometheus**: http://localhost:9090  
- **Grafana**: http://localhost:3000

## 7. Submit Your First Job

As a researcher, submit a sample job:

```bash
curl -X POST https://<server-host>:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "job_001",
    "docker_image": "python:3.9",
    "requirements": {"ram_gb": 1.0},
    "input_files": []
}'
```

- Watch your node pick up **job_001**  
- See execution logs in the client console  
- Check finalization once quorum of nodes agrees on the result

## 8. Visibility & Next Steps

- View live job graph, node health, and contributor leaderboard on the dashboard  
- Explore the full API in **API.md**  
- Join community discussions and file issues on GitHub

Congratulations, you’re now a NexaPod contributor! 🎉
