#!/usr/bin/env python3
"""Expose this checkout's skills in one explicitly selected workspace."""
import argparse
import json
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parent
    workspace = args.workspace.resolve(strict=True)
    manifest = json.loads((repo / "workspace-skills.json").read_text())
    destination = workspace / ".agents" / "skills"
    plan = []
    for relative in manifest["skills"]:
        source = (repo / relative).resolve(strict=True)
        source.relative_to(repo)
        if not (source / "SKILL.md").is_file():
            raise SystemExit(f"Missing SKILL.md: {source}")
        link = destination / source.name
        if os.path.lexists(link):
            if not link.is_symlink() or link.resolve() != source:
                raise SystemExit(f"Refusing to replace existing entry: {link}")
        elif args.check:
            raise SystemExit(f"Missing skill link: {link}")
        plan.append((link, source))
    if not args.check:
        destination.mkdir(parents=True, exist_ok=True)
        for link, source in plan:
            if not os.path.lexists(link):
                link.symlink_to(os.path.relpath(source, destination), target_is_directory=True)
    print(f"{manifest['repository']}: {len(plan)} skills {'verified' if args.check else 'installed'} in {workspace}")


if __name__ == "__main__":
    main()
