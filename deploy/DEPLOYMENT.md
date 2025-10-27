# Google Cloud Run Deployment Guide

This guide walks you through deploying the Wisteria CTR Studio API to Google Cloud Run using modern Google Cloud services.

## Prerequisites

1. **Google Cloud Project**: Create a GCP project with billing enabled
2. **Google Cloud SDK**: Install the [gcloud CLI](https://cloud.google.com/sdk/docs/install) (latest version recommended)
3. **Docker** (optional): For local testing
4. **API Keys**: OpenAI and/or DeepSeek API keys (optional for mock mode)
5. **Permissions**: Editor or Cloud Run Admin role on the project

## Architecture Overview

The deployment uses:
- **Google Artifact Registry**: Modern container registry (replaces deprecated Container Registry)
- **Google Cloud Run**: Serverless container platform with auto-scaling
- **Google Secret Manager**: Secure API key storage
- **Google Cloud Storage**: Optional identity bank data storage
- **uvicorn**: High-performance ASGI server (direct, no gunicorn wrapper)

## Quick Deployment

### Option 1: Automated Deployment (Recommended)

**For Linux/Mac:**
```bash
# Make scripts executable
chmod +x deploy.sh setup-secrets.sh

# Deploy with default project name
./deploy.sh

# Or specify custom project and region
./deploy.sh YOUR_PROJECT_ID us-central1

# Set up API keys
./setup-secrets.sh wisteria-ctr-studio us-central1
```

**For Windows (PowerShell):**
```powershell
# Deploy the application
.\deploy.ps1

# Or with custom parameters
.\deploy.ps1 -ProjectId "YOUR_PROJECT_ID" -Region "us-central1"

# Set up API keys (run setup-secrets.sh via WSL or Git Bash)
```

### Option 2: Manual Deployment

1. **Enable APIs and create Artifact Registry:**
```bash
gcloud config set project wisteria-ctr-studio  # or YOUR_PROJECT_ID
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Create Artifact Registry repository
gcloud artifacts repositories create wisteria-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker repo for Wisteria CTR Studio"

# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev
```

2. **Build and deploy:**
```bash
# Build container image (using Artifact Registry)
gcloud builds submit --tag us-central1-docker.pkg.dev/wisteria-ctr-studio/wisteria-repo/wisteria-ctr-studio

# Deploy to Cloud Run
gcloud run deploy wisteria-ctr-studio \
    --image us-central1-docker.pkg.dev/wisteria-ctr-studio/wisteria-repo/wisteria-ctr-studio \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300s \
    --port 8080 \
    --set-env-vars "PYTHONPATH=/app"
```

## Configuration

### Environment Variables

The service supports these environment variables:

- `PORT`: Server port (default: 8080, set by Cloud Run)
- `OPENAI_API_KEY`: OpenAI API key
- `DEEPSEEK_API_KEY`: DeepSeek API key
- `PYTHONPATH`: Python path (set to /app)
- `GCS_BUCKET_NAME`: Google Cloud Storage bucket for identity bank (default: "wisteria-data-bucket")
- `GCS_IDENTITY_BANK_PATH`: Path to identity bank file in GCS (default: "data/identity_bank.json")

### Google Cloud Storage Setup (Optional)

Set up Google Cloud Storage for dynamic identity bank management:

```bash
# Create a bucket for data storage
gsutil mb gs://your-wisteria-bucket

# Upload identity bank to GCS
gsutil cp data/identity_bank.json gs://your-wisteria-bucket/data/identity_bank.json

# Set bucket permissions
gsutil iam ch serviceAccount:cloud-run-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com:objectViewer gs://your-wisteria-bucket

# Configure environment variables
gcloud run services update wisteria-ctr-studio \
    --update-env-vars GCS_BUCKET_NAME=your-wisteria-bucket \
    --update-env-vars GCS_IDENTITY_BANK_PATH=data/identity_bank.json
```

### Secret Manager (Recommended)

Store API keys securely using Google Secret Manager:

```bash
# Create secrets
gcloud secrets create openai-api-key --data-file=-
gcloud secrets create deepseek-api-key --data-file=-

# Update service to use secrets
gcloud run services update wisteria-ctr-studio \
    --update-secrets="OPENAI_API_KEY=openai-api-key:latest" \
    --update-secrets="DEEPSEEK_API_KEY=deepseek-api-key:latest"
```

## Testing the Deployment

### Automated Testing
```bash
# Run the comprehensive test suite
python test_gcs.py

# Test with custom API URL
API_BASE_URL=https://your-service-url python test_gcs.py
```

### Manual Testing

1. **Health Check:**
```bash
curl https://YOUR_SERVICE_URL/health
```

2. **Identity Bank Status:**
```bash
# Check identity bank source
curl https://YOUR_SERVICE_URL/identities

# Reload identity bank (if using GCS)
curl -X POST https://YOUR_SERVICE_URL/identities/reload
```

3. **API Documentation:**
Visit `https://YOUR_SERVICE_URL/docs` for interactive API documentation.

4. **Test CTR Prediction:**
```bash
curl -X POST "https://YOUR_SERVICE_URL/predict-ctr" \
  -H "Content-Type: application/json" \
  -d '{
    "ad_text": "Special offer on premium coffee",
    "population_size": 100,
    "use_mock": true
  }'
```

## Container & Runtime Configuration

### Docker Container Features
- **Base Image**: Python 3.11 slim (optimized for size and security)
- **Security**: Non-root user execution (appuser)
- **Health Checks**: Built-in health monitoring with 30-second startup grace period
- **Server**: uvicorn ASGI server (high-performance async processing)
- **Dependencies**: Google Cloud Storage support included

### Memory and CPU

Cloud Run is configured with:
- **Memory**: 2 GiB (required for LLM processing and GCS operations)
- **CPU**: 2 vCPUs (for better performance with concurrent requests)
- **Timeout**: 300 seconds (for long-running LLM calls)

### Scaling

- **Min instances**: 0 (cost-effective cold starts)
- **Max instances**: 10 (prevents runaway costs)
- **Concurrency**: Default (handles multiple concurrent requests efficiently)

### Modern Infrastructure
- **Registry**: Google Artifact Registry (replaces deprecated Container Registry)
- **Storage**: Google Cloud Storage integration for dynamic data management
- **Security**: Secret Manager for API keys, service account permissions

## Monitoring and Logs

### View Logs
```bash
gcloud run services logs read wisteria-ctr-studio --region=us-central1
```

### Monitoring
- Use Google Cloud Console > Cloud Run > wisteria-ctr-studio
- Monitor CPU, memory, and request metrics
- Set up alerts for errors or high usage

## Security

### IAM and Permissions

The service uses a dedicated service account with minimal permissions:
- `roles/secretmanager.secretAccessor`: Access to API keys
- `roles/run.invoker`: Service invocation

### API Security

- API keys are stored in Secret Manager
- Service runs with non-root user
- Network access controlled by Cloud Run

## Cost Optimization

### Tips to Reduce Costs

1. **Use Mock Mode**: For development/testing, use `use_mock: true`
2. **Smaller Populations**: Reduce `population_size` for testing
3. **Monitor Usage**: Track API calls and adjust limits
4. **Set Budgets**: Use Google Cloud billing alerts

### Estimated Costs

- **Cloud Run**: ~$0.00001667 per 100ms (2 vCPU, 2 GiB)
- **Artifact Registry**: Storage costs for Docker images (~$0.10/GB/month)
- **Cloud Storage**: GCS storage costs for identity bank (~$0.02/GB/month)
- **OpenAI API**: Varies by model and usage
- **DeepSeek API**: Generally lower cost than OpenAI

## Troubleshooting

### Common Issues

1. **Build Failures:**
   - Check Dockerfile syntax and dependencies in requirements.txt
   - Verify Artifact Registry repository exists and permissions are set
   - Ensure Docker authentication: `gcloud auth configure-docker us-central1-docker.pkg.dev`

2. **Deployment Failures:**
   - Check resource limits (memory/CPU) and timeout settings
   - Verify service account permissions for Secret Manager and GCS
   - Review logs for specific errors: health check timeout (increase start-period)

3. **Runtime Errors:**
   - Check API key configuration in Secret Manager
   - Verify GCS bucket exists and service account has access
   - Monitor memory usage during LLM processing
   - Test identity bank loading: `curl /identities`

4. **GCS Integration Issues:**
   - Verify bucket name and file path environment variables
   - Check service account has `roles/storage.objectViewer` permission
   - Test reload functionality: `curl -X POST /identities/reload`

### Debug Commands

```bash
# Check service status and configuration
gcloud run services describe wisteria-ctr-studio --region=us-central1

# View recent logs with more detail
gcloud run services logs read wisteria-ctr-studio --region=us-central1 --limit=100

# Test container locally with GCS
docker run -p 8080:8080 \
  -e GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json \
  -e GCS_BUCKET_NAME=your-bucket \
  us-central1-docker.pkg.dev/wisteria-ctr-studio/wisteria-repo/wisteria-ctr-studio

# Test Artifact Registry access
gcloud artifacts docker images list us-central1-docker.pkg.dev/wisteria-ctr-studio/wisteria-repo

# Check GCS permissions
gsutil iam get gs://your-bucket-name
```

## Advanced Configuration

### Custom Domain

```bash
# Map custom domain
gcloud run domain-mappings create --service=wisteria-ctr-studio --domain=api.yourdomain.com
```

### VPC Connector

For private network access:
```bash
gcloud run services update wisteria-ctr-studio \
    --vpc-connector=your-vpc-connector \
    --vpc-egress=private-ranges-only
```

### CI/CD Integration

Consider setting up automated deployment with:
- Google Cloud Build triggers
- GitHub Actions
- GitLab CI/CD

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Google Cloud Run documentation
3. Check project issues on GitHub
4. Monitor service logs for error details