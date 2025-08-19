import httpx, json, os

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b-instruct")

async def triage_findings(raw_data: dict, system_prompt: str) -> dict:
    payload = {
        "model": MODEL,
        "prompt": f"""{system_prompt}

RAW_INPUT (JSON):
{json.dumps(raw_data, ensure_ascii=False, indent=2)}
Please produce the JSON response with keys 'findings' and 'summary_md'.""".strip(),
        "stream": False,
        "options": {"temperature": 0.2}
    }
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
        r.raise_for_status()
        # Ollama returns {'response': '...'} containing the text
        text = r.json().get("response", "").strip()
        # Try parsing JSON from the text; if it isn't pure JSON, find the first { ... } block
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(text[start:end+1])
            raise
