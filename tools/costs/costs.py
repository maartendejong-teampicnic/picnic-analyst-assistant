#!/usr/bin/env python3
"""Claude Code API cost calculator — reads all session JSONL files and computes costs."""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# Pricing per million tokens (Claude API, Feb 2026)
PRICING = {
    "claude-sonnet-4-6": {
        "input":       3.00,
        "output":     15.00,
        "cache_write": 3.75,
        "cache_read":  0.30,
    },
    "claude-opus-4-6": {
        "input":       15.00,
        "output":      75.00,
        "cache_write": 18.75,
        "cache_read":   1.50,
    },
    "claude-haiku-4-5": {
        "input":       0.80,
        "output":      4.00,
        "cache_write": 1.00,
        "cache_read":  0.08,
    },
    "claude-haiku-4-5-20251001": {
        "input":       0.80,
        "output":      4.00,
        "cache_write": 1.00,
        "cache_read":  0.08,
    },
}

FALLBACK = "claude-sonnet-4-6"

# Prefixes to strip from user messages before building description
_STRIP_PREFIXES = [
    "Implement the following plan:",
    "implement the following plan:",
    "Please implement",
    "please implement",
]


def get_prices(model: str) -> dict:
    if model in PRICING:
        return PRICING[model]
    for key in PRICING:
        if model.startswith(key) or key.startswith(model):
            return PRICING[key]
    return PRICING[FALLBACK]


def compute_cost(usage: dict, model: str) -> float:
    p = get_prices(model)
    return (
        usage.get("input_tokens", 0)                  * p["input"]       / 1_000_000 +
        usage.get("output_tokens", 0)                 * p["output"]      / 1_000_000 +
        usage.get("cache_creation_input_tokens", 0)   * p["cache_write"] / 1_000_000 +
        usage.get("cache_read_input_tokens", 0)       * p["cache_read"]  / 1_000_000
    )


def extract_text(content) -> str:
    """Pull plain text out of a message content field (string or list of blocks)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return " ".join(parts)
    return ""


def make_description(text: str) -> str:
    """Turn a raw user message into a 4-5 word description."""
    text = text.strip()
    # Strip XML/HTML tags (e.g. <command-message>, <local-command-caveat>)
    text = re.sub(r'<[^>]+>', '', text).strip()
    # Strip common preambles
    for prefix in _STRIP_PREFIXES:
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix):].strip()
    # Strip leading @-imports or slash commands
    text = re.sub(r'^[@/]\S+\s*', '', text).strip()
    # Strip any remaining /word tokens (command-name residue like "/setup")
    text = re.sub(r'(?<!\w)/\w+', '', text).strip()
    # Strip markdown headings (# Plan: ...)
    text = re.sub(r'^#+\s*', '', text).strip()
    # Collapse whitespace / newlines
    text = " ".join(text.split())
    # Take first 5 words
    words = text.split()
    desc = " ".join(words[:5])
    if len(words) > 5:
        desc += "…"
    return desc or "—"


def hhmm(ts: str) -> str:
    """Extract HH:MM from an ISO timestamp string."""
    if ts and "T" in ts:
        return ts[11:16]
    return "—"


def main():
    projects_dir = Path.home() / ".claude" / "projects" / "-home-picnic"
    files = sorted(projects_dir.glob("*.jsonl"))

    sessions     = {}              # session_id -> metadata dict
    daily        = defaultdict(float)
    model_totals = defaultdict(float)

    for fp in files:
        try:
            with open(fp) as f:
                for line in f:
                    try:
                        d = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    entry_type = d.get("type")
                    session_id = d.get("sessionId", "unknown")
                    ts         = d.get("timestamp", "")

                    # Ensure session record exists
                    if session_id not in sessions:
                        sessions[session_id] = {
                            "date":        ts[:10] if ts else "unknown",
                            "start_ts":    ts,
                            "end_ts":      ts,
                            "description": None,
                            "cost":        0.0,
                            "output_tok":  0,
                            "turns":       0,
                            "model":       FALLBACK,
                        }

                    s = sessions[session_id]

                    # Track session time window
                    if ts:
                        if not s["start_ts"] or ts < s["start_ts"]:
                            s["start_ts"] = ts
                            s["date"]     = ts[:10]
                        if not s["end_ts"] or ts > s["end_ts"]:
                            s["end_ts"] = ts

                    # First meaningful user text → description
                    if entry_type == "user" and s["description"] in (None, "—"):
                        content = d.get("message", {}).get("content", "")
                        text = extract_text(content).strip()
                        # Skip interrupted/tool-result-only messages
                        if text and not text.startswith("[Request interrupted"):
                            desc = make_description(text)
                            if desc and desc != "—":
                                s["description"] = desc

                    # Usage accounting (assistant messages only)
                    if entry_type == "assistant":
                        msg   = d.get("message", {})
                        usage = msg.get("usage", {})
                        model = msg.get("model", FALLBACK)

                        if usage and model != "<synthetic>":
                            cost = compute_cost(usage, model)
                            s["cost"]       += cost
                            s["output_tok"] += usage.get("output_tokens", 0)
                            s["turns"]      += 1
                            s["model"]       = model
                            daily[s["date"]]    += cost
                            model_totals[model] += cost

        except Exception:
            continue

    # Drop sessions with zero cost (no assistant usage)
    sessions = {k: v for k, v in sessions.items() if v["cost"] > 0}

    if not sessions:
        print("No usage data found in", projects_dir)
        sys.exit(0)

    W = 80
    print("=" * W)
    print("CLAUDE CODE — API COST OVERVIEW")
    print("=" * W)

    # --- By session ---
    print("\nBy session (most recent first):\n")
    D, T = 32, 5
    header = f"  {'Date':<10}  {'Start':>{T}}–{'End':<{T}}  {'What':<{D}}  {'Cost':>8}  {'Turns':>5}"
    print(header)
    print(f"  {'-'*10}  {'-'*(T*2+1)}  {'-'*D}  {'-'*8}  {'-'*5}")

    for sid, s in sorted(sessions.items(), key=lambda x: x[1]["start_ts"], reverse=True):
        if s["cost"] <= 1.0:
            continue
        desc  = (s["description"] or sid[:D])[:D]
        start = hhmm(s["start_ts"])
        end   = hhmm(s["end_ts"])
        print(f"  {s['date']:<10}  {start:>{T}}–{end:<{T}}  {desc:<{D}}  ${s['cost']:>7.4f}  {s['turns']:>5}")

    # --- By date ---
    print("\n\nBy date:\n")
    print(f"  {'Date':<12} {'Cost':>8}  {'Sessions':>8}")
    print(f"  {'-'*12} {'-'*8}  {'-'*8}")
    sessions_per_day = defaultdict(int)
    for s in sessions.values():
        sessions_per_day[s["date"]] += 1
    for date in sorted(daily.keys(), reverse=True):
        print(f"  {date:<12} ${daily[date]:>7.4f}  {sessions_per_day[date]:>8}")

    # --- By model (only if >1 model) ---
    if len(model_totals) > 1:
        print("\n\nBy model:\n")
        for model, cost in sorted(model_totals.items(), key=lambda x: x[1], reverse=True):
            print(f"  {model:<40}  ${cost:>7.4f}")

    # --- Grand total ---
    total = sum(s["cost"] for s in sessions.values())
    print(f"\n{'=' * W}")
    print(f"  TOTAL{' ' * (W - 14)}${total:>7.4f}")
    print("=" * W)
    print(f"\nPricing: claude-sonnet-4-6 — $3/MTok in · $15/MTok out · $3.75/MTok cache-write · $0.30/MTok cache-read")
    print(f"Sessions: {len(sessions)}  |  Data: {projects_dir}")


if __name__ == "__main__":
    main()
