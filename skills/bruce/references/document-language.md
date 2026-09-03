# Document language

Persisted Bruce documents use the current user's language for natural-language prose.

- When the user writes in Chinese, write the document body in Simplified Chinese by default.
- Markdown section titles and headings (e.g. `#`, `##`, `###`) must also be written in Simplified
  Chinese by default for Chinese requests (e.g. `## 宿主表面` instead of `## Host surface`,
  `## 布局不变量` instead of `## Layout invariants`), unless a heading itself is an untranslated
  proper noun or machine token.
- Keep stable machine-facing tokens unchanged, including code identifiers, paths, protocol names,
  YAML/JSON key names, scenario keywords such as `Given`/`When`/`Then`/`Evidence`, and verdict or
  status values such as `Design: pass|blocked`.
- Preserve user-provided proper nouns and quoted source text; do not translate them merely for
  consistency.
- This rule applies to newly generated or updated documents. It does not require rewriting
  historical artifacts.
