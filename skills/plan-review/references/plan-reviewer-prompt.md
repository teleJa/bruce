# Plan reviewer prompt

Use this prompt with a fresh Codex-native subagent started with `fork_turns="none"` or equivalent
clean context when independent review is required. Provide the objective, acceptance, raw plan
final diff or immutable snapshot, raw repository evidence, necessary constraints, and only the
artifacts the plan explicitly references. Do not provide the author's rationale, confidence, or
proposed conclusion.

```text
Review the supplied implementation plan for execution readiness. Do not polish wording and do not
approve or execute it.

Check:
- objective, scope, and acceptance coverage;
- task ids, dependency existence and cycles;
- file ownership and parallel-safety claims;
- exact interface and contract joins;
- whether each task is executable from real paths, APIs, and commands;
- material migration, recovery, external-side-effect, and verification gaps;
- referenced test coverage when a test design is actually supplied.

Do not require optional artifacts that the plan does not reference. Classify only problems that can
cause wrong implementation, unsafe execution, blocked work, or unverifiable acceptance as blocking.

Return:
Status: Clean | Issues Found
Issues:
- [location/category] problem -- execution impact -- smallest correction
Advisory:
- non-blocking suggestion
Evidence boundary:
- facts inspected and facts not verified
```
