# 🌾 FARMER ASSISTANT - IMAGE CLASSIFICATION MODULE

## 📋 Overview

This module is the **image classification layer** for the Farmer Assistant app. It takes plant leaf images as input and outputs **strictly structured JSON** for the LLM reasoning layer.

**What it does:**

- ✅ Classifies plant diseases from images
- ✅ Outputs clean JSON (NO explanations, NO advice)
- ✅ Integrates seamlessly with LLM reasoning layer
- ✅ Mobile-first and offline-first design

**What it does NOT do:**

- ❌ NO reasoning or advice generation
- ❌ NO treatment suggestions
- ❌ NO natural language explanations

---

## 🏗️ Architecture

```
Image → Classification Model → JSON → LLM Reasoning Layer → Farmer Advice
```

### Model Details

- **Framework:** PyTorch
- **Architecture:** MobileNetV3-Large (ImageNet pretrained)
- **Input:** 224×224 RGB images
- **Output:** Multi-class probabilities
- **Mobile-ready:** Can export to TFLite

---

## 📦 Dataset

**Source:** Kaggle PlantDisease (PlantVillage)

Download using:

```python
import kagglehub
path = kagglehub.dataset_download("emmarex/plantdisease")
```

**Folder structure:**

```
dataset/
 ├── Tomato___Early_blight/
 │   ├── image1.jpg
 │   ├── image2.jpg
 ├── Tomato___Late_blight/
 ├── Tomato___healthy/
 └── ...
```

---

## 🔒 Output Contract (STRICT)

The classifier **MUST** output **ONLY** this JSON:

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

- `confidence` ∈ [0, 1]
- `severity` ∈ {"low", "medium", "high"}
- If `confidence < 0.6` → `issue = "Unknown"`
- **NO extra fields**
- **NO natural language explanation**

---

## 🚀 Installation

### 1. Install Dependencies

```bash
cd image_classifier
pip install -r requirements.txt
```

### 2. Download Dataset

```bash
python -c "import kagglehub; print(kagglehub.dataset_download('emmarex/plantdisease'))"
```

Or manually download from [Kaggle](https://www.kaggle.com/datasets/emmarex/plantdisease)

---

## 🧠 Training

### Basic Training

```bash
python train.py --dataset /path/to/plantvillage --epochs 50 --batch-size 32 --output output
```

### Full Options

```bash
python train.py \
  --dataset /path/to/plantvillage \
  --epochs 50 \
  --batch-size 32 \
  --lr 0.001 \
  --output output \
  --download  # Download dataset automatically
```

**What happens:**

1. ✅ Loads dataset with heavy augmentation
2. ✅ Trains MobileNetV3-Large with transfer learning
3. ✅ Saves best model to `output/best_model.pth`
4. ✅ Saves class mappings to `output/class_map.json`
5. ✅ Generates training curves and confusion matrix

**Output files:**

```
output/
 ├── best_model.pth                 # Trained model weights
 ├── class_map.json                 # Class name mappings
 ├── training_history.json          # Loss/accuracy per epoch
 ├── training_curves.png            # Training plots
 ├── confusion_matrix.png           # Confusion matrix
 └── classification_report.txt      # Per-class metrics
```

---

## 🔍 Inference (Command Line)

### Single Image Classification

```bash
python infer.py \
  --image test_image.jpg \
  --model output/best_model.pth \
  --class-map output/class_map.json
```

**Output:**

```json
{
  "success": true,
  "crop": "Tomato",
  "issue": "Early Blight",
  "confidence": 0.8743,
  "severity": "medium"
}
```

### Top-K Predictions (Debug Mode)

```bash
python infer.py \
  --image test_image.jpg \
  --model output/best_model.pth \
  --class-map output/class_map.json \
  --top-k 5
```

**Output:**

```json
{
  "success": true,
  "crop": "Tomato",
  "issue": "Early Blight",
  "confidence": 0.8743,
  "severity": "medium",
  "top_k": [
    { "crop": "Tomato", "issue": "Early Blight", "confidence": 0.8743 },
    { "crop": "Tomato", "issue": "Late Blight", "confidence": 0.0821 },
    { "crop": "Tomato", "issue": "Leaf Mold", "confidence": 0.0312 },
    { "crop": "Tomato", "issue": "Septoria Leaf Spot", "confidence": 0.0098 },
    { "crop": "Tomato", "issue": "Healthy", "confidence": 0.0026 }
  ]
}
```

---

## 🌐 API Server (FastAPI)

### Start Server

```bash
python api.py --host 0.0.0.0 --port 8000
```

**Access:**

- API: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`

### Endpoints

#### 1. Health Check

```bash
GET /health
```

**Response:**

```json
{
  "status": "ok",
  "model_loaded": true,
  "num_classes": 38
}
```

#### 2. Classify Image

```bash
POST /classify
Content-Type: multipart/form-data
Body: file=@image.jpg
```

**Response:**

```json
{
  "success": true,
  "crop": "Tomato",
  "issue": "Early Blight",
  "confidence": 0.87,
  "severity": "medium"
}
```

### Test with cURL

```bash
curl -X POST "http://localhost:8000/classify" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@tomato_early_blight.jpg"
```

### Test with Python

```python
import requests

url = "http://localhost:8000/classify"
files = {"file": open("test_image.jpg", "rb")}
response = requests.post(url, files=files)

print(response.json())
```

---

## 🔗 Integration with LLM Reasoning Layer

The classification output can be **directly forwarded** to the existing LLM reasoning layer:

```python
import requests

# Step 1: Classify image
classify_url = "http://localhost:8000/classify"
image_file = {"file": open("tomato_diseased.jpg", "rb")}
classification = requests.post(classify_url, files=image_file).json()

# Step 2: Send to LLM reasoning layer
reasoning_url = "http://localhost:8001/reason"
advice = requests.post(reasoning_url, json=classification).json()

# Result: Farmer-friendly advice
print(advice)
```

**No modifications needed** - the JSON output matches the LLM's expected input!

---

## 📊 Confidence & Severity Logic

### Confidence

```python
confidence = max(softmax_output)
```

### Severity Heuristic

```python
if confidence > 0.85:
    severity = "high"
elif confidence > 0.7:
    severity = "medium"
else:
    severity = "low"
```

### Unknown Detection

If `confidence < 0.6`:

```json
{
  "success": true,
  "crop": "Tomato",
  "issue": "Unknown",
  "confidence": 0.45,
  "severity": "low"
}
```

The LLM layer will then return a "Please retake the photo" message.

---

## 📱 Mobile Deployment

### Export to TFLite

```python
from model import PlantDiseaseClassifier, export_to_tflite

# Load trained model
model = PlantDiseaseClassifier(num_classes=38)
checkpoint = torch.load("output/best_model.pth")
model.load_state_dict(checkpoint['model_state_dict'])

# Export to TFLite
export_to_tflite(model, "model.tflite")
```

**Mobile integration:**

1. ✅ Copy `.tflite` file to mobile app
2. ✅ Copy `class_map.json` to mobile app
3. ✅ Use TFLite Interpreter (Android/iOS)
4. ✅ Same preprocessing (224×224, ImageNet normalization)
5. ✅ Same confidence & severity logic

---

## 📂 File Structure

```
image_classifier/
 ├── model.py          # MobileNetV3-Large model + ClassMapper
 ├── dataset.py        # Dataset loading + augmentation
 ├── train.py          # Training script
 ├── infer.py          # Command-line inference
 ├── api.py            # FastAPI service
 ├── requirements.txt  # Python dependencies
 └── README.md         # This file

output/  (generated after training)
 ├── best_model.pth
 ├── class_map.json
 ├── training_history.json
 ├── training_curves.png
 ├── confusion_matrix.png
 └── classification_report.txt
```

---

## 🧪 Testing

### Test Model Creation

```bash
python model.py
```

### Test Dataset Loading

```bash
python dataset.py
```

### Test Inference

```bash
python infer.py --image test.jpg --model output/best_model.pth --class-map output/class_map.json
```

### Test API

```bash
# Terminal 1: Start server
python api.py

# Terminal 2: Test endpoint
curl http://localhost:8000/health
curl -X POST http://localhost:8000/classify -F "file=@test.jpg"
```

---

## 🛑 Hard Constraints

✅ **DO:**

- Output strict JSON format
- Use MobileNetV3-Large or EfficientNet-Lite0
- Apply confidence threshold (0.6)
- Compute severity heuristic
- Export to TFLite

❌ **DO NOT:**

- Add explanations or advice
- Modify JSON output fields
- Use YOLO or object detection
- Call LLM from this module
- Add extra fields to JSON

---

## 🔧 Troubleshooting

### Model not loading

```
❌ Error: Model files not found
✅ Solution: Train the model first using train.py
```

### Out of memory during training

```
❌ Error: CUDA out of memory
✅ Solution: Reduce batch size (--batch-size 16 or 8)
```

### Low accuracy

```
❌ Problem: Test accuracy < 80%
✅ Solutions:
  - Train for more epochs (--epochs 100)
  - Check dataset quality
  - Use larger batch size (if GPU allows)
  - Increase augmentation
```

### API not starting

```
❌ Error: Model not initialized
✅ Solution: Ensure output/best_model.pth and output/class_map.json exist
```

---

## 📚 Dependencies

See [requirements.txt](requirements.txt):

- `torch>=2.0.0`
- `torchvision>=0.15.0`
- `fastapi>=0.100.0`
- `uvicorn>=0.23.0`
- `pillow>=10.0.0`
- `kagglehub>=0.1.0`
- `scikit-learn>=1.3.0`
- `matplotlib>=3.7.0`
- `seaborn>=0.12.0`
- `tqdm>=4.65.0`

---

## 🎯 Quick Start Summary

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download dataset
python -c "import kagglehub; print(kagglehub.dataset_download('emmarex/plantdisease'))"

# 3. Train model
python train.py --dataset /path/to/dataset --epochs 50 --output output

# 4. Test inference
python infer.py --image test.jpg --model output/best_model.pth --class-map output/class_map.json

# 5. Start API server
python api.py --host 0.0.0.0 --port 8000

# 6. Test API
curl -X POST http://localhost:8000/classify -F "file=@test.jpg"
```

---

## 📞 Integration Example

### Full Pipeline (Image → Advice)

```python
import requests

# Classification API
classify_response = requests.post(
    "http://localhost:8000/classify",
    files={"file": open("plant_image.jpg", "rb")}
)

classification = classify_response.json()
print("Classification:", classification)

# LLM Reasoning API (separate service)
reasoning_response = requests.post(
    "http://localhost:8001/reason",
    json=classification
)

advice = reasoning_response.json()
print("Farmer Advice:", advice)
```

---

Built with 🌾 for Indian Farmers | Mobile-First 📱 | Offline-First 🔌
