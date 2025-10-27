#!/bin/bash

# Secret Manager Setup Script for Wisteria CTR Studio
# This script creates secrets for API keys in Google Secret Manager

set -e

PROJECT_ID=${1:-"wisteria-ctr-studio"}
REGION=${2:-"us-central1"}
SERVICE_NAME="wisteria-ctr-studio"

echo "🔐 Setting up secrets for Wisteria CTR Studio"
echo "Project: ${PROJECT_ID}"
echo ""

# Enable Secret Manager API
echo "🔧 Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com

# Function to create or update secret
create_or_update_secret() {
    local secret_name=$1
    local secret_description=$2
    
    echo "📝 Setting up secret: ${secret_name}"
    
    # Check if secret exists
    if gcloud secrets describe ${secret_name} >/dev/null 2>&1; then
        echo "Secret ${secret_name} already exists"
    else
        echo "Creating secret ${secret_name}..."
        gcloud secrets create ${secret_name} \
            --replication-policy="automatic" \
            --data-file="-" \
            --labels="service=${SERVICE_NAME}"
    fi
    
    echo "Please enter the ${secret_description}:"
    read -s secret_value
    
    if [ -n "$secret_value" ]; then
        echo "Updating secret value..."
        echo -n "$secret_value" | gcloud secrets versions add ${secret_name} --data-file=-
        echo "✅ Secret ${secret_name} updated successfully"
    else
        echo "⚠️  No value provided for ${secret_name}"
    fi
    echo ""
}

# Create secrets for API keys
create_or_update_secret "openai-api-key" "OpenAI API Key"
create_or_update_secret "deepseek-api-key" "DeepSeek API Key"

# Create service account for Cloud Run
echo "👤 Creating service account..."
SERVICE_ACCOUNT="cloud-run-service-account"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com"

if gcloud iam service-accounts describe ${SERVICE_ACCOUNT_EMAIL} >/dev/null 2>&1; then
    echo "Service account already exists"
else
    gcloud iam service-accounts create ${SERVICE_ACCOUNT} \
        --display-name="Cloud Run Service Account for Wisteria CTR Studio"
fi

# Grant necessary permissions
echo "🔑 Granting permissions..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/run.invoker"

# Update Cloud Run service to use secrets
echo "🔄 Updating Cloud Run service configuration..."
gcloud run services update ${SERVICE_NAME} \
    --region=${REGION} \
    --service-account=${SERVICE_ACCOUNT_EMAIL} \
    --update-secrets="OPENAI_API_KEY=openai-api-key:latest" \
    --update-secrets="DEEPSEEK_API_KEY=deepseek-api-key:latest" \
    --quiet || echo "⚠️  Service update failed. Make sure the service is deployed first."

echo ""
echo "✅ Secret setup completed!"
echo ""
echo "📋 Summary:"
echo "- Created secrets: openai-api-key, deepseek-api-key"
echo "- Created service account: ${SERVICE_ACCOUNT_EMAIL}"
echo "- Granted necessary permissions"
echo "- Updated Cloud Run service configuration"
echo ""
echo "💡 To verify secrets:"
echo "gcloud secrets list"
echo "gcloud secrets versions access latest --secret=openai-api-key"