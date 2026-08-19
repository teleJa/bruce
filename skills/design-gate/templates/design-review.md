# Design Review

- Objective: <objective>
- Scope: <allowed and excluded scope>
- Implementation boundary: <what this design governs>
- Review mode: <main-agent|independent>
- Behavior implementation: <yes|no>
- Public/cross-component contract change: <yes|no>
- Database/persistence design change: <yes|no>
- Governing UI prototype: <yes|no>

## Candidate Matrix

| Candidate | Applicability | Delivery | Path | Repository-backed evidence |
|---|---|---|---|---|
| Requirement or clarification | required\|skipped | generated\|missing\|skipped | <path or none> | <evidence> |
| Architecture | required\|skipped | generated\|missing\|skipped | <path or none> | <evidence> |
| API/file contracts | required\|skipped | generated\|missing\|skipped | <path or none> | <evidence> |
| Database/table design | required\|skipped | generated\|missing\|skipped | <path or none> | <evidence> |
| Implementation plan | required\|skipped | generated\|missing\|skipped | <path or none> | <evidence> |
| Test design | required\|skipped | generated\|missing\|skipped | <path or none> | <evidence> |
| UI prototype | required\|skipped | generated\|missing\|skipped | <prototype-manifest.md path or none> | <evidence> |

## Readiness

- Facts and consistency: <pass|blocked with evidence>
- Acceptance and verification coverage: <pass|blocked with evidence>
- Risk and recovery coverage: <pass|blocked|not-applicable with evidence>
- Existing-product visual authority and compatibility: <clear or findings for ordered authority,
  selected/effective generation skill and visual plugin/design-system, compatibility evidence, and
  run input summary>
- Deterministic artifact visual assertions: <clear or findings for exact colors/dimensions/brand/
  forbidden tokens and whether manual-only evidence is correctly fail-closed>
- Blocking findings: <none or findings>
- Evidence boundary: <checked and unchecked facts>
- Smallest next action: <none or action>

## Validation

- Command: `python3 <plugin-root>/skills/design-gate/scripts/validate_design_review.py --change-dir <change-directory>`
- Result: <pass with current command evidence>

## Verdict

Design: <pass|blocked>
