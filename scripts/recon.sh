#!/usr/bin/env bash
# recon.sh — gather cheap, high-signal facts about a repository in one pass.
# Usage: bash recon.sh [repo-root]   (defaults to current directory)
# Designed to be read by an agent, so output is grouped and labeled. Never fails
# hard: every probe is guarded so a missing tool or file just prints a note.

set -u
ROOT="${1:-.}"
cd "$ROOT" 2>/dev/null || { echo "!! cannot cd into '$ROOT'"; exit 1; }
ROOT="$(pwd)"
HAS_JQ=0; command -v jq >/dev/null 2>&1 && HAS_JQ=1

section() { printf '\n=== %s ===\n' "$1"; }
exists()  { [ -e "$1" ]; }

# ----------------------------------------------------------------------------
section "REPO"
echo "root: $ROOT"
if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
  echo "remote: $(git remote get-url origin 2>/dev/null || echo '(none)')"
  echo "last commit: $(git log -1 --pretty='%h %ad %s' --date=short 2>/dev/null || echo '(no commits)')"
  # NB: `git shortlog` reads commits from stdin unless given a revision; in a
  # non-interactive script that means an empty stdin -> 0. Pass HEAD explicitly.
  echo "commits: $(git rev-list --count HEAD 2>/dev/null || echo '?')   contributors: $(git shortlog -sn HEAD 2>/dev/null | wc -l | tr -d ' ')"
else
  echo "(not a git repository)"
fi

# ----------------------------------------------------------------------------
section "TREE (depth 2, noise pruned)"
PRUNE='-name .git -o -name node_modules -o -name .venv -o -name venv -o -name dist -o -name build -o -name target -o -name __pycache__ -o -name .next -o -name .turbo -o -name vendor'
find . -maxdepth 2 \( $PRUNE \) -prune -o -print 2>/dev/null \
  | grep -v '^\.$' | sort | sed 's|^\./||' | head -120

# ----------------------------------------------------------------------------
section "MANIFESTS"
print_pkg_json() {
  echo "-- $1 (package.json) --"
  if [ "$HAS_JQ" = 1 ]; then
    jq -r '
      "name: \(.name // "?")",
      "description: \(.description // "(none)")",
      "version: \(.version // "?")",
      "main/module/bin: \(.main // "-") / \(.module // "-") / \((.bin|type) // "-")",
      "scripts: \((.scripts // {}) | keys | join(", "))",
      "deps: \((.dependencies // {}) | keys | join(", "))" ' "$1" 2>/dev/null \
      || echo "(jq could not parse)"
  else
    grep -E '"(name|description|main|version)"' "$1" 2>/dev/null | head -8
  fi
}
FOUND_MANIFEST=0
for f in package.json pyproject.toml setup.py setup.cfg requirements.txt Cargo.toml \
         go.mod pom.xml build.gradle build.gradle.kts Gemfile composer.json \
         Package.swift mix.exs pubspec.yaml deno.json; do
  if exists "$f"; then
    FOUND_MANIFEST=1
    case "$f" in
      package.json) print_pkg_json "$f" ;;
      *) echo "-- $f --"; head -25 "$f" 2>/dev/null ;;
    esac
  fi
done
# nested package.json (monorepo signal)
NESTED=$(find . -maxdepth 3 \( $PRUNE \) -prune -o -name package.json -print 2>/dev/null | grep -v '^\./package.json$' | head -10)
[ -n "$NESTED" ] && { echo "-- nested package.json (monorepo?) --"; echo "$NESTED" | sed 's|^\./||'; }
[ "$FOUND_MANIFEST" = 0 ] && echo "(no recognized manifest at root)"

# ----------------------------------------------------------------------------
section "README (head)"
README=$(ls README* readme* 2>/dev/null | head -1)
if [ -n "${README:-}" ]; then
  echo "-- $README --"; head -45 "$README" 2>/dev/null
else
  echo "(no README found)"
fi

# ----------------------------------------------------------------------------
section "LANGUAGE HISTOGRAM (by extension, top 12)"
find . \( $PRUNE \) -prune -o -type f -name '*.*' -print 2>/dev/null \
  | sed 's|.*\.||' | grep -Ev '^(lock|map|md|txt|json|yml|yaml|toml|cfg|ini|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf)$' \
  | sort | uniq -c | sort -rn | head -12

# ----------------------------------------------------------------------------
section "CANDIDATE ENTRY POINTS"
find . -maxdepth 4 \( $PRUNE \) -prune -o -type f \
  \( -name 'main.*' -o -name 'index.*' -o -name 'app.*' -o -name 'server.*' \
     -o -name 'cli.*' -o -name '__main__.py' -o -name 'manage.py' \) -print 2>/dev/null \
  | sed 's|^\./||' | head -20 | sort
echo "(also check 'bin'/'scripts' in the manifests above)"

# ----------------------------------------------------------------------------
section "INFRA & SIGNALS"
for marker in \
  ".github/workflows:CI (GitHub Actions)" \
  ".gitlab-ci.yml:CI (GitLab)" \
  "Dockerfile:Docker" \
  "docker-compose.yml:docker-compose" \
  "compose.yaml:docker-compose" \
  ".env.example:env template" \
  "Makefile:Makefile" \
  "tsconfig.json:TypeScript" \
  "tests:tests dir" \
  "test:test dir" \
  "__tests__:tests dir" \
  "spec:spec dir" \
  "CLAUDE.md:Claude instructions" \
  ".pre-commit-config.yaml:pre-commit" ; do
  path="${marker%%:*}"; label="${marker#*:}"
  exists "$path" && echo "present: $label  ($path)"
done

section "DONE"
echo "Next: deepen on the entry points and dirs above, then deduce purpose."
