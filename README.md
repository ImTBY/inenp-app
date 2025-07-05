# inenp-app – Helm Charts & Microservice App

Dieses Repository enthält den Quellcode einer Beispiel-Microservice-Applikation sowie die zugehörigen Helm-Charts für die Bereitstellung auf einem Azure Kubernetes Service (AKS) Cluster. Das Deployment erfolgt automatisiert über GitHub Actions und optional GitOps mit ArgoCD.

## 📦 Projektstruktur

```bash
.
├── app/                    # Node.js Express App (z. B. Todo-Liste)
│   ├── server.js
│   ├── Dockerfile
│   ├── public/
│   └── package.json
│
├── charts/                # Helm-Charts für Service A/B & DB
│   └── app/
│       ├── templates/
│       ├── values.yaml
│       └── Chart.yaml
│
└── .github/workflows/     # CI/CD Pipelines für Helm CD
    └── helm-cd.yml
