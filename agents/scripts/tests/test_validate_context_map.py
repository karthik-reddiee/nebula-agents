from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = REPO_ROOT / "agents" / "scripts" / "validate_context_map.py"


def test_context_map_alignment_passes_on_repo() -> None:
    result = subprocess.run(
        ["python3", str(VALIDATOR)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "[PASS]" in result.stdout


def test_default_profiles_do_not_load_reference_globs() -> None:
    if str(REPO_ROOT / "agents" / "scripts") not in sys.path:
        sys.path.insert(0, str(REPO_ROOT / "agents" / "scripts"))

    import validate_context_map as vcm

    importlib.reload(vcm)
    context_map = vcm.load_yaml(REPO_ROOT / "agents" / "context-map.yaml")
    for profile_name, profile in context_map["profiles"].items():
        for always_item in profile.get("always", []):
            assert "*" not in str(always_item), f"{profile_name} eagerly loads glob {always_item}"


def test_all_agent_profiles_are_declared() -> None:
    if str(REPO_ROOT / "agents" / "scripts") not in sys.path:
        sys.path.insert(0, str(REPO_ROOT / "agents" / "scripts"))

    import validate_context_map as vcm

    importlib.reload(vcm)
    agent_map = vcm.load_yaml(REPO_ROOT / "agents" / "agent-map.yaml")
    context_map = vcm.load_yaml(REPO_ROOT / "agents" / "context-map.yaml")
    assert set(agent_map["agents"]) <= set(context_map["profiles"])
