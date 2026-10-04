# Evidence — how to verify every claim (Phase 24)

> Portfolio rule: evidence over decoration. Every number in the README traces
> to one of the artifacts below. Nothing here is a mock or a mock-up.

## Regenerable in one command (do this first)

```bash
./scripts/run_tests.sh    # pytest — last verified: 50 passed / 0 failed
./scripts/run_postman.sh  # Newman — last verified: 61 requests, 231 assertions, 0 failed
```

CI artifacts (JUnit + HTML) upload on every GitHub Actions run for both
workflows — see the badges at the top of the README.

## Committed evidence in this folder

| File | What it proves | How it was produced |
| --- | --- | --- |
| `test-run-summary.md` | Exact passing counts for pytest + Newman | Fresh local runs, 2026-10-04 |
| `api-request-response-example.md` | Real lifecycle transcript (auth → create → round-trip → delete) | Live `requests` calls, 2026-10-04 |
| `schema-validation-example.md` | Real schema + real passing assertion | Checked-in schema + helper, quoted verbatim |

## Manual screenshots (captured by the maintainer, not faked by automation)

The three images below can only be produced by a human looking at the real
UIs, so they are **deliberately absent** rather than fabricated. To complete
the portfolio, capture and drop them here:

- `screenshots/postman-collection.png` — Postman app with folder `08` open,
  `E2E-001` chain visible, Tests tab showing green asserts.
- `screenshots/pytest-html-report.png` — `reports/pytest-report.html` open in
  a browser after `./scripts/run_tests.sh` (50 passed row visible).
- `screenshots/github-actions-run.png` — GitHub Actions page for this repo
  with both workflows green on the same commit.

If a screenshot is missing, the text evidence above still stands on its own —
a missing image is honest, a staged one is not.
