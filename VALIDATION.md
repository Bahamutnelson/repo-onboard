# Validation

This skill was validated on two axes: **what it does once invoked** (quality) and
**whether it gets invoked at the right time, in any language** (triggering).

## 1. Behaviour quality

Three fixture repos with known ground truth, each run with and without the skill
(subagents, graded on objective assertions):

- `todo-api` — README present, fully consistent (Express REST API for todos)
- `csv2json` — **no README**, purpose only inferable from `setup.py` + `cli.py`
- `velocity-ui` — **README contradicts the code** (claims a "dashboard"; actually a
  publishable React component library)

Result: **100% of assertions passed with the skill vs ~75% without.** The skill's
marginal value concentrated in (a) writing the persistent note (baseline never did)
and (b) explicitly asking the user to confirm the deduced purpose before proceeding.

See `validation/quality-evals.json` for the prompts and assertions.

## 2. Language-universal triggering

**Goal:** the description must route the skill from *any* language, and not fire on
narrowly-scoped requests — regardless of script.

**Why not the off-the-shelf optimizer:** the skill-creator description-optimization
loop counts a trigger only if the model's *first* tool call is the skill. An
onboarding skill's natural first move is to *explore* the repo (a shell/read call),
so that detector reported ~0% triggers across all languages — including English. It
is the wrong instrument for an explore-first skill.

**Instrument used instead — a router-judge** (`validation/judge_router.py`,
`validation/judge_negatives.py`): for each query, an independent `claude -p` is given
*only* the skill description + the user message and asked "should this skill
activate? YES/NO", N runs per query, scored against ground truth and broken down per
language / writing system. No repo needed, no first-tool artifact, language-agnostic.

**Eval set** (`validation/trigger-eval.json`): 32 queries across **16 languages / 7
scripts** (Latin, Cyrillic, Han, Kana, Hangul, Arabic/RTL, Devanagari), balanced
16 should-trigger / 16 should-not (near-misses: explain one function/regex, fix an
error, bump a dependency, write a README, review a PR, add a test, rename a
variable, optimize a query, trace one subsystem).

**Result (opus judge, 3 runs/query; negatives re-confirmed at 7 runs):**

- **Should-fire: 16/16 languages at 100%** — universality holds across every script.
- **False positives ~21%, spread uniformly across scripts** — driven by *content*
  (the leakiest near-misses are "explain this function/regex" and "write a README",
  which are conceptually adjacent to onboarding), **not** by language. Apparent
  per-language "failures" jumped between languages run-to-run, i.e. judge noise at
  small sample sizes, not a stable per-script hole.

For an onboarding skill a false trigger is cheap (it orients and asks) while a false
negative is expensive (working blind), so this boundary was judged acceptable.

### Reproduce

```bash
# needs the `claude` CLI on PATH
python3 validation/judge_router.py    --desc-file <(sed -n '/^description:/,/^---/p' SKILL.md) --label current --runs 3
python3 validation/judge_negatives.py --desc-file <(sed -n '/^description:/,/^---/p' SKILL.md) --runs 7
```

(Or point `--desc-file` at a plain-text file containing just the description.)
