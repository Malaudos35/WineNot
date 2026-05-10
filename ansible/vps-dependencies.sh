#!/bin/bash
# VPS lvp.ovh dependencies installation script
# Run with: sudo bash vps-dependencies.sh

set -e

echo "=== Updating system ==="
apt-get update
apt-get dist-upgrade -y

echo "=== Installing Python and build tools ==="
apt-get install -y \
    python3-full \
    python3-dev \
    python3-pip \
    python3-venv \
    build-essential \
    curl \
    wget \
    git

echo "=== Installing Python packages for Ansible ==="
pip3 install --upgrade pip setuptools wheel
pip3 install --upgrade \
    ansible-core>=2.15 \
    kubernetes>=24.0.0 \
    PyYAML>=5.4 \
    jsonpatch>=1.9 \
    pyyaml \
    jinja2

echo "=== Installing Helm ==="
if ! command -v helm &> /dev/null; then
    curl -fsSL https://get.helm.sh/helm-v3.14.0-linux-amd64.tar.gz | tar -xz
    mv linux-amd64/helm /usr/local/bin/
    chmod +x /usr/local/bin/helm
    rm -rf linux-amd64
fi
helm version

echo "=== Verifying kubectl (part of K3s) ==="
kubectl version --short || echo "WARNING: kubectl not in PATH, checking K3s installation..."
/usr/local/bin/k3s --version || echo "K3s should be installed separately"

echo "=== All dependencies installed successfully ==="
