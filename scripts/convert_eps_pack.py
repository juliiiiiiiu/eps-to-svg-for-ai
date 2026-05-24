#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)

COMMAND_RE = re.compile(r"[A-Za-z]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")
LOW_INFO_TOKENS = {
    "eps",
    "svg",
    "vector",
    "vectors",
    "set",
    "pack",
    "collection",
    "illustration",
    "illustrations",
    "clipart",
    "shape",
    "shapes",
    "element",
    "elements",
    "item",
    "items",
    "design",
    "logo",
    "logos",
    "flyer",
    "flyers",
    "presentation",
    "persentation",
    "gift",
    "car",
}


def normalize_stem(name: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    parts = [part for part in cleaned.split("_") if part and part not in LOW_INFO_TOKENS]
    if not parts:
        parts = [segment for segment in cleaned.split("_") if segment] or ["eps_pack"]
    return "_".join(parts)


def locate_tool(name: str) -> str | None:
    candidates = [
        shutil.which(name),
        f"/opt/homebrew/bin/{name}",
        f"/usr/local/bin/{name}",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def run(command: list[str]) -> None:
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        sys.stderr.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        raise SystemExit(completed.returncode)


def parse_viewbox(root: ET.Element) -> tuple[float, float, float, float]:
    view_box = root.attrib.get("viewBox")
    if not view_box:
        raise SystemExit("Full SVG is missing a viewBox")
    parts = [float(value) for value in view_box.replace(",", " ").split()]
    if len(parts) != 4:
        raise SystemExit(f"Unexpected viewBox: {view_box}")
    return parts[0], parts[1], parts[2], parts[3]


def extract_points_from_path(d_value: str) -> list[tuple[float, float]]:
    tokens = COMMAND_RE.findall(d_value)
    points: list[tuple[float, float]] = []
    command = ""
    index = 0
    current = (0.0, 0.0)
    start = (0.0, 0.0)
    last_control = None

    def read_number() -> float:
        nonlocal index
        value = float(tokens[index])
        index += 1
        return value

    def add_point(x: float, y: float, relative: bool) -> tuple[float, float]:
        nonlocal current
        if relative:
            x += current[0]
            y += current[1]
        current = (x, y)
        points.append(current)
        return current

    while index < len(tokens):
        token = tokens[index]
        if re.fullmatch(r"[A-Za-z]", token):
            command = token
            index += 1
        if not command:
            raise SystemExit(f"Malformed path data: {d_value[:120]}")

        relative = command.islower()
        upper = command.upper()

        if upper == "M":
            x = read_number()
            y = read_number()
            current = add_point(x, y, relative)
            start = current
            command = "l" if relative else "L"
        elif upper == "L":
            x = read_number()
            y = read_number()
            add_point(x, y, relative)
        elif upper == "H":
            x = read_number()
            if relative:
                x += current[0]
            current = (x, current[1])
            points.append(current)
        elif upper == "V":
            y = read_number()
            if relative:
                y += current[1]
            current = (current[0], y)
            points.append(current)
        elif upper == "C":
            x1 = read_number()
            y1 = read_number()
            x2 = read_number()
            y2 = read_number()
            x = read_number()
            y = read_number()
            if relative:
                x1 += current[0]
                y1 += current[1]
                x2 += current[0]
                y2 += current[1]
            points.extend([(x1, y1), (x2, y2)])
            add_point(x, y, relative)
            last_control = (x2, y2)
        elif upper == "S":
            x2 = read_number()
            y2 = read_number()
            x = read_number()
            y = read_number()
            if relative:
                x2 += current[0]
                y2 += current[1]
            points.append((x2, y2))
            add_point(x, y, relative)
            last_control = (x2, y2)
        elif upper == "Q":
            x1 = read_number()
            y1 = read_number()
            x = read_number()
            y = read_number()
            if relative:
                x1 += current[0]
                y1 += current[1]
            points.append((x1, y1))
            add_point(x, y, relative)
            last_control = (x1, y1)
        elif upper == "T":
            x = read_number()
            y = read_number()
            add_point(x, y, relative)
        elif upper == "A":
            _rx = read_number()
            _ry = read_number()
            _rotation = read_number()
            _large_arc = read_number()
            _sweep = read_number()
            x = read_number()
            y = read_number()
            add_point(x, y, relative)
        elif upper == "Z":
            current = start
            points.append(current)
            last_control = None
        else:
            raise SystemExit(f"Unsupported path command '{command}' in clip path")

        if upper not in {"C", "S", "Q"}:
            last_control = None

    return points


def path_bbox(clip_path: ET.Element) -> dict[str, float]:
    all_points: list[tuple[float, float]] = []
    for path in clip_path.findall(f".//{{{SVG_NS}}}path"):
        d_value = path.attrib.get("d", "")
        if d_value:
            all_points.extend(extract_points_from_path(d_value))
    if not all_points:
        raise SystemExit(f"Clip path '{clip_path.attrib.get('id', '?')}' contains no path points")
    xs = [point[0] for point in all_points]
    ys = [point[1] for point in all_points]
    return {
        "x": min(xs),
        "y": min(ys),
        "width": max(xs) - min(xs),
        "height": max(ys) - min(ys),
    }


def group_bbox(group: ET.Element) -> dict[str, float] | None:
    points: list[tuple[float, float]] = []
    for path in group.findall(f".//{{{SVG_NS}}}path"):
        d_value = path.attrib.get("d", "")
        if d_value:
            points.extend(extract_points_from_path(d_value))
    if not points:
        return None
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return {
        "x": min(xs),
        "y": min(ys),
        "width": max(xs) - min(xs),
        "height": max(ys) - min(ys),
    }


def shape_sort_key(entry: tuple[str, ET.Element, dict[str, float]]) -> tuple[int, float]:
    bounds = entry[2]
    return round(bounds["y"] / 400), bounds["x"]


def is_large_background(bounds: dict[str, float], full_area: float) -> bool:
    area = bounds["width"] * bounds["height"]
    return area >= full_area * 0.8


def extract_clip_groups(root: ET.Element, clip_paths: dict[str, ET.Element]) -> list[tuple[str, ET.Element, dict[str, float]]]:
    shape_groups: list[tuple[str, ET.Element, dict[str, float]]] = []
    for group in root.findall(f".//{{{SVG_NS}}}g"):
        style = group.attrib.get("style", "")
        if "clip-path:url(#" not in style:
            continue
        clip_id = style.split("clip-path:url(#", 1)[1].split(")", 1)[0]
        if clip_id == "clippath1" or clip_id not in clip_paths:
            continue
        bounds = path_bbox(clip_paths[clip_id])
        if bounds["width"] < 10 or bounds["height"] < 10:
            continue
        shape_groups.append((clip_id, group, bounds))
    return shape_groups


def extract_fill_groups(root: ET.Element, full_area: float) -> list[tuple[str, ET.Element, dict[str, float]]]:
    canvas_group = None
    for group in root.findall(f".//{{{SVG_NS}}}g"):
        style = group.attrib.get("style", "")
        if "clip-path:url(#clippath1)" in style:
            canvas_group = group
            break
    if canvas_group is None:
        return []

    shape_groups: list[tuple[str, ET.Element, dict[str, float]]] = []
    for index, group in enumerate(canvas_group.findall(f"{{{SVG_NS}}}g"), start=1):
        if "fill" not in group.attrib:
            continue
        bounds = group_bbox(group)
        if not bounds:
            continue
        if bounds["width"] < 10 or bounds["height"] < 10:
            continue
        if is_large_background(bounds, full_area):
            continue
        shape_groups.append((f"fillgroup{index}", group, bounds))
    return shape_groups


def convert_eps_pack(eps_path: Path, destination_root: Path, package_name: str | None = None) -> Path:
    gs_path = locate_tool("gs")
    pstoedit_path = locate_tool("pstoedit")
    if not gs_path or not pstoedit_path:
        missing = [name for name, path in {"gs": gs_path, "pstoedit": pstoedit_path}.items() if not path]
        raise SystemExit(f"Missing required tools: {', '.join(missing)}")

    package_stem = package_name or f"{normalize_stem(eps_path.stem)}_svg"
    output_dir = destination_root / package_stem
    output_dir.mkdir(parents=True, exist_ok=True)

    full_svg_path = output_dir / f"{package_stem}_full.svg"
    run(
        [
            pstoedit_path,
            "-f",
            "svg:-standalone -withgrouping",
            str(eps_path),
            str(full_svg_path),
        ]
    )

    tree = ET.parse(full_svg_path)
    root = tree.getroot()
    _view_x, _view_y, view_width, view_height = parse_viewbox(root)
    full_area = view_width * view_height

    clip_paths: dict[str, ET.Element] = {}
    for clip_path in root.findall(f".//{{{SVG_NS}}}clipPath"):
        clip_id = clip_path.attrib.get("id")
        if clip_id:
            clip_paths[clip_id] = clip_path

    clip_groups = extract_clip_groups(root, clip_paths)
    fill_groups = extract_fill_groups(root, full_area)

    if fill_groups and (not clip_groups or len(fill_groups) >= len(clip_groups) + 3):
        shape_groups = fill_groups
    else:
        shape_groups = clip_groups

    if not shape_groups:
        return output_dir

    shape_groups.sort(key=shape_sort_key)

    for index, (clip_id, group, bounds) in enumerate(shape_groups, start=1):
        file_name = f"shape_{index:02d}.svg"
        shape_root = ET.Element(
            f"{{{SVG_NS}}}svg",
            {
                "width": f"{int(round(bounds['width']))}px",
                "height": f"{int(round(bounds['height']))}px",
                "viewBox": (
                    f"{bounds['x']:.2f} {bounds['y']:.2f} "
                    f"{bounds['width']:.2f} {bounds['height']:.2f}"
                ),
            },
        )
        title = ET.SubElement(shape_root, f"{{{SVG_NS}}}title")
        title.text = f"{package_stem} shape {index:02d}"
        if clip_id in clip_paths:
            defs = ET.SubElement(shape_root, f"{{{SVG_NS}}}defs")
            defs.append(copy.deepcopy(clip_paths[clip_id]))
        shape_root.append(copy.deepcopy(group))

        shape_path = output_dir / file_name
        ET.ElementTree(shape_root).write(shape_path, encoding="utf-8", xml_declaration=True)
    return output_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert an EPS pack into a structured SVG package.")
    parser.add_argument("--eps", help="Path to the source EPS file.")
    parser.add_argument("--destination", help="Directory where the SVG package should be created.")
    parser.add_argument("--package-name", help="Optional temporary package folder name.", default=None)
    parser.add_argument("--check-tools", action="store_true", help="Check whether required external tools are installed.")
    args = parser.parse_args()

    if args.check_tools:
        gs_path = locate_tool("gs")
        pstoedit_path = locate_tool("pstoedit")
        result = {
            "gs": gs_path,
            "pstoedit": pstoedit_path,
            "ok": bool(gs_path and pstoedit_path),
        }
        print(json.dumps(result, ensure_ascii=True, indent=2))
        raise SystemExit(0 if result["ok"] else 1)

    if not args.eps or not args.destination:
        raise SystemExit("--eps and --destination are required unless --check-tools is used")

    output_dir = convert_eps_pack(
        Path(args.eps).expanduser().resolve(),
        Path(args.destination).expanduser().resolve(),
        args.package_name,
    )
    print(output_dir)


if __name__ == "__main__":
    main()
