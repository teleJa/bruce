# Repository UI contract: <change name>

Use this file only for an `existing-product-extension`. Record the bounded product surface supplied
to the provider; do not copy unrelated source or CSS.

## Host surface

- Route or page: <route/page and current shell>
- Owning component: <source path and symbol>
- Source revision: <commit/revision or explicit unavailable evidence>
- Current runtime evidence: <screenshot, DOM/accessibility, current HTML, or unavailable with impact>
- Source revision and drift: <none or runtime/source differences and chosen authority>

## Exact entry

- User action: <exact trigger>
- Location and relationship: <parent region/node and relative position>
- Source symbol or selector: <symbol/selector and path>
- Preconditions and permission: <state, role, feature flag, or none>

## Destination surface

- Container: <Modal, Drawer, inline region, route, or other evidenced container>
- Open transition: <trigger to visible state>
- Close or completion transition: <result and restored/next state>
- Size and placement: <evidenced dimensions and responsive behavior>

## UI Surface Contract

- Contract path: <structured YAML/JSON path or `not-applicable` for greenfield>
- Schema version: <integer>
- Surface IDs: <unique `SURFACE-...` ids and their parent/child relationship>
- Regions and hierarchy: <surface regions, parent/child order, and purpose>
- Required states: <default, loading, success, empty, failure, disabled, and blocking coverage>
- Required viewports: <viewport names and width/height>
- Interaction transitions: <trigger, precondition, state transition, success, and failure>
- Observable fields: <user-visible fields, relationships, and empty/error semantics>
- Evidence methods: <contract, unit, chrome-smoke, chrome-layout, screenshot, or other feasible evidence>
- Evidence freshness: <current/planned/stale/unavailable with impact>
- Implementation mapping: <optional `file`, `route`, `template`, `view`, or `source-entry`; no framework AST>

The Surface Contract is the product-surface authority. A repository locator is evidence for mapping,
not a requirement to model React, Vue, DOM, or any component tree. Validate this contract with
`scripts/validate_surface_contract.py` independently from `visual-assertions.json`.

## Layout invariants

| Id | Required invariant | Evidence | Verification |
|---|---|---|---|
| L-01 | <unchanged topology or relationship> | <source/runtime/baseline> | <DOM/selector/screenshot check> |

## Reuse anchors

| Existing component or pattern | Required use | States to preserve | Evidence |
|---|---|---|---|
| <component/pattern> | <how it is reused> | <loading/error/selected/etc.> | <path/runtime> |

## Visual anchors

| Selector or region | Property/state | Exact token or bounded rule | Evidence | Verification |
|---|---|---|---|---|
| <selector/region> | <background/width/active/etc.> | <value/range> | <source/runtime> | <exact/region screenshot> |

Exact normalized colors, dimensions, and radii use exact assertions. Automated screenshot checks
must record viewport and region-specific tolerance; one global score cannot replace critical-region
assertions.

## Visual authority and plugin compatibility

- Authority order: `confirmed requirements > current runtime evidence for unchanged state > repository
  theme/source > confirmed prototype refinement baseline > provider/framework defaults only for
  uncovered gaps`.
- Unchanged visual protection: <shell, palette, typography, brand, spacing, dimensions, radii, and
  geometry that the provider must preserve>
- Selected generation skill: <explicit id/version>
- Selected visual plugin: <explicit id/version or none>
- Selected design system: <explicit id/version or none>
- Selection basis: <repository/runtime evidence>
- Compatibility check: <clear|blocked, evidence path, and whether plugin defaults can override tokens>
- Effective plugin/design system: <exact values passed to `start_run`>
- Run input summary: <exact selection and context identity>
- Exact assertion sidecar: `prototype-context/visual-assertions.json`

```json
{
  "schema_version": 1,
  "exact_colors": [{"selector": ".surface", "value": "#112233"}],
  "exact_dimensions": [{"selector": ".sidebar", "property": "width", "value": "184px"}],
  "required_brand_text": [{"selector": ".brand", "value": "<confirmed brand text>"}],
  "forbidden_tokens": [{"value": "<forbidden provider/default token or text>"}]
}
```

An incompatible or unproven visual plugin/design system is `blocked-before-generation`. Do not
silently select `design-system-ant` for an existing-product extension.

## Baseline artifacts

| Artifact | Type | SHA-256 | What it governs |
|---|---|---|---|
| `prototype-context/baseline/<file>` | <screenshot/DOM/HTML/confirmed prototype> | <digest> | <unchanged structure/visual/refinement baseline> |

## Evidence gaps

- Missing evidence: <none or item>
- Fidelity impact: <none, manual-only Visual evidence, or source-grounded wireframe>
- Explicitly accepted boundary: <user signal or pending>
