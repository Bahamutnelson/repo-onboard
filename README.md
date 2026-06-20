# repo-onboard

A Claude Code [skill](https://docs.claude.com/en/docs/claude-code/skills) that turns
"what even *is* this project?" into a disciplined first move: it reconnoiters an
unfamiliar repository, deduces what it's for from the evidence, **asks you to
confirm or correct that understanding**, and only then asks what you'd like done —
without touching anything first.

It exists because jumping straight into edits on a repo you don't understand is how
you fix the wrong layer, duplicate what already exists, or break an intended
contract. Ten minutes of structured reconnaissance is cheap insurance.

## What it does

Four phases:

1. **Reconnaissance** — runs `scripts/recon.sh` to gather high-signal facts in one
   pass (git remote/branch/last commit, a pruned tree, every package manifest with
   name/scripts/deps extracted, README head, language histogram, entry points,
   CI/Docker/test markers), then deepens selectively on the entry points.
2. **Deduce** — synthesizes what the repo *is* (app/service/library/CLI…), what it
   does and for whom, the stack, and its current state — anchoring every claim to a
   file/dependency/commit and **flagging contradictions** (e.g. the README says one
   thing, the code does another).
3. **Persist + confirm** — writes the understanding to
   `.claude/notes/repo-onboard.md` (survives session crashes, reusable context),
   then presents a concise summary and explicitly asks you to confirm or correct it.
4. **Ask intent** — only after confirmation, asks what you'd like done, offering a
   few concrete, evidence-derived starting points. Then it stops and waits.

The deliverable is a **confirmed, written understanding + a chosen next task** — not
code changes.

## Install

**Manual (any Claude Code setup):**

```bash
git clone https://github.com/Bahamutnelson/repo-onboard.git
mkdir -p ~/.claude/skills
cp -r repo-onboard ~/.claude/skills/repo-onboard
```

Drop it in `~/.claude/skills/` (global, all projects) or a project's
`.claude/skills/` (that project only).

**Via the skills CLI** (if you use [skills.sh](https://skills.sh)):

```bash
npx skills add Bahamutnelson/repo-onboard
```

## Usage

- **Automatic** — just ask, in any language: "onboard me to this repo", "I just
  cloned this, no idea what it is", "c'est quoi ce projet ?", "このリポジトリは何？".
  The skill's description triggers on the *intent*, not keywords.
- **Explicit** — type `/repo-onboard` in Claude Code.

## Language-universal triggering

The trigger description is written around **situation and intent**, not
language-specific keyword lists, so it routes from any language. This was measured,
not assumed — see [`validation/`](validation/) and [VALIDATION.md](VALIDATION.md):
across 16 languages spanning 7 writing systems (Latin, Cyrillic, Han, Kana, Hangul,
Arabic/RTL, Devanagari), the intended onboarding prompt triggered **16/16**, and
false positives were low and spread uniformly across scripts (content-driven, not
language-driven).

## License

Apache-2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE).
