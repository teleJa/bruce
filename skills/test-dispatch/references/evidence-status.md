# Verification track evidence and status

Use only `designed`, `executed`, `passed`, `failed`, and `blocked` for scenario/track status.

- `designed`: the scenario or test exists but no required action was executed.
- `executed`: execution occurred, but required assertions or evidence are incomplete.
- `passed`: all assertions for the declared mode passed with current evidence.
- `failed`: execution reached a required assertion and the observed result did not match.
- `blocked`: a prerequisite, authorization, environment, account, provider, or control boundary prevented reaching the required assertion.

A single HTTP 2xx, created Job, success Toast, screenshot, generated script, or metadata check is insufficient by itself. Track status is evidence for Completion Gate and never a parallel completion decision.
