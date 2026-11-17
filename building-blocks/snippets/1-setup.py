#!/usr/bin/env python3
"""AI visibility check: asks AI engines about your company and builds a report."""
import html
import json
import os
import re
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.parse import urlparse


def load_config(folder="."):
    """Read config.json (from the folder if it has one, otherwise from here)."""
    path = Path(folder) / "config.json"
    if not path.exists():
        path = Path("config.json")
    try:
        cfg = json.loads(path.read_text())
    except Exception as e:
        sys.exit(f"Cannot read {path}: {e}")
    for key in ("company", "domain", "names", "competitors", "prompts", "engines"):
        if not cfg.get(key):
            sys.exit(f"config.json: '{key}' is missing or empty")
    for eng in cfg["engines"]:
        for key in ("name", "dataset_id", "url"):
            if not eng.get(key):
                sys.exit(f"config.json: an engine is missing '{key}': {eng}")
    return cfg


def jobs_from(cfg):
    """One job per (prompt, engine) pair, for example ('p1', prompt, engine)."""
    return [(f"p{i}", prompt, eng)
            for i, prompt in enumerate(cfg["prompts"], 1)
            for eng in cfg["engines"]]


def cmd_plan(arg=None):
    """Show what will run. Costs nothing."""
    cfg = load_config()
    jobs = jobs_from(cfg)
    print(f"Company: {cfg['company']} ({cfg['domain']})")
    print(f"{len(cfg['prompts'])} prompts x {len(cfg['engines'])} engines = {len(jobs)} jobs\n")
    for pid, prompt, eng in jobs:
        how = "REST" if eng.get("trigger") == "rest" else "CLI"
        print(f"  {pid}  {eng['name']:<14} {how:<5} {prompt}")
    print("\nLooks right? Next: python3 visibility.py start")


# >>> paste the next snippet above this line <<<


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "plan"
    handler = globals().get("cmd_" + command)
    if handler is None:
        sys.exit("Unknown command. Try: plan, start, collect, report, html")
    handler(*sys.argv[2:])
