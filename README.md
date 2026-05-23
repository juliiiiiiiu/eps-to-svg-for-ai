# eps-to-svg-pack

Convert EPS artwork packs into organized SVG asset folders.

This repository contains a Codex skill plus deterministic helper scripts for:

- converting `.eps` files into a full-sheet `.svg`
- extracting individual shape SVGs
- generating `manifest.json` and `preview.html`
- renaming the package folder and extracted SVGs with style-first, AI-friendly snake_case names

## What It Produces

Given an input EPS and a destination folder, the workflow creates:

- a package folder
- one full-sheet SVG
- a `shapes/` folder with extracted per-shape SVGs
- a `manifest.json`
- a `preview.html`

After visual naming, it can also rename:

- the package folder
- the full-sheet SVG
- every extracted shape SVG
- the manifest and preview references

## Requirements

The conversion flow expects:

- `ghostscript`
- `pstoedit`

Recommended install commands:

### macOS

```bash
brew install ghostscript pstoedit
```

### Linux

Use your distro package manager, for example:

```bash
sudo apt install ghostscript pstoedit
```

## Skill Usage

Install the skill by placing this folder in your Codex skills directory, for example:

```bash
cp -R eps-to-svg-pack ~/.codex/skills/eps-to-svg-pack
```

Then ask Codex to use `eps-to-svg-pack` with:

- an EPS file path
- a destination folder

## Script Usage

### 1. Check tools

```bash
python3 scripts/convert_eps_pack.py --check-tools
```

### 2. Convert an EPS into a neutral package

```bash
python3 scripts/convert_eps_pack.py \
  --eps "/abs/path/to/file.eps" \
  --destination "/abs/path/to/output-root"
```

### 3. Apply semantic naming

Create a rename spec JSON:

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

## Naming Rules

Folder and file naming rules live in:

- [references/naming_rules.md](references/naming_rules.md)

## Repository Layout

```text
eps-to-svg-pack/
├── SKILL.md
├── README.md
├── LICENSE
├── .gitignore
├── agents/
├── references/
└── scripts/
```
