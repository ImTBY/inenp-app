# inenp-app – Three-Tier Microservice Application

This repository contains a three-tier microservice application with Helm charts for deployment on Azure Kubernetes Service (AKS). The deployment is automated via GitHub Actions with optional GitOps using ArgoCD.

## 🏗️ Architecture

```
┌─────────────┐    HTTP     ┌─────────────┐    PostgreSQL   ┌─────────────┐
│   app_one   │─────────────│   app_two   │─────────────────│  postgres   │
│   (Express) │             │  (FastAPI)  │                 │ (Database)  │
│    :3000    │             │    :8000    │                 │    :5432    │
└─────────────┘             └─────────────┘                 └─────────────┘
```

- **app_one**: Express.js frontend serving a todo application
- **app_two**: FastAPI backend providing REST API for todo persistence
- **postgres**: PostgreSQL database for data storage

## 📦 Project Structure

```bash
.
├── app_one/                    # Express.js Frontend
│   ├── app/
│   │   ├── server.js
│   │   ├── package.json
│   │   └── public/
│   ├── charts/app/             # Helm chart for app_one
│   └── Dockerfile
│
├── app_two/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── charts/app-two/         # Helm chart for app_two
│   └── Dockerfile
│
├── database/                   # PostgreSQL Database
│   └── charts/postgres/        # Helm chart for PostgreSQL
│
└── .github/workflows/          # CI/CD Pipelines
    ├── docker-build-push.yml  # Build and push Docker images
    └── helm-cd.yml             # Deploy to AKS with Helm
```

## 🚀 Quick Start

### Prerequisites

- Kubernetes cluster with kubectl access
- Helm 3.x installed
- Docker images built and available

### Deployment

#### Option 1: Manual Deployment

1. **Create Namespace**
   ```bash
   kubectl create namespace app
   ```

2. **Deploy PostgreSQL Database**
   ```bash
   helm install postgres ./database/charts/postgres --namespace app
   kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgres --namespace app --timeout=300s
   ```

3. **Deploy app_two (FastAPI Backend)**
   ```bash
   helm install app-two ./app_two/charts/app-two --namespace app
   kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=app-two --namespace app --timeout=300s
   ```

4. **Deploy app_one (Express Frontend)**
   ```bash
   helm install app-one ./app_one/charts/app --namespace app
   ```

#### Option 2: Automated Deployment via GitHub Actions

Push to the `main` branch triggers automatic deployment to AKS.

### Access the Application

```bash
# Port-forward to access the todo application
kubectl port-forward svc/app-one 3000:3000 --namespace app
```

Then open http://localhost:3000 in your browser.

## 🔧 Configuration

### Service Communication

Within the "app" namespace, services communicate using these DNS names:

- **PostgreSQL**: `postgres:5432`
- **app_two (FastAPI)**: `app-two:80`  
- **app_one (Express)**: `app-one:3000`

### Environment Variables

#### app_one
- `APP_TWO_URL`: `http://app-two:80`

#### app_two
- `DB_HOST`: `postgres`
- `DB_NAME`: `testdb`
- `DB_USER`: `postgres`
- `DB_PASSWORD`: `password`
- `DB_PORT`: `5432`

#### postgres
- `POSTGRES_DB`: `testdb`
- `POSTGRES_USER`: `postgres`
- `POSTGRES_PASSWORD`: `password`

## 🔍 Verification & Troubleshooting

### Check Deployment Status

```bash
# Check all pods
kubectl get pods --namespace app

# Check services
kubectl get services --namespace app

# Check deployments
kubectl get deployments --namespace app
```

### View Logs

```bash
# app_one logs
kubectl logs -l app.kubernetes.io/name=app --namespace app

# app_two logs
kubectl logs -l app.kubernetes.io/name=app-two --namespace app

# postgres logs
kubectl logs -l app.kubernetes.io/name=postgres --namespace app
```

### Test Connectivity

```bash
# Test app_one -> app_two connection
kubectl exec -it deployment/app-one --namespace app -- curl http://app-two:80/

# Test app_two -> postgres connection
kubectl exec -it deployment/app-two --namespace app -- python -c "
import psycopg2
conn = psycopg2.connect(host='postgres', database='testdb', user='postgres', password='password', port=5432)
print('Connection successful')
"
```

## 🏃‍♂️ CI/CD Pipeline

### Docker Build Pipeline

- Triggers on changes to `app_one/` or `app_two/` directories
- Builds separate Docker images for each application
- Pushes to GitHub Container Registry

### Helm Deployment Pipeline

- Triggers on push to `main` branch
- Deploys to AKS in the correct order:
  1. PostgreSQL Database
  2. app_two (FastAPI Backend)
  3. app_one (Express Frontend)
- Includes connectivity tests and verification

## 📊 Monitoring

The deployment includes:

- **Health Checks**: Liveness and readiness probes for all services
- **Resource Limits**: CPU and memory constraints
- **Persistent Storage**: 10Gi PVC for PostgreSQL data
- **Security**: Non-root containers and security contexts

## 🧹 Cleanup

```bash
helm uninstall app-one --namespace app
helm uninstall app-two --namespace app
helm uninstall postgres --namespace app
kubectl delete namespace app
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with Docker Compose or Kubernetes
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.