# Failure Simulation (Phase 27)

> One controlled break per harness, observed locally on 2026-10-04. No
> deliberately failing GitHub Actions run has been observed; local exit-code
> checks do not prove hosted job behavior.

## pytest

- **Break:** `tests/api/test_health.py` — ping assertion flipped `201 → 200`.
- **Observed:** `1 failed, 1 passed`, exit code **1**.
- **Restore:** `git checkout -- tests/api/test_health.py` → `2 passed`.

## Newman

- **Break:** throwaway copy of the collection (`/tmp`, real files untouched)
  — `HealthCheck - GET ping` assertion flipped `status(201) → status(200)`.
- **Observed:** At the time of this simulation, `215 assertions, 1 failed`,
  exit code **1**. The collection has since gained four persisted-state GET
  checks; the current green baseline is 231 assertions. Copy deleted.
- **Restore:** nothing to restore — the committed collection was never
  modified (`git status` clean on `postman/`).

## CI configuration evidence (not an observed red Actions run)

```text
Wrong assertion
  → pytest exit 1 / newman exit 1 (observed above)
  → api-tests.yml / postman-tests.yml step fails (no continue-on-error anywhere)
  → job fails, artifacts still upload (if: always())
```

The workflow files structurally propagate non-zero test exits and attempt
artifact uploads with `if: always()`. Successful hosted runs are recorded in
GitHub Actions; the hosted red path remains **unverified**. Current local
green baseline: 50 pytest tests and 231 Newman assertions
(`docs/evidence/test-run-summary.md`).
