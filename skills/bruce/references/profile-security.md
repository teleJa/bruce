# Profile security and evidence boundary

Environment and Requirement Verification Profiles, and generated project operation Skills, may describe how a credential or account is used, but never store the secret itself.

## Allowed

```yaml
credential_id: auth-center-test
source_ref: AUTH_CENTER_TEST_API_KEY
required_scopes: [ticket-exchange]
secret_value_persisted: false
expose_to_model: false
redact_logs: true
```

```yaml
account_pool: auth-center-new-users
account_alias: user-managed-test-account
required_initial_state: local_identity_absent
credential_source: user-managed-browser-session
```

## Forbidden

- passwords, API Key values, access tokens, cookies, JWTs, SSO tickets;
- complete external provider responses containing identity or token data;
- secrets copied into generated project Skills, Checkpoints, Handoffs, logs, screenshots, or chat summaries;
- `.env` values passed as command-line arguments or embedded in `argv`/shell text.

## Evidence distinction

A Profile declares required evidence and its source. A generated project operation Skill binds to the source Profile and executes only confirmed commands after per-invocation authorization. A Verification Run/Checkpoint records the actual captured evidence, source revision, environment revision, account binding, operation result, and current status. Profile confirmation and Skill generation do not assert runtime availability or acceptance success.
