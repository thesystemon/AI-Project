import json, os
from typing import List, Dict, Any
from ..utils import run_cmd

def run_nuclei(target: str, extra_args: List[str]) -> List[Dict[str, Any]]:
    # Build nuclei command
    cmd = ["nuclei", "-u", target, "-json"]
    if extra_args:
        cmd.extend(extra_args)
    cp = run_cmd(cmd, timeout=1800)
    if cp.returncode not in (0,1):  # nuclei returns 1 if findings were found
        raise RuntimeError(f"Nuclei error: {cp.stderr}")
    results = []
    # Nuclei outputs JSONL
    for line in cp.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            results.append(obj)
        except json.JSONDecodeError:
            continue
    return results
