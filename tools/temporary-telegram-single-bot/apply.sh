#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PATCH_FILE="$SCRIPT_DIR/telegram-start-verification.patch"
REPO_ARG="${1:-$PWD}"

if [[ ! -d "$REPO_ARG" ]]; then
  echo "ERROR: bot repository directory does not exist: $REPO_ARG" >&2
  exit 2
fi
REPO="$(cd -- "$REPO_ARG" && pwd)"
GIT_ROOT="$(git -C "$REPO" rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$GIT_ROOT" || "$GIT_ROOT" != "$REPO" ]]; then
  echo "ERROR: pass the Git root of the actual bot working copy." >&2
  exit 2
fi
if [[ ! -f "$REPO/main.py" ]]; then
  echo "ERROR: expected main.py at $REPO/main.py" >&2
  exit 2
fi
if [[ ! -f "$PATCH_FILE" ]]; then
  echo "ERROR: patch not found: $PATCH_FILE" >&2
  exit 2
fi
if [[ -n "$(git -C "$REPO" status --porcelain --untracked-files=all)" ]]; then
  echo "ERROR: refusing to patch a dirty bot working copy. Do not discard its changes." >&2
  git -C "$REPO" status --short
  exit 2
fi

git -C "$REPO" apply --check "$PATCH_FILE"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="$(
  cd -- "$(dirname -- "$REPO")"
  printf '%s/%s-tradethesis-backup-%s' "$(pwd)" "$(basename -- "$REPO")" "$STAMP"
)"
mkdir -m 700 -- "$BACKUP"
cp -p -- "$REPO/main.py" "$BACKUP/main.py"
echo "Backed up main.py to: $BACKUP/main.py"

rollback_patch() {
  if git -C "$REPO" apply --reverse --check "$PATCH_FILE"; then
    git -C "$REPO" apply --reverse "$PATCH_FILE"
    echo "Patch rolled back after a validation failure; backup retained." >&2
  else
    echo "ERROR: automatic rollback check failed. Keep the backup and inspect git status." >&2
  fi
}

if ! git -C "$REPO" apply "$PATCH_FILE"; then
  echo "ERROR: patch application failed. No forced application attempted." >&2
  exit 1
fi

if ! (cd "$REPO" && PYTHONDONTWRITEBYTECODE=1 python - <<'PY'
import ast
from pathlib import Path
for filename in ("main.py", "tradethesis_verification_bridge.py"):
    ast.parse(Path(filename).read_text(encoding="utf-8"), filename=filename)
print("Python syntax: OK")
PY
); then
  rollback_patch
  exit 1
fi

if ! (cd "$REPO" && PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p 'test_tradethesis_verification_bridge.py' -v); then
  rollback_patch
  exit 1
fi

if ! git -C "$REPO" diff --check; then
  rollback_patch
  exit 1
fi

echo "SUCCESS: verification handler applied and offline checks passed."
echo "No commit, push or deployment performed."
echo "Keep only one polling process running for this bot token."
