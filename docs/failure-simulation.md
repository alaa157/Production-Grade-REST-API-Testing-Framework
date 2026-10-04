# Failure Simulation (Phase 27)

> One controlled break per harness, observed 2026-10-04. No red commit was
> pushed — CI behavior follows by construction (both workflows run the same
> commands with no `continue-on-error`; see `docs/quality-review.md`).

## pytest

- **Break:** `tests/api/test_health.py` — ping assertion flipped `201 → 200`.
- **Observed:** `1 failed, 1 passed`, exit code **1**.
- **Restore:** `git checkout -- tests/api/test_health.py` → `2 passed`.

## Newman

- **Break:** throwaway copy of the collection (`/tmp`, real files untouched)
  — `HealthCheck - GET ping` assertion flipped `status(201) → status(200)`.
- **Observed:** `215 assertions, 1 failed`, exit code **1**. Copy deleted.
- **Restore:** nothing to restore — the committed collection was never
  modified (`git status` clean on `postman/`).

## Chain (evidence-backed, not asserted)

```text
Wrong assertion
  → pytest exit 1 / newman exit 1 (observed above)
  → api-tests.yml / postman-tests.yml step fails (no continue-on-error anywhere)
  → job fails, artifacts still upload (if: always())
```

The gate is real in both directions: correct code greens (49 passed / 215
assertions, `docs/evidence/test-run-summary.md`), broken code reds.
