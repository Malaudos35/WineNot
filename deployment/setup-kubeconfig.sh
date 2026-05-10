#!/bin/bash
# Setup kubeconfig from VPS K3s for local Ansible execution

set -e

VPS_HOST="debian@lvp.ovh"
VPS_PORT=7022
LOCAL_KUBECONFIG="$HOME/.kube/config-lvp-ovh"

echo "=========================================="
echo "Setup kubeconfig from VPS K3s"
echo "=========================================="

# 1. SSH copy kubeconfig
echo ""
echo "1️⃣  Retrieving kubeconfig from VPS..."
mkdir -p ~/.kube

ssh -p $VPS_PORT $VPS_HOST "cat /etc/rancher/k3s/k3s.yaml" > "$LOCAL_KUBECONFIG"

if [ $? -eq 0 ]; then
    echo "✅ Kubeconfig saved to: $LOCAL_KUBECONFIG"
else
    echo "❌ Failed to retrieve kubeconfig"
    exit 1
fi

# 2. Fix kubeconfig permissions
chmod 600 "$LOCAL_KUBECONFIG"
echo "✅ Permissions fixed"

# 3. Verify kubeconfig
echo ""
echo "2️⃣  Verifying kubeconfig..."
export KUBECONFIG="$LOCAL_KUBECONFIG"

if kubectl cluster-info &>/dev/null; then
    echo "✅ Kubeconfig valid and accessible"
else
    echo "❌ Kubeconfig verification failed"
    exit 1
fi

# 4. Show cluster info
echo ""
echo "3️⃣  Cluster information:"
kubectl cluster-info
echo ""

# 5. Set environment
echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "🔧 To use this kubeconfig:"
echo ""
echo "   export KUBECONFIG=$LOCAL_KUBECONFIG"
echo ""
echo "Or run Ansible with:"
echo ""
echo "   KUBECONFIG=$LOCAL_KUBECONFIG ansible-playbook -i inventory/hosts.yml deploy-argocd-and-app.yml"
echo ""
