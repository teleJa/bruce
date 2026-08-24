# Business risk policy

## Levels

| Risk | Typical triggers | Required behavior |
|---|---|---|
| `low` | Local, reversible work with no public contract, schema, production, security, or irreversible consequence | Implement and verify directly; do not force a reviewer or business question |
| `guarded` | Schema, public API/contract, security-sensitive configuration, or important but recoverable data change | Continue when the current request authorizes the exact change; otherwise ask one business question before mutation; use risk-proportional Completion Gate review |
| `critical` | Production, infrastructure, irreversible data operation, permission boundary, security incident, or irreversible external write | Before mutation, state target, impact, and recovery and obtain explicit confirmation; require independent Completion Gate review; unknown state becomes L4 |

## Reclassification

Change risk only from repository or tool evidence. Upgrade immediately when new facts reveal more
risk. Lower risk when the original trigger is disproved, record the evidence, and continue without a
ceremonial approval. Never lower risk merely to bypass a pending guarded or critical confirmation.

Expanding scope, changing acceptance, or accepting a new business consequence requires a business
decision even if the technical operation is reversible.

## Completion assurance

Every implementation task uses `completion-gate`. Risk changes its review mode, not the number of
completion verdicts:

- low and ordinary guarded work use the main-agent review mode;
- guarded work uses independent mode when it spans multiple components/contracts, combines migration and
  rollout, has semantic novelty or ambiguity, depends mainly on weak executable evidence, follows
  repeated author repair, or carries broad security/data impact;
- critical work and explicitly requested independent review always use independent mode.

Independent mode uses a fresh Codex-native subagent with no inherited author conversation. The worker uses the shared `reviewer` Functional Agent Profile, a clean-context v1 Task Packet, and returns a `review_packet` with findings only; it never emits a Gate verdict. If clean
context is unavailable, `completion-gate` returns `Completion: blocked`. Independent review is an
internal mode, not a separate result that callers combine with completion.

Host permission prompts are outside this policy. Obey Codex and do not use a business-risk label to
grant, deny, or bypass host authority.
