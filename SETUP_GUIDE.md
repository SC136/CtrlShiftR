# 🌾 FARMER ASSISTANT - SETUP GUIDE

Complete guide to set up the image classification and reasoning layers.

---

## 📋 Prerequisites

- **Python:** 3.8 or higher
- **RAM:** 4GB minimum (8GB recommended for training)
- **Disk Space:** 10GB minimum (20GB for dataset)
- **OS:** Windows, Linux, or macOS
- **Optional:** NVIDIA GPU with CUDA (for faster training)

---

## 🚀 Quick Start (Demo Mode)

**Fastest way to see it working!**

```bash
# 1. Clone/navigate to project
cd ATHARVA

# 2. Install dependencies
cd reasoning_layer
pip install -r requirements.txt

# 3. Start reasoning layer (demo mode - no model needed!)
python main_demo.py

# Access at http://localhost:8001
```

This runs the reasoning layer with a built-in knowledge base (4 diseases).

---

## 🏗️ Full Setup (Both Layers)

### Step 1: Install Image Classifier Dependencies

```bash
cd image_classifier
pip install -r requirements.txt
```

**Dependencies:**

- PyTorch
- torchvision
- FastAPI
- Pillow
- scikit-learn
- matplotlib
- kagglehub

### Step 2: Download Dataset

**Option A: Automatic (using kagglehub)**

```bash
python -c "import kagglehub; print(kagglehub.dataset_download('emmarex/plantdisease'))"
```

**Option B: Manual**

1. Go to https://www.kaggle.com/datasets/emmarex/plantdisease
2. Download and extract
3. Note the path (e.g., `/path/to/plantvillage`)

### Step 3: Train Image Classification Model

```bash
# Basic training (50 epochs)
python train.py --dataset /path/to/plantvillage --epochs 50 --output output

# Full options
python train.py \
  --dataset /path/to/plantvillage \
  --epochs 50 \
  --batch-size 32 \
  --lr 0.001 \
  --output output
```

**Training time:**

- CPU: 2-4 hours (50 epochs)
- GPU: 30-60 minutes (50 epochs)

**Output files:**

```
image_classifier/output/
├── best_model.pth              ← Trained model
├── class_map.json              ← Class mappings
├── training_history.json       ← Training logs
├── training_curves.png         ← Plots
├── confusion_matrix.png        ← Confusion matrix
└── classification_report.txt   ← Metrics
```

### Step 4: Test Image Classifier

```bash
# Command-line inference
python infer.py \
  --image test_image.jpg \
  --model output/best_model.pth \
  --class-map output/class_map.json

# Expected output:
{
  "success": true,
  "crop": "Tomato",
  "issue": "Early Blight",
  "confidence": 0.87,
  "severity": "medium"
}
```

### Step 5: Start Both Services

**Option A: Automatic (Windows)**

```bash
# From project root
.\start_services.ps1
```

**Option B: Manual (Two Terminals)**

Terminal 1 (Image Classifier):

```bash
cd image_classifier
python api.py --host 0.0.0.0 --port 8000
```

Terminal 2 (Reasoning Layer):

```bash
cd reasoning_layer
python main_demo.py
```

### Step 6: Test Integration

```bash
# From project root
python test_integration.py --health
python test_integration.py --image test_image.jpg
```

---

## 🧪 Testing Each Component

### Test Image Classifier Module

```bash
cd image_classifier

# Test model creation
python model.py

# Test dataset loading (requires dataset)
python dataset.py

# Test inference
python infer.py --image test.jpg --model output/best_model.pth --class-map output/class_map.json
```

### Test Reasoning Layer

```bash
cd reasoning_layer

# Run unit tests
python test_final.py

# Expected output:
✅ Test 1: Low Confidence
✅ Test 2: Unknown Issue
✅ Test 3: Valid Early Blight
✅ Test 4: Valid Leaf Curl
✅ Test 5: Generic Disease
```

### Test Full Pipeline

```bash
# Make sure both services are running
python test_integration.py --image path/to/test_image.jpg
```

---

## 📊 Dataset Details

**PlantVillage Dataset:**

- **Source:** Kaggle
- **Size:** ~54,000 images
- **Classes:** 38 crop-disease combinations
- **Format:** JPEG images in class folders

**Folder structure:**

```
plantvillage/
├── Tomato___Early_blight/
│   ├── image_001.jpg
│   ├── image_002.jpg
│   └── ...
├── Tomato___Late_blight/
├── Tomato___Leaf_Mold/
├── Tomato___healthy/
└── ...
```

---

## 🔧 Troubleshooting

### "Module not found" errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### "Model not found" error

```bash
# Train the model first
cd image_classifier
python train.py --dataset /path/to/plantvillage --epochs 50 --output output
```

### "Out of memory" during training

```bash
# Reduce batch size
python train.py --dataset /path/to/plantvillage --batch-size 16 --output output
```

### "Cannot connect to API"

```bash
# Check if services are running
curl http://localhost:8000/health
curl http://localhost:8001/health

# Restart services
.\start_services.ps1  # Windows
```

### Training is slow

- Use smaller batch size if using CPU
- Consider using Google Colab with GPU
- Reduce number of epochs for testing

---

## 🌐 API Usage Examples

### cURL Examples

```bash
# Health check (classification)
curl http://localhost:8000/health

# Classify image
curl -X POST http://localhost:8000/classify \
  -F "file=@tomato_disease.jpg"

# Health check (reasoning)
curl http://localhost:8001/health

# Get advice
curl -X POST http://localhost:8001/reason \
  -H "Content-Type: application/json" \
  -d '{"crop":"Tomato","issue":"Early Blight","confidence":0.87,"severity":"medium"}'
```

### Python Examples

```python
import requests

# Classify image
url = "http://localhost:8000/classify"
files = {"file": open("test_image.jpg", "rb")}
response = requests.post(url, files=files)
classification = response.json()
print(classification)

# Get advice
url = "http://localhost:8001/reason"
response = requests.post(url, json=classification)
advice = response.json()
print(advice)
```

### JavaScript Examples

```javascript
// Classify image
const formData = new FormData();
formData.append("file", fileInput.files[0]);

fetch("http://localhost:8000/classify", {
  method: "POST",
  body: formData,
})
  .then((res) => res.json())
  .then((classification) => {
    // Get advice
    return fetch("http://localhost:8001/reason", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(classification),
    });
  })
  .then((res) => res.json())
  .then((advice) => console.log(advice));
```

---

## 📱 Mobile Deployment (Future)

### Export Model to TFLite

```python
from model import PlantDiseaseClassifier, export_to_tflite
import torch

# Load trained model
model = PlantDiseaseClassifier(num_classes=38)
checkpoint = torch.load("output/best_model.pth")
model.load_state_dict(checkpoint['model_state_dict'])

# Export
export_to_tflite(model, "model.tflite")
```

### Files Needed for Mobile App

1. **model.tflite** - Converted model
2. **class_map.json** - Class name mappings
3. **Preprocessing:** 224×224, ImageNet normalization
4. **Confidence threshold:** 0.6
5. **Severity logic:** As defined in model.py

---

## 🔒 Security & Privacy

- ✅ All processing happens locally
- ✅ No user data is collected
- ✅ No internet required after setup
- ✅ No telemetry
- ✅ Open source code

---

## 📚 Next Steps

### For Development

1. ✅ Train on PlantVillage dataset
2. ✅ Test with sample images
3. ✅ Validate API responses
4. ⚠️ Add more crops/diseases
5. ⚠️ Improve accuracy
6. ⚠️ Optimize for mobile

### For Production

1. ⚠️ Collect field data
2. ⚠️ Retrain with diverse images
3. ⚠️ Add multilingual support
4. ⚠️ Build mobile apps
5. ⚠️ Deploy to edge devices
6. ⚠️ Add voice interface

---

## 🎓 Learning Resources

### PyTorch

- https://pytorch.org/tutorials/

### FastAPI

- https://fastapi.tiangolo.com/

### MobileNet

- https://arxiv.org/abs/1905.02244

### TFLite

- https://www.tensorflow.org/lite/guide

---

## 📞 Support

For issues or questions:

1. Check [image_classifier/README.md](image_classifier/README.md)
2. Check [reasoning_layer/README.md](reasoning_layer/README.md)
3. See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
4. Run health checks: `python test_integration.py --health`

---

Built with 🌾 for Indian Farmers | Mobile-First 📱 | Offline-First 🔌
