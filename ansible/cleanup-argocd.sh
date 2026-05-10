#!/bin/bash
# Manual cleanup script for ArgoCD CRDs and resources on VPS
# This is a fallback if Ansible cleanup doesn't work
# Usage: ssh -p 7022 debian@lvp.ovh 'bash -s' < cleanup-argocd.sh

set -e

export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

echo "=== Cleaning up ArgoCD CRDs and resources ==="

echo "1. Deleting ArgoCD custom resources..."
kubectl delete applicationsets,applications,appprojects --all-namespaces --ignore-not-found=true --cascade=foreground 2>/dev/null || true
sleep 2

echo "2. Deleting ArgoCD namespace..."
kubectl delete namespace argocd --ignore-not-found=true --grace-period=30 2>/dev/null || true
sleep 5

echo "3. Deleting orphaned cluster-scoped RBAC resources..."
for resource in $(kubectl get clusterrole,clusterrolebinding -o name 2>/dev/null | grep '^\(clusterrole\|clusterrolebinding\)\.rbac\.authorization\.k8s\.io/argocd' || true); do
  echo "   Deleting $resource..."
  kubectl delete "$resource" --ignore-not-found=true 2>/dev/null || true
done

echo "4. Force patching CRD finalizers..."
for crd in applications.argoproj.io appprojects.argoproj.io applicationsets.argoproj.io argocds.argoproj.io; do
  echo "   Patching $crd..."
  kubectl patch crd "$crd" -p '{"metadata":{"finalizers":[]}}' --type=merge 2>/dev/null || true
done

echo "5. Force deleting orphaned CRDs..."
for crd in applications.argoproj.io appprojects.argoproj.io applicationsets.argoproj.io argocds.argoproj.io; do
  echo "   Deleting $crd..."
  kubectl delete crd "$crd" --ignore-not-found=true --grace-period=0 --force 2>/dev/null || true
done

echo "6. Waiting for cleanup to complete..."
sleep 5

echo "7. Verification:"
echo "   ArgoCD namespaces:"
kubectl get ns argocd --ignore-not-found=true || echo "   ✓ argocd namespace removed"
echo "   ArgoCD CRDs:"
kubectl get crd | grep argoproj || echo "   ✓ No ArgoCD CRDs remaining"

echo ""
echo "=== Cleanup complete ==="
echo "You can now run: ansible-playbook -i ansible/inventory.yaml ansible/site.yaml -l vps_k3s_control"
