#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SNAKE_CASE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


def require_snake_case(value: str, label: str) -> None:
    if not SNAKE_CASE.match(value):
        raise SystemExit(f"{label} must be snake_case: {value}")


def apply_naming(package_dir: Path, rename_spec_path: Path) -> Path:
    package_dir = package_dir.resolve()
    rename_spec = json.loads(rename_spec_path.read_text(encoding="utf-8"))

    package_name = rename_spec["package_name"]
    require_snake_case(package_name, "package_name")

    shape_entries = rename_spec.get("shapes", [])
    rename_map = {entry["from"]: entry["to"] for entry in shape_entries}
    if len(rename_map) != len(shape_entries):
        raise SystemExit("Duplicate source entries found in rename spec")

    current_files = {
        path.name
        for path in package_dir.glob("*.svg")
        if not path.name.endswith("_full.svg") and not path.name.endswith("_sheet.svg")
    }
    missing = sorted(set(rename_map) - current_files)
    if missing:
        raise SystemExit(f"Rename spec references missing files: {', '.join(missing)}")
    unnamed = sorted(current_files - set(rename_map))
    if current_files and unnamed:
        raise SystemExit(f"Rename spec must cover every extracted SVG: {', '.join(unnamed)}")

    new_names = list(rename_map.values())
    if len(new_names) != len(set(new_names)):
        raise SystemExit("Duplicate destination shape names found in rename spec")

    for file_name in new_names:
        if not file_name.endswith(".svg"):
            raise SystemExit(f"Shape file must end with .svg: {file_name}")
        require_snake_case(file_name[:-4], "shape file name")

    full_svg_candidates = sorted(package_dir.glob("*_sheet.svg")) + sorted(package_dir.glob("*full*.svg"))
    if not full_svg_candidates:
        raise SystemExit("Could not find the full-sheet SVG inside the package directory")
    full_svg_path = full_svg_candidates[0]

    if rename_map:
        # Rename shapes through temporary names to avoid collisions.
        temp_paths: dict[str, Path] = {}
        for source_name, dest_name in rename_map.items():
            source_path = package_dir / source_name
            temp_path = package_dir / f"__tmp__{dest_name}"
            source_path.rename(temp_path)
            temp_paths[dest_name] = temp_path

        for dest_name, temp_path in temp_paths.items():
            temp_path.rename(package_dir / dest_name)

        full_svg_path.unlink()
    else:
        full_svg_path.rename(package_dir / f"{package_name}.svg")

    for extra in ("manifest.json", "preview.html"):
        extra_path = package_dir / extra
        if extra_path.exists():
            extra_path.unlink()
    shapes_dir = package_dir / "shapes"
    if shapes_dir.exists() and shapes_dir.is_dir():
        for child in shapes_dir.iterdir():
            child.unlink()
        shapes_dir.rmdir()

    final_package_dir = package_dir.parent / package_name
    if final_package_dir.exists() and final_package_dir != package_dir:
        raise SystemExit(f"Destination package folder already exists: {final_package_dir}")
    package_dir.rename(final_package_dir)
    return final_package_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply semantic naming to a generated EPS-to-SVG package.")
    parser.add_argument("--package-dir", required=True, help="Path to the package directory to rename.")
    parser.add_argument("--rename-spec", required=True, help="Path to the rename spec JSON file.")
    args = parser.parse_args()

    final_dir = apply_naming(
        Path(args.package_dir).expanduser(),
        Path(args.rename_spec).expanduser().resolve(),
    )
    print(final_dir)


if __name__ == "__main__":
    main()
