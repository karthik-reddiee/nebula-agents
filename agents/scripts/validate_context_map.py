#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
import re

import yaml

FRAMEWORK_ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    # agent-map.yaml intentionally uses framework placeholders such as
    # `{PRODUCT_ROOT}/...` in human-readable lists. Quote those placeholders
    # before parsing so validation can inspect the structure without requiring
    # a sweeping formatting rewrite of the public contract file.
    text = re.sub(r"^(\s*-\s*)({[A-Z_]+}[^#\n]*)(\s*(?:#.*)?)$", r'\1"\2"\3', text, flags=re.MULTILINE)
    text = re.sub(r"^(\s*[A-Za-z0-9_-]+:\s*)({[A-Z_]+}[^#\n]*)(\s*(?:#.*)?)$", r'\1"\2"\3', text, flags=re.MULTILINE)
    return yaml.safe_load(text) or {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def validate_context_map() -> list[str]:
    """Validate the layered prompt-loading contract.

    This intentionally checks prompt payload rules, not agent permissions. The
    existing `reads` globs may stay broad so agents can retrieve files on
    demand, but `profiles.*.always` must remain compact and non-globbed.
    """
    errors: list[str] = []
    agent_map_path = FRAMEWORK_ROOT / "agents" / "agent-map.yaml"
    context_map_path = FRAMEWORK_ROOT / "agents" / "context-map.yaml"

    agent_map = load_yaml(agent_map_path)
    context_map = load_yaml(context_map_path)

    agents = agent_map.get("agents", {})
    profiles = context_map.get("profiles", {})
    layers = context_map.get("layers", {})
    actions = agent_map.get("actions", {})
    context_actions = context_map.get("actions", {})

    if agent_map.get("context_loading", {}).get("map") != "agents/context-map.yaml":
        errors.append("agent-map: context_loading.map must point to agents/context-map.yaml")

    for layer_name in ("global_core", "action_core", "agent_core"):
        if layer_name not in layers:
            errors.append(f"context-map: missing required layer {layer_name}")

    for agent_name, config in agents.items():
        profile_name = config.get("prompt_context", {}).get("profile")
        if not profile_name:
            errors.append(f"agent-map: {agent_name} missing prompt_context.profile")
            continue
        if profile_name != agent_name:
            errors.append(f"agent-map: {agent_name} profile should match agent name, got {profile_name}")
        profile = profiles.get(profile_name)
        if not profile:
            errors.append(f"context-map: missing profile {profile_name}")
            continue

        always_layers = _as_list(profile.get("always"))
        for required in ("global_core", "agent_core"):
            if required not in always_layers:
                errors.append(f"context-map: profile {profile_name} missing always layer {required}")
        unknown_layers = [layer for layer in always_layers if layer not in layers]
        if unknown_layers:
            errors.append(f"context-map: profile {profile_name} has unknown layers {', '.join(unknown_layers)}")

        for item in always_layers:
            if "*" in str(item):
                errors.append(f"context-map: profile {profile_name} always layer cannot contain glob {item}")

        for item in _as_list(profile.get("on_demand")):
            item_text = str(item)
            if "/references/" in item_text and "ROUTER.md" not in item_text:
                errors.append(f"context-map: reference on_demand entry must mention ROUTER.md: {profile_name} {item_text}")

    for action_name, config in actions.items():
        if action_name not in context_actions:
            errors.append(f"context-map: missing action prompt template mapping for {action_name}")
            continue
        doc = config.get("doc", "")
        if doc and not (FRAMEWORK_ROOT / doc).exists():
            errors.append(f"agent-map: action {action_name} doc does not exist: {doc}")
        template = context_actions[action_name].get("prompt_template", "")
        if "{mode}" not in template:
            errors.append(f"context-map: action {action_name} prompt_template must include {{mode}}")

    return errors


def main() -> int:
    errors = validate_context_map()
    print("Context map validation")
    print("-" * 60)
    if errors:
        print("Errors:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("[PASS] context map profiles align with agent map.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
