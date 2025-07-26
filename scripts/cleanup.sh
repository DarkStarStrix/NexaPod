#!/usr/bin/env bash
# Cleanup all NexaPod Kubernetes resources
set -e
kubectl delete -f Infrastruture/k8s/ --ignore-not-found
kubectl delete configmap prometheus-scrape-nexapod -n monitoring --ignore-not-found
echo "NexaPod resources cleaned up successfully."

