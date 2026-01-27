# Farmer Assistant LLM Reasoning Layer

## Setup

### Quick Start

```powershell
# Run automated setup
.\quick_start.ps1
```

### Manual Setup

1. Install dependencies:
```powershell
pip install -r requirements.txt
```

2. Download llama.cpp binary for Windows from [releases](https://github.com/ggerganov/llama.cpp/releases) and extract to `llama/` folder.

3. Download Qwen model from [Hugging Face](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF) and place in `models/` folder.

## Usage

### Start Server

Production mode (real LLM):
```powershell
uvicorn main:app --reload
```

Demo mode (hardcoded responses):
```powershell
uvicorn main_demo:app --reload
```

### API Endpoint

POST `/reason` with JSON:
```json
{
  "crop": "Tomato",
  "issue": "Early Blight",
  "confidence": 0.87,
  "season": "Kharif",
  "location": "Maharashtra"
}
```

## Testing

Run comprehensive tests:
```powershell
python test_final.py
```

## Project Structure

```
├── main.py              # Production server with LLM
├── main_demo.py         # Demo server with hardcoded responses
├── requirements.txt     # Dependencies
├── test_final.py        # Test suite
├── sample_*.json        # Test data
├── llama/               # llama.cpp binaries (download separately)
├── models/              # Qwen model (download separately)
└── docs/                # Documentation
```