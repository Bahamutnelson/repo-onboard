#!/usr/bin/env python3
"""Router-judge per-language triggering test.

For each query in trigger-eval.json, ask an independent `claude -p` judge whether,
given ONLY the skill description, the skill should be activated for that message.
Measures the routing decision the description drives — language-agnostic, needs no
repo, and avoids the first-tool-call artifact of trigger detectors that require the
skill to be the model's very first action.

Requires the `claude` CLI on PATH.
Usage: python3 judge_router.py --desc-file <file> --label <name> [--runs 3]
"""
import argparse, json, os, re, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVAL = HERE / "trigger-eval.json"
THRESH = 0.5
MODEL = os.environ.get("JUDGE_MODEL", "claude-opus-4-8")
# language/script of each [should_trigger, should_not] pair, in eval-file order
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
    ap.add_argument("--label", default="description")
    ap.add_argument("--runs", type=int, default=3)
    args = ap.parse_args()

    desc = Path(args.desc_file).read_text().strip()
    evals = json.loads(EVAL.read_text())
    qmeta = {it["query"]: (*ORDER[i // 2], it["should_trigger"]) for i, it in enumerate(evals)}

    fires = {it["query"]: [] for it in evals}
    tasks = [(it["query"], r) for it in evals for r in range(args.runs)]
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(judge, desc, q): q for (q, _) in tasks}
        for fut in as_completed(futs):
            v = fut.result()
            if v is not None:
                fires[futs[fut]].append(v)

    rate = {q: (sum(v)/len(v) if v else None) for q, v in fires.items()}
    per = {lang: {} for lang, _ in ORDER}
    for q, (lang, script, expect) in qmeta.items():
        r = rate[q]
        ok = None if r is None else ((r >= THRESH) if expect else (r < THRESH))
        per[lang]["T" if expect else "F"] = (r, ok)

    print(f"\n=== Router-judge per-language scores: {args.label}  (model={MODEL}, runs={args.runs}) ===\n")
    print(f"{'Language':<12}{'Script':<13}{'should-fire':<14}{'should-NOT-fire':<16}{'verdict'}")
    print("-"*70)
    nok = 0; by_s = {}
    for lang, script in ORDER:
        t = per[lang].get("T"); f = per[lang].get("F")
        def cell(x):
            if x is None or x[0] is None: return "n/a"
            return f"{x[0]*100:3.0f}% {'OK' if x[1] else 'XX'}"
        both = bool(t and f and t[1] and f[1]); nok += both
        by_s.setdefault(script, [0,0]); by_s[script][0]+=both; by_s[script][1]+=1
        print(f"{lang:<12}{script:<13}{cell(t):<14}{cell(f):<16}{'OK' if both else '<-- CHECK'}")
    print("-"*70)
    tot_t = sum(1 for l,_ in ORDER if per[l].get('T') and per[l]['T'][1])
    tot_f = sum(1 for l,_ in ORDER if per[l].get('F') and per[l]['F'][1])
    print(f"should-fire correct: {tot_t}/16   should-NOT-fire correct: {tot_f}/16   languages fully clean: {nok}/16")
    print("By script family: " + " | ".join(f"{s} {ok}/{tt}" for s,(ok,tt) in by_s.items()))

if __name__ == "__main__":
    main()
