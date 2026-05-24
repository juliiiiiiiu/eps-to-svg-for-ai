---
name: eps-to-svg-pack
description: Convert EPS artwork packs into organized SVG asset folders whose final contents are just the exported SVG assets. Use when Codex needs to process one or more `.eps` files into reusable SVG resources, place them into a destination folder, and rename both the generated folder and the individual SVG files using the established snake_case naming rules for style-first folders and semantic shape filenames.
---

# Eps To Svg Pack

## Overview

Use this skill to turn an EPS pack into a reusable SVG package with deterministic extraction and AI-guided naming. The scripts handle conversion and fallback extraction; Codex handles visual naming decisions.

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
- a temporary full-sheet SVG used during extraction
- `shape_01.svg`, `shape_02.svg`, ... in the package root when individual shapes are found

3. Inspect the extraction strategy before naming.

- First prefer the automatically extracted shape SVGs.
- If extraction produced nothing or produced only a few coarse groups that do not match the visible artwork, inspect the full-sheet SVG structure.
- When the converted SVG already contains one visual shape per fill group or per top-level group, treat those groups as the true extraction units and rebuild the per-shape SVGs from them.
- Do not assume `clipPath` extraction is authoritative. In today's failure case, the sticker pack had its shapes already separated into sibling fill groups, but the old workflow only looked for non-canvas clip groups and missed them.

4. Inspect the shapes visually before naming.

If a matching JPG/PNG preview exists next to the EPS, open it or inspect it directly for the overall composition. Then inspect the generated SVGs:

- use the visual output, not just filenames or clip ids, to decide names
- if helpful, run `scripts/generate_preview_html.py` to create a temporary preview page from the root-level SVGs

5. Apply naming rules.

Read `references/naming_rules.md`. Follow it exactly:

- rename the generated package folder to a style-first snake_case folder name
- rename every extracted shape SVG to a semantic snake_case filename
- the final resource pack should keep only the exported SVG assets in the package root
- do not keep `manifest.json`, `preview.html`, or a `shapes/` subfolder in the final package

6. Apply the rename map with the script.

Create a rename spec JSON like:

```json
{
  "package_name": "neon_gradient_fluid",
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

This renames the exported SVGs, deletes temporary scaffolding such as the full-sheet SVG and preview files, and renames the package folder last.

## Decision Rules

- Use the source EPS stem only as a temporary package name. Do not treat it as the final naming source.
- Use adjacent preview JPG/PNG files when present to understand the intended artwork set.
- Use extracted SVG previews to name individual shapes.
- Prefer the quietest accurate name. Do not over-describe.
- Keep filenames stable and machine-friendly. Use snake_case only.
- If non-canvas `clipPath` extraction is empty or suspiciously coarse, inspect whether the real shapes are already separated into sibling fill groups or top-level groups and extract from those instead.
- If no trustworthy per-shape extraction exists after both passes, keep a single SVG asset for the whole pack rather than inventing fake shapes.

## Scripts

### `scripts/convert_eps_pack.py`

Convert EPS into a package with a temporary full-sheet SVG and extracted root-level shape SVGs. The script now falls back to top-level fill-group extraction when clip-group extraction misses already separated shapes.

### `scripts/generate_preview_html.py`

Generate a temporary `preview.html` by scanning root-level SVGs in a package.

### `scripts/apply_pack_naming.py`

Apply a rename spec, flatten the final package to SVG assets only, and rename the package folder.

## References

### `references/naming_rules.md`

Load this reference before naming folders or individual SVGs.
