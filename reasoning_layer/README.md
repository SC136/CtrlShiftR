# 🌾 FARMER ASSISTANT - LLM REASONING LAYER

## 📋 Overview

This module is the **LLM reasoning layer** for the Farmer Assistant app. It receives structured JSON from the image classification module and generates farmer-friendly advice using an LLM (Qwen 2.5 via llama.cpp) or a knowledge base.

**What it does:**

- ✅ Receives classification JSON from image classifier
- ✅ Generates farmer-friendly advice
- ✅ Provides organic and chemical solutions
- ✅ Suggests prevention measures
- ✅ Works offline with local LLM or knowledge base

**Input:** Classification JSON from image_classifier module
**Output:** Structured advice for farmers

---

## 🏗️ Architecture

```
Classification JSON → Reasoning Layer → Farmer-Friendly Advice
```

### Input Format (from Image Classifier)

```json
{
  "success": true,
  "crop": "Tomato",
  "issue": "Early Blight",
  "confidence": 0.87,
  "severity": "medium"
}
```

### Output Format

```json
{
  "problem": "Your tomato plant has Early Blight...",
  "reason": "This happens due to warm humid weather...",
  "immediate_actions": [
    "Remove all infected leaves...",
    "Stop overhead watering...",
    "Improve spacing between plants..."
  ],
  "organic_solutions": [
    "Spray neem oil solution...",
    "Use baking soda spray..."
  ],
  "chemical_solution": "Consult agriculture officer...",
  "prevention": ["Use drip irrigation...", "Apply mulch around plants..."],
  "confidence_note": "Detection confidence is 87 percent"
}
```

---

## 🚀 Quick Start

### Option 1: Demo Mode (Knowledge Base)

**Fastest** - No model download required!

```bash
cd reasoning_layer
python main_demo.py
```

Access at: `http://localhost:8001`

### Option 2: Production Mode (LLM)

**Full AI** - Requires model download

```bash
cd reasoning_layer

# 1. Download model
python -c "import requests; open('models/qwen2.5-1.5b-instruct-q4_k_m.gguf', 'wb').write(requests.get('https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf').content)"

# 2. Build llama.cpp (requires CMake)
# See llama/llama.cpp.txt for instructions

# 3. Run
python main.py
```

Access at: `http://localhost:8001`

---

## 📚 Files

- **main_demo.py** - Demo mode with knowledge base (4 diseases)
- **main.py** - Production mode with LLM (unlimited diseases)
- **test_final.py** - Unit tests for all scenarios
- **requirements.txt** - Python dependencies
- **sample\_\*.json** - Test input samples
- **llama/** - llama.cpp documentation
- **models/** - LLM model files (after download)

---

## 🧪 Testing

```bash
python test_final.py
```

Tests:

- ✅ Low confidence handling
- ✅ Unknown issue handling
- ✅ Valid disease classification
- ✅ API endpoints

---

## 🔗 Integration with Image Classifier

### Full Pipeline

```python
import requests

# Step 1: Classify image (port 8000)
classify_response = requests.post(
    "http://localhost:8000/classify",
    files={"file": open("plant_image.jpg", "rb")}
)
classification = classify_response.json()

# Step 2: Get advice (port 8001)
advice_response = requests.post(
    "http://localhost:8001/reason",
    json=classification
)
advice = advice_response.json()

print(advice)
```

---

## 📊 Deployment Modes

| Mode                  | Response Time | Memory | Diseases  | Status         |
| --------------------- | ------------- | ------ | --------- | -------------- |
| Demo (Knowledge Base) | <10ms         | ~100MB | 4         | ✅ Working     |
| Production (LLM)      | 1-3s          | ~2GB   | Unlimited | ⚠️ Needs setup |

---

## 🔒 Safety Features

1. **Confidence threshold:** < 0.6 → "Image not clear"
2. **Unknown detection:** Issue = "Unknown" → Safe fallback
3. **No re-diagnosis:** LLM only provides advice, not diagnosis
4. **Chemical advisory:** Always recommends consulting experts

---

Built with 🌾 for Indian Farmers | Mobile-First 📱 | Offline-First 🔌
