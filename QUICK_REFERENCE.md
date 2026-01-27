# 🌾 FARMER ASSISTANT - QUICK REFERENCE

One-page guide for quick access to common commands.

---

## 🚀 Quick Start Commands

### Demo Mode (Fastest - No Training)

```bash
cd reasoning_layer
pip install -r requirements.txt
python main_demo.py
```

Access: http://localhost:8001

---

## 📦 Installation

### Image Classifier

```bash
cd image_classifier
pip install -r requirements.txt
```

### Reasoning Layer

```bash
cd reasoning_layer
pip install -r requirements.txt
```

---

## 🧠 Training

### Download Dataset

```bash
python -c "import kagglehub; print(kagglehub.dataset_download('emmarex/plantdisease'))"
```

### Train Model

```bash
cd image_classifier
python train.py --dataset /path/to/data --epochs 50 --output output
```

---

## 🔍 Testing

### Test Inference (CLI)

```bash
cd image_classifier
python infer.py --image test.jpg --model output/best_model.pth --class-map output/class_map.json
```

### Test Reasoning

```bash
cd reasoning_layer
python test_final.py
```

### Test Integration

```bash
python test_integration.py --health
python test_integration.py --image test.jpg
```

---

## 🌐 Start Services

### Manual (2 Terminals)

```bash
# Terminal 1: Image Classifier
cd image_classifier
python api.py --port 8000

# Terminal 2: Reasoning Layer
cd reasoning_layer
python main_demo.py
```

### Automated (Windows)

```bash
.\start_services.ps1
```

---

## 🔗 API Endpoints

### Classification API (Port 8000)

```bash
# Health check
curl http://localhost:8000/health

# Classify image
curl -X POST http://localhost:8000/classify -F "file=@image.jpg"

# Interactive docs
http://localhost:8000/docs
```

### Reasoning API (Port 8001)

```bash
# Health check
curl http://localhost:8001/health

# Get advice
curl -X POST http://localhost:8001/reason \
  -H "Content-Type: application/json" \
  -d '{"crop":"Tomato","issue":"Early Blight","confidence":0.87,"severity":"medium"}'

# Interactive docs
http://localhost:8001/docs
```

---

## 📱 Export to Mobile

### Convert to TFLite

```python
from model import PlantDiseaseClassifier, export_to_tflite
import torch

model = PlantDiseaseClassifier(num_classes=38)
checkpoint = torch.load("output/best_model.pth")
model.load_state_dict(checkpoint['model_state_dict'])
export_to_tflite(model, "model.tflite")
```

---

## 📊 JSON Format

### Classification Output

```json
{
  "success": true,
  "crop": "Tomato",
  "issue": "Early Blight",
  "confidence": 0.87,
  "severity": "medium"
}
```

### Advice Output

```json
{
  "problem": "Your tomato plant has Early Blight...",
  "reason": "This fungal infection...",
  "immediate_actions": ["Remove infected leaves", "Improve air circulation"],
  "organic_solutions": ["Neem oil spray", "Baking soda solution"],
  "chemical_solution": "Consult local agriculture officer...",
  "prevention": ["Use drip irrigation", "Apply mulch"]
}
```

---

## 🔧 Troubleshooting

### Model not found

```bash
cd image_classifier
python train.py --dataset /path/to/data --epochs 50 --output output
```

### Port already in use

```bash
# Use different port
python api.py --port 8002
```

### Out of memory

```bash
# Reduce batch size
python train.py --dataset /path/to/data --batch-size 16 --output output
```

### Service not responding

```bash
# Check if running
curl http://localhost:8000/health
curl http://localhost:8001/health

# Restart
.\start_services.ps1
```

---

## 📚 Documentation Files

| File                   | Quick Link                                               |
| ---------------------- | -------------------------------------------------------- |
| Project Overview       | [PROJECT_README.md](PROJECT_README.md)                   |
| Setup Guide            | [SETUP_GUIDE.md](SETUP_GUIDE.md)                         |
| Implementation Summary | [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)   |
| Visual Overview        | [VISUAL_OVERVIEW.md](VISUAL_OVERVIEW.md)                 |
| Deliverables           | [DELIVERABLES.md](DELIVERABLES.md)                       |
| Image Classifier       | [image_classifier/README.md](image_classifier/README.md) |
| Reasoning Layer        | [reasoning_layer/README.md](reasoning_layer/README.md)   |
| Architecture           | [ARCHITECTURE.md](ARCHITECTURE.md)                       |

---

## 🎯 Common Tasks

### 1. Just Want to See It Work?

```bash
cd reasoning_layer && python main_demo.py
```

### 2. Train a Model

```bash
# Download data first, then:
cd image_classifier
python train.py --dataset /path/to/data --epochs 50 --output output
```

### 3. Test with Image

```bash
cd image_classifier
python infer.py --image test.jpg --model output/best_model.pth --class-map output/class_map.json
```

### 4. Start Full System

```bash
.\start_services.ps1
```

### 5. Test Full Pipeline

```bash
python test_integration.py --image test.jpg
```

---

## 📞 Need Help?

1. Check specific README for your module
2. See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions
3. See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
4. Run health checks: `python test_integration.py --health`

---

Built with 🌾 for Indian Farmers | Mobile-First 📱 | Offline-First 🔌
