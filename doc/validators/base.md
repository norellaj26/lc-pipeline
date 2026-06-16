The Concept First

Think about your validators — Amount, LEI, SWIFT, Date, Party. They all do different checks, but they all follow the same workflow:

1. Start fresh (no leftover errors)

2. Run checks (different for each validator)

3. Collect errors along the way

4. Return all errors found

Steps 1, 3, and 4 are identical for every validator. Only step 2 changes. So why would you rewrite the same logic six times?

That's what BaseValidator solves. It says:


"I handle the workflow. You — the child class — just tell me what your specific checks are."

This is called the Template Method Pattern. The base class defines the template (the workflow), and child classes fill in the method (the specific checks).

| Part | Restaurant | Your Code |
|------|-----------|-----------|
| `validate` | The waiter (same process every table) | Reset, run, return |
| `_validate` | The chef (different dish each time) | Specific checks |
| `**context` | Special requests ("no onions") | Extra info needed |

Every validator you build from now on just needs to:

Extend BaseValidator

Implement _validate

Call self._add_error when something's wrong