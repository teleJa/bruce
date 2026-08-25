# Prototype brief: <change name>

## Identity

- Change: <change id and title>
- Repository: <repository identity>
- Target surface: <page, flow, dialog, overlay, or application>
- Surface classification: <greenfield or existing-product-extension>
- Frontend type: <management web, desktop web, mobile web, or miniprogram>
- Run objective: <first generation or revision>
- Prior run: <none or explicit project/run ids and baseline SHA-256>

## Context evidence

- Product or requirement evidence: <paths and relevant sections>
- Repository UI contract: <path or not applicable for greenfield>
- Design system evidence: <paths or approved greenfield constraints>
- `selected_generation_skill`: <explicit id/version or none>
- `generation_skill_readiness`: <clear, partial, or blocked plus reusable workflow/seed evidence>
- `selected_visual_plugin`: <explicit id/version or none>
- `selected_design_system`: <explicit id/version or none>
- `selection_basis`: <repository/runtime evidence or greenfield rationale>
- `compatibility_check`: <clear|blocked with evidence and override-risk assessment>
- `effective_plugin`: <exact plugin id passed to `start_run`, or none>
- `effective_design_system`: <exact design-system id passed to `start_run`, or none>
- `run_input_summary`: <exact Agent/skill/plugin/design-system/project/context identity>
- `discovery_mode`: <selective, full, or legacy>
- `direction_selection`: <skip, provider-capability, or legacy-unknown>
- `context_hash`: <none or sha256 of compact provider-facing context>
- `context_files`: <compact provider input plus local evidence references>
- `sync_mode`: <full, incremental, or legacy>
- Source/runtime evidence: <paths, screenshots, DOM, current HTML, or current browser evidence>
- Confirmed refinement baseline: <path and SHA-256 or none>
- Known evidence gaps: <none or explicit gaps and fidelity impact>

## Evidence authority

- Confirmed requirements govern changed behavior.
- Current runtime evidence governs unchanged visible state; source revision and drift remain recorded.
- Repository source governs structural ownership and reuse anchors.
- Repository theme/source governs unchanged shell, palette, typography, brand, spacing, dimensions,
  radius, and geometry when evidenced.
- The confirmed prototype governs the refinement baseline.
- Provider/framework defaults fill only uncovered gaps.

### Visual authority contract

- Authority order: `confirmed requirements > current runtime evidence for unchanged state > repository
  theme/source > confirmed prototype refinement baseline > provider/framework defaults only for
  uncovered gaps`.
- Fidelity mode: <high-fidelity, source-grounded wireframe, or exploratory>
- Unchanged-surface protection: <shell/layout/palette/typography/brand/geometry that must not be
  redesigned>

## Fact register

Use only `confirmed`, `inferred`, or `unresolved`. Material `unresolved` facts block generation unless
the user explicitly authorizes an exploratory fidelity boundary.

| Status | Fact | Evidence | Limitation or decision needed |
|---|---|---|---|
| confirmed\|inferred\|unresolved | <statement> | <source> | <none or limitation> |

## Surface scope

### <surface name>

- Surface ID: <stable `SURFACE-...` id>
- Entry and precondition: <exact entry, host relationship, and prior state>
- Actors and permissions: <confirmed roles and permissions>
- User goal: <observable goal>
- Information structure: <regions and hierarchy; each region has a stable region ID>
- Required states: <default/loading/success/failure/empty/disabled/blocking states and observable result>
- Interaction transitions: <trigger, precondition, transition, success result, and failure response>
- Observable fields: <field/value/state that a user or evidence check can observe, including empty/error semantics>
- Layout invariants: <stable topology, relationship, sizing, wrapping, overflow, and responsive rules>
- Visual anchors: <evidenced hierarchy, brand, palette, typography, spacing, and geometry>
- Required viewports: <viewport names and width/height>
- Evidence methods: <contract, unit, chrome-smoke, chrome-layout, screenshot, or other feasible evidence>
- Implementation mapping: <optional generic file/route/template/view/source-entry locator; never a framework requirement>
- Navigation: <source and destination>
- Explicit non-goals: <excluded pages, fields, actions, roles, states, and rules>

Use one row per surface when the target has multiple views or overlays. Keep child regions in the
hierarchy rather than inventing a framework-specific component tree.

## Regression assertions

Every confirmed correction must add at least one assertion in each table before refinement.

### Positive assertions

| Id | Required observable result | Evidence method |
|---|---|---|
| P-01 | <required state, relationship, token, or transition> | <DOM/selector/interaction/screenshot> |

### Negative assertions

| Id | Forbidden regression | Evidence method |
|---|---|---|
| N-01 | <forbidden redesign, state, relationship, token, or data exposure> | <DOM/selector/interaction/screenshot> |

## Design and implementation constraints

- Reuse the evidenced design system, tokens, components, typography, and icon sources.
- Do not introduce unconfirmed pages, fields, actions, roles, states, or business rules.
- Preserve every unchanged layout and visual invariant in the repository UI contract.
- The prototype must not contain credentials, tokens, cookies, test accounts, private keys, remote
  resources, or real authenticated backend connections.
- Existing-product exact visual values and forbidden defaults must be listed in
  `prototype-context/visual-assertions.json`; do not rely on prompt wording alone.
- Prototype source is design evidence, not production frontend implementation.

## Output contract

- Artifact type: <complete prototype, high-fidelity design, source-grounded wireframe, or local UI evidence>
- Entry file: <expected entry name>
- Required pages: <list>
- Required states: <list>
- Required interactions: <list>
- Required viewports: <list or unavailable with impact>
- Allowed static simulation: <list>
- Acceptance focus: <Functional, Visual, Safety, and Provenance assertions>

## Current user feedback

- <not applicable for first generation, or confirmed itemized feedback linked to P/N assertion ids>
