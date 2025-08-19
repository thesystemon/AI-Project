import os, json, pathlib
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from .models import ScanRequest, ScanResponse, RawScanResult, TriageResult, Finding, ReportRequest
from .utils import gen_scan_id, save_json, load_json, DATA_DIR
from .scanners.nuclei_runner import run_nuclei
from .scanners.zap_runner import run_zap_baseline
from .ai.llm import triage_findings

app = FastAPI(title="AI Automated Web Scanner (Open‑Source)", version="0.1.0")

def scan_dir(scan_id: str) -> str:
    d = os.path.join(DATA_DIR, scan_id)
    os.makedirs(d, exist_ok=True)
    return d

@app.post("/scan", response_model=ScanResponse)
async def scan(req: ScanRequest):
    scan_id = gen_scan_id(req.target)
    outdir = scan_dir(scan_id)

    # 1) Run Nuclei
    nuclei_raw = run_nuclei(req.target, req.nuclei_args)
    save_json(os.path.join(outdir, "nuclei.json"), nuclei_raw)

    # 2) Optionally run ZAP Baseline
    zap_raw = {}
    if req.run_zap:
        try:
            zap_raw = run_zap_baseline(req.target)
        except Exception as e:
            zap_raw = {"error": str(e)}
    save_json(os.path.join(outdir, "zap.json"), zap_raw)

    raw = RawScanResult(target=req.target, nuclei=nuclei_raw, zap=zap_raw)

    # 3) AI Triage via Ollama
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "triage.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_prompt = f.read()
    triaged = await triage_findings(raw.model_dump(), system_prompt)

    # Validate/normalize AI output
    def norm_finding(x):
        return Finding(
            source=x.get("source","nuclei"),
            severity=x.get("severity","INFO").upper(),
            name=x.get("name","Unnamed"),
            description=x.get("description"),
            matched_at=x.get("matched_at"),
            evidence=x.get("evidence"),
            references=x.get("references",[]),
            tags=x.get("tags",[]),
        )
    findings = [norm_finding(f) for f in triaged.get("findings", [])]
    summary_md = triaged.get("summary_md","No summary.")

    triage = TriageResult(findings=findings, summary_md=summary_md)
    save_json(os.path.join(outdir, "triage.json"), triage.model_dump())

    resp = ScanResponse(scan_id=scan_id, raw=raw, triage=triage)
    save_json(os.path.join(outdir, "response.json"), resp.model_dump())
    return resp

@app.post("/report", response_class=PlainTextResponse)
async def report(req: ReportRequest):
    outdir = scan_dir(req.scan_id)
    resp_path = os.path.join(outdir, "response.json")
    if not os.path.exists(resp_path):
        raise HTTPException(404, f"scan_id {req.scan_id} not found")
    resp = load_json(resp_path)

    # Simple Markdown report
    md = [
        f"# AI Web Scan Report",
        f"**Scan ID:** `{req.scan_id}`  ",
        f"**Target:** {resp['raw']['target']}  ",
        "",
        "## Executive Summary",
        resp['triage'].get('summary_md', 'No summary.'),
        "",
        "## Findings",
    ]
    for f in resp['triage'].get('findings', []):
        md.extend([
            f"### {f.get('severity','INFO')} — {f.get('name','')}",
            f"- **Source:** {f.get('source','')}",
            f"- **Location:** {f.get('matched_at','')}",
            f"- **Details:** {f.get('description','')}",
            f"- **Tags:** {', '.join(f.get('tags', []))}",
            f"- **References:** {', '.join(f.get('references', []))}",
            "",
        ])
    return "\n".join(md)
