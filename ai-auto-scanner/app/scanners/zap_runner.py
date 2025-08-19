import json, os, shutil, tempfile
from typing import Dict, Any
from ..utils import run_cmd

def run_zap_baseline(target: str) -> Dict[str, Any]:
    # Assumes zap-baseline.py is in PATH when ZAP container is used with docker cp or mounted.
    # Alternatively call ZAP API directly; for simplicity we try the baseline script.
    script = shutil.which("zap-baseline.py")
    if not script:
        # Try dockerized invocation (requires Docker)
        docker = shutil.which("docker")
        if not docker:
            return {"error": "ZAP baseline not available"}
        with tempfile.TemporaryDirectory() as td:
            json_path = os.path.join(td, "zap.json")
            cmd = ["docker","run","--rm","-v",f"{td}:/zap/wrk","owasp/zap2docker-stable",
                   "zap-baseline.py","-t",target,"-J","/zap/wrk/zap.json","-I"]
            cp = run_cmd(cmd, timeout=3600)
            if cp.returncode not in (0,2):  # 2 indicates warnings/failures found
                return {"error": f"ZAP baseline failed: {cp.stderr[:500]}"}
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
    else:
        # Local script path
        with tempfile.TemporaryDirectory() as td:
            json_path = os.path.join(td, "zap.json")
            cmd = [script,"-t",target,"-J",json_path,"-I"]
            cp = run_cmd(cmd, timeout=3600)
            if cp.returncode not in (0,2):
                return {"error": f"ZAP baseline failed: {cp.stderr[:500]}"}
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
