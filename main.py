import json
import os
import re
import subprocess
from typing import Any, Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Farmer Assistant Reasoning Layer")


class ClassificationInput(BaseModel):
    crop: str = Field(..., min_length=1)
    issue: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)
    season: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)


FALLBACK_LOW_CONFIDENCE = {
    "message": "Image is not clear. Please take a clear photo of the affected leaf in daylight."
}

FALLBACK_MISSING_INPUT = {
    "message": "Required input is missing. Please resend crop, issue, confidence, season, location."
}

SAFE_FALLBACK = {
    "message": "Image is not clear. Please take a clear photo of the affected leaf in daylight."
}


def _build_prompt(payload: ClassificationInput) -> str:
    """Build a prompt that encourages clean JSON output"""
    return (
        "You are an Agricultural Reasoning Assistant. Output ONLY valid JSON.\n\n"
        f"Input: {payload.model_dump_json()}\n\n"
        "If confidence < 0.6 OR issue is Unknown:\n"
        '{"message":"Image is not clear. Please take a clear photo of the affected leaf in daylight."}\n\n'
        "Otherwise output this JSON (arrays must contain strings, not objects):\n"
        '{"problem":"brief description","reason":"why this happens","immediate_actions":["action1","action2"],'
        '"organic_solutions":["solution1","solution2"],"chemical_solution":"safe dosage",'
        '"prevention":["tip1","tip2"],"confidence_note":"brief note"}\n\n'
        "JSON Output:"
    )


def _run_llama(prompt: str) -> str:
    """Run llama.cpp binary to generate response"""
    llama_cli = os.getenv("LLAMA_CLI_PATH", "llama/llama-cli.exe")
    model_path = os.getenv(
        "LLAMA_MODEL_PATH", "models/qwen2.5-1.5b-instruct-q4_k_m.gguf"
    )
    max_tokens = os.getenv("LLAMA_MAX_TOKENS", "400")

    cmd = [
        llama_cli,
        "-m",
        model_path,
        "-p",
        prompt,
        "-n",
        str(max_tokens),
        "--temp",
        "0.1",
        "-c",
        "2048",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
    )

    if result.returncode != 0:
        return ""

    # STDOUT contains: prompt + generated text
    # STDERR contains: llama.cpp debug info
    output = result.stdout

    # Extract only the generated text after "JSON Output:"
    if "JSON Output:" in output:
        parts = output.split("JSON Output:", 1)
        if len(parts) > 1:
            generated = parts[1].strip()
            
            # Remove [end of text] marker if present
            generated = generated.replace('[end of text]', '').strip()
            
            return generated

    return output.strip()


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None

    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    candidate = match.group(0)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def _validate_output(data: Dict[str, Any]) -> bool:
    if "message" in data:
        return isinstance(data.get("message"), str)

    required_keys = {
        "problem",
        "reason",
        "immediate_actions",
        "organic_solutions",
        "chemical_solution",
        "prevention",
        "confidence_note",
    }
    if set(data.keys()) != required_keys:
        return False

    if not isinstance(data["immediate_actions"], list):
        return False
    if not isinstance(data["organic_solutions"], list):
        return False
    if not isinstance(data["prevention"], list):
        return False

    return True


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/reason")
def reason(payload: ClassificationInput) -> Dict[str, Any]:
    if not payload.crop or not payload.issue or not payload.season or not payload.location:
        return FALLBACK_MISSING_INPUT

    if payload.confidence < 0.6 or payload.issue.strip().lower() == "unknown":
        return FALLBACK_LOW_CONFIDENCE

    prompt = _build_prompt(payload)
    raw = _run_llama(prompt)
    parsed = _extract_json(raw)

    if parsed and _validate_output(parsed):
        return parsed

    return SAFE_FALLBACK
