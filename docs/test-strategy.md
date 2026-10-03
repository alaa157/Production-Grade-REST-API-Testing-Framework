# Test Strategy — RESTful Booker API Testing

> Phase 2. Ground truth: `docs/api-inventory.md` (live-verified 2026-10-03).
> Nothing below asserts behavior that was not observed; open questions are
> marked for Phase 9/12 probes instead of assumed.

## 1. Scope

In scope — the public RESTful Booker instance
(`https://restful-booker.herokuapp.com`):

- Health check (`GET/HEAD /ping`)
- Authentication (`POST /auth`: valid, invalid, missing/empty credentials;
  token and Basic-auth usage on writes)
- Booking lifecycle: create, retrieve, full/partial update, delete,
  listing + filtering (`firstname`, `lastname`, `checkin`, `checkout`)
- Cross-cutting: positive, negative, boundary, contract/schema (status,
  headers, `Content-Type`, JSON shape), data integrity (request↔response
  round-trip), one end-to-end lifecycle workflow
- Two automation surfaces over the same scenarios: Postman/Newman collection
  and Python (`pytest` + `requests` + `jsonschema`), both gated in CI

## 2. Out of scope

- Performance/load/stress testing (2 s client-side response-time guards in
  Postman are smoke thresholds only, not SLAs — no k6/JMeter in this repo)
- Security penetration testing beyond auth-contract checks (no ZAP/SAST;
  auth tests assert contract, not exploitability)
- XML and URL-encoded request bodies (API supports them; this project pins
  JSON and treats XML only as a response-negotiation risk, per inventory §4)
- UI, mobile, and downstream consumer systems (no frontend exists)
- Availability/SLO monitoring of the public demo host

## 3. Test objectives

1. Prove each endpoint honors its observed contract (status + headers +
   body shape), with emphasis on the six documented-vs-observed discrepancies
   in `api-inventory.md` §2 (ping 201, delete 201, auth-failure 200, malformed
   ID 404, re-delete 405, missing-field 500).
2. Prove valid CRUD workflows preserve data end to end (create → read →
   update → patch → delete → verify-gone, with payload comparison at each hop).
3. Characterize the API's lenient validation honestly: wrong-type numerics,
   string booleans, bad/inverted dates, empty/negative/zero prices, unknown
   fields and `null` optionals are all accepted with coercion (inventory §7).
   Tests assert the *actual* contract and flag — not silently pass — the
   coercion risks for the Phase 21 defect review.
4. Deliver the same coverage in two runnable forms (Postman + pytest) with a
   traceability matrix linking requirement → scenario → Postman test → pytest
   → CI (Phase 22).

## 4. Test levels & types

- **Levels:** API component tests (per endpoint) + one integration-style
  workflow test (booking lifecycle across endpoints). No unit tests — the
  server is third-party; no system/E2E UI layer exists.
- **Types and where they run:**

| Type | Meaning here | Postman | pytest |
| --- | --- | --- | --- |
| Smoke | Ping + auth + create + get reachability | ✅ folder 01–04 happy paths | ✅ `-m smoke` |
| Functional / positive | Valid requests, expected successes | ✅ | ✅ `-m positive` |
| Negative | Invalid/missing/malformed inputs, auth failures | ✅ folder 07 | ✅ `-m negative` |
| Boundary | Empty, zero, negative, huge, inverted/bad dates | ✅ sampled | ✅ parametrized |
| Contract / schema | Status, headers, `Content-Type`, JSON schema | ✅ per-request + schema asserts | ✅ `jsonschema` |
| Authentication | Token lifecycle, Cookie vs Basic, 403 paths | ✅ folder 02 + 07 | ✅ `-m auth` |
| Regression | Full collection + full pytest suite on every push/PR | ✅ CI | ✅ CI |
| Workflow (e2e) | Stateful lifecycle with chained IDs/tokens | ✅ folder 08 | ✅ `-m e2e` |

## 5. Test approach

1. **Reconnaissance first** (done, Phase 1): docs → live probes → inventory.
   Assertions are written against observed behavior; every discrepancy is a
   scenario, not an assumption.
2. **Scenario design before automation** (Phase 3): 40–60 meaningful,
   ID-addressed scenarios (`HLTH-`, `AUTH-`, `BOOK-`, `FILT-`, `NEG-`,
   `BND-`, `CON-`, `E2E-`). No filler variations — each scenario names the
   risk it covers.
3. **Dual implementation, single contract** (Phases 5–16): Postman folders
   mirror pytest modules; JSON schemas are conceptually shared
   (`postman/schemas/` ↔ `tests/schemas/`).
4. **Independent tests by default;** shared state only inside the explicit
   lifecycle workflow, which creates its own booking, chains the live ID and
   token via variables/fixtures, and cleans up (delete + verify-gone).
5. **Weak assertions are banned:** every test asserts exact status codes,
   required fields/types, and — for create/update — round-tripped values
   (Rule 6 of the implementation plan). `assert response.status_code`-style
   existence checks are a review failure.
6. **Failures are evidence:** unexpected API behavior is captured (request,
   expected, actual, timestamp) and routed to the defect review — never
   caught-and-swallowed to keep CI green (Rule 9).

## 6. Environment & test data

- **Environment:** public demo host; no staging/prod split. Base URL, username,
  password, timeout come from env vars (`.env.example` defaults); CI injects
  them as secrets/env. Recorded baseline: ~0.3 s/call, ~968 bookings listed
  on 2026-10-03 — volatile, never asserted.
- **Data strategy (detail: `docs/test-data.md`, Phase 4):** tests create their
  own bookings with unique `firstname` values per run (cross-traffic safe);
  no hardcoded IDs; list-count assertions are shape-only (`array of
  {bookingid}`), never exact totals. Invalid/boundary payloads derive from the
  nine leniency probes in inventory §7–§8.
- **Reset awareness:** the host reportedly resets to seed data periodically;
  tests must not depend on pre-existing IDs (notably `/booking/1` was 404 on
  2026-10-03) and must tolerate concurrent modification.

## 7. Tools

| Tool | Role |
| --- | --- |
| Postman | Collection authoring, folders 01–08, per-request asserts, variables/chaining |
| Newman + JUnit/HTML reporters | CLI + CI execution of the collection |
| Python 3.12+, `requests` | `src/api_client.py` session wrapper (base URL, timeout, token cookie) |
| `pytest` + markers (`smoke`, `positive`, `negative`, `boundary`, `contract`, `auth`, `e2e`) | Selective, independent test execution |
| `jsonschema` | Response-contract validation, shared conceptually with Postman schemas |
| `pytest-html` (+ JUnit XML in CI) | Human- and machine-readable reports |
| GitHub Actions | `api-tests.yml` + `postman-tests.yml` on push/PR/dispatch; artifacts uploaded |
| Markdown + Mermaid | This documentation set |

## 8. Risk areas (ranked, from inventory evidence)

1. **Silent coercion accepted as success** — wrong-type price → `null`,
   string boolean → `true`, bad date → `"0NaN-aN-aN"`, all HTTP 200. Highest
   defect-density area; drives most `NEG-`/`BND-` scenarios.
2. **Auth-failure contract** — invalid credentials return 200 + reason string.
   Clients keying on status alone will mis-handle failures.
3. **Destructive-operation statuses** — DELETE 201/`Created`, re-delete 405,
   unauthenticated writes 403 (not 401). Consumers and tests must match.
4. **Missing-field 500** — absent `firstname` crashes instead of 400-validating.
5. **Volatile shared data** — counts/IDs shift underfoot; hardcoded-ID and
   exact-count assertions will flake.
6. **Filter semantics unverified** — date-window and combined filters returned
   `[]` in probes; AND/OR and inclusivity unknown.
7. **Content negotiation** — `Accept: application/xml` flips representation;
   clients not pinning `Accept: application/json` get a different contract.

## 9. Entry criteria

- Phase 0 skeleton present; `api-inventory.md` verified (done).
- Public host reachable (`GET /ping` responds; any 2xx/201 counts — exact
  status asserted per inventory, not assumed).
- `pip install -r requirements.txt` succeeds; `pytest --collect-only` clean;
  Newman install documented for Phase 11.

## 10. Exit criteria (link to Definition of Done, Phase 30)

- All P0 scenarios (happy paths + auth enforcement + lifecycle) pass in
  **both** Postman/Newman and pytest, locally and in CI.
- No P1 scenario fails silently: every failure produces request/expected/
  actual evidence and a defect-review disposition (genuine discrepancy vs
  accepted contract).
- Schemas validate the four contracts (auth, booking, create-response,
  list); CI publishes JUnit + HTML artifacts.
- Docs complete and consistent: strategy ⇆ plan ⇆ scenarios ⇆ test-data ⇆
  traceability ⇆ defect-summary ⇆ README, with zero fabricated metrics.

## 11. Defect strategy

- Any observed behavior contradicting the reasonable API contract is logged
  with: Defect ID, title, severity/priority, environment, endpoint/method,
  preconditions, repro steps, request, expected, actual, evidence (verbatim
  body + timestamp), impact, status (`docs/defect-summary.md`, Phase 21).
- No invented defects: if a quirk is judged "accepted leniency" rather than a
  bug, it is recorded as a risk with rationale, not a defect.
- Severity guide: crash/500 and data-corruption-shaped coercion (bad-date
  artifact) ≥ major; misleading statuses (auth 200, delete 201) = minor–major
  by consumer impact; XML/405 nuances = minor.

## 12. Automation strategy

- **Postman first** (Phases 5–10): folders 01–08, variables
  (`baseUrl`, `token`, `bookingId`), chained lifecycle, per-request asserts
  (status, ≤2 s response-time smoke guard, `Content-Type`, fields/types,
  round-tripped values), schema checks, dedicated negative folder.
- **Python second** (Phases 12–16): thin `ApiClient`, fixtures
  (`api_client`, `auth_token`, `created_booking`, `valid_booking_payload`),
  parametrized negative/boundary cases, `jsonschema` on the same contracts.
- **CI last** (Phases 18–19): two workflows with hard gates — any pytest or
  Newman failure (including schema violations) fails the run; JUnit/HTML
  artifacts uploaded; failure simulation (Phase 27) proves the gate is real.
