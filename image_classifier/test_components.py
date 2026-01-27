"""
🌾 FARMER ASSISTANT - IMAGE CLASSIFIER COMPONENT TESTS
Tests all components before training
"""

import sys
import os

# Suppress OpenMP warning
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import torch
from pathlib import Path

print("="*70)
print("🧪 IMAGE CLASSIFIER - COMPONENT TESTS")
print("="*70)

# Test 1: Model Creation
print("\n📋 Test 1: Model Creation")
print("-"*70)
try:
    from model import PlantDiseaseClassifier, ClassMapper, compute_severity
    
    # Test model with different class sizes
    for num_classes in [10, 38, 50]:
        model = PlantDiseaseClassifier(num_classes=num_classes, pretrained=False)
        dummy_input = torch.randn(1, 3, 224, 224)
        output = model(dummy_input)
        
        assert output.shape == (1, num_classes), f"Output shape mismatch: {output.shape}"
        print(f"   ✅ Model with {num_classes} classes: OK")
    
    print("✅ Test 1 PASSED: Model creation works")
except Exception as e:
    print(f"❌ Test 1 FAILED: {e}")
    sys.exit(1)

# Test 2: Class Mapper
print("\n📋 Test 2: Class Mapper")
print("-"*70)
try:
    class_names = [
        "Tomato___Early_blight",
        "Tomato___Late_blight",
        "Tomato___healthy",
        "Potato___Early_blight",
        "Pepper___Bacterial_spot"
    ]
    
    mapper = ClassMapper(class_names)
    
    # Test parsing
    expected = [
        ("Tomato", "Early Blight"),
        ("Tomato", "Late Blight"),
        ("Tomato", "Healthy"),
        ("Potato", "Early Blight"),
        ("Pepper", "Bacterial Spot")
    ]
    
    for idx, (exp_crop, exp_issue) in enumerate(expected):
        crop, issue = mapper.get_crop_issue(idx)
        assert crop == exp_crop, f"Crop mismatch at {idx}: {crop} != {exp_crop}"
        assert issue == exp_issue, f"Issue mismatch at {idx}: {issue} != {exp_issue}"
        print(f"   ✅ Class {idx}: {crop} - {issue}")
    
    # Test save/load
    temp_file = "test_class_map.json"
    mapper.save(temp_file)
    loaded_mapper = ClassMapper.load(temp_file)
    
    for idx in range(len(class_names)):
        assert mapper.get_crop_issue(idx) == loaded_mapper.get_crop_issue(idx)
    
    os.remove(temp_file)
    print("   ✅ Save/Load: OK")
    
    print("✅ Test 2 PASSED: Class mapper works")
except Exception as e:
    print(f"❌ Test 2 FAILED: {e}")
    sys.exit(1)

# Test 3: Severity Computation
print("\n📋 Test 3: Severity Computation")
print("-"*70)
try:
    test_cases = [
        (0.95, "high"),
        (0.87, "high"),
        (0.85, "high"),
        (0.75, "medium"),
        (0.70, "medium"),
        (0.65, "low"),
        (0.50, "low"),
        (0.30, "low")
    ]
    
    for confidence, expected_severity in test_cases:
        severity = compute_severity(confidence)
        assert severity == expected_severity, f"Severity mismatch for {confidence}: {severity} != {expected_severity}"
        print(f"   ✅ Confidence {confidence:.2f} → {severity}")
    
    print("✅ Test 3 PASSED: Severity computation works")
except Exception as e:
    print(f"❌ Test 3 FAILED: {e}")
    sys.exit(1)

# Test 4: Dataset Transforms
print("\n📋 Test 4: Dataset Transforms")
print("-"*70)
try:
    from dataset import get_train_transforms, get_val_transforms, get_inference_transforms
    from PIL import Image
    import numpy as np
    
    # Create a dummy image
    dummy_img = Image.fromarray(np.random.randint(0, 255, (500, 500, 3), dtype=np.uint8))
    
    # Test train transforms
    train_tfm = get_train_transforms()
    train_out = train_tfm(dummy_img)
    assert train_out.shape == (3, 224, 224), f"Train transform output shape: {train_out.shape}"
    assert isinstance(train_out, torch.Tensor), "Train output should be tensor"
    print(f"   ✅ Train transforms: {len(train_tfm.transforms)} steps → {train_out.shape}")
    
    # Test val transforms
    val_tfm = get_val_transforms()
    val_out = val_tfm(dummy_img)
    assert val_out.shape == (3, 224, 224), f"Val transform output shape: {val_out.shape}"
    assert isinstance(val_out, torch.Tensor), "Val output should be tensor"
    print(f"   ✅ Val transforms: {len(val_tfm.transforms)} steps → {val_out.shape}")
    
    # Test inference transforms
    inf_tfm = get_inference_transforms()
    inf_out = inf_tfm(dummy_img)
    assert inf_out.shape == (3, 224, 224), f"Inference transform output shape: {inf_out.shape}"
    assert isinstance(inf_out, torch.Tensor), "Inference output should be tensor"
    print(f"   ✅ Inference transforms: {len(inf_tfm.transforms)} steps → {inf_out.shape}")
    
    print("✅ Test 4 PASSED: Dataset transforms work")
except Exception as e:
    print(f"❌ Test 4 FAILED: {e}")
    sys.exit(1)

# Test 5: Model with Pretrained Weights
print("\n📋 Test 5: Model with Pretrained Weights")
print("-"*70)
try:
    model = PlantDiseaseClassifier(num_classes=38, pretrained=True)
    dummy_input = torch.randn(2, 3, 224, 224)  # Batch of 2
    output = model(dummy_input)
    
    assert output.shape == (2, 38), f"Output shape: {output.shape}"
    
    # Test softmax
    probs = torch.softmax(output, dim=1)
    assert torch.allclose(probs.sum(dim=1), torch.ones(2), atol=1e-5), "Probabilities don't sum to 1"
    
    print(f"   ✅ Pretrained model loaded")
    print(f"   ✅ Batch inference: {dummy_input.shape} → {output.shape}")
    print(f"   ✅ Softmax probabilities sum to 1")
    
    print("✅ Test 5 PASSED: Pretrained model works")
except Exception as e:
    print(f"❌ Test 5 FAILED: {e}")
    sys.exit(1)

# Test 6: Full Inference Pipeline Simulation
print("\n📋 Test 6: Full Inference Pipeline Simulation")
print("-"*70)
try:
    from PIL import Image
    import torch.nn.functional as F
    
    # Create model and class mapper
    class_names = ["Tomato___Early_blight", "Tomato___Late_blight", "Tomato___healthy"]
    model = PlantDiseaseClassifier(num_classes=len(class_names), pretrained=False)
    mapper = ClassMapper(class_names)
    model.eval()
    
    # Create dummy image
    dummy_img = Image.fromarray(np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8))
    
    # Apply transforms
    transform = get_inference_transforms()
    img_tensor = transform(dummy_img).unsqueeze(0)
    
    # Inference
    with torch.no_grad():
        output = model(img_tensor)
        probs = F.softmax(output, dim=1)
        confidence, pred_idx = probs.max(1)
    
    confidence = float(confidence.item())
    pred_idx = int(pred_idx.item())
    
    # Get crop and issue
    crop, issue = mapper.get_crop_issue(pred_idx)
    severity = compute_severity(confidence)
    
    # Apply threshold
    if confidence < 0.6:
        issue = "Unknown"
    
    # Build result
    result = {
        "success": True,
        "crop": crop,
        "issue": issue,
        "confidence": round(confidence, 4),
        "severity": severity
    }
    
    print(f"   ✅ Simulated inference result:")
    print(f"      Crop: {result['crop']}")
    print(f"      Issue: {result['issue']}")
    print(f"      Confidence: {result['confidence']}")
    print(f"      Severity: {result['severity']}")
    
    # Validate structure
    assert "success" in result
    assert "crop" in result
    assert "issue" in result
    assert "confidence" in result
    assert "severity" in result
    assert isinstance(result["success"], bool)
    assert isinstance(result["crop"], str)
    assert isinstance(result["issue"], str)
    assert isinstance(result["confidence"], float)
    assert result["severity"] in ["low", "medium", "high"]
    
    print("   ✅ Output JSON structure is valid")
    
    print("✅ Test 6 PASSED: Full inference pipeline works")
except Exception as e:
    print(f"❌ Test 6 FAILED: {e}")
    sys.exit(1)

# Summary
print("\n" + "="*70)
print("🎉 ALL TESTS PASSED!")
print("="*70)
print("\n✅ Components tested:")
print("   1. Model creation (multiple sizes)")
print("   2. Class mapper (parsing, save/load)")
print("   3. Severity computation")
print("   4. Dataset transforms (train/val/inference)")
print("   5. Pretrained model loading")
print("   6. Full inference pipeline simulation")
print("\n✅ Ready for:")
print("   - Training on real dataset")
print("   - API deployment")
print("   - Integration with reasoning layer")
print("\n" + "="*70)
