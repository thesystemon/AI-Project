# AI Automated Web Scanner (Open‑Source)

An end‑to‑end starter kit for an AI‑assisted web vulnerability scanner that stitches together:
- **ProjectDiscovery Nuclei** for fast templated checks.
- **(Optional) OWASP ZAP Baseline** for passive checks.
- **Ollama** (local, open‑source LLM runner) to triage, de‑duplicate, prioritize and summarize findings.

> ⚠️ **Legal/Ethical Use Only**: Scan **only** assets you own or have **explicit** written permission to test.

---

## Quickstart

### 0) Prerequisites
- Python 3.9+
- Docker (recommended) if you want to run OWASP ZAP easily.
- Install Nuclei: https://github.com/projectdiscovery/nuclei#install
- Install Ollama: https://ollama.com/download

Pull a good instruction model for security text:
```bash
ollama pull llama3.1:8b-instruct
# (alternatives) qwen2.5:7b-instruct, mistral:7b-instruct
```

### 1) Create a virtualenv & install deps
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) (Optional) Start ZAP in Docker
```bash
docker run -u zap -p 8090:8090 -i ghcr.io/zaproxy/zaproxy:stable zap.sh -daemon -port 8090 -host 0.0.0.0
```
> The app will call ZAP's baseline script only if available. Nuclei alone also works fine.

### 3) Run the API server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4) Kick off a scan
```bash
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "https://example.com", "run_zap": false}'
```

The API will:
1. Run Nuclei (`-json`), parse findings
2. Optionally run ZAP Baseline (if requested and available)
3. Send raw findings to **Ollama** for AI‑triage
4. Return machine‑readable JSON + a human summary

### 5) Produce a PDF/Markdown report (optional)
```bash
curl -X POST http://localhost:8000/report \
  -H "Content-Type: application/json" \
  -d '{"scan_id": "<paste id from /scan response>"}' > report.md
```
Render to PDF with any Markdown to PDF tool if you like.

---

## Project Structure

```
ai-auto-scanner/
├─ README.md
├─ requirements.txt
├─ docker-compose.yml
├─ app/
│  ├─ main.py
│  ├─ models.py
│  ├─ utils.py
│  ├─ ai/llm.py
│  ├─ prompts/triage.md
│  └─ scanners/
│     ├─ nuclei_runner.py
│     └─ zap_runner.py   (optional)
└─ data/
   └─ scans/   (results stored here)
```

---

## Notes & Tips

- **Speed vs Depth**: Start with Nuclei for breadth; add authenticated testing and active scans later.
- **Templates**: Keep Nuclei templates updated (`nuclei -update`). Add your own custom templates in a folder and pass via `--templates`.
- **Model Choice**: If you have a GPU, try larger models via Ollama (e.g., 8B–14B). For CPU‑only, 7B models are fine.
- **Privacy**: Ollama runs locally; no data leaves the box.
- **Extensibility**: Add more scanners (e.g., `whatweb`, `wpscan`, `trivy`, `gitleaks`) and feed outputs into the same AI triage pipeline.

---

## License

MIT
