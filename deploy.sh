#!/bin/bash

# Google Cloud Run Deployment Script for Wisteria CTR Studio
# Usage: ./deploy.sh [PROJECT_ID] [REGION]

set -e

# Configuration
PROJECT_ID=${1:-"your-gcp-project-id"}
REGION=${2:-"us-central1"}
SERVICE_NAME="wisteria-ctr-studio"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying Wisteria CTR Studio to Google Cloud Run"
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

# Build and push container image
echo "🏗️  Building container image..."
gcloud builds submit --tag ${IMAGE_NAME}

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