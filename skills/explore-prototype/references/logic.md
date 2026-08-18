# Logic exploration

Build one self-contained HTML file that lets a non-developer drive a state model and see the complete
relevant state after every action.

## Shape

1. Show the exact question and why it matters.
2. Isolate the logic from the page as a pure reducer, explicit state machine, pure functions, or a
   small state-owning module. The logic must not reference DOM APIs.
3. Render readable domain fields rather than only raw JSON.
4. Provide free-play actions and guided scenarios for the happy path, at least one awkward edge case,
   and an illegal or rejected action.
5. Reset every guided scenario to a known initial state so it is repeatable.

Keep the shell framework-free, dependency-free, and usable by double-clicking the file. Use restrained
styling and domain language. The point is to expose a model error, not to demonstrate visual polish.

## Boundaries

- Keep state in memory unless persistence is the question.
- Do not add production tests to the prototype itself; verification is manual scenario execution.
- Do not generalize for hypothetical future cases.
- Do not ship the HTML shell. Reimplement a validated logic decision with normal production tests.
