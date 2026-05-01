# Deployment with Ansible

This folder contains an Ansible playbook to install ArgoCD in the cluster and create an ArgoCD `Application` that deploys the `winenot` Helm chart from this repository.

Pre-requisites:
- `kubectl` configured to access the target cluster from the host running Ansible
- `ansible` installed (the playbook runs locally, no remote hosts required)

Usage:

1. Edit `group_vars/all.yml` to set `repo_url` to your repository URL and other variables (email, host, etc.).

2. Run the playbook locally:

```bash
cd deployment
ansible-playbook -i inventory/hosts.yml deploy-argocd-and-app.yml
```

What it does:
- Creates the `argocd` namespace
- Installs ArgoCD using the official install manifest
- Waits for the `argocd-server` to be ready
- Creates the application namespace (defined in `group_vars/all.yml`)
- Renders and applies an `Application` manifest (templates/argocd-application.yaml.j2) into the `argocd` namespace

Notes:
- The playbook uses `kubectl` commands to apply manifests. If you prefer, this can be converted to use the `kubernetes.core` Ansible collection.
- The rendered Application references the Helm chart path `kube/winenot` inside the same repository — ensure the `repo_url` and `repo_path` are correct and accessible to ArgoCD.
