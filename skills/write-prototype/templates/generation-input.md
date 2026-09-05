# Provider generation input：<change name>

这是给 Open Design Agent 的精简输入，不是第二份需求文档。详细源码、UI contract、视觉断言和
baseline 保留在本地 change 目录；这里只保留生成所需的稳定事实、当前增量和引用身份。

## Identity

- repository: `<repository>`
- change: `<change>`
- surface: `<surface>`
- source_revision: `<revision or unknown>`
- context_hash: `<sha256 after materialization>`
- sync_mode: `<full or incremental>`
- source_evidence: `<local paths and hashes>`

## Fixed authority

- visual_authority: `<runtime, repository, confirmed-prototype, or provider-default-only>`
- direction_selection: `<skip or provider-capability>`
- prototype_generator_profile: `prototype-generator`
- effective_model: `gemini-3.8-flash` or explicitly resolved override
- native_reasoning_effort: `high` or explicitly resolved override
- selected_agent: `<Open Design agent id/version>`
- selected_generation_skill: `<skill>`
- generation_skill_readiness: `<clear, partial, or blocked>`
- selected_visual_plugin: `<none or explicit id>`
- selected_design_system: `<none or explicit id>`

## Required output

- pages/surfaces: `<bounded list>`
- states: `<bounded list>`
- interactions: `<bounded list>`
- positive_assertions: `<ids>`
- negative_assertions: `<ids>`
- non_goals: `<bounded list>`

## Current increment

- `<none for first generation, or changed facts/assertions/baseline paths only>`

Do not read unrelated repository files, enumerate provider catalogs when ids are already fixed, call
unknown CLI subcommands, or replace repository visual authority with provider defaults.
