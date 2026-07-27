# API and file contracts: Completion Gate skill id

## completion-gate-skill-id

- Change: `changed`
- Provider: Bruce plugin skill discovery under `skills/`
- Consumers: users invoking the skill, `skills/bruce`, `skills/goal-execution`, Bruce policy references, UI metadata, and contract tests
- Authoritative source: `skills/completion-gate/SKILL.md` frontmatter and directory name
- Compatibility: breaking rename from `verify-completion` to `completion-gate`; no compatibility alias is retained
- Authentication/authorization: none

### Request, event, or input

```text
Old invocation: $verify-completion
New invocation: $completion-gate

The skill continues to consume the task contract, final workspace state and diff,
current acceptance evidence, applicable design-review.md, failure history, and
delivery boundaries. Input semantics do not change.
```

### Success result

```text
The Completion Gate continues to return exactly one terminal field:
Completion: pass|issues|blocked

Its main-agent|independent review modes and decision criteria are unchanged.
The design-gate skill id and design-review.md artifact name are unchanged.
```

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| A caller still invokes `$verify-completion` after refreshing the plugin | Skill discovery cannot resolve the removed id | Replace the invocation with `$completion-gate`; retrying the old id has no effect |
| An installed plugin cache still exposes the old id | The cached plugin continues to show `$verify-completion` until refreshed | Refresh or reinstall the local plugin, then start a new Codex task and verify discovery |
| An active runtime document still references the old id | Contract validation fails | Update active source and tests; historical `docs/change/**` records remain unchanged |

### Verification

- Provider: `python3 scripts/validate_plugin.py`
- Consumer: `python3 -m unittest discover -s tests -p 'test_*.py'`
- Static migration check: verify `verify-completion` remains only in explicit negative migration guards and historical `docs/change/**` records
