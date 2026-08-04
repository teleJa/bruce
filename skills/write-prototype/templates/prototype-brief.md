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
- Source/runtime evidence: <paths, screenshots, DOM, current HTML, or current browser evidence>
- Confirmed refinement baseline: <path and SHA-256 or none>
- Known evidence gaps: <none or explicit gaps and fidelity impact>

## Evidence authority

- Confirmed requirements govern changed behavior.
- Current runtime evidence governs unchanged visible state; source revision and drift remain recorded.
- Repository source governs structural ownership and reuse anchors.
- The confirmed prototype governs the refinement baseline.
- Provider/framework defaults fill only uncovered gaps.

## Fact register

Use only `confirmed`, `inferred`, or `unresolved`. Material `unresolved` facts block generation unless
the user explicitly authorizes an exploratory fidelity boundary.

| Status | Fact | Evidence | Limitation or decision needed |
|---|---|---|---|
| confirmed\|inferred\|unresolved | <statement> | <source> | <none or limitation> |

## Surface scope

### <surface name>

- Entry and precondition: <exact entry, host relationship, and prior state>
- Actors and permissions: <confirmed roles and permissions>
- User goal: <observable goal>
- Information structure: <regions and hierarchy>
- Key actions: <action, success result, and failure response>
- Required states: <default, loading, success, failure, empty, disabled, or blocking>
- Navigation: <source and destination>
- Explicit non-goals: <excluded pages, fields, actions, roles, states, and rules>

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
