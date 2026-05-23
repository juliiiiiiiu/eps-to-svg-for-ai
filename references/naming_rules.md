# Naming Rules

Use these rules for every generated package and every extracted SVG.

## Folder Names

- Use `snake_case`.
- Keep 2 to 4 high-signal style words.
- Order words from broad style to more specific trait.
- Remove low-information words such as `shape`, `shapes`, `vector`, `set`, `pack`, `collection`, `illustration`, `clipart`, `element`, `item`, `design`, `logo`, `flyer`, `presentation`, `persentation`, `gift`, `car`.
- Preserve meaningful style layers when the source name contains them.

Examples:

- `flat-design-colorful-retro-geometric-shape-illustration` -> `colorful_retro_geometric`
- `colourful-abstract-shapes-fluid-hand-drawn-organic-shapes-vector-shape-creative-element` -> `colourful_abstract_fluid_hand_drawn`
- `gradient-grainy-gradient-shapes` -> `gradient_grainy`

## Full-Sheet SVG Name

- Use `<folder_name>_shapes_sheet.svg`.

Examples:

- `neon_gradient_fluid_shapes_sheet.svg`
- `colorful_retro_geometric_shapes_sheet.svg`

## Individual Shape SVG Names

- Use `snake_case`.
- Prefer 3 to 5 tokens.
- Start with dominant color or palette when it helps disambiguate.
- End with a shape descriptor such as `blob`, `oval_blob`, `teardrop_blob`, `hook_blob`, `leaf_blob`, `splash_blob`.
- Add one qualifier only when it meaningfully distinguishes the silhouette.
- Avoid numeric suffixes unless two shapes are otherwise indistinguishable.

Recommended pattern:

- `{color_or_palette}_{shape_descriptor}.svg`
- `{color_or_palette}_{qualifier}_{shape_descriptor}.svg`

Examples:

- `aqua_violet_crescent_blob.svg`
- `orange_red_arch_blob.svg`
- `mint_green_bowtie_blob.svg`
- `peach_pink_rounded_rect_blob.svg`

## Naming Style

- Prefer simple visual nouns over metaphor-heavy names.
- Prefer `leaf_blob` over `organic_dynamic_asymmetric_form`.
- Prefer `hook_blob` over `question_mark_shape`.
- Prefer `rounded_rect_blob` over `soft_square_liquid`.

## Final Check

Before applying names, verify:

- folder name matches the pack’s style family
- full-sheet file name uses the final folder name
- each extracted SVG name is unique
- names are short enough to scan quickly
- no spaces, hyphens, or uppercase letters remain
