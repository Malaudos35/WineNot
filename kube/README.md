# WineNot Kubernetes (winenot Helm Chart)

This folder contains a Helm chart `winenot` to deploy the WineNot stack (backend, CDN, Playwright, MySQL) and manifests to make the chart ArgoCD-ready.

Quick overview of what was added:

- `values.yaml` updated with defaults for `ingress`, `certManager`, `serviceAccount` and autoscaling.
- `templates/` additions:
  - `serviceaccount.yaml` — creates a ServiceAccount
  - `role.yaml`, `rolebinding.yaml` — namespace-scoped Role and RoleBinding for the ServiceAccount
  - `ingress.yaml` — Ingress for `lvp.ovh`, routes `/` to CDN and `/api` to backend
  - `certificate.yaml` — cert-manager `Certificate` resource to request TLS secret
  - `clusterissuers.yaml` — ClusterIssuer manifest (LetsEncrypt staging or prod) when enabled
  - `hpa-backend.yaml`, `hpa-cdn.yaml` — HorizontalPodAutoscaler manifests
  - `argocd-application.yaml` — example ArgoCD Application manifest to deploy the chart

Prerequisites for production deployment
---------------------------------------
You need the following components installed in your cluster before relying on automatic TLS and autoscaling:

1. Ingress Controller (example: nginx-ingress)
2. cert-manager (https://cert-manager.io/docs/)
3. A `ClusterIssuer` for Let's Encrypt (the chart can create one if `certManager.createClusterIssuer=true` but creating cluster-scoped resources often requires cluster-admin rights for ArgoCD)
4. metrics-server or Prometheus Adapter (for HPA to work) — ensure `metrics.k8s.io` API is available
5. ArgoCD (if you plan to deploy via ArgoCD)

Install cert-manager (example)
-----------------------------
```bash
kubectl apply --validate=false -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.crds.yaml
kubectl create namespace cert-manager
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager --namespace cert-manager --version v1.12.0
```

Create a ClusterIssuer (example using Let's Encrypt staging or production)
-----------------------------------------------------------------------
You can let the Helm chart create a `ClusterIssuer` if `certManager.createClusterIssuer=true` and ArgoCD has cluster-admin rights. Alternatively create it manually using:

`cluster-issuer-prod.yaml` (example):
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: you@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
```

Apply with:
```bash
kubectl apply -f cluster-issuer-prod.yaml
```

Deploy with ArgoCD
------------------
Edit `kube/winenot/argocd-application.yaml` and replace the `repoURL` with your repository URL, then apply it to the `argocd` namespace. The example file passes Helm values enabling ingress and cert-manager by default.

Notes and recommendations
-------------------------
- Replace `latest` image tags with fixed versions in `values.yaml` for reproducible deployments.
- If you don't want the chart to create cluster-scoped `ClusterIssuer` resources, set `certManager.createClusterIssuer=false` and create issuers manually with cluster-admin privileges.
- Monitor cert-manager logs and certificate/issuer status with `kubectl describe certificate <name>` and `kubectl describe clusterissuer <name>`.

If you want, I can:
- Add a `cluster-issuer` example file pre-filled with `email` from `values.yaml`.
- Make the ArgoCD Application create a separate `Namespace` manifest rather than relying on `CreateNamespace=true`.
- Lock image tags and add `imagePullSecrets` support to the ArgoCD manifest.

*** End of README
