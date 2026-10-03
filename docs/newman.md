# Newman CLI Execution (Phase 11)

> Collection: `postman/collections/restful-booker-api.postman_collection.json`
> (8 folders, 57 requests, 215 assertions).
> Environment: `postman/environments/restful-booker.postman_environment.json`.
>
> Layout note (review consolidation, Phase 9): folders 02–04 are happy-path
> only (auth issuance, creation, reads/filters); every negative lives in
> 07 — auth failures, invalid IDs, payload/header/boundary coercions.

## 1. Install

Pinned local install (recommended — matches CI):

```bash
npm ci            # installs newman ^6.2.2 from package-lock.json
npx newman --version
```

Or global: `npm install -g newman`. Either path works; `scripts/run_postman.sh`
prefers a local binary when present and falls back to `newman` on `PATH`.

## 2. Run

```bash
# Full suite with environment (215 assertions)
npm run postman
# equivalent:
newman run postman/collections/restful-booker-api.postman_collection.json \
  -e postman/environments/restful-booker.postman_environment.json

# Bare run — collection variables carry defaults, also green
npm run postman:bare

# CI shape: CLI + JUnit XML for gates/artifacts
npm run postman:ci   # writes reports/newman-results.xml
```

`scripts/run_postman.sh` wraps the same commands (uses `-e` when the
environment file exists, otherwise the bare collection run).

## 3. Reports

| Reporter | Command | Use |
| --- | --- | --- |
| `cli` | default | human-readable run output, exit code gates CI |
| `junit` | `-r cli,junit --reporter-junit-export reports/newman-results.xml` | CI artifacts, failure triage per request |

JUnit output is one `<testsuite>` per request (57 suites, all with
`failures="0"`). HTML is intentionally not bundled: JUnit XML is the
CI-preferred format per the plan, and `pytest-html` covers the human-readable
side for Python. (`newman-reporter-htmlextra` can be added later without
changing the collection.)

`reports/` is git-ignored (`reports/newman-results.xml` verified locally then
removed); CI re-generates and uploads it on every run (Phase 18).

## 4. Exit codes & gates

Newman exits non-zero on any failed assertion, which fails the wrapper
script (`set -euo pipefail`) and therefore the CI job. Verified behavior, not
assumed — Phase 27 failure simulation re-proves it.

## 5. Operational notes (observed)

- **Cold start:** the first request in a run can take ~5 s (Heroku dyno wake;
  observed once at 5.3 s). Only the `GET /ping` guard is cold-start tolerant
  (10 s); all other guards stay at 2 s. A repeat failure on ping is signal;
  a lone slow first ping is infrastructure.
- **Shared data:** the suite creates its own bookings with unique names and
  chains live IDs — never reorders, never hardcodes. Reruns are safe;
  leftovers from killed runs are harmless (server resets periodically).
- **Variable scopes:** test scripts write `token`/`bookingId`/names to both
  collection and environment scopes because environment values shadow
  collection values at runtime. If chaining ever breaks after an edit, check
  scope shadowing first (this bit us once in Phase 6).

## 6. Evidence

2026-10-03, local + global newman 6.2.2: **57/57 requests, 215/215 assertions,
0 failed**, with `-e` and bare. JUnit export verified (57 suites, 0 failures).
