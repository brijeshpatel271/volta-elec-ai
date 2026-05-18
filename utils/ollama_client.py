"""
utils/ollama_client.py
Handles communication with the local Ollama LLM server.
Supports streaming responses and model management.
"""

import requests
import json
from typing import Generator


OLLAMA_BASE_URL = "http://localhost:11434"

# Recommended models (in order of preference for EE tasks)
RECOMMENDED_MODELS = [
    "deepseek-r1:7b",      # Best for STEM reasoning
    "deepseek-r1:1.5b",    # Lighter version
    "llama3.1:8b",          # Good general purpose
    "mistral:7b",           # Fast and capable
    "llama3.2:3b",          # Lightweight option
]


def get_available_models() -> list[str]:
    """Fetch list of models installed in Ollama."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        return []
    except requests.exceptions.ConnectionError:
        return []
    except Exception:
        return []


def check_ollama_running() -> bool:
    """Check if Ollama server is up and running."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        return response.status_code == 200
    except Exception:
        return False


def stream_chat(
    model: str,
    messages: list[dict],
    system_prompt: str = "",
    temperature: float = 0.3,
) -> Generator[str, None, None]:
    """
    Stream a chat completion from Ollama.
    
    Args:
        model: Ollama model name (e.g. 'deepseek-r1:7b')
        messages: List of {"role": "user"|"assistant", "content": str}
        system_prompt: System instruction string
        temperature: 0.0 = deterministic, 1.0 = creative
    
    Yields:
        str: Token chunks as they arrive
    """
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "stream": True,
        "options": {
            "temperature": temperature,
            "num_predict": 4096,
            "top_p": 0.9,
        },
    }

    try:
        with requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            stream=True,
            timeout=120,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            yield content
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
    except requests.exceptions.ConnectionError:
        yield "\n\n⚠️ **Cannot connect to Ollama.** Make sure Ollama is running: `ollama serve`"
    except requests.exceptions.Timeout:
        yield "\n\n⚠️ **Request timed out.** The model may be loading — try again in a moment."
    except Exception as e:
        yield f"\n\n⚠️ **Error:** {str(e)}"


def chat_simple(
    model: str,
    messages: list[dict],
    system_prompt: str = "",
    temperature: float = 0.3,
) -> str:
    """Non-streaming version — returns full response as string."""
    return "".join(stream_chat(model, messages, system_prompt, temperature))


def pull_model(model: str) -> Generator[str, None, None]:
    """
    Pull/download a model from Ollama registry.
    Yields status updates.
    """
    try:
        with requests.post(
            f"{OLLAMA_BASE_URL}/api/pull",
            json={"name": model},
            stream=True,
            timeout=3600,
        ) as response:
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        status = data.get("status", "")
                        total = data.get("total", 0)
                        completed = data.get("completed", 0)
                        if total and completed:
                            pct = int((completed / total) * 100)
                            yield f"{status}: {pct}%"
                        else:
                            yield status
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        yield f"Error: {e}"
