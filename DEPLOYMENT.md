# Google Cloud Run Deployment Guide

This guide walks you through deploying the Wisteria CTR Studio API to Google Cloud Run.

## Prerequisites

1. **Google Cloud Project**: Create a GCP project with billing enabled
2. **Google Cloud SDK**: Install the [gcloud CLI](https://cloud.google.com/sdk/docs/install)
3. **Docker** (optional): For local testing
4. **API Keys**: OpenAI and/or DeepSeek API keys

## Quick Deployment

### Option 1: Automated Deployment (Recommended)

**For Linux/Mac:**
```bash
# Make scripts executable
chmod +x deploy.sh setup-secrets.sh

# Deploy the application
./deploy.sh YOUR_PROJECT_ID us-central1

# Set up API keys
./setup-secrets.sh YOUR_PROJECT_ID us-central1
```

**For Windows (PowerShell):**
```powershell
# Deploy the application
.\deploy.ps1 -ProjectId "YOUR_PROJECT_ID" -Region "us-central1"

# Set up API keys (run setup-secrets.sh via WSL or Git Bash)
```

### Option 2: Manual Deployment

1. **Set up your project:**
```bash
gcloud config set project YOUR_PROJECT_ID
gcloud services enable cloudbuild.googleapis.com run.googleapis.com
```

2. **Build and deploy:**
```bash
# Build container image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/wisteria-ctr-studio

# Deploy to Cloud Run
gcloud run deploy wisteria-ctr-studio \
    --image gcr.io/YOUR_PROJECT_ID/wisteria-ctr-studio \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300s \
    --port 8080
```

## Configuration

### Environment Variables

The service supports these environment variables:

- `PORT`: Server port (default: 8080, set by Cloud Run)
- `OPENAI_API_KEY`: OpenAI API key
- `DEEPSEEK_API_KEY`: DeepSeek API key
- `PYTHONPATH`: Python path (set to /app)

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

1. **Health Check:**
```bash
curl https://YOUR_SERVICE_URL/health
```

2. **API Documentation:**
Visit `https://YOUR_SERVICE_URL/docs` for interactive API documentation.

3. **Test CTR Prediction:**
```bash
curl -X POST "https://YOUR_SERVICE_URL/predict-ctr" \
  -H "Content-Type: application/json" \
  -d '{
    "ad_text": "Special offer on premium coffee",
    "population_size": 100,
    "use_mock": true
  }'
```

## Resource Configuration

### Memory and CPU

Cloud Run is configured with:
- **Memory**: 2 GiB (required for LLM processing)
- **CPU**: 2 vCPUs (for better performance)
- **Timeout**: 300 seconds (for long-running LLM calls)

### Scaling

- **Min instances**: 0 (cost-effective)
- **Max instances**: 10 (prevents runaway costs)
- **Concurrency**: Default (handles multiple requests)

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
- **OpenAI API**: Varies by model and usage
- **DeepSeek API**: Generally lower cost than OpenAI
- **Container Registry**: Storage costs for Docker images

## Troubleshooting

### Common Issues

1. **Build Failures:**
   - Check Dockerfile syntax
   - Verify all dependencies in requirements.txt
   - Ensure proper file permissions

2. **Deployment Failures:**
   - Check resource limits (memory/CPU)
   - Verify service account permissions
   - Review logs for specific errors

3. **Runtime Errors:**
   - Check API key configuration
   - Verify network connectivity
   - Monitor memory usage

### Debug Commands

```bash
# Check service status
gcloud run services describe wisteria-ctr-studio --region=us-central1

# View recent logs
gcloud run services logs read wisteria-ctr-studio --region=us-central1 --limit=50

# Test container locally
docker run -p 8080:8080 gcr.io/YOUR_PROJECT_ID/wisteria-ctr-studio
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