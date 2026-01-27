# 🌾 FARMER ASSISTANT - COMPLETE SYSTEM

A mobile-first, offline-first AI system to help Indian farmers diagnose and treat plant diseases.

## 📋 System Overview

```
Plant Image → Image Classification → LLM Reasoning → Farmer Advice
```

### Two-Layer Architecture

1. **Image Classification Layer** (`image_classifier/`)
   - Classifies plant diseases from images
   - Outputs structured JSON
   - MobileNetV3-Large model
   - Can export to TFLite for mobile

2. **LLM Reasoning Layer** (`reasoning_layer/`)
   - Receives classification JSON
   - Generates farmer-friendly advice
   - Uses local LLM (Qwen 2.5) or knowledge base
   - Provides organic/chemical solutions

---

## 🚀 Quick Start

### Option 1: Demo Mode (Fastest)

No model download required!

```bash
# Terminal 1: Start Image Classifier (Demo - without trained model)
cd image_classifier
pip install -r requirements.txt
# Note: Will show warning until model is trained

# Terminal 2: Start Reasoning Layer (Demo Mode)
cd reasoning_layer
pip install -r requirements.txt
python main_demo.py
```

### Option 2: Full System

With trained image classifier and LLM

```bash
# 1. Train image classifier
cd image_classifier
pip install -r requirements.txt
python train.py --dataset /path/to/plantvillage --epochs 50 --output output

# 2. Start image classification API
python api.py --port 8000

# 3. Start reasoning API (separate terminal)
cd ../reasoning_layer
python main_demo.py --port 8001

# 4. Test full pipeline
curl -X POST http://localhost:8000/classify -F "file=@test_image.jpg" > result.json
curl -X POST http://localhost:8001/reason -H "Content-Type: application/json" -d @result.json
```

---

## 📂 Project Structure

```
ATHARVA/
├── image_classifier/          # Layer 1: Image Classification
│   ├── model.py              # MobileNetV3-Large model
│   ├── dataset.py            # PlantVillage dataset loader
│   ├── train.py              # Training script
│   ├── infer.py              # Command-line inference
│   ├── api.py                # FastAPI service (port 8000)
│   ├── requirements.txt      # Python dependencies
│   └── README.md             # Module documentation
│
├── reasoning_layer/           # Layer 2: LLM Reasoning
│   ├── main_demo.py          # Demo mode (knowledge base)
│   ├── main.py               # Production mode (LLM)
│   ├── test_final.py         # Unit tests
│   ├── llama/                # llama.cpp documentation
│   ├── models/               # LLM model files
│   ├── requirements.txt      # Python dependencies
│   └── README.md             # Module documentation
│
├── ARCHITECTURE.md            # System architecture
├── QUICKSTART.md             # Setup guide
├── quick_start.ps1           # Windows setup script
└── README.md                 # This file
```

---

## 🎯 Key Features

### ✅ Mobile-First

- Lightweight model (MobileNetV3)
- Can export to TFLite
- Fast inference (<300ms target)
- Works on mobile devices

### ✅ Offline-First

- No internet required
- Local model execution
- Runs on device
- Privacy-preserving

### ✅ Farmer-Friendly

- Simple language
- Actionable advice
- Organic solutions first
- Expert consultation guidance

### ✅ Safe & Reliable

- Confidence thresholds
- "Unknown" detection
- No unsafe advice
- Fallback mechanisms

---

## 🔗 API Endpoints

### Image Classification API (Port 8000)

```bash
# Health check
GET http://localhost:8000/health

# Classify image
POST http://localhost:8000/classify
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

### Reasoning API (Port 8001)

```bash
# Health check
GET http://localhost:8001/health

# Get advice
POST http://localhost:8001/reason
Content-Type: application/json
Body: {classification JSON from above}
```

**Response:**

```json
{
  "problem": "Your tomato plant has Early Blight disease...",
  "reason": "This fungal infection occurs in warm, humid conditions...",
  "immediate_actions": ["Remove infected leaves", "Improve air circulation"],
  "organic_solutions": ["Neem oil spray", "Baking soda solution"],
  "chemical_solution": "Consult local agriculture officer...",
  "prevention": ["Use drip irrigation", "Apply mulch"],
  "confidence_note": "Detection confidence is 87 percent"
}
```

---

## 📊 Data Flow

```
1. FARMER CAPTURES IMAGE
   └→ Plant leaf photo

2. IMAGE CLASSIFICATION (Port 8000)
   └→ POST /classify
   └→ {crop, issue, confidence, severity}

3. LLM REASONING (Port 8001)
   └→ POST /reason
   └→ {problem, reason, actions, solutions, prevention}

4. FARMER RECEIVES ADVICE
   └→ Displays on mobile app
   └→ Text-to-speech (optional)
   └→ WhatsApp/SMS (optional)
```

---

## 🧪 Testing

### Test Image Classifier

```bash
cd image_classifier
python infer.py --image test.jpg --model output/best_model.pth --class-map output/class_map.json
```

### Test Reasoning Layer

```bash
cd reasoning_layer
python test_final.py
```

### Test Full Pipeline

```bash
# 1. Start both services
# 2. Run integration test
python test_integration.py  # (create this file)
```

---

## 📱 Mobile Deployment Path

### Current (Laptop/Server)

```
Python FastAPI → PyTorch Model → llama.cpp → JSON Response
```

### Future (Mobile)

```
Native App (Java/Kotlin/Swift) → TFLite Model → llama.cpp (ARM64) → JSON Response
```

**Migration steps:**

1. Export PyTorch model to TFLite (see `model.py`)
2. Compile llama.cpp for ARM64 (Android/iOS)
3. Port Python logic to native code
4. Same JSON contract - no changes needed!

---

## 🔧 System Requirements

### Development

- Python 3.8+
- 4GB+ RAM
- 10GB disk space
- CPU (GPU optional)

### Production (Laptop/Server)

- Python 3.8+
- 8GB+ RAM (for LLM)
- 20GB disk space
- CPU or GPU

### Mobile (Future)

- Android 8.0+ or iOS 12+
- 2GB+ RAM
- 1GB storage
- ARM64 processor

---

## 📦 Datasets

### PlantVillage Dataset

- **Source:** Kaggle
- **Size:** 54,000+ images
- **Classes:** 38 crop-disease combinations
- **Download:** `kagglehub.dataset_download("emmarex/plantdisease")`

---

## 🛡️ Safety & Privacy

- ✅ No user data collection
- ✅ All processing on-device
- ✅ No internet required
- ✅ No telemetry
- ✅ Open source

---

## 📚 Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Complete system architecture
- [QUICKSTART.md](QUICKSTART.md) - Setup guide
- [image_classifier/README.md](image_classifier/README.md) - Classification module
- [reasoning_layer/README.md](reasoning_layer/README.md) - Reasoning module
- [DELIVERY.md](DELIVERY.md) - Deployment guide

---

## 🎓 Tech Stack

### Image Classification

- **Framework:** PyTorch
- **Model:** MobileNetV3-Large
- **API:** FastAPI
- **Export:** TFLite

### LLM Reasoning

- **LLM:** Qwen 2.5 (1.5B parameters)
- **Engine:** llama.cpp
- **API:** FastAPI
- **Fallback:** Knowledge base

### Infrastructure

- **Language:** Python 3.8+
- **Web:** FastAPI + Uvicorn
- **Testing:** pytest
- **Deployment:** Docker (optional)

---

## 🚀 Deployment Options

### Option 1: Laptop/PC Demo

```bash
python main_demo.py  # Reasoning layer only
```

### Option 2: Full Server

```bash
docker-compose up  # Both layers + monitoring
```

### Option 3: Mobile App

```
Native Android/iOS app with embedded models
```

---

## 🤝 Contributing

This is a hackathon project. For production use:

1. Expand knowledge base
2. Train on more diverse data
3. Add more crops and diseases
4. Implement mobile apps
5. Add multilingual support

---

## 📄 License

Built for hackathon - open for education and research.

---

## 🙏 Acknowledgments

- **Dataset:** PlantVillage (Kaggle)
- **LLM:** Qwen 2.5 by Alibaba Cloud
- **Engine:** llama.cpp by Georgi Gerganov
- **Framework:** PyTorch, FastAPI

---

Built with 🌾 for Indian Farmers | Mobile-First 📱 | Offline-First 🔌

**For detailed documentation, see:**

- [Image Classifier README](image_classifier/README.md)
- [Reasoning Layer README](reasoning_layer/README.md)
- [System Architecture](ARCHITECTURE.md)
