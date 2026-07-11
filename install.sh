#!/bin/sh
# Agent-Workspace-Templates one-command install.
#
#   curl -fsSL https://raw.githubusercontent.com/CORBEL-Technology/agent-workspace-templates/main/install.sh | sh
#   curl -fsSL .../install.sh | sh -s -- ~/my-workspace     # choose the workspace path
#
# What it does, in order (and nothing else): check git + Python 3.8+, clone this repository
# into ./agent-workspace-templates (or reuse it), make sure PyYAML is importable (pip --user
# if not), instantiate a fresh workspace, and print the next step. POSIX systems (Linux/Mac);
# on Windows follow START-HERE.md instead.
set -e

TARGET="${1:-$HOME/my-workspace}"
REPO_URL="https://github.com/CORBEL-Technology/agent-workspace-templates.git"
REPO_DIR="agent-workspace-templates"

say() { printf '%s\n' "$*"; }
die() { printf 'install: %s\n' "$*" >&2; exit 1; }

command -v git >/dev/null 2>&1 || die "git is not installed. Mac: run 'xcode-select --install'. Linux: 'sudo apt install git' (or your package manager). Then re-run this command."

PY=""
for c in python3 python; do
    if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
[ -n "$PY" ] || die "Python 3 is not installed. Get it from python.org/downloads, then re-run this command."
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' \
    || die "Python 3.8 or newer is required (you have $($PY -V 2>&1)). Update from python.org/downloads."

if [ -d "$REPO_DIR/.git" ]; then
    say "-> using existing $REPO_DIR/ (git pull to update it later)"
elif [ -f "instantiate.py" ] && [ -d "folder-agent-workspace" ]; then
    REPO_DIR="."
    say "-> running from inside the template repository"
else
    say "-> cloning the templates..."
    git clone --quiet "$REPO_URL" "$REPO_DIR"
fi

if ! "$PY" -c 'import yaml' >/dev/null 2>&1; then
    say "-> installing PyYAML (pip --user)..."
    "$PY" -m pip install --user --quiet "PyYAML>=6,<7" \
        || die "could not install PyYAML. Run: $PY -m pip install --user PyYAML  then re-run this command."
fi

[ -e "$TARGET" ] && die "$TARGET already exists - choose another path: ... | sh -s -- ~/another-name"

say "-> creating your workspace at $TARGET"
"$PY" "$REPO_DIR/instantiate.py" folder-agent-workspace "$TARGET"

say ""
say "Done. Next step:"
say "    cd $TARGET"
say "then open it in your agent runtime (for Claude Code just run: claude) and say:"
say "    Read AGENTS.md and introduce yourself."
say "Onboarding takes it from there. Full walkthrough: $REPO_DIR/START-HERE.md"
