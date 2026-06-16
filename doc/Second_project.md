TODO: Dataset v3 should include:
- 10-20 CONFIRMED LCs with confirming bank data
- 30-40 LCs with additional_conditions filled

| Scenario | In Your Data? | Rule |
|----------|---------------|------|
| Blank + no bank | NO | Would be LC008 MEDIUM |
| Blank + has bank | NO | Would be LC008 CRITICAL |
| Invalid value (MAYBE) | YES (1) | LC008 HIGH |

Composition (ErrorCollector) | Multiple unrelated classes need error tracking | Overkill for now |