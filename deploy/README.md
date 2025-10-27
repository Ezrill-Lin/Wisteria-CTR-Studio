# Deployment Files

This folder contains all files needed for deploying the Wisteria CTR Studio to various platforms.

## 📁 Files Overview

### **Core Deployment Scripts**
- **`deploy.sh`** - Linux/Mac deployment script for Google Cloud Run
- **`deploy.ps1`** - Windows PowerShell deployment script for Google Cloud Run
- **`setup-secrets.sh`** - Script to configure API keys in Google Secret Manager
- **`setup.sh`** - Initial setup script to make deployment scripts executable

### **Container Configuration**
- **`Dockerfile`** - Container image definition with Python 3.11, uvicorn server
- **`.dockerignore`** - Files to exclude from Docker build context
- **`cloud-run-service.yaml`** - Google Cloud Run service configuration template

### **Documentation**
- **`DEPLOYMENT.md`** - Comprehensive deployment guide with troubleshooting

## 🚀 Quick Start

### Automated Deployment

**Linux/Mac:**
```bash
# Make scripts executable
chmod +x deploy/deploy.sh deploy/setup-secrets.sh

# Deploy to Google Cloud Run
./deploy/deploy.sh wisteria-ctr-studio us-central1

# Set up API keys
./deploy/setup-secrets.sh wisteria-ctr-studio
```

**Windows PowerShell:**
```powershell
# Deploy to Google Cloud Run
.\deploy\deploy.ps1 -ProjectId "wisteria-ctr-studio" -Region "us-central1"

# Set up secrets (use WSL or Git Bash for setup-secrets.sh)
```

### Manual Deployment

1. **Build and push container:**
```bash
# From project root directory
docker build -f deploy/Dockerfile -t wisteria-ctr-studio .

# Or use Cloud Build
gcloud builds submit --config deploy/cloudbuild.yaml
```

2. **Deploy to Cloud Run:**
```bash
gcloud run deploy wisteria-ctr-studio \
  --image us-central1-docker.pkg.dev/PROJECT_ID/wisteria-repo/wisteria-ctr-studio \
  --platform managed \
  --region us-central1
```

## 🔧 Configuration

### Environment Variables
All deployment scripts support these configuration options:
- **Project ID**: Google Cloud Project ID (default: "wisteria-ctr-studio")
- **Region**: Deployment region (default: "us-central1")
- **Service Name**: Cloud Run service name (default: "wisteria-ctr-studio")

### Prerequisites
1. **Google Cloud SDK** installed and configured
2. **Docker** (optional, for local testing)
3. **Billing enabled** on your Google Cloud Project
4. **Required APIs** enabled (done automatically by scripts):
   - Cloud Build API
   - Cloud Run API
   - Artifact Registry API
   - Secret Manager API (for API keys)

## 📖 Detailed Documentation

For comprehensive deployment instructions, troubleshooting, and advanced configuration, see:
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Complete deployment guide

## 🛠️ Platform Support

### Supported Deployment Targets
- **Google Cloud Run** (recommended) - Serverless, auto-scaling
- **Docker** - Any container platform
- **Kubernetes** - Using the generated container image
- **Other Cloud Providers** - AWS ECS, Azure Container Instances, etc.

### Features
- **Modern Registry**: Uses Google Artifact Registry
- **Security**: Non-root container, Secret Manager integration
- **Performance**: uvicorn ASGI server, health checks
- **Scaling**: 0-10 instances, 2 vCPU, 2 GiB memory
- **Storage**: Google Cloud Storage integration for identity banks

## 🚨 Important Notes

- **Run from project root**: All deployment commands should be executed from the project root directory
- **File paths**: Scripts reference files relative to project root (e.g., `requirements.txt`, `api.py`)
- **Permissions**: Ensure you have appropriate Google Cloud permissions before deploying
- **API Keys**: Store sensitive API keys in Google Secret Manager, not in environment variables

## 🔗 Related Files

These deployment files work with:
- **`../api.py`** - Main FastAPI application
- **`../requirements.txt`** - Python dependencies
- **`../data/identity_bank.json`** - Default identity bank data
- **`../test_gcs.py`** - Deployment verification script