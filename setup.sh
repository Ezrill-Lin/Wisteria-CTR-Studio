#!/bin/bash

# Setup script to make deployment scripts executable
# Run this after cloning the repository on Linux/Mac

echo "🔧 Setting up Wisteria CTR Studio deployment scripts..."

# Make scripts executable
chmod +x deploy.sh
chmod +x setup-secrets.sh

echo "✅ Scripts are now executable!"
echo ""
echo "📋 Available commands:"
echo "  ./deploy.sh [PROJECT_ID] [REGION]     - Deploy to Google Cloud Run"
echo "  ./setup-secrets.sh [PROJECT_ID]      - Configure API keys"
echo "  python api.py                        - Run development server"
echo "  docker build -t wisteria-ctr-studio . - Build Docker image"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT.md"