"""Example client script for the Wisteria CTR Studio API.

This script demonstrates how to interact with the REST API service
to predict click-through rates for advertisements.
"""

import requests
import json
from typing import Dict, Any


class CTRApiClient:
    """Simple client for the Wisteria CTR Studio API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the API client.
        
        Args:
            base_url: Base URL of the API service.
        """
        self.base_url = base_url.rstrip('/')
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def list_providers(self) -> Dict[str, Any]:
        """Get available providers and platforms."""
        response = requests.get(f"{self.base_url}/providers")
        response.raise_for_status()
        return response.json()
    
    def get_identities(self) -> Dict[str, Any]:
        """Get the identity bank configuration."""
        response = requests.get(f"{self.base_url}/identities")
        response.raise_for_status()
        return response.json()
    
    def reload_identities(self) -> Dict[str, Any]:
        """Reload the identity bank from the data source."""
        response = requests.post(f"{self.base_url}/identities/reload")
        response.raise_for_status()
        return response.json()
    
    def predict_ctr(
        self,
        ad_text: str,
        ad_platform: str = "facebook",
        population_size: int = 1000,
        provider: str = "openai",
        model: str = None,
        use_mock: bool = False,
        include_details: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Predict CTR for an advertisement.
        
        Args:
            ad_text: Advertisement text to evaluate.
            ad_platform: Platform where ad is shown.
            population_size: Number of identities to sample.
            provider: LLM provider to use.
            model: Model name (optional).
            use_mock: Whether to use mock predictions.
            include_details: Whether to include detailed per-identity results.
            **kwargs: Additional parameters.
            
        Returns:
            CTR prediction results.
        """
        payload = {
            "ad_text": ad_text,
            "ad_platform": ad_platform,
            "population_size": population_size,
            "provider": provider,
            "use_mock": use_mock,
            **kwargs
        }
        
        if model:
            payload["model"] = model
        
        params = {"include_details": include_details} if include_details else {}
        
        response = requests.post(
            f"{self.base_url}/predict-ctr",
            json=payload,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def predict_ctr_batch(self, requests_list: list) -> list:
        """Predict CTR for multiple advertisements.
        
        Args:
            requests_list: List of request dictionaries.
            
        Returns:
            List of CTR prediction results.
        """
        response = requests.post(
            f"{self.base_url}/predict-ctr-batch",
            json=requests_list
        )
        response.raise_for_status()
        return response.json()


def main():
    """Example usage of the CTR API client."""
    
    # Initialize client
    client = CTRApiClient()
    
    try:
        # Check API health
        print("Checking API health...")
        health = client.health_check()
        print(f"API Status: {health['status']}")
        print(f"Available providers: {', '.join(health['available_providers'])}")
        print()
        
        # Get provider information
        print("Getting provider information...")
        providers = client.list_providers()
        print("Available providers:")
        for provider, info in providers["available_providers"].items():
            print(f"  - {provider}: {info['description']} (default: {info['default_model']})")
        print(f"Supported platforms: {', '.join(providers['platforms'])}")
        print()
        
        # Get identity bank information
        print("Getting identity bank information...")
        try:
            identities = client.get_identities()
            print(f"Identity bank loaded from: {identities.get('source', 'unknown')}")
            bank = identities['identity_bank']
            print("Available identity categories:")
            for category in bank.keys():
                print(f"  - {category}")
            print()
        except Exception as e:
            print(f"Could not load identity bank: {e}")
            print()
        
        print(f"Supported platforms: {', '.join(providers['platforms'])}")
        print()
        
        # Example 1: Basic CTR prediction with mock
        print("Example 1: Basic CTR prediction (mock mode)")
        result = client.predict_ctr(
            ad_text="Special 0% APR credit card offer for travel rewards",
            ad_platform="facebook",
            population_size=100,
            use_mock=True
        )
        
        print(f"CTR: {result['ctr']}")
        print(f"Clicks: {result['total_clicks']}/{result['total_identities']}")
        print(f"Runtime: {result['runtime_seconds']}s")
        print(f"Provider: {result['provider_used']}")
        print()
        
        # Example 2: Different platform
        print("Example 2: TikTok platform prediction (mock mode)")
        result = client.predict_ctr(
            ad_text="Latest smartphone with AI camera features",
            ad_platform="tiktok",
            population_size=200,
            use_mock=True
        )
        
        print(f"CTR: {result['ctr']}")
        print(f"Platform: {result['ad_platform']}")
        print(f"Processing: {result['processing_mode']}")
        print()
        
        # Example 3: Batch prediction
        print("Example 3: Batch prediction (mock mode)")
        batch_requests = [
            {
                "ad_text": "Premium coffee subscription service",
                "ad_platform": "facebook",
                "population_size": 50,
                "use_mock": True
            },
            {
                "ad_text": "Eco-friendly cleaning products",
                "ad_platform": "amazon",
                "population_size": 50,
                "use_mock": True
            }
        ]
        
        batch_results = client.predict_ctr_batch(batch_requests)
        
        for i, result in enumerate(batch_results):
            if result.get("success", True):
                print(f"  Ad {i+1}: CTR = {result['ctr']}, Platform = {result['ad_platform']}")
            else:
                print(f"  Ad {i+1}: Error - {result.get('error', 'Unknown error')}")
        print()
        
        # Example 4: Detailed results (first few only)
        print("Example 4: Prediction with detailed results (first 5 identities)")
        result = client.predict_ctr(
            ad_text="Affordable health insurance plans",
            population_size=20,
            use_mock=True,
            include_details=True
        )
        
        print(f"Overall CTR: {result['ctr']}")
        if result.get("detailed_results"):
            print("Sample detailed results:")
            for detail in result["detailed_results"][:5]:
                profile = detail["profile"]
                click = detail["click_prediction"]
                print(f"  ID {detail['id']}: {profile['gender']}, {profile['age']}, "
                      f"{profile['occupation']} -> Click: {click}")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API server.")
        print("Make sure the server is running: python api.py")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()