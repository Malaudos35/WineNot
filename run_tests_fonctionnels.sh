#!/bin/bash

# Script pour lancer les tests fonctionnels de WineNot

set -e

echo "=== WineNot - Tests Fonctionnels ==="
echo ""

# Vérifier que Docker est en cours d'exécution
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker n'est pas disponible. Veuillez démarrer Docker."
    exit 1
fi

echo "✅ Docker détecté"
echo ""

# Démarrer Docker Compose si ce n'est pas déjà fait
if ! docker compose ps | grep -q "backend.*Up"; then
    echo "🚀 Démarrage de Docker Compose..."
    docker compose up --build -d
    
    echo "⏳ Attente du démarrage de l'API (5 secondes)..."
    sleep 5
fi

echo "✅ Stack Docker démarrée"
echo ""

# Lancer les tests (exécutés DANS le conteneur backend)
echo "🧪 Lancement des tests fonctionnels (dans le conteneur)..."
echo ""

# Attendre que l'API réponde sur le port 5000 (max 60s)
API_URL="http://localhost:5000/api"
echo "⏳ Attente de l'API à $API_URL (timeout 60s)..."
try=0
until [ $try -ge 60 ]
do
    code=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL" || echo 000)
    if [ "$code" != "000" ]; then
        echo "API répond (HTTP $code)"
        break
    fi
    try=$((try+1))
    sleep 1
done
if [ $try -ge 60 ]; then
    echo "❌ Timeout waiting for API to be available"
    exit 2
fi

# Exécuter pytest à l'intérieur du conteneur backend
# Installe pytest si besoin (éphémère)
if [ "$1" == "" ]; then
    docker compose exec backend bash -lc "pip install --no-cache-dir pytest pytest-cov >/dev/null 2>&1 || true; cd /app; pytest tests/test_functional_workflows.py -v"
else
    docker compose exec backend bash -lc "pip install --no-cache-dir pytest pytest-cov >/dev/null 2>&1 || true; cd /app; pytest tests/test_functional_workflows.py::$1 -v"
fi

echo ""
echo "✅ Tests terminés"
