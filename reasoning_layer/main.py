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
    """Build a prompt that STRONGLY encourages clean JSON output only"""
    return (
        "You are an Agricultural Expert. You MUST respond with ONLY valid JSON. NO other text.\n\n"
        f"Input Data:\n"
        f"- Crop: {payload.crop}\n"
        f"- Issue: {payload.issue}\n"
        f"- Confidence: {payload.confidence}\n"
        f"- Season: {payload.season}\n"
        f"- Location: {payload.location}\n\n"
        "CRITICAL RULES:\n"
        "1. Output ONLY a single JSON object\n"
        "2. NO explanations before or after the JSON\n"
        "3. NO markdown code blocks\n"
        "4. Arrays must contain ONLY strings, never objects\n\n"
        "REQUIRED JSON FORMAT:\n"
        "{\n"
        '  "problem": "Brief description of the disease/issue",\n'
        '  "reason": "Why this disease occurs",\n'
        '  "immediate_actions": ["Action 1", "Action 2", "Action 3"],\n'
        '  "organic_solutions": ["Organic solution 1", "Organic solution 2"],\n'
        '  "chemical_solution": "Safe chemical recommendation with EXACT dosage",\n'
        '  "prevention": ["Prevention tip 1", "Prevention tip 2", "Prevention tip 3"],\n'
        '  "confidence_note": "Brief note about the detection confidence"\n'
        "}\n\n"
        "Provide farmer-friendly advice for Indian agricultural conditions.\n"
        "Make recommendations safe and practical.\n\n"
        "JSON:"
    )


def _run_llama(prompt: str) -> str:
    """Run llama.cpp binary to generate response"""
    llama_cli = os.getenv("LLAMA_CLI_PATH", "llama/llama-cli.exe")
    model_path = os.getenv(
        "LLAMA_MODEL_PATH", "../models/qwen2.5-1.5b-instruct-q4_k_m.gguf"
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
    """
    Extract and parse JSON from LLM response.
    Handles multiple JSON blocks, markdown code blocks, and duplicates.
    Returns the FIRST valid JSON found.
    """
    if not text:
        return None

    text = text.strip()
    
    # Remove markdown code blocks if present
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Try direct parsing first (for clean responses)
    if text.startswith("{") and text.endswith("}"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    
    # Find ALL JSON objects in the text
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.finditer(json_pattern, text, re.DOTALL)
    
    # Try to parse each match, return the FIRST valid one
    for match in matches:
        candidate = match.group(0)
        try:
            parsed = json.loads(candidate)
            # Additional validation: ensure it's a dict
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue
    
    return None


def _validate_output(data: Dict[str, Any]) -> bool:
    """
    Validate that the output JSON has the correct structure.
    Returns True if valid, False otherwise.
    """
    if not isinstance(data, dict):
        return False
    
    # Check for fallback message format
    if "message" in data:
        return isinstance(data.get("message"), str) and len(data) == 1
    
    # Check for full advice format
    required_keys = {
        "problem",
        "reason",
        "immediate_actions",
        "organic_solutions",
        "chemical_solution",
        "prevention",
        "confidence_note",
    }
    
    # Must have exactly these keys
    if set(data.keys()) != required_keys:
        return False
    
    # Validate array fields
    array_fields = ["immediate_actions", "organic_solutions", "prevention"]
    for field in array_fields:
        if not isinstance(data[field], list):
            return False
        # All items must be strings
        if not all(isinstance(item, str) for item in data[field]):
            return False
        # Must have at least one item
        if len(data[field]) == 0:
            return False
    
    # Validate string fields
    string_fields = ["problem", "reason", "chemical_solution", "confidence_note"]
    for field in string_fields:
        if not isinstance(data[field], str):
            return False
        # Must not be empty
        if len(data[field].strip()) == 0:
            return False
    
    return True


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/reason")
def reason(payload: ClassificationInput) -> Dict[str, Any]:
    """
    Generate agricultural advice with GUARANTEED valid JSON output.
    Implements retry logic for robustness.
    """
    # Validate required fields
    if not payload.crop or not payload.issue or not payload.season or not payload.location:
        return FALLBACK_MISSING_INPUT

    # Handle low confidence or unknown issue immediately
    if payload.confidence < 0.6 or payload.issue.strip().lower() == "unknown":
        return FALLBACK_LOW_CONFIDENCE

    # Build prompt
    prompt = _build_prompt(payload)
    
    # ATTEMPT 1: Try to get valid JSON
    raw_response = _run_llama(prompt)
    parsed_json = _extract_json(raw_response)
    
    if parsed_json and _validate_output(parsed_json):
        return parsed_json
    
    # ATTEMPT 2: Retry with modified prompt (more explicit)
    retry_prompt = (
        "CRITICAL: You MUST output ONLY valid JSON. No other text.\n\n"
        + prompt
        + "\n\nReminder: Output starts with { and ends with }"
    )
    
    raw_response_retry = _run_llama(retry_prompt)
    parsed_json_retry = _extract_json(raw_response_retry)
    
    if parsed_json_retry and _validate_output(parsed_json_retry):
        return parsed_json_retry
    
    # FINAL FALLBACK: Both attempts failed
    return SAFE_FALLBACK
