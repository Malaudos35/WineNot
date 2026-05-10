#!/bin/bash
# Deploy WineNot on K3s VPS using ArgoCD
# Run this script DIRECTLY ON THE VPS (ssh -p 7022 debian@lvp.ovh "bash deploy-from-vps.sh")

set -e
set +o pipefail

export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
NAMESPACE_ARGOCD="argocd"
NAMESPACE_WINENOT="winenot"
APP_NAME="winenot"

echo "=========================================="
echo "Deploy WineNot via ArgoCD on K3s"
echo "=========================================="
echo ""

# 1. Verify kubectl
echo "1️⃣  Verifying kubectl..."
if ! kubectl cluster-info &>/dev/null; then
    echo "❌ kubectl not accessible"
    exit 1
fi
echo "✅ Kubectl accessible"
kubectl cluster-info

# 2. Create ArgoCD namespace
echo ""
echo "2️⃣  Creating ArgoCD namespace..."
kubectl create namespace $NAMESPACE_ARGOCD --dry-run=client -o yaml | kubectl apply -f -
echo "✅ ArgoCD namespace ready"

# 3. Install ArgoCD
echo ""
echo "3️⃣  Installing ArgoCD..."
kubectl apply --server-side --force-conflicts -n $NAMESPACE_ARGOCD -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
echo "⏳ Waiting for ArgoCD to be ready..."
kubectl -n $NAMESPACE_ARGOCD rollout status deployment/argocd-server --timeout=180s
echo "✅ ArgoCD installed and ready"

# 4. Create WineNot namespace
echo ""
echo "4️⃣  Creating WineNot namespace..."
kubectl create namespace $NAMESPACE_WINENOT --dry-run=client -o yaml | kubectl apply -f -
echo "✅ WineNot namespace ready"

# 5. Create certificates and ClusterIssuers
echo ""
echo "5️⃣  Creating Let's Encrypt ClusterIssuers..."
kubectl apply -f - <<'ISSUER_EOF' || true
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@lvp.ovh
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
    - http01:
        ingress:
          class: traefik
---
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: admin@lvp.ovh
    privateKeySecretRef:
      name: letsencrypt-staging-key
    solvers:
    - http01:
        ingress:
          class: traefik
ISSUER_EOF
echo "✅ ClusterIssuers created"

# 6. Create self-signed certificate
echo ""
echo "6️⃣  Creating self-signed TLS certificate..."
cd /tmp
openssl req -x509 -newkey rsa:2048 -nodes -keyout tls.key -out tls.crt -subj "/CN=lvp.ovh" -days 365 2>/dev/null
kubectl create secret tls lvp-ovh-tls-selfsigned \
    --cert=tls.crt \
    --key=tls.key \
    -n $NAMESPACE_WINENOT \
    --dry-run=client -o yaml | kubectl apply -f -
rm -f tls.key tls.crt
echo "✅ Self-signed certificate created"

# 7. Create ArgoCD Application
echo ""
echo "7️⃣  Creating ArgoCD Application for WineNot..."
kubectl -n $NAMESPACE_ARGOCD apply -f - <<'APP_EOF'
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: winenot
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://github.com/Malaudos35/WineNot.git'
    targetRevision: 'dev/Malaudos35/kube'
    path: 'kube/winenot'
    helm:
      values: |
        backend:
          image:
            repository: winenot-backend
            tag: local
        mysql:
          image:
            tag: '9.5'
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: winenot
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
APP_EOF
echo "✅ ArgoCD Application created"

# 8. Wait for sync
echo ""
echo "8️⃣  Waiting for initial sync..."
sleep 5
kubectl -n argocd get application winenot

# 9. Wait for pods
echo ""
echo "⏳ Waiting 30 seconds for pods to start..."
sleep 30

# 10. Check status
echo ""
echo "9️⃣  Final status..."
echo ""
echo "🔹 Pods:"
kubectl -n $NAMESPACE_WINENOT get pods

echo ""
echo "🔹 Ingress:"
kubectl -n $NAMESPACE_WINENOT get ingress

echo ""
echo "🔹 TLS Certificates:"
kubectl -n $NAMESPACE_WINENOT get secret | grep tls

echo ""
echo "🔹 ArgoCD Application:"
kubectl -n $NAMESPACE_ARGOCD get application $APP_NAME

# 11. Get ArgoCD password
echo ""
echo "🔑 ArgoCD Initial Admin Password:"
ARGOCD_PASS=$(kubectl -n $NAMESPACE_ARGOCD get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' 2>/dev/null | base64 -d)
if [ -n "$ARGOCD_PASS" ]; then
    echo "   Username: admin"
    echo "   Password: $ARGOCD_PASS"
fi

# 12. Start ArgoCD port-forward in background
echo ""
echo "1️⃣0️⃣  Starting ArgoCD port-forward..."
kubectl port-forward -n $NAMESPACE_ARGOCD svc/argocd-server 8080:443 >/dev/null 2>&1 &
PORT_FORWARD_PID=$!
echo "✅ ArgoCD port-forward started (PID: $PORT_FORWARD_PID)"

echo ""
echo "========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "🌐 Access WineNot:"
echo "   https://lvp.ovh (self-signed TLS)"
echo ""
echo "📊 Access ArgoCD (port-forward active):"
echo "   https://localhost:8080"
echo "   Username: admin"
if [ -n "$ARGOCD_PASS" ]; then
    echo "   Password: $ARGOCD_PASS"
fi
echo ""
echo "📋 Check status:"
echo "   kubectl -n winenot get pods"
echo "   kubectl -n winenot logs deployment/winenot-backend -f"
echo ""
