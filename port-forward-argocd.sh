#!/bin/bash
# Script to open ArgoCD port-forward

echo "Connecting to VPS and starting ArgoCD port-forward..."
echo "Port: 8080"
echo "URL: https://localhost:8080"
echo "Username: admin"
echo ""
echo "Press Ctrl+C to stop the port-forward"
echo ""

ssh -p 7022 debian@lvp.ovh "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml && kubectl port-forward -n argocd svc/argocd-server 8080:443"
