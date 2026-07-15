#!/usr/bin/env python3
"""Single source of truth for the template-managed workspace spine."""
from pathlib import Path


MANAGED_PREFIXES = (
    "core/",
    "tools/",
    ".claude/hooks/",
    ".claude/skills/",
    "30_schemas/",
    "60_workflows/",
    "40_templates/",
)
MANAGED_ROOT_FILES = frozenset({"AGENTS.md", "CLAUDE.md", "GEMINI.md"})
MANAGED_EXACT_FILES = frozenset(
    {
        "00_meta/agent-os-design.md",
        "10_doctrine/context-decomposition.md",
        "10_doctrine/memory-homeostasis.md",
    }
)


def is_managed(relpath):
    rel = Path(relpath).as_posix()
    if rel.startswith("./"):
        rel = rel[2:]
    return (
        rel in MANAGED_ROOT_FILES
        or rel in MANAGED_EXACT_FILES
        or any(rel.startswith(p) for p in MANAGED_PREFIXES)
    )


def managed_files(root):
    """Return managed regular-file paths, excluding generated pacnew/bytecode files."""
    root = Path(root)
    return sorted(
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file()
        and is_managed(p.relative_to(root))
        and "__pycache__" not in p.parts
        and p.suffix not in {".pyc", ".pyo"}
        and not p.name.endswith(".template-new")
    )
