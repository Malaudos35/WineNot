#!/bin/bash
# Deploy WineNot via ArgoCD using Ansible
# Usage: ./deploy-via-argocd.sh [--skip-kubeconfig]

set -e

VPS_HOST="debian@lvp.ovh"
VPS_PORT=7022
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_KUBECONFIG="$HOME/.kube/config-lvp-ovh"
SKIP_KUBECONFIG=false

# Parse arguments
if [ "$1" == "--skip-kubeconfig" ]; then
    SKIP_KUBECONFIG=true
fi

echo "=========================================="
echo "Deploy WineNot via ArgoCD"
echo "=========================================="
echo ""

# 1. Setup kubeconfig (unless skipped)
if [ "$SKIP_KUBECONFIG" != "true" ]; then
    echo "1️⃣  Setting up kubeconfig..."
    echo ""
    
    if [ ! -f "$LOCAL_KUBECONFIG" ]; then
        echo "📥 Fetching kubeconfig from VPS..."
        mkdir -p ~/.kube
        
        ssh -p $VPS_PORT $VPS_HOST "cat /etc/rancher/k3s/k3s.yaml" > "$LOCAL_KUBECONFIG"
        chmod 600 "$LOCAL_KUBECONFIG"
        
        if kubectl --kubeconfig="$LOCAL_KUBECONFIG" cluster-info &>/dev/null; then
            echo "✅ Kubeconfig fetched and verified"
        else
            echo "❌ Kubeconfig verification failed"
            exit 1
        fi
    else
        echo "✅ Kubeconfig already exists: $LOCAL_KUBECONFIG"
    fi
    
    echo ""
fi

# 2. Export kubeconfig for Ansible
export KUBECONFIG="${KUBECONFIG:-$LOCAL_KUBECONFIG}"

echo "2️⃣  Verifying cluster access..."
if kubectl cluster-info &>/dev/null; then
    echo "✅ Cluster accessible"
    echo "   Kubeconfig: $KUBECONFIG"
else
    echo "❌ Cluster not accessible"
    echo "   Please check: export KUBECONFIG=$LOCAL_KUBECONFIG"
    exit 1
fi

# 3. Verify Ansible
echo ""
echo "3️⃣  Checking Ansible..."
if ! command -v ansible-playbook &> /dev/null; then
    echo "❌ ansible-playbook not found. Install with: pip install ansible"
    exit 1
fi
echo "✅ Ansible found: $(ansible-playbook --version | head -1)"

# 4. Run playbook
echo ""
echo "4️⃣  Running Ansible playbook..."
echo "   Working directory: $SCRIPT_DIR"
echo ""

cd "$SCRIPT_DIR"

ansible-playbook \
    -i inventory/hosts.yml \
    deploy-argocd-and-app.yml \
    -v

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ DEPLOYMENT SUCCESSFUL"
    echo "=========================================="
    echo ""
    echo "🔗 Next steps:"
    echo ""
    echo "1️⃣  Get ArgoCD initial password:"
    echo "    kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d"
    echo ""
    echo "2️⃣  Port-forward to ArgoCD UI:"
    echo "    kubectl port-forward -n argocd svc/argocd-server 8080:443"
    echo ""
    echo "3️⃣  Access ArgoCD:"
    echo "    https://localhost:8080"
    echo "    Username: admin"
    echo "    Password: (from step 1)"
    echo ""
    echo "4️⃣  Check WineNot application:"
    echo "    kubectl -n winenot get pods"
    echo ""
else
    echo ""
    echo "❌ DEPLOYMENT FAILED"
    echo ""
    echo "Troubleshooting:"
    echo "  • Check kubeconfig: kubectl cluster-info"
    echo "  • Check namespace: kubectl get namespace argocd"
    echo "  • Check pods: kubectl -n argocd get pods"
    echo ""
    exit 1
fi
