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

## Files
- `data/identity_bank.json`: Identity category definitions and sampling distributions
- `sampler.py`: Sampling utilities to generate synthetic identities
- `base_client.py`: Abstract base class for LLM client implementations
- `openai_client.py`: OpenAI/ChatGPT client implementation
- `deepseek_client.py`: DeepSeek API client implementation
- `template_client.py`: Template for implementing new LLM provider clients
- `llm_click_model.py`: Main predictor with provider registry and mock fallback
- `demo.py`: CLI entry point to run experiments and compute CTR

## Supported Providers
- **OpenAI**: GPT models (gpt-4o-mini, gpt-4, etc.)
- **DeepSeek**: DeepSeek models (deepseek-chat, etc.)
- **Extensible**: Use `template_client.py` to add new providers

## Quick Start

### 1. Environment Setup
Create/activate a Python 3.10+ environment and install dependencies:
```bash
pip install openai  # Required for OpenAI and DeepSeek clients
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

