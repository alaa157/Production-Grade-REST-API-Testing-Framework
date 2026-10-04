# Test-run summary (observed 2026-10-04)

## pytest

```text
tests/api/test_booking_get.py .....                                      [ 32%]
tests/api/test_booking_negative.py ......................                [ 77%]
tests/api/test_booking_update.py ......                                  [ 89%]
tests/api/test_health.py ..                                              [ 93%]
tests/api/test_request_headers.py .                                      [ 95%]
tests/test_fixture_cleanup.py ..                                         [100%]

============================= 49 passed in 11.31s ==============================
```

47 scenario tests + 2 suite-hygiene meta-tests
(`test_fixture_cleanup.py`, which guard the fixtures themselves and trace to
no scenario by design — see `docs/traceability-matrix.md`).

## Newman

```text
│                requests │                57 │                 0 │
│              assertions │               215 │                 0 │
```

57 requests across 8 folders, 215 assertions, 0 failures — collection plus
environment (`-e`). The bare run (no `-e`, collection-scope variables only)
is also green by design; CI runs the `-e` form via `npm run postman:ci`
(CLI + JUnit to `reports/newman-results.xml`).

## How to reproduce

```bash
pytest -q
npx newman run postman/collections/restful-booker-api.postman_collection.json \
  -e postman/environments/restful-booker.postman_environment.json
```
