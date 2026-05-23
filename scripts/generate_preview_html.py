#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <style>
      body {{
        margin: 0;
        padding: 24px;
        font-family: system-ui, sans-serif;
        background: #f6f4f1;
        color: #111;
      }}
      h1 {{
        margin: 0 0 16px;
        font-size: 28px;
      }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 16px;
      }}
      .card {{
        background: #fff;
        border: 1px solid #e6e0d8;
        border-radius: 18px;
        padding: 14px;
      }}
      .frame {{
        display: grid;
        place-items: center;
        min-height: 220px;
        border-radius: 14px;
        background: #faf8f6;
        overflow: hidden;
      }}
      .frame svg {{
        width: 100%;
        height: 100%;
        max-width: 220px;
        max-height: 220px;
      }}
      .name {{
        margin-top: 10px;
        font-size: 13px;
        word-break: break-word;
      }}
    </style>
  </head>
  <body>
    <h1>{title}</h1>
    <div class="grid" id="grid"></div>
    <script>
      const files = {files_json};
      async function load() {{
        const grid = document.getElementById("grid");
        for (const file of files) {{
          const response = await fetch(`./shapes/${{file}}`);
          const svg = await response.text();
          const card = document.createElement("article");
          card.className = "card";
          const frame = document.createElement("div");
          frame.className = "frame";
          frame.innerHTML = svg;
          const name = document.createElement("div");
          name.className = "name";
          name.textContent = file;
          card.append(frame, name);
          grid.append(card);
        }}
      }}
      load();
    </script>
  </body>
</html>
"""


def build_preview(package_dir: Path) -> Path:
    manifest_path = package_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = [entry["file"] for entry in manifest["shapes"]]
    title = package_dir.name
    html = HTML_TEMPLATE.format(title=title, files_json=json.dumps(files))
    output = package_dir / "preview.html"
    output.write_text(html, encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate preview HTML for an EPS-to-SVG package.")
    parser.add_argument("--package-dir", required=True, help="Path to the generated package directory.")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).expanduser().resolve()
    output = build_preview(package_dir)
    print(output)


if __name__ == "__main__":
    main()
