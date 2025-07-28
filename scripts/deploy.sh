#!/usr/bin/env bash
# shellcheck disable=SC2289
"""
Deploy NexaPod Kubernetes resources.
"""
set -euo pipefail
IFS=$'\n\t'

: "${KUBE_NAMESPACE:=default}"

kubectl apply -f ../Infrastruture/k8s/ -n "$KUBE_NAMESPACE"
kubectl apply -f ../Infrastruture/k8s/prometheus-scrape-nexapod.yaml -n "$KUBE_NAMESPACE"
kubectl rollout status deployment/nexapod-server -n "$KUBE_NAMESPACE"
kubectl rollout status deployment/nexapod-client -n "$KUBE_NAMESPACE"
echo "NexaPod deployed successfully to namespace '$KUBE_NAMESPACE'."
