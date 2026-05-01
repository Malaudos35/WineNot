#!/bin/bash
# Script de redéploiement WineNot K3s sur VPS lvp.ovh
# Usage: ./deploy-winenot.sh

set -e

KUBECONFIG="/etc/rancher/k3s/k3s.yaml"
NAMESPACE="winenot"
CHART_PATH="kube/winenot"
DOMAIN="lvp.ovh"

echo "=========================================="
echo "REDÉPLOIEMENT WINENOT K3s"
echo "=========================================="

# Vérifier kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl non trouvé"
    exit 1
fi

export KUBECONFIG

echo "✅ kubectl trouvé"

# 1. Vérifier que le certificat auto-signé existe
echo ""
echo "1️⃣  Vérification du certificat auto-signé..."
if kubectl -n $NAMESPACE get secret lvp-ovh-tls-selfsigned &>/dev/null; then
    echo "✅ Secret lvp-ovh-tls-selfsigned existant"
else
    echo "⚠️  Création du certificat auto-signé..."
    cd /tmp
    openssl req -x509 -newkey rsa:2048 -nodes -keyout tls.key -out tls.crt -subj "/CN=$DOMAIN" -days 365 2>/dev/null
    kubectl create secret tls lvp-ovh-tls-selfsigned --cert=tls.crt --key=tls.key -n $NAMESPACE
    rm -f tls.key tls.crt
    echo "✅ Certificat auto-signé créé"
fi

# 2. Créer ClusterIssuers Let's Encrypt
echo ""
echo "2️⃣  Création ClusterIssuers Let's Encrypt..."
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@$DOMAIN
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
    email: admin@$DOMAIN
    privateKeySecretRef:
      name: letsencrypt-staging-key
    solvers:
    - http01:
        ingress:
          class: traefik
EOF
echo "✅ ClusterIssuers créés"

# 3. Helm lint et template check
echo ""
echo "3️⃣  Validation Helm chart..."
if helm lint $CHART_PATH &>/dev/null; then
    echo "✅ Helm chart valide"
else
    echo "❌ Erreur Helm lint"
    exit 1
fi

# 4. Redéployer avec Helm
echo ""
echo "4️⃣  Redéploiement Helm..."
helm upgrade --install winenot $CHART_PATH \
    --namespace $NAMESPACE \
    --create-namespace \
    --values $CHART_PATH/values.yaml \
    --wait \
    --timeout 5m

echo "✅ Déploiement Helm complété"

# 5. Vérifier les pods
echo ""
echo "5️⃣  Vérification des pods..."
kubectl -n $NAMESPACE get pods
echo ""

# Attendre que les pods soient prêts
echo "⏳ Attente du démarrage des pods (30s)..."
sleep 30

# 6. Tester les endpoints
echo ""
echo "6️⃣  Tests des endpoints..."
echo ""
echo "🔹 HTTP (80):"
curl -s -I http://$DOMAIN/ | head -3 || echo "❌ HTTP échoué"

echo ""
echo "🔹 HTTPS (443) - self-signed:"
curl -s -k -I https://$DOMAIN/ | head -3 || echo "❌ HTTPS échoué"

echo ""
echo "7️⃣  État des certificats..."
kubectl -n $NAMESPACE get certificate
kubectl -n $NAMESPACE get secret | grep tls

echo ""
echo "=========================================="
echo "✅ REDÉPLOIEMENT TERMINÉ"
echo "=========================================="
echo ""
echo "🌐 Accès:"
echo "   - HTTP:  http://$DOMAIN"
echo "   - HTTPS: https://$DOMAIN (certificat auto-signé)"
echo ""
echo "📝 Pour activer Let's Encrypt:"
echo "   1. SSH sur le VPS et arrêter Apache:"
echo "      sudo systemctl stop apache2"
echo "      sudo systemctl disable apache2"
echo "   2. Modifier values.yaml: ingress.tls.secretName -> lvp-ovh-tls"
echo "   3. Redéployer: helm upgrade --install winenot ..."
echo "   4. Monitorer: kubectl -n winenot get certificate -w"
echo ""
