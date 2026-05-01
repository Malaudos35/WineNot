# Deployment with Ansible

This folder contains an Ansible playbook to install ArgoCD in the cluster and create an ArgoCD `Application` that deploys the `winenot` Helm chart from this repository.

## Prerequisites

- `ansible` installed: `pip install ansible`
- SSH access to the K3s VPS (default: `ssh -p 7022 debian@lvp.ovh`)
- K3s cluster running with kubeconfig accessible

## Quick Start

### Option 1: Automated Deployment (Recommended)

Run the deployment wrapper script:

```bash
cd deployment
bash deploy-via-argocd.sh
```

This script will:
1. ✅ Fetch kubeconfig from VPS K3s
2. ✅ Verify cluster access
3. ✅ Run Ansible playbook to deploy ArgoCD
4. ✅ Create WineNot application in ArgoCD

### Option 2: Manual Deployment

#### Step 1: Setup kubeconfig

```bash
cd deployment
bash setup-kubeconfig.sh
```

This retrieves the kubeconfig from the VPS K3s cluster to `~/.kube/config-lvp-ovh`.

#### Step 2: Export kubeconfig

```bash
export KUBECONFIG=~/.kube/config-lvp-ovh
```

#### Step 3: Verify cluster access

```bash
kubectl cluster-info
kubectl get nodes
```

#### Step 4: Edit configuration

Edit `group_vars/all.yml` to customize:
- `repo_url`: Your WineNot repository URL
- `target_revision`: Git branch (default: `dev/Malaudos35/kube`)
- `ingress_host`: Domain name (default: `lvp.ovh`)
- `email`: ACME email for Let's Encrypt
- `use_staging`: Use staging Let's Encrypt (default: `false`)

#### Step 5: Run playbook

```bash
ansible-playbook -i inventory/hosts.yml deploy-argocd-and-app.yml
```

## Configuration

### group_vars/all.yml

```yaml
repo_url: 'https://github.com/Malaudos35/WineNot.git'  # Your repo
repo_path: 'kube/winenot'                               # Helm chart path
target_revision: 'dev/Malaudos35/kube'                  # Git branch
app_namespace: 'winenot'                                # K8s namespace
app_name: 'winenot'                                     # App name
argocd_namespace: 'argocd'                              # ArgoCD namespace
ingress_host: 'lvp.ovh'                                 # Domain
email: 'admin@lvp.ovh'                                  # ACME email
use_staging: false                                      # Let's Encrypt staging
ingress_enabled: true                                   # Enable ingress
backend_min_replicas: 2                                 # Min backend pods
backend_max_replicas: 5                                 # Max backend pods
```

## What It Does

1. **Creates ArgoCD namespace** in the K8s cluster
2. **Installs ArgoCD** using the official upstream manifest
3. **Waits for ArgoCD server** to be ready
4. **Creates application namespace** (default: `winenot`)
5. **Renders ArgoCD Application manifest** from template
6. **Applies Application** to start syncing WineNot

## After Deployment

### Access ArgoCD UI

```bash
# 1. Port-forward to ArgoCD server
kubectl port-forward -n argocd svc/argocd-server 8080:443

# 2. Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d

# 3. Open browser
https://localhost:8080
```

### Verify WineNot Deployment

```bash
# Check pods
kubectl -n winenot get pods

# Check application status
kubectl -n argocd get application winenot -o wide

# Check ingress
kubectl -n winenot get ingress

# Check certificate
kubectl -n winenot get certificate
```

## Troubleshooting

### "permission denied" on kubeconfig

**Error:**
```
error: error loading config file "/etc/rancher/k3s/k3s.yaml": open /etc/rancher/k3s/k3s.yaml: permission denied
```

**Solution:**
```bash
# Run the setup script to fetch kubeconfig locally
bash setup-kubeconfig.sh

# Then export it
export KUBECONFIG=~/.kube/config-lvp-ovh
```

### Kubeconfig not found

**Error:**
```
Unable to read /etc/rancher/k3s/k3s.yaml
```

**Solution:**
```bash
# Verify SSH access to VPS
ssh -p 7022 debian@lvp.ovh "kubectl version"

# Setup kubeconfig
bash setup-kubeconfig.sh
```

### Ansible not found

**Error:**
```
ansible-playbook: command not found
```

**Solution:**
```bash
pip install ansible
ansible-playbook --version
```

### ArgoCD pods not starting

```bash
# Check ArgoCD namespace
kubectl -n argocd get pods

# Check logs
kubectl -n argocd logs -l app=argocd-server --tail=50

# Check events
kubectl -n argocd get events --sort-by='.lastTimestamp'
```

## Notes

- The playbook uses `kubectl` commands to apply manifests
- The rendered Application references the Helm chart path `kube/winenot` inside the repository
- Ensure `repo_url` is accessible to ArgoCD (public repo or with credentials)
- The playbook runs locally (`connection: local`), no SSH to remote hosts needed by Ansible
- However, setup scripts use SSH to fetch kubeconfig from the VPS

## Useful Commands

```bash
# Check cluster
kubectl cluster-info
kubectl get nodes
kubectl get namespace

# Check ArgoCD
kubectl -n argocd get all
kubectl -n argocd describe application winenot

# Check WineNot
kubectl -n winenot get pods
kubectl -n winenot get ingress
kubectl -n winenot get certificate

# Sync application manually
kubectl -n argocd patch application winenot -p '{"metadata":{"annotations":{"argocd.argoproj.io/compare-result":"unknown"}}}'
argocd app sync winenot  # If ArgoCD CLI installed
```
