#!/usr/bin/env python3
"""Artificial Diastole Experiment (v0.1.0)

A/B test:
- Control: continuous generation (neutral instructions)
- Treatment: diastolic generation (Bridge Formula prompt enforcing pause + holding space)

Outputs:
- outputs/continuous/<id>.json
- outputs/diastolic/<id>.json
- outputs.jsonl (lean transcript)
- comparison.md (blinded side-by-side)
- key.json (unblinding key)

Requirements:
- Python 3.10+
- pip install openai
- export OPENAI_API_KEY=...

Uses OpenAI Responses API via the official Python SDK.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from openai import OpenAI

DEFAULT_MODEL = os.getenv("DIASTOLIC_MODEL", "gpt-4.1")
DEFAULT_TEMPERATURE = float(os.getenv("DIASTOLIC_TEMPERATURE", "0.2"))

@dataclass
class RunConfig:
    model: str
    temperature: float
    seed: int
    out_dir: Path
    prompts_path: Path
    max_output_tokens: int

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]

def load_prompts(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "prompts" not in data or not isinstance(data["prompts"], list):
        raise ValueError("prompts.json must have top-level key 'prompts' as a list.")
    return data["prompts"]

def ensure_dirs(out_dir: Path) -> None:
    (out_dir / "outputs" / "continuous").mkdir(parents=True, exist_ok=True)
    (out_dir / "outputs" / "diastolic").mkdir(parents=True, exist_ok=True)

def call_model(
    client: OpenAI,
    *,
    model: str,
    instructions: str,
    user_prompt: str,
    temperature: float,
    max_output_tokens: int,
) -> Dict[str, Any]:
    resp = client.responses.create(
        model=model,
        instructions=instructions,
        input=user_prompt,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )
    out_text = getattr(resp, "output_text", None) or ""
    raw = resp.model_dump() if hasattr(resp, "model_dump") else json.loads(resp.json())
    return {"output_text": out_text, "raw": raw}

def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def append_jsonl(path: Path, obj: Any) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def blinded_label(prompt_id: str, mode: str, salt: str) -> str:
    h = stable_hash(f"{salt}:{prompt_id}")
    bit = int(h, 16) % 2
    if bit == 0:
        return "A" if mode == "continuous" else "B"
    return "B" if mode == "continuous" else "A"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--max_output_tokens", type=int, default=900)
    ap.add_argument("--prompts", default="prompts.json")
    ap.add_argument("--out", default=".")
    ap.add_argument("--sleep", type=float, default=0.0)
    args = ap.parse_args()

    cfg = RunConfig(
        model=args.model,
        temperature=args.temperature,
        seed=args.seed,
        out_dir=Path(args.out).resolve(),
        prompts_path=Path(args.prompts).resolve(),
        max_output_tokens=args.max_output_tokens,
    )

    ensure_dirs(cfg.out_dir)
    prompts = load_prompts(cfg.prompts_path)

    continuous_instructions = (cfg.out_dir / "continuous_instructions.txt").read_text(encoding="utf-8")
    diastolic_instructions = (cfg.out_dir / "diastolic_instructions.txt").read_text(encoding="utf-8")

    client = OpenAI()
    random.seed(cfg.seed)

    salt = f"{cfg.seed}:{utc_now()}"
    key_map: Dict[str, Any] = {
        "meta": {"seed": cfg.seed, "salt": salt, "model": cfg.model, "temperature": cfg.temperature},
        "pairs": [],
    }

    jsonl_path = cfg.out_dir / "outputs.jsonl"
    if jsonl_path.exists():
        jsonl_path.unlink()

    comparison_lines: List[str] = [
        "# Artificial Diastole — Blinded Comparisons",
        "",
        f"- model: `{cfg.model}`",
        f"- temperature: `{cfg.temperature}`",
        f"- seed: `{cfg.seed}`",
        "",
    ]

    for p in prompts:
        pid = p["id"]
        category = p.get("category", "UNKNOWN")
        user_prompt = p["prompt"]

        modes = ["continuous", "diastolic"]
        random.shuffle(modes)

        results: Dict[str, Dict[str, Any]] = {}

        for mode in modes:
            instructions = continuous_instructions if mode == "continuous" else diastolic_instructions
            t0 = time.time()
            r = call_model(
                client,
                model=cfg.model,
                instructions=instructions,
                user_prompt=user_prompt,
                temperature=cfg.temperature,
                max_output_tokens=cfg.max_output_tokens,
            )
            dt = time.time() - t0

            record = {
                "ts": utc_now(),
                "prompt_id": pid,
                "category": category,
                "mode": mode,
                "model": cfg.model,
                "temperature": cfg.temperature,
                "latency_s": round(dt, 3),
                "prompt": user_prompt,
                "output_text": r["output_text"],
                "raw_response": r["raw"],
            }

            out_path = cfg.out_dir / "outputs" / mode / f"{pid}.json"
            write_json(out_path, record)
            append_jsonl(jsonl_path, {k: v for k, v in record.items() if k != "raw_response"})
            results[mode] = record

            if args.sleep > 0:
                time.sleep(args.sleep)

        label_cont = blinded_label(pid, "continuous", salt)
        # Determine which output is A/B
        recA = results["continuous"] if label_cont == "A" else results["diastolic"]
        recB = results["diastolic"] if label_cont == "A" else results["continuous"]

        comparison_lines.extend([
            f"## {pid} — {category}",
            "",
            "**Prompt**",
            "",
            "```",
            user_prompt.strip(),
            "```",
            "",
            "### Response A",
            "",
            recA["output_text"].strip(),
            "",
            "### Response B",
            "",
            recB["output_text"].strip(),
            "",
            "---",
            "",
        ])

        key_map["pairs"].append({
            "prompt_id": pid,
            "category": category,
            "A": recA["mode"],
            "B": recB["mode"],
        })

    (cfg.out_dir / "comparison.md").write_text("\n".join(comparison_lines), encoding="utf-8")
    write_json(cfg.out_dir / "key.json", key_map)

    print("DONE")
    print(f"- outputs.jsonl: {jsonl_path}")
    print(f"- comparison.md: {cfg.out_dir / 'comparison.md'}")
    print(f"- key.json: {cfg.out_dir / 'key.json'}")
    print(f"- per-prompt JSON: {cfg.out_dir / 'outputs/continuous'} and {cfg.out_dir / 'outputs/diastolic'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
