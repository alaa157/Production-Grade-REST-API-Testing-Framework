# API Inventory — RESTful Booker (verified live, 2026-10-03)

> Phase 1 reconnaissance. Every "Observed" value below was produced by real
> requests against `https://restful-booker.herokuapp.com` on 2026-10-03
> (timings ~0.3 s per call, sample only — not a performance claim).
> Documentation references: public apidoc + Postman network docs for
> Restful-Booker (token via `POST /auth`, CRUD on `/booking`).
> The API is intentionally bug-laden and resets periodically; shared public
> data is volatile (see §7).

## 1. Base URL & conventions

- Base URL: `https://restful-booker.herokuapp.com`
- Data format: JSON (default). XML is also negotiated via `Accept` (observed:
  `Accept: application/xml` on `GET /booking/{id}` returns XML markup with
  `Content-Type: text/html; charset=utf-8`).
- Authenticated writes accept **either** `Cookie: token=<token>` **or**
  `Authorization: Basic <base64(admin:password123)>` (both verified working
  for `PUT`; token-cookie verified for `PUT`/`PATCH`/`DELETE`).
- Demo credentials: `admin` / `password123` (public demo account, also the
  defaults in `.env.example`).

## 2. Endpoint inventory (documented vs observed)

| Endpoint | Method | Purpose | Auth | Documented status | Observed status (2026-10-03) |
| --- | --- | --- | --- | --- | --- |
| `/ping` | GET | Health check | No | 200 (assumed) | **201**, `text/plain`, body `Created` |
| `/ping` | HEAD | Health check (headers only) | No | — | **201**, empty body |
| `/auth` | POST | Generate token | No | 200 | 200, `{"token":"<hex>"}` |
| `/booking` | GET | List booking IDs (optional filters) | No | 200 | 200, `[{"bookingid":n}, …]` |
| `/booking` | POST | Create booking | No | 200 | 200, `{"bookingid":n,"booking":{…}}` |
| `/booking` | OPTIONS | CORS / allowed methods | No | — | 200, `Allow: GET, HEAD, POST`, body `GET, HEAD, POST` |
| `/booking/{id}` | GET | Retrieve booking | No | 200 | 200 if exists; **404** `Not Found` (`text/plain`) if missing/malformed ID |
| `/booking/{id}` | PUT | Full replace | Yes | 200 | 200 with auth; **403** `Forbidden` without/invalid auth |
| `/booking/{id}` | PATCH | Partial update | Yes | 200 | 200 with auth; **403** without/invalid auth |
| `/booking/{id}` | DELETE | Delete booking | Yes | 201 | **201** `Created` (`text/plain`) with auth; **403** without auth; **405** re-deleting same ID |

Key discrepancies vs naive expectations (tracked as risk areas, formal
verdict in `docs/defect-summary.md`, Phase 21):

1. `GET /ping` returns **201**, not 200.
2. `DELETE` success returns **201** with body `Created` (not 200/204 + JSON).
3. Invalid credentials on `POST /auth` return **200** with
   `{"reason":"Bad credentials"}` — not 401/403. Missing/empty body behaves
   the same (verified `{}` → same 200 + reason).
4. `GET /booking/abc` (malformed ID) returns **404**, not 400.
5. Re-`DELETE` of the same ID returns **405 Method Not Allowed**, not 404.
6. `POST /booking` without `firstname` returns **500 Internal Server Error**,
   not 400 (verified 2026-10-03).

## 3. Authentication

- Request: `POST /auth`, `Content-Type: application/json`,
  body `{"username":"admin","password":"password123"}`.
- Success (valid): `200`, `application/json`, `{"token":"<16-hex>"}`.
  Token observed single-use-session style; each login returns a fresh value.
- Failure (wrong password, unknown user, `{}` body): `200`,
  `{"reason":"Bad credentials"}`. No `token` field. Tests must assert on the
  body, not the status code.
- Usage: `Cookie: token=<token>` header on `PUT`/`PATCH`/`DELETE`, or
  `Authorization: Basic <base64>` (both verified for `PUT`).
- Missing/invalid token on writes: `403 Forbidden` (`text/plain`).

## 4. Request headers

| Header | Required | Notes |
| --- | --- | --- |
| `Content-Type: application/json` | Yes for `POST /auth`, `POST/PUT/PATCH /booking` | Verified: malformed JSON → `400 Bad Request` (`text/plain`). True header-omission tolerance not yet isolated (client libs auto-set it) — re-verify in Phase 9 with raw socket/curl. |
| `Accept: application/json` | Recommended | Default responses are JSON; `Accept: application/xml` switches `GET /booking/{id}` to XML — contract tests must pin `Accept`. |
| `Cookie: token=…` | Yes for writes (or Basic alternative) | See §3. |
| `Authorization: Basic …` | Alternative for writes | Verified working for `PUT` on a live booking. |

## 5. Booking resource shapes

Create (`POST /booking`) request — all fields observed accepted as below:

```json
{
  "firstname": "PhaseOne",
  "lastname": "Verify",
  "totalprice": 150,
  "depositpaid": true,
  "bookingdates": { "checkin": "2026-01-01", "checkout": "2026-01-05" },
  "additionalneeds": "Breakfast"
}
```

Create response (`200`, JSON):

```json
{
  "bookingid": 1198,
  "booking": {
    "firstname": "PhaseOne",
    "lastname": "Verify",
    "totalprice": 150,
    "depositpaid": true,
    "bookingdates": { "checkin": "2026-01-01", "checkout": "2026-01-05" },
    "additionalneeds": "Breakfast"
  }
}
```

Retrieve (`GET /booking/{id}`) response (`200`, JSON) — the inner `booking`
object only (no `bookingid` wrapper):

```json
{
  "firstname": "PhaseOne",
  "lastname": "Verify",
  "totalprice": 150,
  "depositpaid": true,
  "bookingdates": { "checkin": "2026-01-01", "checkout": "2026-01-05" },
  "additionalneeds": "Breakfast"
}
```

`PUT` echoes the full replacement object; `PATCH` returns the merged object
(verified: `PATCH {"firstname":"Patched"}` preserved all other fields).

## 6. Listing / filtering

- `GET /booking` → `200`, array of `{"bookingid": n}` (observed ~968 entries
  on a shared instance — count is volatile, never assert exact totals).
- Verified filters: `?firstname=Sally` returns matching subset
  (e.g. 4 IDs on 2026-10-03); `?checkin=2013-01-01&checkout=2014-12-31`
  returned `[]` for that window (filter semantics exist, data-dependent).
- Documented filter keys (per Postman docs; behavior partially verified):
  `firstname`, `lastname`, `checkin`, `checkout`. Combined/edge semantics
  (AND vs OR, date inclusivity) are **unverified** — explicit Phase 9/12 probes.

## 7. Known limitations & volatility

- Shared public instance: anyone can create/delete; observed ID counter >1400
  and `GET /booking/1` → `404` on 2026-10-03. **Never hardcode booking IDs**
  except transiently within a chained workflow.
- Docs state a reset to 10 seed records every ~10 minutes; observed counts far
  higher between resets — tests must create their own data and tolerate
  cross-traffic (unique names per run, no global-count assertions).
- Validation is extremely lenient (all verified 2026-10-03, `POST /booking`
  → `200` unless noted): empty-string names, `totalprice` 0 / negative /
  999999999, `checkout` before `checkin`, unknown extra fields (silently
  dropped), `additionalneeds: null` (stored as `null`) all accepted.
- Type coercion instead of rejection: `totalprice: "not-a-number"` → `200`
  with `totalprice: null`; `depositpaid: "yes"` → `200` with `true`;
  `checkin: "not-a-date"` → `200` with `"0NaN-aN-aN"` (JS-Date artifact).
  These are the primary contract-risk areas for negative/boundary testing.

## 8. Potential failure conditions (input to Phases 2–3)

Health/auth, missing/invalid token (403), bad credentials (200 + reason),
nonexistent/malformed IDs (404), double delete (405), missing `firstname`
(500), wrong-type numerics/booleans/dates (200 + coercion), malformed JSON
(400), empty/oversized/negative/zero values (200, stored as-is), unknown
fields (200, ignored), `null` optionals (200), XML-vs-JSON negotiation,
volatile IDs and list counts, ~0.3 s typical latency (no SLA asserted).

## 9. Verification log (reproducible)

All observations via `requests` against the base URL on 2026-10-03:
`GET /ping`; `POST /auth` (valid/invalid/empty); `GET /booking` (+2 filter
combos); full lifecycle create→get→put→patch→delete→get→re-delete on live
IDs (e.g. 1198, 1283, 1371); unauthenticated/invalid-token writes (403);
Basic-auth `PUT` (200); `Accept: application/xml` retrieval; 9 boundary
payloads (empty/huge/negative/zero price, inverted/bad dates,
string boolean, extra field, null optional). Raw bodies recorded above are
trimmed only for length; statuses and shapes are verbatim.
