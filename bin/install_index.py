#!/usr/bin/env python3
"""Install one Codex routing skill and move personal skills out of discovery."""

import argparse
import json
from pathlib import Path
import re
import shutil
import tempfile


ROOT = Path(__file__).resolve().parents[1]

def description(path):
    text = (path / "SKILL.md").read_text()
    match = re.search(r"^description: *(.*(?:\n[ \t]+[^\n]+)*)", text, re.M)
    value = " ".join(match.group(1).split()) if match else path.name
    return value.lstrip(">| ").strip("\"'").split(". ")[0][:180].replace("|", "/")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    home = Path.home()
    discovered = home / ".codex/skills"
    library = home / ".codex/skill-library"
    backup = None

    def retire(path):
        nonlocal backup
        if not path.exists() and not path.is_symlink():
            return
        if args.dry_run:
            print(f"Would archive: {path}")
            return
        if backup is None:
            (ROOT / "backups").mkdir(exist_ok=True)
            backup = Path(tempfile.mkdtemp(prefix="index.", dir=ROOT / "backups"))
        target = backup / path.relative_to(home)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(target))
        print(f"Archived: {path}")

    sources = {p.name: p for p in library.glob("*")
               if (p / "SKILL.md").is_file()}
    for path in sorted(discovered.glob("*")):
        if path.name.startswith(".") or path.name == "skill-index":
            continue
        target = library / path.name
        if path.name in sources:
            retire(path)
        elif not (path / "SKILL.md").is_file():
            continue
        else:
            if args.dry_run:
                print(f"Would move: {path} -> {target}")
                sources[path.name] = path
            else:
                library.mkdir(parents=True, exist_ok=True)
                shutil.move(str(path), str(target))
                sources[path.name] = target

    manifest = json.loads((ROOT / "manifest.json").read_text())
    groups = {entry["slug"]: entry["group"] for entry in manifest["skills"]}
    lines = ["# Personal skill catalog", "", "Read only the skill matching the user's request.", ""]
    for group in sorted({groups.get(name, "other") for name in sources}):
        lines += [f"## {group}", ""]
        for name in sorted(sources):
            if groups.get(name, "other") != group:
                continue
            target = library / name / "SKILL.md"
            lines.append(f"- [{name}](<{target}>): {description(sources[name])}")
        lines.append("")

    index = discovered / "skill-index"
    if args.dry_run:
        print(f"Would install skill-index at {index}")
        return
    index.mkdir(parents=True, exist_ok=True)
    for name, content in {
        "SKILL.md": (ROOT / "index/SKILL.md").read_text(),
        "catalog.md": "\n".join(lines),
    }.items():
        target = index / name
        if not target.exists() or target.read_text() != content:
            retire(target)
            target.write_text(content)
    print(f"Indexed {len(sources)} skills; Codex discovers one personal index.")
    if backup:
        print(f"Backups: {backup}")


if __name__ == "__main__":
    main()
