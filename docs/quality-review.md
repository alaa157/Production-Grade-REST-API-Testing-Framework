# Test Quality Review (Phase 26)

> Performed 2026-10-04 against the working tree, five-axis style
> (correctness, readability, architecture, security, performance omitted —
> no hot paths in a test suite — plus repo and CI). Every verdict below names
> its check; nothing is rubber-stamped.

## Test quality — PASS

| Check (plan §26) | Result |
| --- | --- |
| Independent? | **Yes.** `test_booking_negative.py` alone: 23 passed; `test_auth.py` alone: 5 passed (2026-10-04). Function-scoped `created_booking` gives every test fresh data; session fixtures (`api_client`, `auth_token`) are stateless. Only intentional statefulness is the E2E chain (folder 08) and hop-by-hop pytest equivalents. |
| Meaningful assertions? | **Yes.** Grep: zero bare `assert response.status_code` and zero vacuous asserts. Status-only checks are limited to cases whose stated contract is the code; malformed-ID and re-delete checks also pin the observed body and `text/plain` content type. Other responses assert meaningful shapes or values (`{"reason": ...}`, round-trip equality, `text == "Forbidden"`). |
| Negative cases useful? | **Yes.** 24 scenarios: 4 auth failures, 5 missing-field `500`s, coercion trio, malformed JSON, header cases, invalid IDs (including `9999999999`), re-delete — each asserting observed behavior with a contract-opinion note, never a weakened assertion. |
| Edge cases included? | **Yes.** 7 BND scenarios (0/−50/huge price, inverted dates, 500-char name, huge ID, minimal-payload floor). |
| Status codes validated? | **Yes.** All 10 endpoint×method combos pin observed codes incl. 201-ping, 201-delete, 403/404/405 paths. |
| Bodies validated? | **Yes.** Round-trip equality on create/update/patch; echo field-for-field; error bodies (`Created`, `Not Found`, `Forbidden`, `Bad credentials`). |
| Schemas meaningful? | **Yes.** 4 strict Draft-7 contracts (required + types + `additionalProperties: false` where fitting), asserted in both harnesses; failures print `<path>: <message>`. |

## Code quality — PASS (2 noted nuances, both justified)

| Check | Result |
| --- | --- |
| Readable? | **Yes.** Small modules, behavior-naming (`test_redelete_returns_405`), docstrings state the scenario ID. |
| Duplication minimized? | **Yes.** One canonical `auth_headers()` helper; one `validate_schema()`; payload factories in `src/test_data.py`. No bespoke near-duplicates found. |
| Fixtures appropriate? | **Yes.** Session scope for stateless shared state, function scope for entity data, best-effort cleanup that warns instead of failing passed tests. |
| Functions small and focused? | **Yes.** `ApiClient` is 67 lines, one verb per method; no abstraction beyond need (Rule 5). |
| Config externalized? | **Yes.** All four knobs via env vars with public-demo defaults; `.env` git-ignored, absent from git history. Nuance: `config.py` contains the literal `password123` default — accepted: it is the API's published demo credential (also in `.env.example`), overridable per variable, and the secrets scan confirms it is the only such literal. |
| Exceptions handled sensibly? | **Yes.** Single broad `except Exception` lives only in fixture *cleanup* (`conftest.py:32`), where it converts teardown noise into `RuntimeWarning` — it cannot mask a test outcome, and `test_fixture_cleanup.py` meta-tests pin the warn behavior. No `except: pass`, no swallowed failures (Rule 9). |

## Repository quality — PASS

| Check | Result |
| --- | --- |
| README complete? | **Yes.** Setup, run commands, config table, chaining, schemas, CI, observed coverage, ordered doc guide, honesty note. Badges: 2 CI only, by policy. |
| Setup reproducible? | **Yes.** `run_tests.sh` / `run_postman.sh` from clone; pinned `newman` via `package-lock.json`; Python floor in `requirements.txt`. |
| Secrets excluded? | **Yes.** `git ls-files` shows no `.env`; scan finds only the demo default. |
| Reports understandable? | **Yes.** JUnit totals + self-contained HTML; `docs/evidence/test-run-summary.md` shows what good looks like. |
| Folder structure logical? | **Yes.** docs / postman / tests+src / .github / scripts / reports separation per plan §5. |

## CI quality — PASS

| Check | Result |
| --- | --- |
| Works from clean environment? | **Yes.** Both workflows start at `checkout` + full install (`pip install -r requirements.txt`, `npm ci`) — no cached state assumed. |
| Failure fails the workflow? | **Structurally yes; red Actions run not observed.** Grep: zero `continue-on-error` in `.github/`; test steps exit non-zero on any failure; only artifact uploads use `if: always()`. Local pytest/Newman non-zero exits are documented in Phase 27. An actual failing GitHub Actions run remains unverified. |
| Artifacts uploaded? | **Yes.** `pytest-reports` (JUnit + HTML) and `newman-reports` (JUnit) on every run, pass or fail. |
| Failures reproducible by another developer? | **Yes.** JUnit names `file::function[param]`; schema failures print violation paths; defect entries give repro steps. |

## Verdict

**Approve with one verification limitation.** The demo-credential default and
best-effort cleanup exception are justified. Both workflows have successful
green runs and fail-closed configuration, but a deliberately failing GitHub
Actions run has not been observed; Phase 27 records that as an open evidence
item rather than treating local exit-code checks as proof of hosted CI
behavior. The refreshed Phase 28 audit records the current follow-up items.
