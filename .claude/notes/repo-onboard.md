# Repo Onboard — repo-onboard

_Deduced 2026-06-21 from main@79d1ac4. Confirmed by user: pending._

## What this repo is
The **source repository for a Claude Code skill** named `repo-onboard` — not an app
or library, but a skill bundle (Markdown + a shell script) plus its validation
harness, packaged as a standalone git repo for distribution. It serves Claude Code
users/developers who want a disciplined "understand the repo before touching it"
first move.

## What it does
Defines a four-phase onboarding workflow the assistant runs against an *unfamiliar*
repo: (1) **recon** via `scripts/recon.sh`, (2) **deduce** what the repo is and flag
contradictions, (3) **persist** the understanding to `.claude/notes/repo-onboard.md`
and ask the user to confirm, (4) **ask** what they want done — without editing
anything. The repo also ships a validation harness proving the skill works.

## Stack & how to run
- Languages: **Markdown** (the skill itself), **Bash** (`scripts/recon.sh`),
  **Python 3** (validation harness). No package manifest — it is a skill bundle, not
  a buildable package.
- Entry point(s): `SKILL.md` — frontmatter `description:` is the routing trigger;
  body is the 4-phase workflow. `scripts/recon.sh` — the Phase-1 recon collector.
- Install: `cp -r repo-onboard ~/.claude/skills/repo-onboard` (per README).
- Reproduce validation (needs `claude` CLI on PATH):
  `python3 validation/judge_router.py --desc-file <(...) --label current --runs 3`
  and `python3 validation/judge_negatives.py --desc-file <(...) --runs 7`.

## Map (the parts that matter)
- `SKILL.md` — the skill definition: routing description + four-phase workflow + note template + guardrails.
- `scripts/recon.sh` — high-signal recon: git facts, pruned tree, manifests, README head, lang histogram, entry points, infra markers.
- `README.md` — public-facing pitch + install instructions.
- `VALIDATION.md` — how the skill was validated on two axes (behaviour quality, language-universal triggering).
- `validation/trigger-eval.json` — 32 queries / 16 languages / 7 scripts, balanced 16 should-fire / 16 near-miss negatives.
- `validation/quality-evals.json` — 3 behaviour fixtures (todo-api, csv2json, velocity-ui) with ground-truth assertions.
- `validation/fixtures/` — the three fixture repos themselves (+ a README mapping them to the evals).
- `validation/judge_router.py`, `judge_negatives.py` — router-judge harness using independent `claude -p` calls.
- `LICENSE`, `NOTICE` — licensing.
- `.remember/` — session-memory buffer; harness-local state, not part of the skill.

## State & signals
- Maturity: **shipped but young** — 2 commits, single author (Bahamutnelson /
  Guillaume), validated on both axes (100% quality assertions with skill vs ~75%
  without; 16/16 languages fire at 100%, ~21% false positives judged acceptable).
- In flight: last commit (today, 2026-06-21) is a docs note confirming the shipped
  description — with its behavioral tail — re-tested as routing-neutral. Reads as a
  just-finished polish pass, no open TODOs found.

## Open questions / contradictions
- ~~Quality-axis fixtures are not in the repo.~~ **Resolved 2026-06-21:** the three
  fixtures (`todo-api`, `csv2json`, `velocity-ui`) are now committed under
  `validation/fixtures/`, with a README and updated `VALIDATION.md` reproduce steps.
- ~~`recon.sh` reported `contributors: 0` despite 2 commits.~~ **Resolved 2026-06-21:**
  `git shortlog -sn` reads commits from stdin in a non-interactive script (empty →
  0); now passes `HEAD` explicitly.
