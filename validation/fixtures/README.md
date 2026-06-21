# Quality-axis fixtures

Three throwaway repos with **known ground truth**, used to grade *what the skill
does once invoked* (the behaviour-quality axis in [`../../VALIDATION.md`](../../VALIDATION.md)).
Each one targets a different recon challenge. The graded prompts and the
objective assertions live in [`../quality-evals.json`](../quality-evals.json),
keyed by the `fixture` field.

| Fixture        | Ground truth                                   | What it tests |
|----------------|------------------------------------------------|---------------|
| `todo-api`     | Express REST API for todo lists                | Clear, **consistent** README — does the skill confirm rather than skip the obvious? |
| `csv2json`     | Python CLI that converts CSV → JSON            | **No README** — purpose must be inferred from `setup.py` console_scripts + `cli.py` without hallucinating features. |
| `velocity-ui`  | Publishable React component library            | **README contradicts the code** — claims a "real-time analytics dashboard"; `package.json` (dist build, react peerDeps, `publishConfig`, no `start`) + `src` exporting `Button`/`Card`/`Chart` say library. Does the skill surface the contradiction? |

These are intentionally tiny and not wired to a build/install — they exist to
carry recon *signals* (manifests, entry points, README vs code), not to run.

## Reproduce the quality axis

There is no automated grader for this axis (unlike the trigger axis, which ships
`judge_router.py` / `judge_negatives.py`). It was run by hand with subagents.
To reproduce one case:

1. Pick a fixture and its entry from `quality-evals.json` (matching `fixture`).
2. Run the `prompt` against a fresh agent **in that fixture directory**, once
   with the `repo-onboard` skill available and once without.
3. Score the transcript against that entry's `assertions` (objective
   yes/no checks).

The skill's marginal value concentrates in the assertions a no-skill baseline
tends to miss: writing the persistent note, and explicitly asking the user to
confirm the deduced purpose before doing anything.
