#!/usr/bin/env python3
"""High-resolution false-positive test: the should-NOT-fire queries only, many runs.

Settles whether negative-side leakage on a given language is a real boundary hole or
just judge noise at small sample sizes (a single stray YES = 33% at runs=3).

Requires the `claude` CLI on PATH.
Usage: python3 judge_negatives.py --desc-file <file> [--runs 7]
"""
import argparse, json, os, re, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVAL = HERE / "trigger-eval.json"
MODEL = os.environ.get("JUDGE_MODEL", "claude-opus-4-8")
ORDER = [
    ("English","Latin"),("French","Latin"),("Spanish","Latin"),("Portuguese","Latin"),
    ("German","Latin"),("Turkish","Latin"),("Russian","Cyrillic"),("Ukrainian","Cyrillic"),
    ("Swedish","Latin"),("Finnish","Latin"),("Norwegian","Latin"),("Chinese","Han"),
    ("Japanese","Kana/Han"),("Korean","Hangul"),("Arabic","Arabic(RTL)"),("Hindi","Devanagari"),
]
JUDGE = """You are the skill-routing layer of a coding assistant. One skill is available.

SKILL NAME: repo-onboard
SKILL DESCRIPTION:
{desc}

The user's message (may be in any language):
{query}

Based ONLY on the description, should this skill be activated for this message?
The skill is meant to fire for its described situation no matter what language the
user writes in, and must NOT fire for unrelated or narrowly-scoped requests.
Answer with exactly one word: YES or NO."""

def judge(desc, query):
    env = os.environ.copy(); env.pop("CLAUDECODE", None)
    try:
        p = subprocess.run(["claude","-p", JUDGE.format(desc=desc, query=query), "--model", MODEL],
                           capture_output=True, text=True, timeout=90, env=env)
        m = re.search(r"\b(YES|NO)\b", p.stdout.strip().upper())
        return (m.group(1) == "YES") if m else None
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--desc-file", required=True)
    ap.add_argument("--runs", type=int, default=7)
    args = ap.parse_args()
    desc = Path(args.desc_file).read_text().strip()
    evals = json.loads(EVAL.read_text())
    negs = [(i, it) for i, it in enumerate(evals) if not it["should_trigger"]]

    fires = {it["query"]: [] for _, it in negs}
    tasks = [(it["query"], r) for _, it in negs for r in range(args.runs)]
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(judge, desc, q): q for (q, _) in tasks}
        for fut in as_completed(futs):
            v = fut.result()
            if v is not None:
                fires[futs[fut]].append(v)

    print(f"\n=== High-res false-positive test (negatives only) — runs={args.runs}, model={MODEL} ===\n")
    print(f"{'Language':<12}{'Script':<13}{'fires':<8}{'rate':<8}{'verdict'}")
    print("-"*52)
    total_fire = total_run = 0; rows = []
    for i, it in negs:
        lang, script = ORDER[i // 2]
        v = fires[it["query"]]; f = sum(v); n = len(v); rate = f / n if n else 0
        total_fire += f; total_run += n
        rows.append((lang, script, rate, it["query"]))
        print(f"{lang:<12}{script:<13}{f}/{n:<5}{rate*100:4.0f}%   {'OK' if rate < 0.5 else 'FALSE-POSITIVE'}")
    print("-"*52)
    fp = total_fire / total_run if total_run else 0
    nfail = sum(1 for *_, rate, _ in [(r[0], r[1], r[2], r[3]) for r in rows] if rate >= 0.5)
    print(f"Overall false-positive rate: {total_fire}/{total_run} = {fp*100:.1f}%   |   languages over 50%: {nfail}/16")

if __name__ == "__main__":
    main()
