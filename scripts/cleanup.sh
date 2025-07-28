#!/usr/bin/env bash
# shellcheck disable=SC2289
"""
Cleanup NexaPod Kubernetes resources.
"""
set -euo pipefail
IFS=$'\n\t'

: "${KUBE_NAMESPACE:=default}"

kubectl delete -f ../Infrastruture/k8s/ -n "$KUBE_NAMESPACE" --ignore-not-found
kubectl delete configmap prometheus-scrape-nexapod -n monitoring --ignore-not-found
echo "NexaPod resources cleaned up from namespace '$KUBE_NAMESPACE'."
