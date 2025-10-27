# Wisteria CTR Studio

## Overview
- Generates synthetic identities from a configurable identity bank JSON
- Uses modular LLM clients to predict binary clicks (1/0) for advertisements across different platforms
- Supports multiple LLM providers with async/sync processing modes
- Computes CTR from predictions and optionally saves detailed results
- Includes intelligent mock fallback for offline development and testing

## Architecture
The project uses a modular client system for LLM providers:
- **Base Client**: `base_client.py` - Abstract base class defining the client interface
- **Provider Clients**: Concrete implementations for different LLM providers
- **Registry System**: Dynamic provider registration in `llm_click_model.py`
- **Extensibility**: Easy to add new providers using the template client

## System Workflow
The following flowchart illustrates the complete working structure of the Wisteria CTR Studio web application:

```
                        ┌───────────────────────┐
                        │ 1. Ad Ingestion Layer │
                        └───────────────────────┘
                                    │
      ┌─────────────────────────────┼─────────────────────────────┐
      │                             │                             │
┌──────────────┐           ┌────────────────┐            ┌────────────────┐
│ Textual Ads  │           │ Graphic Ads    │            │ Video Ads      │
└──────────────┘           └────────────────┘            └────────────────┘
      │                             │                             │
      └─────────────────────────────┴─────────────────────────────┘
                                    │
                                    ▼
                       ┌────────────────────────┐
                       │2. Simulated Ad Platform│
                       │(e.g., mock webpage sim │
                       │of Facebook/TikTok etc.)│
                       └────────────────────────┘
                                    │
                                    ▼
                       ┌────────────────────────┐
                       │3. Data Conversion Agent│
                       │(OCR + Text Extractor   │
                       │ + Metadata Parser)     │
                       └────────────────────────┘
                                    │
                                    ▼
                       ┌──────────────────────┐
                       │ 4. Prompt Generator  │
                       │ (Combines extracted  │
                       │  text + platform ctx │
                       │  + ad metadata)      │
                       └──────────────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────────┐
       │ 5. Persona Simulation Layer (Big Five Personality Agents)  │
       └────────────────────────────────────────────────────────────┘
           │          │          │          │          │
           ▼          ▼          ▼          ▼          ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│ Openness     ││ Conscientious││ Extraversion ││ Agreeableness││ Neuroticism  │
│ Agent        ││ Agent        ││ Agent        ││ Agent        ││ Agent        │
└──────────────┘└──────────────┘└──────────────┘└──────────────┘└──────────────┘
           │          │          │          │          │          │
           └──────────┴──────────┴──────────┴──────────┴──────────┘
                                    │
                                    ▼
                 ┌────────────────────────────────────┐
                 │ 6. Response Aggregator             │
                 │ (Collects persona outputs, merges  │
                 │  descriptive paragraphs + features)│
                 └────────────────────────────────────┘
                                    │
                                    ▼
                 ┌────────────────────────────────────┐
                 │ 7. Synthetic Population Integrator │
                 │ (Combines persona results with     │
                 │  demographic data from Identity Bank)│
                 └────────────────────────────────────┘
                                    │
                                    ▼
                 ┌────────────────────────────────────┐
                 │ 8. CTR Prediction Agent            │
                 │ (Generates final predicted CTR     │
                 │  values for given ad/platform)     │
                 └────────────────────────────────────┘
                                    │
                                    ▼
                 ┌────────────────────────────────────┐
                 │ 9. Visualization Layer             │
                 │ (CTR dashboard, persona breakdown, │
                 │   platform comparisons, etc.)      │
                 └────────────────────────────────────┘
```

## Files
- `data/identity_bank.json`: Identity category definitions and sampling distributions
- `sampler.py`: Sampling utilities to generate synthetic identities
- `base_client.py`: Abstract base class for LLM client implementations
- `openai_client.py`: OpenAI/ChatGPT client implementation
- `deepseek_client.py`: DeepSeek API client implementation
- `template_client.py`: Template for implementing new LLM provider clients
- `llm_click_model.py`: Main predictor with provider registry and mock fallback
- `demo.py`: CLI entry point to run experiments and compute CTR
- `api.py`: FastAPI web service for REST API access
- `example_client.py`: Example Python client for the REST API
- `test_gcs.py`: Test script for Google Cloud Storage integration
- `requirements.txt`: Python dependency specifications
- `deploy/`: Complete deployment configuration and scripts
  - `Dockerfile`: Container configuration for deployment
  - `DEPLOYMENT.md`: Comprehensive deployment guide  
  - `deploy.sh` / `deploy.ps1`: Automated deployment scripts
  - `setup-secrets.sh`: Script for configuring API keys securely
  - `cloud-run-service.yaml`: Cloud Run service configuration
  - `.dockerignore`: Docker build context exclusions

## Supported Providers
- **OpenAI**: GPT models (gpt-4o-mini, gpt-4, etc.)
- **DeepSeek**: DeepSeek models (deepseek-chat, etc.)
- **Extensible**: Use `template_client.py` to add new providers

## Quick Start

### 1. Environment Setup
Create/activate a Python 3.10+ environment and install dependencies:
```bash
# Install from requirements file (recommended)
pip install -r requirements.txt

# Or install manually
pip install openai fastapi uvicorn  # Core dependencies
# Optional: pip install pydantic  # Usually included with FastAPI
```

### 2. Mock Mode (No API Key Required)
Run with mock LLM for testing and development:
```bash
python demo.py --ad "Special 0% APR credit card offer for travel rewards" --population-size 1000 --use-mock --out results.csv
```

### 3. Real LLM Calls

#### OpenAI
Set your API key and run:
```bash
# Windows
setx OPENAI_API_KEY "your_api_key_here"
# Linux/Mac
export OPENAI_API_KEY="your_api_key_here"

python demo.py --ad "Affordable health insurance plans" --provider openai --model gpt-4o-mini --population-size 500 --batch-size 50 --out results.csv
```

#### DeepSeek
Set your DeepSeek API key:
```bash
# Windows  
setx DEEPSEEK_API_KEY "your_api_key_here"
# Linux/Mac
export DEEPSEEK_API_KEY="your_api_key_here"

python demo.py --ad "Latest smartphone with AI features" --provider deepseek --model deepseek-chat --population-size 500 --batch-size 50 --out results.csv
```

## Platform Support
The system supports different ad platforms with platform-specific context:
- **Facebook**: Ads in news feed while browsing social content
- **TikTok**: Ads between videos while scrolling short-form content  
- **Amazon**: Ads while shopping or browsing products

## Processing Modes
- **Async Parallel** (default): Fast concurrent API calls for better performance
- **Sync Sequential**: Traditional sequential processing with `--use-sync` flag

## CLI Options

### Required
- `--ad`: The advertisement text to evaluate

### Identity Generation
- `--population-size`: Number of identities to sample (default: 1000)
- `--identity-bank`: Path to identity bank JSON (default: `data/identity_bank.json`)
- `--seed`: Random seed for reproducibility (default: 42)

### Platform & Context
- `--ad-platform`: Platform where ad is shown - `facebook`, `tiktok`, or `amazon` (default: facebook)

### LLM Configuration
- `--provider`: LLM provider - `openai`, `deepseek` (default: openai)
- `--model`: Model name (default: `gpt-4o-mini` for OpenAI, `deepseek-chat` for DeepSeek)
- `--batch-size`: Profiles per LLM call (default: 50)
- `--api-key`: Override provider API key (else uses environment variable)

### Processing Options
- `--use-mock`: Force mock predictions (no network/API key required)
- `--use-sync`: Use synchronous sequential processing instead of async parallel

### Output
- `--out`: Optional CSV output path for detailed per-identity results

## Notes
- The program samples identities according to distributions in `data/identity_bank.json`
- Region is stored as a string `City, ST` format
- Health status includes an `illness` field only when `health_status` is true
- The mock predictor uses a sophisticated heuristic combining ad keywords with identity attributes
- All providers automatically fall back to mock mode if API keys are missing or calls fail
- The system includes runtime performance reporting and detailed result statistics

## REST API Service

The project includes a FastAPI web service (`api.py`) that provides REST endpoints for CTR prediction.

### Starting the API Server
```bash
# Development server with auto-reload
python api.py

# Or using uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

### API Endpoints

#### POST `/predict-ctr`
Predict CTR for a single advertisement.

**Request Body:**
```json
{
  "ad_text": "Special 0% APR credit card offer for travel rewards",
  "ad_platform": "facebook",
  "population_size": 1000,
  "provider": "openai",
  "model": "gpt-4o-mini",
  "use_mock": false
}
```

**Response:**
```json
{
  "success": true,
  "ctr": 0.247,
  "total_clicks": 247,
  "total_identities": 1000,
  "runtime_seconds": 12.34,
  "provider_used": "openai",
  "model_used": "gpt-4o-mini",
  "processing_mode": "asynchronous parallel",
  "ad_platform": "facebook",
  "timestamp": "2025-10-26T10:30:00Z"
}
```

#### POST `/predict-ctr-batch`
Predict CTR for multiple advertisements in batch (max 10).

#### GET `/health`
Health check endpoint.

#### GET `/providers`
List available LLM providers and supported platforms.

#### GET `/identities`
Get the current identity bank configuration and data source information.

**Response:**
```json
{
  "success": true,
  "identity_bank": { /* full identity bank structure */ },
  "source": "gcs",  // or "local"
  "timestamp": "2025-10-27T10:30:00Z"
}
```

#### POST `/identities/reload`
Force reload of the identity bank from data source (GCS or local file).

**Response:**
```json
{
  "success": true,
  "message": "Identity bank reloaded from Google Cloud Storage",
  "source": "gcs",
  "timestamp": "2025-10-27T10:30:00Z"
}
```

#### GET `/health`
Health check endpoint with system status and available providers.

#### GET `/`
API information and available endpoints.

## Google Cloud Storage Integration

The API supports loading identity banks from Google Cloud Storage for flexible data management and easy updates without redeploying the service.

### Configuration

Set these environment variables:
- `GCS_BUCKET_NAME`: Your Google Cloud Storage bucket name (default: "wisteria-data-bucket")
- `GCS_IDENTITY_BANK_PATH`: Path to the identity bank file in the bucket (default: "data/identity_bank.json")

### Data Source Priority

The API uses this priority order for loading identity banks:
1. **Custom path**: If specified in the request (`identity_bank_path` parameter)
2. **Cached version**: Previously loaded identity bank stored in memory
3. **Local file**: `data/identity_bank.json` in the application directory
4. **Google Cloud Storage**: Remote file from the configured GCS bucket

### Setup GCS Identity Bank

1. **Upload your identity bank to GCS:**
```bash
gsutil cp data/identity_bank.json gs://your-bucket/data/identity_bank.json
```

2. **Set environment variables:**
```bash
export GCS_BUCKET_NAME="your-bucket"
export GCS_IDENTITY_BANK_PATH="data/identity_bank.json"
```

3. **Ensure proper permissions:**
The service account needs `Storage Object Viewer` role for the bucket.

### Dynamic Reloading

Update the identity bank without restarting the service:
```bash
# Upload new identity bank to GCS
gsutil cp updated_identity_bank.json gs://your-bucket/data/identity_bank.json

# Reload via API
curl -X POST "https://your-service-url/identities/reload"
```

### API Parameters
- `ad_text` (required): Advertisement text to evaluate
- `ad_platform`: Platform where ad is shown (facebook/tiktok/amazon, default: facebook)
- `population_size`: Number of identities to sample (1-10000, default: 1000)
- `seed`: Random seed for reproducibility (default: 42)
- `provider`: LLM provider (openai/deepseek, default: openai)
- `model`: Model name (uses provider default if not specified)
- `batch_size`: Batch size per LLM call (1-200, default: 50)
- `use_mock`: Force mock predictions (default: false)
- `use_sync`: Use synchronous processing (default: false)
- `api_key`: API key override
- `identity_bank_path`: Custom identity bank path

### API Usage Examples

**Using curl:**
```bash
# Basic CTR prediction
curl -X POST "http://localhost:8000/predict-ctr" \
  -H "Content-Type: application/json" \
  -d '{
    "ad_text": "Premium coffee subscription service",
    "ad_platform": "facebook",
    "population_size": 500,
    "use_mock": true
  }'

# With detailed results
curl -X POST "http://localhost:8000/predict-ctr?include_details=true" \
  -H "Content-Type: application/json" \
  -d '{
    "ad_text": "Eco-friendly cleaning products",
    "provider": "deepseek"
  }'
```

**Using Python requests:**
```python
import requests

response = requests.post("http://localhost:8000/predict-ctr", json={
    "ad_text": "New fitness app with AI personal trainer",
    "ad_platform": "tiktok",
    "population_size": 1000,
    "provider": "openai",
    "model": "gpt-4o-mini"
})

result = response.json()
print(f"CTR: {result['ctr']}")
```

**Using the example client:**
For more comprehensive examples, see `example_client.py`:
```bash
python example_client.py
```

This script demonstrates health checks, provider listing, single predictions, batch predictions, and detailed results.

## Docker & Cloud Deployment

The project includes comprehensive containerization and deployment support for production environments.

### Docker

**Build and run locally:**
```bash
# Build the container (Dockerfile is in deploy/ folder)
docker build -f deploy/Dockerfile -t wisteria-ctr-studio .

# Run locally with environment variables
docker run -p 8080:8080 \
  -e OPENAI_API_KEY="your-key" \
  -e GCS_BUCKET_NAME="your-bucket" \
  wisteria-ctr-studio

# Access the API at http://localhost:8080
```

**Container Features:**
- **Optimized**: Python 3.11 slim base image for minimal size
- **Secure**: Non-root user execution
- **Health checks**: Built-in health monitoring (30s startup grace period)
- **Performance**: Direct uvicorn server for optimal async performance

### Google Cloud Run (Recommended)

**Quick deployment:**
```bash
# Linux/Mac (uses Artifact Registry)
./deploy/deploy.sh wisteria-ctr-studio us-central1

# Windows PowerShell  
.\deploy\deploy.ps1 -ProjectId "wisteria-ctr-studio" -Region "us-central1"
```

**Features:**
- **Modern Registry**: Uses Google Artifact Registry (not deprecated Container Registry)
- **Serverless**: Automatic scaling from 0 to 10 instances
- **Cost-effective**: Pay only for actual usage
- **Secure**: API keys stored in Secret Manager, GCS integration
- **Production-ready**: Health checks, monitoring, logging
- **High-performance**: 2 vCPU, 2 GiB memory, 300s timeout

**Manual deployment with Artifact Registry:**
```bash
# Enable APIs and create repository
gcloud services enable artifactregistry.googleapis.com
gcloud artifacts repositories create wisteria-repo \
  --repository-format=docker --location=us-central1

# Build and deploy
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/wisteria-repo/wisteria-ctr-studio
gcloud run deploy wisteria-ctr-studio \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/wisteria-repo/wisteria-ctr-studio

# Set up API keys and GCS
gcloud secrets create openai-api-key --data-file=-
gcloud run services update wisteria-ctr-studio \
  --update-secrets="OPENAI_API_KEY=openai-api-key:latest" \
  --update-env-vars="GCS_BUCKET_NAME=your-bucket-name"
```

### Other Platforms

The Docker container can be deployed to:
- **AWS ECS/Fargate**: Container orchestration
- **Azure Container Instances**: Serverless containers  
- **Kubernetes**: On any cloud or on-premises
- **DigitalOcean App Platform**: Simple container hosting
- **Heroku**: With container registry

See `DEPLOYMENT.md` for detailed deployment instructions, troubleshooting, and production configuration.

## Adding New LLM Providers

The system is designed for easy extensibility. To add a new LLM provider:

1. **Copy the template**: Start with `template_client.py`
2. **Implement the client**: Replace placeholder methods with your provider's API calls
3. **Register the client**: Add your client to the `CLIENT_REGISTRY` in `llm_click_model.py`
4. **Set environment variables**: Configure API keys and base URLs as needed

Example for a hypothetical "MyProvider":
```python
# my_provider_client.py
from template_client import TemplateClient

class MyProviderClient(TemplateClient):
    def __init__(self, model: str = "my-model", api_key: str = None):
        super().__init__(model, api_key)
        self.provider_name = "myprovider"
        self.env_key_name = "MYPROVIDER_API_KEY"
    
    def _get_client(self):
        from myprovider_sdk import MyProviderClient
        return MyProviderClient(api_key=self.api_key)
    
    # ... implement other required methods

# In llm_click_model.py
CLIENT_REGISTRY = {
    "openai": OpenAIClient,
    "deepseek": DeepSeekClient, 
    "myprovider": MyProviderClient,  # Add here
}
```

## Example Output
```
Sampled identities: 1000
Ad platform: facebook
Batch size: 50
Model Provider: deepseek | Model: deepseek-chat
Processing mode: asynchronous parallel
Clicks: 247 | Non-clicks: 753
CTR: 0.2470
Runtime: 12.34 seconds
Saved results to results.csv
```

