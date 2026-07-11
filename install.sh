#!/bin/sh
# Agent-Workspace-Templates one-command install.
#
#   curl -fsSL https://raw.githubusercontent.com/CORBEL-Technology/agent-workspace-templates/main/install.sh | sh
#       -> a folder-agent-workspace at ~/my-workspace (the common case)
#
#   ... | sh -s -- ~/second-workspace                      # another workspace, your path
#   ... | sh -s -- shared-context                          # the shared store  -> ~/my-shared
#   ... | sh -s -- capability-registry                     # the registry      -> ~/my-registry
#   ... | sh -s -- shared-context ~/our-brain              # member AND path
#
# What it does, in order (and nothing else): check git + Python 3.8+, clone this repository
# atomically into ./agent-workspace-templates (or reuse it), make sure PyYAML is importable,
# instantiate the chosen member, and print the next step. If system Python is protected by
# PEP 668, PyYAML goes into <workspace>/.venv instead. POSIX systems (Linux/Mac and Windows via
# WSL); see START-HERE.md for the walkthrough.
set -e

REPO_URL="https://github.com/CORBEL-Technology/agent-workspace-templates.git"
REPO_DIR="agent-workspace-templates"
MEMBER="folder-agent-workspace"
TARGET=""
CLONE_TMP=""
PIP_LOG=""
RESUME_TARGET=0
CREATED_TARGET=0

say() { printf '%s\n' "$*"; }
die() { printf 'install: %s\n' "$*" >&2; exit 1; }
shell_quote() {
    printf "'"
    printf '%s' "$1" | sed "s/'/'\\\\''/g"
    printf "'"
}
retry_command() {
    printf '    curl -fsSL https://raw.githubusercontent.com/CORBEL-Technology/agent-workspace-templates/main/install.sh | sh -s -- '
    shell_quote "$MEMBER"
    printf ' '
    shell_quote "$TARGET"
    printf '\n'
}
show_members() {
    say "Valid members: folder-agent-workspace, shared-context, capability-registry."
}
cleanup() {
    [ -z "$CLONE_TMP" ] || rm -rf -- "$CLONE_TMP"
    [ -z "$PIP_LOG" ] || rm -f -- "$PIP_LOG"
}
trap cleanup EXIT HUP INT TERM

if [ "$#" -gt 2 ]; then
    show_members >&2
    die "too many arguments. Use: sh install.sh [member] [target-path]"
fi

case "${1:-}" in
    folder-agent-workspace|shared-context|capability-registry)
        MEMBER="$1"
        TARGET="${2:-}"
        ;;
    "") ;;
    *)
        case "$1" in
            */*) SUGGESTED_MEMBER="" ;;
            folder-agent-*) SUGGESTED_MEMBER="folder-agent-workspace" ;;
            shared-*) SUGGESTED_MEMBER="shared-context" ;;
            capab*) SUGGESTED_MEMBER="capability-registry" ;;
            *) SUGGESTED_MEMBER="" ;;
        esac
        if [ "$#" -eq 2 ]; then
            show_members >&2
            if [ -n "$SUGGESTED_MEMBER" ]; then
                say "install: '$1' looks mistyped. Did you mean '$SUGGESTED_MEMBER'? Run:" >&2
                MEMBER="$SUGGESTED_MEMBER"
                TARGET="$2"
                retry_command >&2
                exit 1
            fi
            die "'$1' is not a member name. Choose one of the three valid names, then run the command again."
        fi
        case "$SUGGESTED_MEMBER" in
            ?*)
                show_members >&2
                say "install: '$1' looks mistyped. Did you mean '$SUGGESTED_MEMBER'? Run:" >&2
                printf '    curl -fsSL https://raw.githubusercontent.com/CORBEL-Technology/agent-workspace-templates/main/install.sh | sh -s -- ' >&2
                shell_quote "$SUGGESTED_MEMBER" >&2
                printf '\n' >&2
                exit 1
                ;;
            *) TARGET="$1" ;;
        esac
        ;;
esac

if [ -z "$TARGET" ]; then
    case "$MEMBER" in
        folder-agent-workspace) TARGET="$HOME/my-workspace" ;;
        shared-context)         TARGET="$HOME/my-shared" ;;
        capability-registry)    TARGET="$HOME/my-registry" ;;
    esac
fi

command -v git >/dev/null 2>&1 || die "git is not installed. Mac: run 'xcode-select --install'. Linux/WSL: run 'sudo apt install git'. Then re-run the same install command."

PY=""
for c in python3 python; do
    if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
[ -n "$PY" ] || die "Python 3 is not installed. Install it from https://python.org/downloads, then re-run the same install command."
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' \
    || die "Python 3.8 or newer is required (you have $($PY -V 2>&1)). Update it from https://python.org/downloads, then re-run the same install command."

# Make every displayed command safe to paste, including when the target contains spaces.
TARGET=$("$PY" -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().absolute())' "$TARGET")

if [ -e "$TARGET" ]; then
    if [ -f "$TARGET/.uninitialised" ] && [ -d "$TARGET/.git" ]; then
        RESUME_TARGET=1
        printf '%s' '-> a fresh workspace already exists at '
        shell_quote "$TARGET"
        printf '; resuming the dependency check without overwriting it\n'
    elif [ -d "$TARGET/.git" ]; then
        printf 'install: a workspace already exists at ' >&2
        shell_quote "$TARGET" >&2
        printf '. Nothing was overwritten. Open it with:\n    cd ' >&2
        shell_quote "$TARGET" >&2
        printf '\n' >&2
        exit 1
    else
        printf 'install: the target already exists: ' >&2
        shell_quote "$TARGET" >&2
        printf '. Nothing was overwritten. Choose an unused path, for example:\n' >&2
        OLD_TARGET="$TARGET"
        TARGET="$TARGET-new"
        retry_command >&2
        TARGET="$OLD_TARGET"
        exit 1
    fi
fi

if [ -d "$REPO_DIR/.git" ]; then
    say "-> using existing $REPO_DIR/ (run 'git -C $REPO_DIR pull' to update it later)"
elif [ -f "instantiate.py" ] && [ -d "folder-agent-workspace" ]; then
    REPO_DIR="."
    say "-> running from inside the template repository"
elif [ -e "$REPO_DIR" ]; then
    printf 'install: %s exists but is not a complete template download. Remove it, then retry:\n    rm -rf -- ' "$REPO_DIR" >&2
    shell_quote "$REPO_DIR" >&2
    printf '\n' >&2
    retry_command >&2
    exit 1
else
    say "-> downloading the templates..."
    CLONE_TMP="$REPO_DIR.installing.$$"
    if ! git clone --quiet "$REPO_URL" "$CLONE_TMP"; then
        rm -rf -- "$CLONE_TMP"
        CLONE_TMP=""
        say "install: download failed. No partial template download was kept; any existing workspace was untouched." >&2
        say "Check your internet connection, then run:" >&2
        retry_command >&2
        exit 1
    fi
    mv -- "$CLONE_TMP" "$REPO_DIR"
    CLONE_TMP=""
fi

NEED_VENV=0
if ! "$PY" -c 'import yaml' >/dev/null 2>&1; then
    say "-> installing PyYAML for your Python user..."
    PIP_LOG=$(mktemp)
    if "$PY" -m pip install --user --quiet "PyYAML>=6,<7" >"$PIP_LOG" 2>&1; then
        :
    elif grep -Eqi 'externally[- ]managed[- ]environment|externally managed' "$PIP_LOG"; then
        NEED_VENV=1
        say "-> system Python is protected (PEP 668); using an isolated .venv in your workspace"
    elif grep -qi 'No module named pip' "$PIP_LOG"; then
        NEED_VENV=1
        say "-> system Python has no pip; using an isolated .venv in your workspace"
    else
        say "install: PyYAML could not be downloaded. No workspace files were changed." >&2
        say "Check your internet connection, then run:" >&2
        retry_command >&2
        exit 1
    fi
    rm -f -- "$PIP_LOG"
    PIP_LOG=""
fi

if [ "$RESUME_TARGET" -eq 0 ]; then
    say "-> creating your $MEMBER at $TARGET"
    if ! "$PY" "$REPO_DIR/instantiate.py" "$MEMBER" "$TARGET"; then
        say "install: the workspace was not created. Follow the exact fix above, then run:" >&2
        retry_command >&2
        exit 1
    fi
    CREATED_TARGET=1
fi

if [ "$NEED_VENV" -eq 1 ]; then
    if [ -x "$TARGET/.venv/bin/python" ] \
       && "$TARGET/.venv/bin/python" -c 'import yaml' >/dev/null 2>&1; then
        say "-> reusing the ready .venv already in your workspace"
    else
        rm -rf -- "$TARGET/.venv"
    fi
    if [ ! -x "$TARGET/.venv/bin/python" ] && ! "$PY" -m venv "$TARGET/.venv"; then
        if [ "$CREATED_TARGET" -eq 1 ]; then
            rm -rf -- "$TARGET"
            say "install: Python could not create a virtual environment, so the new workspace was removed." >&2
        else
            say "install: Python could not create a virtual environment. Existing tracked workspace files were kept." >&2
        fi
        say "On Debian/Ubuntu/WSL run: sudo apt install python3-venv" >&2
        say "Then run:" >&2
        retry_command >&2
        exit 1
    fi
    VENV_PY="$TARGET/.venv/bin/python"
    if ! "$VENV_PY" -c 'import yaml' >/dev/null 2>&1 \
       && ! "$VENV_PY" -m pip install --quiet "PyYAML>=6,<7"; then
        if [ "$CREATED_TARGET" -eq 1 ]; then
            rm -rf -- "$TARGET"
            say "install: PyYAML could not be downloaded into the isolated environment, so the new workspace was removed." >&2
        else
            rm -rf -- "$TARGET/.venv"
            say "install: PyYAML could not be downloaded into the isolated environment. Existing tracked workspace files were kept." >&2
        fi
        say "Check your internet connection, then run:" >&2
        retry_command >&2
        exit 1
    fi
fi

say ""
say "Done. Next step:"
printf '    cd '
shell_quote "$TARGET"
printf '\n'
if [ "$NEED_VENV" -eq 1 ]; then
    say "    . .venv/bin/activate"
    say "Keep that second command: run it whenever you open this workspace."
fi
say "Then open it in your agent runtime and say:"
say "    Read AGENTS.md and introduce yourself."
say "Onboarding takes it from there. Full walkthrough: $REPO_DIR/START-HERE.md"
