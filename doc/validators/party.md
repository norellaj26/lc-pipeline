| Problem | Error Code | Severity | Count |
|---------|-----------|----------|-------|
| Missing applicant_name | PTY001 | CRITICAL | 1 |
| Name too short ("A") | PTY002 | HIGH | 3 |
| Missing applicant_address | PTY004 | HIGH | 2 |
| Invalid country code (XX) | PTY005 | HIGH | 1 |

| Level | What | Who Does It | When |
|-------|------|-------------|------|
| KYC (Know Your Customer) | Full address verification | Compliance team | Account opening |
| LC Processing | Address is present + reasonable | Trade finance ops | LC issuance |
| Sanctions Screening | Country check | Automated system | Every transaction |

Address accuracy → NOT our job. That was done during KYC when the client opened their account. By the time a transaction reaches our pipeline, the bank already verified who this company is.

| Check | Catches | Python Type |
|-------|---------|-------------|
| `is None` | `None` | NoneType |
| `pd.isna()` | `None` + `float('nan')` + `pd.NaT` | multiple |