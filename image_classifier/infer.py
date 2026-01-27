"""
🌾 FARMER ASSISTANT - INFERENCE MODULE
Loads trained model and performs single-image inference
Outputs STRICT JSON format for LLM reasoning layer
"""

import torch
import torch.nn.functional as F
from PIL import Image
from pathlib import Path
import json
from typing import Dict, Union

from model import PlantDiseaseClassifier, ClassMapper, compute_severity
from dataset import get_inference_transforms


class PlantDiseaseInference:
    """
    Inference engine for plant disease classification.
    
    Usage:
        classifier = PlantDiseaseInference("output/best_model.pth", "output/class_map.json")
        result = classifier.predict("image.jpg")
        print(json.dumps(result, indent=2))
    """
    
    def __init__(
        self,
        model_path: str,
        class_map_path: str,
        device: str = "auto",
        confidence_threshold: float = 0.6
    ):
        """
        Initialize inference engine.
        
        Args:
            model_path: Path to trained model checkpoint (.pth)
            class_map_path: Path to class mapping JSON
            device: "cuda", "cpu", or "auto"
            confidence_threshold: Minimum confidence (below this → "Unknown")
        """
        self.confidence_threshold = confidence_threshold
        
        # Set device
        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        print(f"🖥️  Using device: {self.device}")
        
        # Load class mapper
        self.mapper = ClassMapper.load(class_map_path)
        print(f"✅ Loaded class mappings: {self.mapper.num_classes} classes")
        
        # Load model
        self.model = self._load_model(model_path)
        self.model.eval()
        print(f"✅ Model loaded from {model_path}")
        
        # Load transforms
        self.transform = get_inference_transforms()
        print(f"✅ Inference ready")
    
    def _load_model(self, model_path: str) -> PlantDiseaseClassifier:
        """Load trained model from checkpoint."""
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # Create model
        model = PlantDiseaseClassifier(
            num_classes=self.mapper.num_classes,
            pretrained=False
        )
        
        # Load weights
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(self.device)
        
        return model
    
    def predict(self, image_input: Union[str, Path, Image.Image]) -> Dict:
        """
        Predict crop and disease from image.
        
        Args:
            image_input: Path to image file or PIL Image
            
        Returns:
            STRICT JSON output matching the contract:
            {
              "success": true,
              "crop": "Tomato",
              "issue": "Early Blight",
              "confidence": 0.87,
              "severity": "medium"
            }
        """
        # Load image
        if isinstance(image_input, (str, Path)):
            image = Image.open(image_input).convert('RGB')
        else:
            image = image_input
        
        # Preprocess
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # Inference
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = F.softmax(outputs, dim=1)
            confidence, predicted_idx = probabilities.max(1)
        
        # Extract values
        confidence = float(confidence.item())
        predicted_idx = int(predicted_idx.item())
        
        # Get crop and issue
        crop, issue = self.mapper.get_crop_issue(predicted_idx)
        
        # Apply confidence threshold
        if confidence < self.confidence_threshold:
            issue = "Unknown"
        
        # Compute severity
        severity = compute_severity(confidence)
        
        # Build output JSON (STRICT FORMAT)
        result = {
            "success": True,
            "crop": crop,
            "issue": issue,
            "confidence": round(confidence, 4),
            "severity": severity
        }
        
        return result
    
    def predict_with_top_k(self, image_input: Union[str, Path, Image.Image], k: int = 3) -> Dict:
        """
        Predict with top-k results (for debugging/analysis).
        
        Returns:
            {
              "success": true,
              "crop": "Tomato",
              "issue": "Early Blight",
              "confidence": 0.87,
              "severity": "medium",
              "top_k": [
                {"crop": "Tomato", "issue": "Early Blight", "confidence": 0.87},
                {"crop": "Tomato", "issue": "Late Blight", "confidence": 0.08},
                {"crop": "Tomato", "issue": "Leaf Mold", "confidence": 0.03}
              ]
            }
        """
        # Load image
        if isinstance(image_input, (str, Path)):
            image = Image.open(image_input).convert('RGB')
        else:
            image = image_input
        
        # Preprocess
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # Inference
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = F.softmax(outputs, dim=1)
        
        # Get top-k
        top_k_probs, top_k_indices = probabilities.topk(k, dim=1)
        top_k_probs = top_k_probs.squeeze().cpu().numpy()
        top_k_indices = top_k_indices.squeeze().cpu().numpy()
        
        # Primary prediction
        confidence = float(top_k_probs[0])
        predicted_idx = int(top_k_indices[0])
        crop, issue = self.mapper.get_crop_issue(predicted_idx)
        
        # Apply confidence threshold
        if confidence < self.confidence_threshold:
            issue = "Unknown"
        
        severity = compute_severity(confidence)
        
        # Build top-k list
        top_k_results = []
        for idx, prob in zip(top_k_indices, top_k_probs):
            c, i = self.mapper.get_crop_issue(int(idx))
            top_k_results.append({
                "crop": c,
                "issue": i,
                "confidence": round(float(prob), 4)
            })
        
        # Build output
        result = {
            "success": True,
            "crop": crop,
            "issue": issue,
            "confidence": round(confidence, 4),
            "severity": severity,
            "top_k": top_k_results
        }
        
        return result


def main():
    """Command-line inference tool."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Plant Disease Inference")
    parser.add_argument("--image", type=str, required=True, help="Path to image")
    parser.add_argument("--model", type=str, required=True, help="Path to model checkpoint")
    parser.add_argument("--class-map", type=str, required=True, help="Path to class_map.json")
    parser.add_argument("--device", type=str, default="auto", help="Device (cuda/cpu/auto)")
    parser.add_argument("--threshold", type=float, default=0.6, help="Confidence threshold")
    parser.add_argument("--top-k", type=int, default=None, help="Show top-k predictions")
    parser.add_argument("--output", type=str, default=None, help="Save result to JSON file")
    args = parser.parse_args()
    
    # Create classifier
    classifier = PlantDiseaseInference(
        model_path=args.model,
        class_map_path=args.class_map,
        device=args.device,
        confidence_threshold=args.threshold
    )
    
    # Predict
    print(f"\n🔍 Analyzing image: {args.image}")
    
    if args.top_k:
        result = classifier.predict_with_top_k(args.image, k=args.top_k)
    else:
        result = classifier.predict(args.image)
    
    # Print result
    print("\n" + "="*70)
    print("📊 CLASSIFICATION RESULT")
    print("="*70)
    print(json.dumps(result, indent=2))
    print("="*70)
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n✅ Result saved to {args.output}")
    
    # Interpretation
    if result["issue"] == "Unknown":
        print("\n⚠️  Low confidence detection - image may be unclear")
    else:
        print(f"\n✅ Detected: {result['crop']} - {result['issue']}")
        print(f"   Confidence: {result['confidence']*100:.2f}%")
        print(f"   Severity: {result['severity']}")


if __name__ == "__main__":
    main()
