| Problem | Error Code | Severity | Count Found |
|---------|-----------|----------|-------------|
| Non-numeric (INVALID) | AMT005 | CRITICAL | 1 |
| Malformed commas | AMT005 | CRITICAL | 6 |
| Zero amounts | AMT001 | CRITICAL | 3 |
| Negative amounts | AMT002 | CRITICAL | 11 |
| Exceeds maximum | AMT003 | HIGH | 2 |
| Too many decimals | AMT006 | MEDIUM | 3 |

Phase 1: Can I even read this? (format checks)

Phase 2: If yes, is the number valid? (numeric checks)

If Phase 1 fails, you collect those errors and stop. No point checking if garbage is negative.
