#!/bin/bash

# Google Cloud Run Deployment Script for Wisteria CTR Studio
# Usage: ./deploy.sh [PROJECT_ID] [REGION]

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root directory
cd "$PROJECT_ROOT"

# Configuration
PROJECT_ID=${1:-"wisteria-ctr-studio"}
REGION=${2:-"us-central1"}
SERVICE_NAME="wisteria-ctr-studio"
IMAGE_NAME="us-central1-docker.pkg.dev/${PROJECT_ID}/wisteria-repo/${SERVICE_NAME}"

echo "🚀 Deploying Wisteria CTR Studio to Google Cloud Run"
echo "Project Root: ${PROJECT_ROOT}"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo "📋 Setting GCP project..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Create Artifact Registry repository if it doesn't exist
echo "🔧 Checking Artifact Registry repository..."
if gcloud artifacts repositories describe wisteria-repo --location=us-central1 >/dev/null 2>&1; then
    echo "✅ Repository 'wisteria-repo' already exists. Skipping creation."
else
    echo "📦 Creating Artifact Registry repository 'wisteria-repo'..."
    gcloud artifacts repositories create wisteria-repo \
        --repository-format=docker \
        --location=us-central1 \
        --description="Docker repo for Wisteria CTR Studio"
fi

# Authenticate Docker with Artifact Registry
echo "🔐 Authenticating Docker with Artifact Registry..."
gcloud auth configure-docker us-central1-docker.pkg.dev


# Build and push container image
echo "🏗️  Building container image..."
gcloud builds submit --tag ${IMAGE_NAME} --file deploy/Dockerfile .

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300s \
    --min-instances 0 \
    --max-instances 10 \
    --port 8080 \
    --set-env-vars "PYTHONPATH=/app"

# Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)")

echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 Service URL: ${SERVICE_URL}"
echo "📖 API Documentation: ${SERVICE_URL}/docs"
echo "🏥 Health Check: ${SERVICE_URL}/health"
echo ""
echo "💡 Next steps:"
echo "1. Set up API keys using Secret Manager (see setup-secrets.sh)"
echo "2. Test the deployment using the service URL"
echo "3. Configure custom domain if needed"
echo ""

# Show logs
echo "📝 Recent logs:"
gcloud run services logs read ${SERVICE_NAME} --region=${REGION} --limit=10