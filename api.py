"""FastAPI web service for CTR simulation.

This module provides a REST API interface for the Wisteria CTR Studio,
allowing users to predict click-through rates via HTTP requests.
"""

import os
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn

from sampler import load_identity_bank, sample_identities
from llm_click_model import LLMClickPredictor


# Pydantic models for request/response validation
class CTRRequest(BaseModel):
    """Request model for CTR prediction."""
    ad_text: str = Field(..., description="Advertisement text to evaluate", min_length=1)
    ad_platform: str = Field(default="facebook", description="Platform where ad is shown")
    population_size: int = Field(default=1000, description="Number of identities to sample", ge=1, le=10000)
    seed: Optional[int] = Field(default=42, description="Random seed for reproducibility")
    provider: str = Field(default="openai", description="LLM provider to use")
    model: Optional[str] = Field(default=None, description="Model name (uses provider default if not specified)")
    batch_size: int = Field(default=50, description="Batch size per LLM call", ge=1, le=200)
    use_mock: bool = Field(default=False, description="Force mock predictions")
    use_sync: bool = Field(default=False, description="Use synchronous processing")
    api_key: Optional[str] = Field(default=None, description="API key override")
    identity_bank_path: Optional[str] = Field(default=None, description="Custom identity bank path")

    class Config:
        schema_extra = {
            "example": {
                "ad_text": "Special 0% APR credit card offer for travel rewards",
                "ad_platform": "facebook",
                "population_size": 1000,
                "provider": "openai",
                "model": "gpt-4o-mini",
                "use_mock": False
            }
        }


class IdentityProfile(BaseModel):
    """Individual identity profile model."""
    gender: str
    age: int
    region: str
    occupation: str
    annual_salary: float
    liability_status: float
    is_married: bool
    health_status: bool
    illness: Optional[str] = None


class DetailedResult(BaseModel):
    """Detailed prediction result for a single identity."""
    id: int
    profile: IdentityProfile
    click_prediction: int


class CTRResponse(BaseModel):
    """Response model for CTR prediction."""
    success: bool
    ctr: float
    total_clicks: int
    total_identities: int
    runtime_seconds: float
    provider_used: str
    model_used: str
    processing_mode: str
    ad_platform: str
    timestamp: str
    detailed_results: Optional[List[DetailedResult]] = None

    class Config:
        schema_extra = {
            "example": {
                "success": True,
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
        }


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    available_providers: List[str]
    version: str


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool
    error: str
    timestamp: str


# Initialize FastAPI app
app = FastAPI(
    title="Wisteria CTR Studio API",
    description="REST API for click-through rate prediction using synthetic identities and LLM models",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global configuration
DEFAULT_IDENTITY_BANK_PATH = os.path.join("data", "identity_bank.json")
AVAILABLE_PROVIDERS = ["openai", "deepseek"]
AVAILABLE_PLATFORMS = ["facebook", "tiktok", "amazon"]


def compute_ctr(clicks: List[int]) -> float:
    """Compute click-through rate from binary predictions."""
    if not clicks:
        return 0.0
    return sum(1 for x in clicks if x) / float(len(clicks))


def validate_request(request: CTRRequest) -> None:
    """Validate request parameters."""
    if request.ad_platform not in AVAILABLE_PLATFORMS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid ad_platform. Must be one of: {AVAILABLE_PLATFORMS}"
        )
    
    if request.provider not in AVAILABLE_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider. Must be one of: {AVAILABLE_PROVIDERS}"
        )


def get_default_model(provider: str) -> str:
    """Get default model for a provider."""
    defaults = {
        "openai": "gpt-4o-mini",
        "deepseek": "deepseek-chat"
    }
    return defaults.get(provider, "gpt-4o-mini")


def format_identity_profile(profile: Dict[str, Any]) -> IdentityProfile:
    """Convert identity dictionary to IdentityProfile model."""
    return IdentityProfile(
        gender=profile.get("gender", ""),
        age=profile.get("age", 0),
        region=profile.get("region", ""),
        occupation=profile.get("occupation", ""),
        annual_salary=profile.get("annual_salary", 0.0),
        liability_status=profile.get("liability_status", 0.0),
        is_married=profile.get("is_married", False),
        health_status=profile.get("health_status", False),
        illness=profile.get("illness")
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat() + "Z",
        available_providers=AVAILABLE_PROVIDERS,
        version="1.0.0"
    )


@app.post("/predict-ctr", response_model=CTRResponse)
async def predict_ctr(request: CTRRequest, include_details: bool = False):
    """
    Predict click-through rate for an advertisement.
    
    Args:
        request: CTR prediction request parameters
        include_details: Whether to include detailed per-identity results
        
    Returns:
        CTR prediction results with summary statistics
    """
    try:
        # Validate request
        validate_request(request)
        
        # Load identity bank
        identity_bank_path = request.identity_bank_path or DEFAULT_IDENTITY_BANK_PATH
        if not os.path.exists(identity_bank_path):
            raise HTTPException(
                status_code=400,
                detail=f"Identity bank file not found: {identity_bank_path}"
            )
        
        bank = load_identity_bank(identity_bank_path)
        
        # Generate synthetic identities
        identities = sample_identities(
            request.population_size, 
            bank, 
            seed=request.seed
        )
        
        # Get model name
        model = request.model or get_default_model(request.provider)
        
        # Initialize predictor
        predictor = LLMClickPredictor(
            provider=request.provider,
            model=model,
            batch_size=request.batch_size,
            use_mock=request.use_mock,
            use_async=not request.use_sync,
            api_key=request.api_key,
        )
        
        # Predict clicks
        start_time = time.time()
        clicks = predictor.predict_clicks(
            request.ad_text, 
            identities, 
            request.ad_platform
        )
        end_time = time.time()
        runtime = end_time - start_time
        
        # Compute CTR
        ctr = compute_ctr(clicks)
        
        # Prepare response
        provider_used = request.provider if not request.use_mock else "mock"
        model_used = model if not request.use_mock else "mock model (no LLM)"
        processing_mode = "synchronous sequential" if request.use_sync else "asynchronous parallel"
        
        response = CTRResponse(
            success=True,
            ctr=round(ctr, 4),
            total_clicks=sum(clicks),
            total_identities=len(identities),
            runtime_seconds=round(runtime, 2),
            provider_used=provider_used,
            model_used=model_used,
            processing_mode=processing_mode,
            ad_platform=request.ad_platform,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
        # Add detailed results if requested
        if include_details:
            detailed_results = []
            for i, (profile, click) in enumerate(zip(identities, clicks)):
                detailed_results.append(DetailedResult(
                    id=i,
                    profile=format_identity_profile(profile),
                    click_prediction=click
                ))
            response.detailed_results = detailed_results
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/predict-ctr-batch")
async def predict_ctr_batch(requests: List[CTRRequest]):
    """
    Predict CTR for multiple advertisements in batch.
    
    Args:
        requests: List of CTR prediction requests
        
    Returns:
        List of CTR prediction results
    """
    if len(requests) > 10:
        raise HTTPException(
            status_code=400,
            detail="Batch size cannot exceed 10 requests"
        )
    
    results = []
    for req in requests:
        try:
            result = await predict_ctr(req, include_details=False)
            results.append(result)
        except Exception as e:
            results.append(ErrorResponse(
                success=False,
                error=str(e),
                timestamp=datetime.utcnow().isoformat() + "Z"
            ))
    
    return results


@app.get("/providers")
async def list_providers():
    """List available LLM providers and their default models."""
    provider_info = {
        "openai": {
            "default_model": "gpt-4o-mini",
            "description": "OpenAI GPT models",
            "env_var": "OPENAI_API_KEY"
        },
        "deepseek": {
            "default_model": "deepseek-chat", 
            "description": "DeepSeek models",
            "env_var": "DEEPSEEK_API_KEY"
        }
    }
    
    return {
        "available_providers": provider_info,
        "platforms": AVAILABLE_PLATFORMS
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Wisteria CTR Studio API",
        "version": "1.0.0",
        "description": "REST API for click-through rate prediction using synthetic identities and LLM models",
        "endpoints": {
            "health": "/health",
            "predict": "/predict-ctr",
            "batch_predict": "/predict-ctr-batch", 
            "providers": "/providers",
            "docs": "/docs"
        }
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error=exc.detail,
            timestamp=datetime.utcnow().isoformat() + "Z"
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            error=f"Internal server error: {str(exc)}",
            timestamp=datetime.utcnow().isoformat() + "Z"
        ).dict()
    )


if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )