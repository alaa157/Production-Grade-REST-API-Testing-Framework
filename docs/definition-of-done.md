# Definition of Done (Phase 30)

> Verdict per checkbox, 2026-10-04. Checked items were verified against the
> repository, local test runs, or recorded CI evidence. Evidence/screenshots
> are partial, and hosted failure propagation is structurally configured but
> has not been proven by a deliberately failing GitHub Actions run.

## API Coverage

- [x] Health endpoint tested (`HLTH-001…003`, both harnesses)
- [x] Authentication tested (`AUTH-001…009`, token + Basic)
- [x] Create booking tested (`BOOK-001/002`)
- [x] Retrieve booking tested (`BOOK-003/004/005`)
- [x] Update booking tested (`BOOK-006/007`)
- [x] Partial update tested (`BOOK-008/009`)
- [x] Delete booking tested (`BOOK-010/011/012`)
- [x] Booking listing/filtering tested (`FILT-001…005` — `002` in both
  harnesses; `003/004/005` Postman-covered with stated pytest gaps, see
  traceability matrix)

## Functional Testing

- [x] Positive cases implemented
- [x] Negative cases implemented (24 scenarios)
- [x] Boundary cases implemented (7 scenarios)
- [x] Data integrity verified (create round-trip, PUT/PATCH persistence, and
  delete verify-gone checks; pytest flows remain independent)
- [x] End-to-end workflow implemented (token + Basic lifecycles; GET verifies
  persisted state after PUT and PATCH)

## Validation

- [x] Status codes validated (10 endpoint×method combos, observed codes)
- [x] Headers validated (`Content-Type` families, auth cookie, `Accept` pin)
- [x] Response content validated (echo, error bodies, verify-gone)
- [x] JSON schema validation implemented (4 contracts × 2 harnesses)
- [x] Data types validated (incl. coercion traps pinned verbatim)
- [x] Required properties validated (strict schemas + missing-field `500`s)

## Postman

- [x] Professional collection structure (8 folders, 61 requests)
- [x] Environment variables (dual-scope, runs with and without `-e`)
- [x] Dynamic variables (epoch-unique names, no hardcoded IDs)
- [x] Request chaining (auth → create → use → delete; folder 08 lifecycles)
- [x] Assertions (231, status + latency guard + CT + fields/types + values)
- [x] Negative tests (folder 07, 20 requests)
- [x] Schema validation (inline `jsonSchema` on key responses)

## Newman

- [x] Collection runs from CLI (`run_postman.sh`, bare and `-e` forms)
- [x] Environment supported
- [x] Local CI-compatible exit codes (Phase 27: pytest/Newman failure →
  exit 1, observed); hosted red run not yet observed
- [x] Reports generated (CLI + JUnit via `postman:ci`)

## Python

- [x] pytest implemented (50 passed)
- [x] requests implemented (via session-based `ApiClient`)
- [x] reusable API client (`src/api_client.py`, 67 lines)
- [x] fixtures (session + function scopes, best-effort cleanup)
- [x] parameterized tests (auth failures, missing fields, prices, IDs)
- [x] schema validation (shared helper, `<path>: <message>` failures)
- [x] negative tests (23 in `test_booking_negative.py` + auth/header files)

## CI/CD

- [x] GitHub Actions configured (2 workflows, push/PR/dispatch)
- [x] pytest runs automatically (`api-tests.yml`)
- [x] Newman runs automatically (`postman-tests.yml`)
- [x] Workflows structurally fail jobs for non-zero test exits
  (`continue-on-error` absent); local red path is proven
- [ ] Hosted red path — a deliberately failing GitHub Actions run has not
  been observed (`docs/failure-simulation.md`)
- [x] reports/artifacts available (JUnit + HTML uploaded every run)

## Documentation

- [x] Test strategy · [x] Test plan · [x] Test scenarios · [x] API inventory
- [x] Test data strategy · [x] Traceability matrix · [x] Defect analysis
- [x] README

## Portfolio Quality

- [x] Professional repository structure
- [x] Clear README (30-second test passed in Phase 28 audit)
- [x] Architecture diagram (system + lifecycle + workflow, Mermaid)
- [x] CI badge (well-formed; goes green on first post-push run)
- [ ] Evidence/screenshots — **partial:** verbatim text evidence committed
  (`docs/evidence/`); 3 GUI screenshots pending manual capture (shot list
  in `docs/evidence/README.md`)
- [x] No secrets (scan clean; `.env` never in git)
- [x] No fake defects (7 observed findings, methodology noted)
- [x] No fabricated metrics (all counts from 2026-10-04 runs)
- [x] Reproducible setup (run scripts, npm lockfile, and environment defaults)

**Core deliverables are present.** Final completion evidence still needs
three manually captured GUI screenshots and an observed failing GitHub
Actions run; neither is claimed from inference or local simulation.
