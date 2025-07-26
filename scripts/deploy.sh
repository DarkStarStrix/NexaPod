#!/usr/bin/env bash
# Deploy all Kubernetes manifests for NexaPod
set -e
kubectl apply -f Infrastruture/k8s/
kubectl apply -f Infrastruture/k8s/prometheus-scrape-nexapod.yaml
kubectl rollout status deployment/nexapod-server
kubectl rollout status deployment/nexapod-client
echo "NexaPod deployed successfully."

