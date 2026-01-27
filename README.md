# 🌾 Farmer Assistant - LLM Reasoning Layer

**Mobile-First, Offline-First Agricultural Reasoning System**

## 📋 Overview

This is the LLM Reasoning Layer of a Farmer Assistant App that provides actionable agricultural advice to Indian farmers based on plant disease classifications.

### Architecture

```
Farmer
  ↓
Camera (Plant Image)
  ↓
Image Classification Model (ML/CV)
  ↓
Structured Result (JSON)
  ↓
LLM Reasoning Layer (THIS MODULE) ← You are here
  ↓
Explanation + Solution
  ↓
UI / Chat / WhatsApp
```

## ✨ Features

- ✅ **Guardrails**: Validates confidence before reasoning
- ✅ **Safety-First**: No unsafe chemical dosage or medical advice
- ✅ **Farmer-Friendly**: Simple language, practical solutions
- ✅ **Offline-First**: CPU-only, runs without internet
- ✅ **Mobile-Ready**: Optimized for low-resource devices
- ✅ **Deterministic**: Consistent outputs with seed control

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **LLM Runtime**: llama.cpp (C++)
- **Model**: Qwen2.5-1.5B-Instruct (Q4 GGUF)
- **Deployment**: CPU-only, no GPU required

## 📦 Installation

### Quick Start (Recommended)

Run the automated setup script:

```powershell
.\quick_start.ps1
```

This will:
1. Install Python dependencies
2. Download llama.cpp binary (pre-built)
3. Download Qwen model
4. Start the server

### Manual Installation

#### Step 1: Install Python Dependencies

```powershell
pip install -r requirements.txt
```

Requirements:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation

#### Step 2: Get llama.cpp Binary

**Windows**: Download pre-built binary from [llama.cpp releases](https://github.com/ggerganov/llama.cpp/releases)
- Look for: `llama-*-bin-win-avx2-x64.zip`
- Extract to `llama/` folder

**Linux/Mac**: Build from source or download pre-built binary

#### Step 3: Download the GGUF Model

Download from [Hugging Face](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF):
- File: `qwen2.5-1.5b-instruct-q4_k_m.gguf` (~1GB)
- Place in: `models/qwen2.5-1.5b-instruct-q4_k_m.gguf`

#### Step 4: Test llama.cpp

```powershell
.\llama\llama-cli.exe -m models\qwen2.5-1.5b-instruct-q4_k_m.gguf -p "Test prompt" -n 50
```

## 🚀 Usage

### Start the Server

**Production Mode** (Real LLM):
```powershell
uvicorn main:app --reload
```

**Demo Mode** (Hardcoded responses for testing):
```powershell
uvicorn main_demo:app --reload
```
.\llama.cpp\build\bin\Release\llama-cli.exe -m llama.cpp\models\qwen2.5-1.5b-instruct-q4_k_m.gguf -p "Hello" -n 50
```

Expected: Text generation output

## 🚀 Usage

### Start the API Server

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000
```

Or with auto-reload for development:

```powershell
uvicorn main:app --reload
```

### Test the API

Run the test suite:

```powershell
python test_api.py
```

Or manually test with curl:

```bash
curl -X POST http://localhost:8000/reason \
  -H "Content-Type: application/json" \
  -d @sample_high_confidence.json
```

## 📝 API Reference

### Endpoint: `/reason`

**Method**: POST

**Input Format**:

```json
{
  "crop": "Tomato",
  "issue": "Early Blight",
  "confidence": 0.87,
  "season": "Kharif",
  "location": "Maharashtra"
}
```

**Output (High Confidence ≥ 0.6)**:

```json
{
  "problem": "Your tomato plant has Early Blight disease",
  "reason": "This happens due to warm humid weather and poor air circulation",
  "immediate_actions": [
    "Remove all infected leaves immediately",
    "Stop overhead watering",
    "Improve spacing between plants"
  ],
  "organic_solutions": [
    "Spray neem oil solution every 7 days",
    "Use baking soda spray 1 tablespoon per liter water"
  ],
  "chemical_solution": "Consult local agriculture officer for copper fungicide guidance",
  "prevention": [
    "Use drip irrigation instead of overhead watering",
    "Apply mulch to prevent soil splash"
  ],
  "confidence_note": "Detection confidence is 87 percent"
}
```

**Output (Low Confidence < 0.6 or Unknown Issue)**:

```json
{
  "message": "Image is not clear. Please take a clear photo of the affected leaf in daylight."
}
```

## 🔧 Configuration

Set environment variables to customize paths:

```powershell
# Windows
$env:LLAMA_CLI_PATH = "D:\path\to\llama-cli.exe"
$env:LLAMA_MODEL_PATH = "D:\path\to\model.gguf"
$env:LLAMA_MAX_TOKENS = "256"

# Linux/Mac
export LLAMA_CLI_PATH=/path/to/llama-cli
export LLAMA_MODEL_PATH=/path/to/model.gguf
export LLAMA_MAX_TOKENS=256
```

**Defaults**:

- `LLAMA_CLI_PATH`: `llama/llama-cli.exe` (Windows) or `llama/llama-cli` (Linux)
- `LLAMA_MODEL_PATH`: `models/qwen2.5-1.5b-instruct-q4_k_m.gguf`
- `LLAMA_MAX_TOKENS`: `400`

## 🧪 Testing

### Automated Testing

Run the comprehensive test suite:

```powershell
python test_final.py
```

This tests:
- Health endpoint
- Real LLM with high confidence input
- Safety guardrails (low confidence)
- Different disease scenarios

### Manual Testing

Three sample JSON files are provided:

1. **sample_high_confidence.json**: Valid disease detection (confidence 0.87)
2. **sample_low_confidence.json**: Low confidence < 0.6
3. **sample_unknown_issue.json**: Unknown disease

Test with curl or Invoke-WebRequest:

```powershell
# Start server
uvicorn main:app --reload

# In another terminal (PowerShell)
$payload = Get-Content sample_high_confidence.json
Invoke-WebRequest -Uri "http://localhost:8000/reason" -Method POST -Body $payload -ContentType "application/json"
```

## 🛡️ Safety Guardrails

1. **Confidence Check**: Rejects inputs with confidence < 0.6
2. **Unknown Issues**: Returns safe fallback for "Unknown" classifications
3. **No Re-diagnosis**: Never overrides image classification results
4. **Advisory Only**: Chemical solutions are marked as advisory
5. **Fallback Handling**: Always returns safe message on errors

## 📱 Mobile Deployment (Future)

This layer is designed to be mobile-ready:

- **Same Model**: Use the same GGUF file on Android/iOS
- **No Dependencies**: llama.cpp compiles to native mobile libs
- **Low Memory**: Q4 quantization keeps model under 1GB
- **CPU-Only**: Works without GPU acceleration

## 🐛 Troubleshooting

### llama-cli not found

**Solution**: Verify binary exists

```powershell
# Check if binary exists
Test-Path ".\llama\llama-cli.exe"

# Set explicit path
$env:LLAMA_CLI_PATH = "D:\HACATHONS\ATHARVA\llama\llama-cli.exe"
```

### Model file not found

**Solution**: Verify model location

```powershell
# Check if model exists
Test-Path ".\models\qwen2.5-1.5b-instruct-q4_k_m.gguf"

# Set correct path
$env:LLAMA_MODEL_PATH = "D:\HACATHONS\ATHARVA\models\qwen2.5-1.5b-instruct-q4_k_m.gguf"
```

### API returns fallback for valid inputs

**Solution**: Test llama-cli directly

```powershell
.\llama\llama-cli.exe -m models\qwen2.5-1.5b-instruct-q4_k_m.gguf -p "Test" -n 50
```

If this works, the issue is likely with path configuration.

### Import errors

**Solution**: Install dependencies

```powershell
pip install -r requirements.txt
```

## 📁 Project Structure

```
ATHARVA/
├── main.py                          # FastAPI server (Production with Real LLM)
├── main_demo.py                     # FastAPI server (Demo mode with hardcoded responses)
├── requirements.txt                 # Python dependencies (FastAPI, uvicorn, pydantic)
├── quick_start.ps1                  # Automated setup script
├── test_final.py                    # Comprehensive test suite
├── sample_high_confidence.json      # Test: Valid disease (confidence 0.87)
├── sample_low_confidence.json       # Test: Low confidence (< 0.6)
├── sample_unknown_issue.json        # Test: Unknown disease
├── README.md                        # Documentation (this file)
├── QUICKSTART.md                    # Quick setup guide
├── ARCHITECTURE.md                  # System architecture
├── DELIVERY.md                      # Deployment guide
├── INDEX.md                         # Project index
├── llama/                           # llama.cpp runtime binaries
│   ├── llama-cli.exe               # Main binary for inference
│   └── *.dll                       # Required libraries
└── models/                          # LLM models
    └── qwen2.5-1.5b-instruct-q4_k_m.gguf  # Qwen 1.5B Q4 model (~1GB)
```

## 🎯 Design Principles

1. **Safety First**: Better to refuse than to give wrong advice
2. **Offline-First**: Works without internet connectivity
3. **Mobile-Ready**: Optimized for resource-constrained devices
4. **Deterministic**: Consistent outputs for testing
5. **Simple Language**: Farmer-friendly explanations
6. **JSON-Only**: Structured, parseable responses

## 📄 License

This project is part of a hackathon submission.

## 🤝 Contributing

This is a controlled reasoning engine with strict guardrails. Any modifications should maintain:

- Safety guarantees
- Offline capability  
- Mobile compatibility
- Deterministic behavior

## 📞 Support

For issues or questions, refer to:

- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [llama.cpp documentation](https://github.com/ggerganov/llama.cpp)
- [FastAPI documentation](https://fastapi.tiangolo.com/)

---

**Built for Indian Farmers 🇮🇳 | Mobile-First 📱 | Offline-First 🔌**
