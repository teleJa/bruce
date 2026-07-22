# API and event contracts: <change name>

## <stable-contract-anchor>

- Provider: `<component or external system>`
- Consumer: `<component or actor>`
- Compatibility: `<additive/versioned/breaking and migration rule>`
- Authentication/authorization: `<requirements>`

### Request, event, or input

```text
<method and route, RPC/event name, file/data shape, fields and types>
```

### Success result

```text
<status/result shape and semantics>
```

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| <condition> | <status/error/event> | <rule> |

### Verification

- Provider: <contract/unit/integration check>
- Consumer: <mock/contract/integration check>
