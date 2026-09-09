# Business risk policy

## Levels

| Risk | Typical triggers | Required behavior |
|---|---|---|
| `low` | Local, reversible work with no public contract, schema, production, security, or irreversible consequence | Implement and verify within scope; require independent completion review without a ceremonial business question |
| `guarded` | Schema, public API/contract, security-sensitive configuration, or important but recoverable data change | Continue when the current request authorizes the exact change; otherwise ask one business question before mutation; use risk-proportional Completion Gate review |
| `critical` | Production, infrastructure, irreversible data operation, permission boundary, security incident, or irreversible external write | Before mutation, state target, impact, and recovery and obtain explicit confirmation; require independent Completion Gate review; unknown state becomes L4 |

## Reclassification

Change risk only from repository or tool evidence. Upgrade immediately when new facts reveal more
risk. Lower risk when the original trigger is disproved, record the evidence, and continue without a
ceremonial approval. Never lower risk merely to bypass a pending guarded or critical confirmation.

Expanding scope, changing acceptance, or accepting a new business consequence requires a business
decision even if the technical operation is reversible.

## Completion assurance

Every implementation task uses `completion-gate` with an independent `reviewer`, including low-risk
and ordinary guarded tasks. Risk changes review depth and focus, not independence or verdict count.
Plan review also requires an independent reviewer whenever that optional capability is invoked.
Key design quality review follows Design Gate's independent-review predicate; deterministic artifact
checks alone do not claim independent design review.

Independent mode uses a fresh Codex-native subagent with no inherited author conversation. The worker
uses the shared `reviewer` Functional Agent Profile, a clean-context v1 Task Packet, and returns a
`review_packet` with findings only; it never emits a Gate verdict. If the model is unavailable or
unconfirmed, pause the affected review and ask the user to select an available replacement. No automatic
model fallback, main-agent self-review, or verifier substitution is allowed. Required clean context and
tools must also be available. The owning Completion Gate returns `Completion: blocked` while required
review is unavailable. Independence remains internal to the existing Gate, not a third verdict.

Host permission prompts are outside this policy. Obey Codex and do not use a business-risk label to
grant, deny, or bypass host authority.
