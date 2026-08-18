# UI variant exploration

Compare two to five structurally different approaches on the real host surface. Default to three.
Variants must disagree about layout, information hierarchy, or primary affordance; color-only or
copy-only variations do not answer a UI design question.

## Placement

Prefer the existing route and retain its real shell, data fetching, parameters, permissions, and
density. Switch only the rendered prototype subtree with a shareable `?variant=` URL parameter.

Create a throwaway route only when no natural host page exists. Follow the repository router and name
the route clearly as a prototype. Do not invent a new top-level application structure.

## Variant switcher

- Use one small development-only switcher with previous/next controls and the current variant name.
- Update the URL through the project's router so refresh and sharing preserve the selected variant.
- Support left/right keyboard navigation without intercepting input, textarea, select, or editable
  element interaction.
- Ensure the switcher cannot render in a production build.

Keep existing read-only data realistic. Stub mutations and external effects. Do not share so much
layout code that the variants can no longer diverge structurally.

## Evaluation

Open every variant through the Codex App Chrome capability, exercise the primary interaction, inspect
the visible state and relevant DOM/geometry, and capture screenshots when layout comparison matters.
Record which parts the user selects and why. A winning variant still requires production-quality
implementation; remove the switcher and losing variants from the production change.
