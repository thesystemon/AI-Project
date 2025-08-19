import os, json, subprocess, uuid, datetime, shutil
from typing import List, Dict, Any, Optional
from slugify import slugify
from rich.console import Console

console = Console()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data", "scans")
os.makedirs(DATA_DIR, exist_ok=True)

def gen_scan_id(target: str) -> str:
    ts = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    return f"{slugify(target)}-{ts}-{uuid.uuid4().hex[:6]}"

def run_cmd(cmd: List[str], cwd: Optional[str]=None, timeout: Optional[int]=None) -> subprocess.CompletedProcess:
    console.log(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)

def save_json(path: str, obj: Any):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
