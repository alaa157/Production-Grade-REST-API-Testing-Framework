# Production-Grade API Testing Framework — RESTful Booker

> The Postman/Newman collection and Python API suite are implemented; GitHub
> Actions and later portfolio phases remain tracked in `implementaion_plane.md`.

Professional API QA automation project against the public
[RESTful Booker API](https://restful-booker.herokuapp.com/apidoc/index.html),
covering functional, negative, boundary, contract/schema, authentication, and
end-to-end workflow testing via **Postman/Newman** and **Python (pytest + requests + jsonschema)**,
executed in **GitHub Actions**.

## Technologies

- Postman + Newman (collection-driven API tests)
- Python 3.12+ / pytest / requests / jsonschema / pytest-html
- GitHub Actions (pytest + Newman on push / PR / manual dispatch)
- Markdown docs + Mermaid diagrams

## Planned coverage (implemented Phase 5+)

- Health check (`GET /ping`)
- Authentication (`POST /auth`)
- Booking CRUD: create, retrieve, update (PUT), partial update (PATCH), delete, listing/filtering
- Negative / boundary / schema-contract / data-integrity / end-to-end lifecycle workflow

Latest observed local run: 47 pytest tests passed; Newman completed 57 requests
and 215 assertions with no failures.

## Repository structure

```text
.
├── docs/                  # test-strategy, test-plan, scenarios, test-data, defect-summary, architecture
├── postman/
│   ├── collections/       # restful-booker-api.postman_collection.json (Phase 5+)
│   ├── environments/      # restful-booker.postman_environment.json (Phase 5+)
│   └── schemas/           # auth / booking JSON schemas (Phase 7+)
├── tests/
│   ├── api/               # pytest suites (Phase 12+)
│   └── schemas/           # JSON schemas for Python validation (Phase 15)
├── src/                   # api_client.py, config.py, test_data.py
├── scripts/               # run_tests.sh, run_postman.sh
├── .github/workflows/    # api-tests.yml, postman-tests.yml (Phase 18+)
├── reports/               # generated artifacts (git-ignored)
├── requirements.txt
├── pytest.ini
├── .env.example
└── LICENSE
```

## Setup

Requirements: Python 3.12+, Node.js 18+ (for Newman, Phase 11+), Git.

```bash
# 1. Clone
git clone <repo-url>
cd <repo>

# 2. Virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Dependencies
pip install -r requirements.txt

# 4. Configuration (no secrets committed — ever)
cp .env.example .env
# edit .env if needed; defaults target the public demo API
```

Config resolution (`src/config.py`, env vars with sane defaults):

| Variable       | Default                               |
| -------------- | ------------------------------------- |
| `API_BASE_URL` | `https://restful-booker.herokuapp.com` |
| `API_USERNAME` | `admin`                               |
| `API_PASSWORD` | `password123`                         |
| `API_TIMEOUT`  | `10` (seconds)                        |

`.env` is git-ignored. CI uses repository secrets / env vars instead.

## How to run

```bash
./scripts/run_tests.sh            # venv + pip install + pytest
./scripts/run_postman.sh          # Newman: collection + environment

# Manual equivalents
pytest -v
pytest -m "smoke or positive" -v
newman run postman/collections/restful-booker-api.postman_collection.json \
  -e postman/environments/restful-booker.postman_environment.json
```

Current verified state: pytest 49 passed / 0 skipped; Newman 57 requests /
215 assertions passed, with and without `-e`. Reports regenerate per run
(`reports/`, git-ignored) and upload as CI artifacts.

## Variables & chaining (Phase 8)

No booking ID is ever hardcoded (the only literal IDs in the collection are
the intentional negative probes `999999`, `9999999999`, `abc`). Runtime state
flows through variables, written to **both** collection and environment scope
so runs work with and without `-e`:

| Variable | Set by | Used by | Purpose |
| --- | --- | --- | --- |
| `baseUrl` | collection / environment | every request | host override per environment |
| `token` | auth requests (`AUTH-001`, E2E auth) | `Cookie: token={{token}}` writes | session credential |
| `bookingId` | create requests | read / update / delete / E2E | live entity under test |
| `firstName` / `lastName` | pre-request (`PM-<epoch>`) | create body + round-trip asserts | unique, cross-traffic-safe data |
| `e2eFirst` | E2E pre-request (`E2E-<epoch>`) | E2E create + read-back | isolated lifecycle identity |

Workflows (folder 08, `E2E-001` and `E2E-002`): token and Basic auth each run
auth → create → get → put → get → patch → get → delete → verify-gone, asserting
every hop; folders 02–06 chain the same way (auth → create → use → delete).

## Contract schemas (Phase 7)

`postman/schemas/` holds `auth-schema.json`, `booking-schema.json`
(`$ref`'d by), `booking-response-schema.json`, and `booking-list-schema.json`
(draft-07, strict on required properties/types/nesting). Key responses assert
them inline via `pm.response.to.have.jsonSchema()` against identical embedded
copies: token issue, booking creation, live retrieval, ID listing.

## CI

Two fail-closed GitHub Actions workflows (`.github/workflows/`), each green-gated
with JUnit + HTML artifacts uploaded on every run:

- `api-tests.yml` — Python 3.12, `pip install -r requirements.txt`, structure
  validation, `pytest --junitxml --html`, upload `pytest-reports`.
- `postman-tests.yml` — Node 20, `npm ci`, collection JSON validation,
  `npm run postman:ci` (CLI + JUnit), upload `newman-reports`.

Both trigger on `push`, `pull_request`, and `workflow_dispatch`. Any failed
test, failed install, or missing artifact fails its job — no
`continue-on-error` anywhere; only the upload steps use `if: always()`.

## Docs

- `docs/test-strategy.md`, `docs/test-plan.md` — Phase 2
- `docs/test-scenarios.md` — Phase 3 (target 40–60 meaningful scenarios)
- `docs/test-data.md` — Phase 4
- `docs/architecture.md` — Phase 25
- `docs/defect-summary.md` — Phase 21 (only genuine observed behavior, never fabricated)

## Status

- [x] Phases 0–4 — repository foundation, reconnaissance, test design, and test data
- [x] Phases 5–6 — Postman collection (8 folders) with per-request
  assertions (status, ≤2 s smoke guard, `Content-Type`, fields/types, values,
  chaining)
- [x] Phase 7 — JSON schemas (`postman/schemas/`, 4 contracts) asserted inline
  on key responses
- [x] Phase 8 — dual-scope variables + chained E2E lifecycle, no hardcoded IDs
- [x] Phase 9 — negative section consolidated in folder 07 (auth failures,
  invalid IDs, payload / header / boundary cases, all pinning observed
  contracts; truly-omitted `Content-Type` covered in pytest since Newman
  auto-adds the header); Newman green with and without `-e`
- [x] Phase 10 — E2E lifecycles over token auth (`E2E-001`) and Basic auth
  (`E2E-002`), every hop asserted
- [x] Phase 11 — Newman via pinned `npm ci` install (`package.json`),
  `docs/newman.md`, CLI + JUnit reporting, `--ci` wrapper mode
- [x] Phase 12 — pytest spine live: health, auth (incl. token-authorizes-write
  proof), create + round-trip, retrieval, listing/filtering, update, delete,
  negative, boundary, and schema-contract cases (49 passed / 0 skipped)
- [x] Phase 13 — `ApiClient` hardened: centralized base URL / JSON headers /
  timeout, all five methods + `head()`, `auth_headers()` cookie helper;
  shared session never carries credentials
- [x] Phase 14 — canonical fixtures (`api_client`, `base_url`, `auth_token`
  session-scoped; `valid_booking_payload`, `created_booking`
  function-scoped with best-effort cleanup); independence proven per-file,
  full-suite, and repeat runs
- [x] Phase 15 — Python Draft 7 schemas validated through a shared helper with
  useful violation paths and same-directory `$ref` support
- [x] Phase 16 — related auth, update, delete, and negative cases use pytest
  parameterization (missing-field floor, coercions, boundary values)
- [x] Phase 17 — configuration audit: env-var-only secrets, override/fallback
  verified, no committed credentials beyond public demo defaults
- [x] Phase 18 — `api-tests.yml` + `postman-tests.yml` (push/PR/dispatch,
  pinned Python 3.12 + Node 20, structure validation, artifact uploads)
- [x] Phase 19 — fail-closed quality gates (any test/install failure fails the
  job; JUnit published; collection + dependency checks up front)
- [x] Phase 20 — reporting proven locally exactly as CI runs it (JUnit totals /
  failures / time + self-contained HTML; artifacts cleaned, regenerable)
- [ ] Phase 21+ — see `implementaion_plane.md`
