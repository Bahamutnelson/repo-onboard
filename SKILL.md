---
name: repo-onboard
description: >-
  Use this when someone with little or no context about an ENTIRE codebase wants
  you to look around and tell them what it is — the first-contact "what even is
  this project?" moment, before any actual work. The situation: a user new to a
  whole repo / folder / monorepo / service (they just cloned it, inherited it,
  were handed it, took it over, or were told to "figure it out") who wants the big
  picture — what it is, what it does, the stack, its state, where to begin, or how
  you could help. Recognize this intent in ANY language and ANY phrasing; the
  words "onboard", "repo", or "codebase" need not appear — match meaning, not
  vocabulary. Do NOT trigger when the user is asking you to DO or EXPLAIN one
  specific thing — that signals they already know the project well enough to point
  at a part of it. Skip it whenever the message names a particular file, function,
  symbol, error, script, or feature, or asks to perform a scoped task — add, fix,
  write, refactor, review, rename, test, bump, or optimize something, or trace a
  single flow or subsystem — even when it also says "this repo", "this codebase",
  or "walk me through". Discriminator: whole-project orientation from near-zero
  context means use it; anything scoped to one part or one task means don't. Once
  triggered, it reconnoiters the repo, deduces its purpose from the evidence,
  writes that understanding to .claude/notes/repo-onboard.md, asks the user to
  confirm or correct it, and only then asks what they'd like done — without
  starting any work first.
---

# Repo Onboard

## Why this exists

Jumping straight into edits on a repo you don't understand is how you "fix" the
wrong layer, duplicate something that already exists, or break an intended
contract. The cheap insurance is ten minutes of structured reconnaissance, a
deduced statement of purpose the user can correct, and an explicit "what do you
want me to do?" before touching anything. The point of this skill is to make
that the default opening move, and to make the deduced understanding survive the
session by writing it down.

The deliverable of this skill is **not** code changes. It is a confirmed,
written understanding of the repo plus a chosen next task. Do not start the work
until the user has picked it.

## Workflow

Four phases. Don't skip the confirmation — a deduction the user never saw is just
a guess.

### Phase 1 — Reconnaissance (gather signals, don't read everything)

Run the bundled recon script first; it collects the cheap high-signal facts in
one pass so you don't reinvent them:

```bash
bash <skill-dir>/scripts/recon.sh <repo-root>
```

It prints: git remote/branch/last commit, a depth-limited tree, every package
manifest (with name/description/scripts/entry points pulled out), the README
head, a language histogram, candidate entry points, and the presence of tests /
CI / Docker / env templates.

Then deepen selectively based on what the recon surfaced — prefer semantic
navigation (LSP `goToDefinition` / `findReferences`, or an Explore-style search)
over grepping blindly:

- **README / docs** — the stated intent (treat as a claim to verify, not truth).
- **Manifest** — name, description, dependencies (the deps reveal the domain:
  a web framework, a CLI parser, a trading SDK, an ML stack…), scripts, `bin`.
- **Entry points** — `main`/`index`/`app`/`server`/`cli`/`__main__`: what does
  the program actually start up and do?
- **Directory shape** — top-level layout tells you app vs library vs monorepo
  vs service.
- **Tests** — test names are a free spec of intended behavior.
- **Recent git history** — what's actively being worked on right now.

Read excerpts, not whole files. You're triangulating, not auditing.

### Phase 2 — Deduce the purpose

Synthesize the signals into a claim about what the repo is *for*. Triangulate —
one signal can mislead, agreement across several is trustworthy. Specifically
resolve:

- **What it is** — app / service / library / CLI / script collection / infra.
- **What it does and for whom** — the domain and the user it serves, in plain
  language, not a restatement of the folder names.
- **Stack & entry points** — language(s), framework, how you'd run it.
- **Current state** — mature / WIP / abandoned; what the recent commits and open
  TODOs suggest is in flight.

**Flag contradictions explicitly.** If the README advertises X but the code does
Y, if there's a manifest for a framework that's barely used, if tests cover a
feature the docs never mention — say so. Contradictions are the highest-value
thing you can surface, and they're exactly what a confident summary hides.

Every claim should be anchored to evidence (a file path, a dependency, a commit).
If you're inferring rather than reading, mark it as inference. Never invent a
purpose to sound decisive — "the signals are ambiguous between A and B" is a
better answer than a confident wrong one.

### Phase 3 — Persist, then confirm

Write the understanding to `.claude/notes/repo-onboard.md` at the repo root
(create the `.claude/notes/` directory if needed). This survives session
crashes and becomes reusable context. Use the template below.

Then present a **concise** summary in chat (aim for ~10 lines, not the whole
note) and **explicitly ask the user to confirm or correct it.** This is the
pivot of the skill — you are checking your deduction against the one person who
knows the ground truth. Phrase it as a real question, e.g. "Here's what I think
this repo is — is that right, or am I off anywhere?"

If the user corrects you, update the note before moving on.

### Phase 4 — Ask what they want

Only after the purpose is confirmed, ask what they'd like you to do. Don't leave
it fully open — use the analysis to offer a few concrete, evidence-derived
starting points (a failing test you noticed, an obvious TODO, missing docs, a
half-finished feature in recent commits), while making clear they can ask for
anything. Then **stop and wait.** Do not begin the chosen task inside this skill;
hand off to normal working mode once they've picked.

## The note template

Write `.claude/notes/repo-onboard.md` in this shape:

```markdown
# Repo Onboard — <repo name>

_Deduced <date> from <branch>@<short-sha>. Confirmed by user: <yes/no/pending>._

## What this repo is
<one or two sentences: type + who it serves>

## What it does
<plain-language description of the core behavior>

## Stack & how to run
- Language/framework: …
- Entry point(s): `path` — …
- Run / build / test: `commands from manifest`

## Map (the parts that matter)
- `path/` — role
- `path/` — role

## State & signals
- Maturity: …
- In flight (recent commits / TODOs): …

## Open questions / contradictions
- <anything the evidence didn't settle, or where docs and code disagree>
```

Keep it tight and evidence-anchored. This is a map, not a transcript.

## Guardrails

- **Don't start the work.** This skill ends at "what would you like me to do?".
  Confirmed understanding + chosen task is the finish line.
- **Don't fabricate.** Ambiguity stated honestly beats false confidence. Anchor
  claims to file paths / deps / commits; mark inferences as inferences.
- **Read shallow, reason deep.** Excerpts and entry points, not every file.
- **The README is a claim, not the truth** — verify it against the code.
- **Respect a partial repo.** Empty/skeleton/scaffold repos are a valid finding:
  say "this looks like a fresh scaffold with no real logic yet" rather than
  inventing purpose.
