"""
🌾 Farmer Assistant - Image Classification Module

A mobile-first, offline-first plant disease classifier that outputs
strictly structured JSON for the LLM reasoning layer.

Modules:
    model: MobileNetV3-Large classifier and class mapping
    dataset: PlantVillage dataset loading and augmentation
    train: Model training script
    infer: Inference engine
    api: FastAPI service

Usage:
    # Training
    python train.py --dataset /path/to/data --epochs 50 --output output
    
    # Inference
    from infer import PlantDiseaseInference
    classifier = PlantDiseaseInference("output/best_model.pth", "output/class_map.json")
    result = classifier.predict("image.jpg")
    
    # API
    python api.py --port 8000
"""

__version__ = "1.0.0"
__author__ = "ATHARVA Team"

from .model import PlantDiseaseClassifier, ClassMapper, compute_severity
from .infer import PlantDiseaseInference

__all__ = [
    "PlantDiseaseClassifier",
    "ClassMapper",
    "compute_severity",
    "PlantDiseaseInference",
]
