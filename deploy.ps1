# Google Cloud Run Deployment Script for Wisteria CTR Studio (PowerShell)
# Usage: .\deploy.ps1 [PROJECT_ID] [REGION]

param(
    [string]$ProjectId = "your-gcp-project-id",
    [string]$Region = "us-central1"
)

$ServiceName = "wisteria-ctr-studio"
$ImageName = "gcr.io/$ProjectId/$ServiceName"

Write-Host "🚀 Deploying Wisteria CTR Studio to Google Cloud Run" -ForegroundColor Green
Write-Host "Project: $ProjectId"
Write-Host "Region: $Region"
Write-Host "Service: $ServiceName"
Write-Host ""

# Check if gcloud is installed
if (!(Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: gcloud CLI is not installed" -ForegroundColor Red
    Write-Host "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Set project
Write-Host "📋 Setting GCP project..." -ForegroundColor Yellow
gcloud config set project $ProjectId

# Enable required APIs
Write-Host "🔧 Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push container image
Write-Host "🏗️  Building container image..." -ForegroundColor Yellow
gcloud builds submit --tag $ImageName

# Deploy to Cloud Run
Write-Host "🚀 Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --image $ImageName `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --timeout 300s `
    --min-instances 0 `
    --max-instances 10 `
    --port 8080 `
    --set-env-vars "PYTHONPATH=/app"

# Get service URL
$ServiceUrl = gcloud run services describe $ServiceName --region=$Region --format="value(status.url)"

Write-Host ""
Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
Write-Host "🌐 Service URL: $ServiceUrl" -ForegroundColor Cyan
Write-Host "📖 API Documentation: $ServiceUrl/docs" -ForegroundColor Cyan
Write-Host "🏥 Health Check: $ServiceUrl/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Next steps:" -ForegroundColor Yellow
Write-Host "1. Set up API keys using Secret Manager (see setup-secrets.ps1)"
Write-Host "2. Test the deployment using the service URL"
Write-Host "3. Configure custom domain if needed"
Write-Host ""

# Show logs
Write-Host "📝 Recent logs:" -ForegroundColor Yellow
gcloud run services logs read $ServiceName --region=$Region --limit=10