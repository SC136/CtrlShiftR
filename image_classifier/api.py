"""
🌾 FARMER ASSISTANT - IMAGE CLASSIFICATION API
FastAPI service for plant disease classification
Integrates with existing LLM reasoning layer

Endpoints:
  POST /classify - Upload image, get classification JSON
  GET /health - Health check
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from PIL import Image
import io
import uvicorn
from pathlib import Path
from typing import Optional
import logging

from infer import PlantDiseaseInference

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="🌾 Farmer Assistant - Image Classifier",
    description="Plant disease classification microservice",
    version="1.0.0"
)

# CORS middleware (for web/mobile apps)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global classifier instance
classifier: Optional[PlantDiseaseInference] = None


# Response models (for OpenAPI docs)
class ClassificationResponse(BaseModel):
    """STRICT output format matching the contract."""
    success: bool = Field(True, description="Whether classification succeeded")
    crop: str = Field(..., description="Detected crop name", example="Tomato")
    issue: str = Field(..., description="Detected issue or 'Unknown'", example="Early Blight")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence [0, 1]", example=0.87)
    severity: str = Field(..., description="Severity level", example="medium")


class HealthResponse(BaseModel):
    status: str = Field(..., example="ok")
    model_loaded: bool = Field(..., example=True)
    num_classes: Optional[int] = Field(None, example=38)


class ErrorResponse(BaseModel):
    success: bool = Field(False)
    error: str = Field(..., example="Model not initialized")


@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    global classifier
    
    try:
        # Path to model files (adjust as needed)
        model_path = "output/best_model.pth"
        class_map_path = "output/class_map.json"
        
        # Check if files exist
        if not Path(model_path).exists() or not Path(class_map_path).exists():
            logger.warning("⚠️  Model files not found. Classifier will not be initialized.")
            logger.warning("   Please train the model first using train.py")
            classifier = None
            return
        
        # Initialize classifier
        classifier = PlantDiseaseInference(
            model_path=model_path,
            class_map_path=class_map_path,
            device="auto",
            confidence_threshold=0.6
        )
        
        logger.info("✅ Classifier initialized successfully")
        logger.info(f"   Device: {classifier.device}")
        logger.info(f"   Classes: {classifier.mapper.num_classes}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize classifier: {e}")
        classifier = None


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with service info."""
    return {
        "service": "🌾 Farmer Assistant - Image Classifier",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "classify": "POST /classify - Upload image for classification",
            "health": "GET /health - Check service health"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    model_loaded = classifier is not None
    num_classes = classifier.mapper.num_classes if model_loaded else None
    
    return {
        "status": "ok",
        "model_loaded": model_loaded,
        "num_classes": num_classes
    }


@app.post("/classify", response_model=ClassificationResponse, responses={
    200: {"model": ClassificationResponse},
    400: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def classify_image(file: UploadFile = File(...)):
    """
    Classify plant disease from uploaded image.
    
    **Input:**
    - Image file (JPEG, PNG) via multipart/form-data
    
    **Output:**
    - STRICT JSON matching the contract:
      ```json
      {
        "success": true,
        "crop": "Tomato",
        "issue": "Early Blight",
        "confidence": 0.87,
        "severity": "medium"
      }
      ```
    
    **Rules:**
    - confidence ∈ [0, 1]
    - severity ∈ {"low", "medium", "high"}
    - If confidence < 0.6 → issue = "Unknown"
    - NO extra fields
    - NO natural language explanation
    """
    # Check if classifier is loaded
    if classifier is None:
        logger.error("Classifier not initialized")
        raise HTTPException(
            status_code=500,
            detail="Model not initialized. Please train the model first."
        )
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        logger.warning(f"Invalid file type: {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an image (JPEG, PNG)."
        )
    
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        logger.info(f"Processing image: {file.filename} ({image.size[0]}x{image.size[1]})")
        
        # Classify
        result = classifier.predict(image)
        
        logger.info(f"Classification result: {result['crop']} - {result['issue']} ({result['confidence']:.4f})")
        
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Classification failed: {str(e)}"
        )


@app.post("/classify-with-top-k", response_model=dict, include_in_schema=False)
async def classify_with_top_k(file: UploadFile = File(...), k: int = 3):
    """
    Classify with top-k predictions (for debugging/analysis).
    Not part of the main API contract - use /classify for production.
    """
    if classifier is None:
        raise HTTPException(status_code=500, detail="Model not initialized")
    
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        result = classifier.predict_with_top_k(image, k=k)
        
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Run the API server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Plant Disease Classification API")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address")
    parser.add_argument("--port", type=int, default=8000, help="Port number")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()
    
    print("="*70)
    print("🌾 FARMER ASSISTANT - IMAGE CLASSIFICATION API")
    print("="*70)
    print(f"Starting server at http://{args.host}:{args.port}")
    print(f"API docs available at http://{args.host}:{args.port}/docs")
    print("="*70)
    
    uvicorn.run(
        "api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
