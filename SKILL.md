---
name: eps-to-svg-pack
description: Convert EPS artwork packs into organized SVG asset folders with a full-sheet SVG, extracted per-shape SVGs, preview HTML, and manifest metadata. Use when Codex needs to process one or more `.eps` files into reusable SVG resources, place them into a destination folder, and rename both the generated folder and the individual SVG files using the established snake_case naming rules for style-first folders and semantic shape filenames.
---

# Eps To Svg Pack

## Overview

Use this skill to turn an EPS pack into a reusable SVG package with deterministic extraction and AI-guided naming. The scripts handle conversion and folder scaffolding; Codex handles visual naming decisions.

## Workflow

1. Check dependencies.

Run `scripts/convert_eps_pack.py --check-tools` first. If required tools are missing, install them before continuing. This workflow expects `ghostscript` and `pstoedit`. Prefer Homebrew on macOS and the system package manager on Linux.

2. Convert the EPS into a neutral SVG package.

Run:

```bash
python3 scripts/convert_eps_pack.py \
  --eps "/abs/path/to/file.eps" \
  --destination "/abs/path/to/output-root"
```

This creates:

- a package folder with a neutral temporary name
- a full-sheet SVG
- `shapes/shape_01.svg`, `shape_02.svg`, ...
- `manifest.json`
- `preview.html`

3. Inspect the shapes visually before naming.

If a matching JPG/PNG preview exists next to the EPS, open it or inspect it directly for the overall composition. Then preview the generated SVGs:

- prefer serving the package folder with a temporary local server
- open `preview.html` in the Browser plugin when available
- use the visual output, not just filenames or clip ids, to decide names

4. Apply naming rules.

Read `references/naming_rules.md`. Follow it exactly:

- rename the generated package folder to a style-first snake_case folder name
- rename the full-sheet SVG to `<folder_name>_shapes_sheet.svg`
- rename every extracted shape SVG to a semantic snake_case filename

5. Apply the rename map with the script.

Create a rename spec JSON like:

```json
{
  "package_name": "neon_gradient_fluid",
  "sheet_name": "neon_gradient_fluid_shapes_sheet.svg",
  "shapes": [
    { "from": "shape_01.svg", "to": "aqua_violet_crescent_blob.svg" }
  ]
}
```

Then run:

```bash
python3 scripts/apply_pack_naming.py \
  --package-dir "/abs/path/to/generated-package" \
  --rename-spec "/abs/path/to/rename-spec.json"
```

This updates file names, `manifest.json`, and `preview.html`, then renames the package folder last.

## Decision Rules

- Use the source EPS stem only as a temporary package name. Do not treat it as the final naming source.
- Use adjacent preview JPG/PNG files when present to understand the intended artwork set.
- Use extracted SVG previews to name individual shapes.
- Prefer the quietest accurate name. Do not over-describe.
- Keep filenames stable and machine-friendly. Use snake_case only.
- If extraction fails because the EPS does not use clip groups in the expected way, keep the full-sheet SVG and stop before inventing fake per-shape files.

## Scripts

### `scripts/convert_eps_pack.py`

Convert EPS into a package with a full-sheet SVG, extracted shape SVGs, manifest, and preview HTML.

### `scripts/generate_preview_html.py`

Regenerate `preview.html` from `manifest.json`.

### `scripts/apply_pack_naming.py`

Apply a rename spec, update `manifest.json`, regenerate `preview.html`, and rename the package folder.

## References

### `references/naming_rules.md`

Load this reference before naming folders or individual SVGs.
