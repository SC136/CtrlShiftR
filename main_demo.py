"""
Mock/Demo Mode - FastAPI server with simulated LLM responses
Use this for testing the API structure without needing llama.cpp

This demonstrates the complete system with hardcoded intelligent responses
"""

import json
from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Farmer Assistant Reasoning Layer (Demo Mode)")


class ClassificationInput(BaseModel):
    crop: str = Field(..., min_length=1)
    issue: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)
    season: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)


# Knowledge base for demo responses
DISEASE_KNOWLEDGE = {
    "Early Blight": {
        "problem": "Your {crop} plant has Early Blight disease. You can see dark brown spots with rings on older leaves.",
        "reason": "This happens due to warm humid weather and poor air circulation. Fungus spreads from infected plant parts or soil.",
        "immediate_actions": [
            "Remove all infected leaves and burn them away from the field",
            "Stop overhead watering and water at the base of plants only",
            "Improve spacing between plants for better air flow"
        ],
        "organic_solutions": [
            "Spray neem oil solution every 7 days. Mix 5 ml neem oil with 1 liter water",
            "Use baking soda spray. Mix 1 tablespoon baking soda with 1 liter water and few drops of soap"
        ],
        "chemical_solution": "Consult your local agriculture officer for copper fungicide guidance. Do not use chemicals without expert advice.",
        "prevention": [
            "Use drip irrigation instead of overhead watering",
            "Apply mulch around plants to prevent soil splash on leaves"
        ]
    },
    "Late Blight": {
        "problem": "Your {crop} plant has Late Blight disease. Leaves show dark water soaked spots that spread fast.",
        "reason": "This happens in cool wet weather. Fungus spreads very fast through wind and rain water.",
        "immediate_actions": [
            "Remove infected plants completely from the field",
            "Do not compost infected plants. Burn or bury them deep",
            "Avoid working in wet fields to prevent spreading"
        ],
        "organic_solutions": [
            "Spray copper based organic fungicide every 5 to 7 days",
            "Use garlic and chili spray. Crush 100 gram garlic with 10 chilies in 1 liter water"
        ],
        "chemical_solution": "This is serious disease. Contact agriculture officer immediately for systemic fungicide recommendation.",
        "prevention": [
            "Plant resistant varieties if available in your area",
            "Maintain good drainage and avoid water logging"
        ]
    },
    "Leaf Curl": {
        "problem": "Your {crop} leaves are curling and becoming thick. This is viral disease spread by whiteflies.",
        "reason": "Tiny whitefly insects carry virus from infected plants. They feed on leaf bottom and spread disease.",
        "immediate_actions": [
            "Remove badly affected plants to stop virus spread",
            "Control whitefly by spraying water jet under leaves",
            "Use yellow sticky traps to catch whiteflies"
        ],
        "organic_solutions": [
            "Spray neem oil mixed with soap water every 5 days",
            "Plant marigold flowers around the crop to repel whiteflies"
        ],
        "chemical_solution": "Consult agriculture officer for approved insecticide for whitefly control. Virus has no direct cure.",
        "prevention": [
            "Use virus resistant varieties",
            "Cover young plants with net to prevent whitefly"
        ]
    },
    "Powdery Mildew": {
        "problem": "Your {crop} leaves have white powdery coating. This is fungus disease.",
        "reason": "This happens in dry weather with high humidity. Fungus grows on leaf surface and takes plant nutrients.",
        "immediate_actions": [
            "Remove affected leaves and destroy them",
            "Increase air circulation by proper spacing",
            "Water in morning so leaves dry quickly"
        ],
        "organic_solutions": [
            "Spray milk solution. Mix 1 part milk with 9 parts water",
            "Use baking soda spray. Mix 1 tablespoon in 1 liter water with soap"
        ],
        "chemical_solution": "Sulfur based fungicide works well. Consult agriculture officer for correct dose.",
        "prevention": [
            "Plant in location with good air movement",
            "Do not overcrowd plants"
        ]
    }
}


def _generate_response(payload: ClassificationInput) -> Dict[str, Any]:
    """Generate intelligent demo response based on the issue"""
    
    # Check confidence threshold
    if payload.confidence < 0.6 or payload.issue.strip().lower() == "unknown":
        return {
            "message": "Image is not clear. Please take a clear photo of the affected leaf in daylight."
        }
    
    # Get disease knowledge or use generic response
    disease_info = DISEASE_KNOWLEDGE.get(payload.issue)
    
    if disease_info:
        return {
            "problem": disease_info["problem"].format(crop=payload.crop),
            "reason": disease_info["reason"],
            "immediate_actions": disease_info["immediate_actions"],
            "organic_solutions": disease_info["organic_solutions"],
            "chemical_solution": disease_info["chemical_solution"],
            "prevention": disease_info["prevention"],
            "confidence_note": f"Detection confidence is {int(payload.confidence * 100)} percent"
        }
    else:
        # Generic response for unknown diseases
        return {
            "problem": f"Your {payload.crop} plant shows signs of {payload.issue}.",
            "reason": "This condition may be caused by environmental stress or disease. Local conditions play important role.",
            "immediate_actions": [
                "Remove and destroy affected plant parts",
                "Improve air circulation around plants",
                "Check soil drainage and water properly"
            ],
            "organic_solutions": [
                "Apply neem oil spray as general purpose organic treatment",
                "Use compost tea to boost plant immunity"
            ],
            "chemical_solution": "Contact your local agriculture extension officer for specific treatment recommendation.",
            "prevention": [
                "Maintain good field hygiene",
                "Monitor plants regularly for early detection"
            ],
            "confidence_note": f"Detection confidence is {int(payload.confidence * 100)} percent. Please consult local expert for confirmation."
        }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "mode": "demo"}


@app.post("/reason")
def reason(payload: ClassificationInput) -> Dict[str, Any]:
    """Reasoning endpoint with simulated LLM responses"""
    
    if not payload.crop or not payload.issue or not payload.season or not payload.location:
        return {
            "message": "Required input is missing. Please resend crop, issue, confidence, season, location."
        }
    
    return _generate_response(payload)


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🌾 FARMER ASSISTANT - DEMO MODE")
    print("=" * 60)
    print("Running without LLM (using knowledge base)")
    print("This demonstrates the complete API structure")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
