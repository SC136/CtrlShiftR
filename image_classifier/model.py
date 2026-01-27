"""
🌾 FARMER ASSISTANT - IMAGE CLASSIFICATION MODEL
Model: MobileNetV3-Large with Transfer Learning
Input: 224x224 RGB plant leaf images
Output: Crop + Issue classification

Mobile-first: Can be exported to TFLite
Offline-first: No internet dependencies
"""

import torch
import torch.nn as nn
import torchvision.models as models
from typing import Dict, List
import json


class PlantDiseaseClassifier(nn.Module):
    """
    MobileNetV3-Large based classifier for plant disease detection.
    
    Architecture:
    - Base: MobileNetV3-Large (ImageNet pretrained)
    - Head: Custom classifier for multi-class disease classification
    - Input: 224x224 RGB images
    - Output: Class probabilities (softmax)
    """
    
    def __init__(self, num_classes: int, pretrained: bool = True):
        """
        Initialize the classifier.
        
        Args:
            num_classes: Number of disease classes (crops × issues)
            pretrained: Use ImageNet pretrained weights
        """
        super(PlantDiseaseClassifier, self).__init__()
        
        # Load MobileNetV3-Large
        weights = models.MobileNet_V3_Large_Weights.IMAGENET1K_V1 if pretrained else None
        self.mobilenet = models.mobilenet_v3_large(weights=weights)
        
        # Get the number of input features for the classifier
        # MobileNetV3-Large has a classifier with structure:
        # Sequential(Linear(960, 1280), Hardswish, Dropout, Linear(1280, num_classes))
        in_features = self.mobilenet.classifier[0].in_features
        
        # Replace the classifier head
        self.mobilenet.classifier = nn.Sequential(
            nn.Linear(in_features, 1280),
            nn.Hardswish(),
            nn.Dropout(p=0.2, inplace=True),
            nn.Linear(1280, num_classes)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor [batch_size, 3, 224, 224]
            
        Returns:
            Logits [batch_size, num_classes]
        """
        return self.mobilenet(x)


class ClassMapper:
    """
    Maps model output indices to crop names and issue names.
    Parses PlantVillage folder naming convention.
    
    Example: "Tomato___Early_blight" → crop="Tomato", issue="Early Blight"
    """
    
    def __init__(self, class_names: List[str]):
        """
        Initialize the mapper.
        
        Args:
            class_names: List of class folder names (e.g., ["Tomato___Early_blight", ...])
        """
        self.class_names = class_names
        self.num_classes = len(class_names)
        self._build_mappings()
    
    def _build_mappings(self):
        """Build internal mappings from class names."""
        self.idx_to_crop = {}
        self.idx_to_issue = {}
        
        for idx, class_name in enumerate(self.class_names):
            crop, issue = self._parse_class_name(class_name)
            self.idx_to_crop[idx] = crop
            self.idx_to_issue[idx] = issue
    
    def _parse_class_name(self, class_name: str) -> tuple:
        """
        Parse PlantVillage folder name.
        
        Args:
            class_name: Folder name (e.g., "Tomato___Early_blight")
            
        Returns:
            (crop, issue) tuple (e.g., ("Tomato", "Early Blight"))
        """
        parts = class_name.split("___")
        
        if len(parts) != 2:
            # Fallback for unexpected format
            return (class_name, "Unknown")
        
        crop = parts[0].strip()
        issue = parts[1].strip()
        
        # Format issue name
        issue = issue.replace("_", " ")
        issue = issue.title()  # Capitalize words
        
        # Special case: "healthy" → "Healthy"
        if issue.lower() == "healthy":
            issue = "Healthy"
        
        return (crop, issue)
    
    def get_crop_issue(self, class_idx: int) -> tuple:
        """
        Get crop and issue for a class index.
        
        Args:
            class_idx: Model output class index
            
        Returns:
            (crop, issue) tuple
        """
        crop = self.idx_to_crop.get(class_idx, "Unknown")
        issue = self.idx_to_issue.get(class_idx, "Unknown")
        return (crop, issue)
    
    def save(self, filepath: str):
        """Save mappings to JSON file."""
        data = {
            "class_names": self.class_names,
            "idx_to_crop": self.idx_to_crop,
            "idx_to_issue": self.idx_to_issue
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, filepath: str):
        """Load mappings from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        mapper = cls(data["class_names"])
        mapper.idx_to_crop = {int(k): v for k, v in data["idx_to_crop"].items()}
        mapper.idx_to_issue = {int(k): v for k, v in data["idx_to_issue"].items()}
        return mapper


def compute_severity(confidence: float) -> str:
    """
    Compute severity level based on confidence.
    
    Args:
        confidence: Model confidence [0, 1]
        
    Returns:
        Severity level: "low", "medium", or "high"
    """
    if confidence >= 0.85:
        return "high"
    elif confidence >= 0.7:
        return "medium"
    else:
        return "low"


def export_to_tflite(model: PlantDiseaseClassifier, output_path: str, input_shape=(1, 3, 224, 224)):
    """
    Export PyTorch model to TFLite for mobile deployment.
    
    Args:
        model: Trained PyTorch model
        output_path: Path to save .tflite file
        input_shape: Input tensor shape
    """
    import torch.onnx
    import onnx
    from onnx_tf.backend import prepare
    import tensorflow as tf
    
    model.eval()
    
    # Step 1: PyTorch → ONNX
    dummy_input = torch.randn(input_shape)
    onnx_path = output_path.replace(".tflite", ".onnx")
    
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        export_params=True,
        opset_version=11,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    
    # Step 2: ONNX → TensorFlow
    onnx_model = onnx.load(onnx_path)
    tf_rep = prepare(onnx_model)
    tf_model_path = output_path.replace(".tflite", "_tf")
    tf_rep.export_graph(tf_model_path)
    
    # Step 3: TensorFlow → TFLite
    converter = tf.lite.TFLiteConverter.from_saved_model(tf_model_path)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    
    with open(output_path, 'wb') as f:
        f.write(tflite_model)
    
    print(f"✅ Model exported to TFLite: {output_path}")


if __name__ == "__main__":
    # Test model creation
    num_classes = 38  # Example: PlantVillage has 38 classes
    model = PlantDiseaseClassifier(num_classes=num_classes, pretrained=True)
    
    # Test forward pass
    dummy_input = torch.randn(1, 3, 224, 224)
    output = model(dummy_input)
    print(f"✅ Model created successfully")
    print(f"   Input shape: {dummy_input.shape}")
    print(f"   Output shape: {output.shape}")
    print(f"   Number of classes: {num_classes}")
    
    # Test class mapper
    example_classes = [
        "Tomato___Early_blight",
        "Tomato___Late_blight",
        "Tomato___healthy",
        "Potato___Early_blight"
    ]
    mapper = ClassMapper(example_classes)
    
    for idx in range(len(example_classes)):
        crop, issue = mapper.get_crop_issue(idx)
        print(f"   Class {idx}: {crop} - {issue}")
