#!/usr/bin/env python3
"""知识管线：先精炼 (skeleton + Projects)，再深化 (deep Knowledge)"""
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

print("=== Step 1/2: Knowledge Refinery (Projects + skeleton) ===")
subprocess.run(
    [sys.executable, str(BASE / "knowledge_refinery.py")],
    check=True, timeout=300
)

print("=== Step 2/2: Knowledge Deepener (deep articles) ===")
subprocess.run(
    [sys.executable, str(BASE / "knowledge_deepener_v2.py")],
    check=True, timeout=300
)

print("=== Pipeline complete ===")
