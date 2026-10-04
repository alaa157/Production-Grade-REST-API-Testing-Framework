# Failure Simulation (Phase 27)

> One controlled break per harness, observed locally on 2026-10-04. CI
> enforcement is checked from the workflow configuration rather than by
> pushing a deliberately failing commit.

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

## CI configuration check

```text
Wrong assertion
  → pytest exit 1 / newman exit 1 (observed above)
  → api-tests.yml / postman-tests.yml test step fails
  → artifact upload is attempted (if: always())
```

Both workflow test steps run these commands without `continue-on-error`;
artifact uploads use `if: always()` so report collection is attempted on
failure. Successful hosted runs are available in GitHub Actions. Current
local green baseline: 50 pytest tests and 231 Newman assertions
(`docs/evidence/test-run-summary.md`).
