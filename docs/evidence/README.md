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

## Evidence format

The portfolio uses reproducible text transcripts, checked-in schemas, Mermaid
diagrams, and CI-generated JUnit/HTML reports. GUI screenshots are
intentionally outside the deliverables; no image is needed to reproduce or
verify the documented results.
