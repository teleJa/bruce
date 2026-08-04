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

## Baseline artifacts

| Artifact | Type | SHA-256 | What it governs |
|---|---|---|---|
| `prototype-context/baseline/<file>` | <screenshot/DOM/HTML/confirmed prototype> | <digest> | <unchanged structure/visual/refinement baseline> |

## Evidence gaps

- Missing evidence: <none or item>
- Fidelity impact: <none, manual-only Visual evidence, or source-grounded wireframe>
- Explicitly accepted boundary: <user signal or pending>
