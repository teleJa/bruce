# Business risk policy

## Levels

| Risk | Typical triggers | Required behavior |
|---|---|---|
| `low` | Local, reversible work with no public contract, schema, production, security, or irreversible consequence | Implement and verify directly; do not force a reviewer or business question |
| `guarded` | Schema, public API/contract, security-sensitive configuration, or important but recoverable data change | Continue when the current request already authorizes the exact change; otherwise ask one business question before mutation; always run completion review |
| `critical` | Production, infrastructure, irreversible data operation, permission boundary, security incident, or irreversible external write | Before mutation, state target, impact, and recovery and obtain explicit confirmation; always run completion review; unknown state becomes L4 |

## Reclassification

Change risk only from repository or tool evidence. Upgrade immediately when new facts reveal more
risk. Lower risk when the original trigger is disproved, record the evidence, and continue without a
ceremonial approval. Never lower risk merely to bypass a pending guarded or critical confirmation.

Expanding scope, changing acceptance, or accepting a new business consequence requires a business
decision even if the technical operation is reversible.

## Completion review

Use `verify-completion` for all guarded and critical work. For ordinary guarded work, perform a
distinct main-agent second pass. Prefer a fresh Codex-native subagent when a guarded change is broad
enough to span multiple components/contracts, combine migration and rollout, or carry a broad
security/data blast radius. Critical work and explicitly requested independent reviews require a
fresh reviewer; if none is available, report blocked rather than relabeling a main-agent pass as
independent.

Host permission prompts are outside this policy. Obey Codex and do not use a business-risk label to
grant, deny, or bypass host authority.
