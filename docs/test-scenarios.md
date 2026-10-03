# Test Scenarios — RESTful Booker (Phase 3)

> 56 meaningful scenarios, all **[observed]** — the last open pin (`E2E-002`,
> full Basic-auth chain) was proven in Phase 10. See `docs/api-inventory.md`
> §9 plus Phase 4/5 probes (all 2026-10-03) for evidence.
> Priorities: **P0** = must-pass happy path / auth enforcement / lifecycle;
> **P1** = negative / boundary / contract depth. No filler variations.

## Health — `HLTH-`

| ID | Area | Scenario | Type | Priority | Expected |
| --- | --- | --- | --- | --- | --- |
| HLTH-001 | Health | `GET /ping` reachability | Smoke | P0 | **[observed]** 201, body `Created`, `text/plain` |
| HLTH-002 | Health | `HEAD /ping` headers-only | Functional | P1 | **[observed]** 201, empty body |
| HLTH-003 | Health | Health response contract (`Content-Type`, client-side latency guard, no SLA) | Contract | P1 | **[observed]** `text/plain`; latency ~0.3 s sample |

## Authentication — `AUTH-`

| ID | Area | Scenario | Type | Priority | Expected |
| --- | --- | --- | --- | --- | --- |
| AUTH-001 | Authentication | Valid `admin`/`password123` yields usable token | Positive | P0 | **[observed]** 200 + `{"token":"<non-empty>"}`; token authorizes a write |
| AUTH-002 | Authentication | Wrong password rejected as failure | Negative | P1 | **[observed]** 200 + `{"reason":"Bad credentials"}`, no `token` |
| AUTH-003 | Authentication | Unknown username rejected as failure | Negative | P1 | **[observed]** 200 + `{"reason":"Bad credentials"}` (same shape as AUTH-002) |
| AUTH-004 | Authentication | Empty `{}` body rejected as failure | Negative | P1 | **[observed]** 200 + `{"reason":"Bad credentials"}` |
| AUTH-005 | Authentication | Empty-string credentials rejected | Negative | P1 | **[observed]** 200 + `{"reason":"Bad credentials"}` (probed 2026-10-03) |
| AUTH-006 | Authentication | Cookie-token write succeeds (`PUT` on live booking) | Positive | P0 | **[observed]** 200 + replaced object |
| AUTH-007 | Authentication | Basic-auth write succeeds (alternative mechanism) | Positive | P1 | **[observed]** 200 on live ID (proves alt path, guards regression) |
| AUTH-008 | Authentication | Missing-token write refused per method (`PUT`/`PATCH`/`DELETE`) | Negative | P0 | **[observed]** 403 `Forbidden` (`text/plain`) each method |
| AUTH-009 | Authentication | Invalid-token write refused (`Cookie: token=invalid123`) | Negative | P1 | **[observed]** 403 `Forbidden` |

## Booking functional — `BOOK-`

| ID | Area | Scenario | Type | Priority | Expected |
| --- | --- | --- | --- | --- | --- |
| BOOK-001 | Create | Valid payload creates booking, echo matches request | Positive | P0 | **[observed]** 200 + `{bookingid:int, booking:{…}}` field-for-field equal |
| BOOK-002 | Create | Create → immediate `GET` round-trip identical | Positive / integrity | P0 | **[observed]** `GET` body equals created `booking` object |
| BOOK-003 | Get | Retrieve existing booking by live ID | Positive | P0 | **[observed]** 200 + full booking object |
| BOOK-004 | Get | Nonexistent ID (`999999`) | Negative | P1 | **[observed]** 404 `Not Found` (`text/plain`) |
| BOOK-005 | Get | Malformed ID (`abc`) | Negative | P1 | **[observed]** 404 (not 400) — pinned quirk |
| BOOK-006 | Update (PUT) | Authenticated full replace persists | Positive | P0 | **[observed]** 200 echo == replacement; follow-up `GET` equal |
| BOOK-007 | Update (PUT) | `PUT` without/invalid token refused, data untouched | Negative | P1 | **[observed]** 403; `GET` still returns pre-attempt state |
| BOOK-008 | Update (PATCH) | Authenticated partial update merges, preserves other fields | Positive | P0 | **[observed]** 200 merged object; `GET` confirms |
| BOOK-009 | Update (PATCH) | `PATCH` without/invalid token refused | Negative | P1 | **[observed]** 403 |
| BOOK-010 | Delete | Authenticated delete removes booking | Positive | P0 | **[observed]** 201 `Created` (`text/plain`); follow-up `GET` → 404 |
| BOOK-011 | Delete | `DELETE` without/invalid token refused, booking survives | Negative | P1 | **[observed]** 403; `GET` still 200 |
| BOOK-012 | Delete | Re-delete of same ID | Negative | P1 | **[observed]** 405 Method Not Allowed (not 404) — pinned quirk |

## Listing / filtering — `FILT-`

| ID | Area | Scenario | Type | Priority | Expected |
| --- | --- | --- | --- | --- | --- |
| FILT-001 | Filtering | List returns ID array (shape-only, never exact count) | Positive | P0 | **[observed]** 200, `[{bookingid:int},…]` (~968 entries on 2026-10-03, volatile) |
| FILT-002 | Filtering | `?firstname=` narrows to matching IDs | Positive | P1 | **[observed]** subset (e.g. `Sally` → 4 IDs); assert narrowing + shape |
| FILT-003 | Filtering | `?lastname=` narrows to matching IDs | Positive | P1 | **[observed]** 200, narrowing subset (e.g. `Brown` → 20+ IDs on 2026-10-03); shape-only |
| FILT-004 | Filtering | `?checkin=&checkout=` window semantics | Functional | P1 | **[observed]** `[]` for probed window — assert shape, record data-dependence |
| FILT-005 | Filtering | Combined filters (e.g. name + date) conjunction semantics | Functional | P1 | **[observed]** AND-narrowing (`firstname=Sally&lastname=Brown` → `[3]` on 2026-10-03); shape-only |

## Negative payloads — `NEG-`

| ID | Area | Scenario | Type | Priority | Expected |
| --- | --- | --- | --- | --- | --- |
| NEG-001 | Create | Missing `firstname` | Negative | P1 | **[observed]** 500 Internal Server Error — crash, top defect candidate |
| NEG-002 | Create | Missing `lastname` | Negative | P1 | **[observed]** 500 Internal Server Error (probed 2026-10-03, same as NEG-001) |
| NEG-003 | Create | Missing `bookingdates` object | Negative | P1 | **[observed]** 500 (probed 2026-10-03); missing `totalprice`/`depositpaid` also 500 |
| NEG-004 | Create | Wrong-type `totalprice` (`"not-a-number"`) | Negative | P1 | **[observed]** 200 with `totalprice:null` — coercion, defect candidate |
| NEG-005 | Create | Wrong-type `depositpaid` (`"yes"`) | Negative | P1 | **[observed]** 200 with `true` — coercion |
| NEG-006 | Create | Bad date strings (`"not-a-date"`) | Negative | P1 | **[observed]** 200 with `"0NaN-aN-aN"` artifact — coercion |
| NEG-007 | Create | Empty-string names | Negative | P1 | **[observed]** 200, stored `""` — leniency |
| NEG-008 | Create | Malformed JSON body | Negative | P1 | **[observed]** 400 `Bad Request` (`text/plain`) |
| NEG-009 | Create | Unknown extra field (`"surprise"`) | Negative | P1 | **[observed]** 200, field silently dropped |
| NEG-010 | Create | `null` optional (`additionalneeds:null`) | Negative | P1 | **[observed]** 200, stored `null` |
| NEG-011 | Headers | Missing/invalid `Content-Type` on write | Negative | P1 | **[observed]** 500 for `text/plain` (Postman) and absent header with JSON body (raw `requests` test); malformed JSON with JSON content type returns 400 |
| NEG-012 | Get | `GET` on just-deleted ID (verify-gone) | Negative | P0 | **[observed]** 404 — the deletion proof, reused inside `E2E-001` |

## Boundary values — `BND-`

| ID | Area | Scenario | Type | Priority | Expected |
| --- | --- | --- | --- | --- | --- |
| BND-001 | Create | `totalprice: 0` | Boundary | P1 | **[observed]** 200, stored `0` |
| BND-002 | Create | `totalprice: -50` (negative) | Boundary | P1 | **[observed]** 200, stored `-50` — leniency |
| BND-003 | Create | `totalprice: 999999999` (huge) | Boundary | P1 | **[observed]** 200, stored as-is |
| BND-004 | Create | `checkout` before `checkin` (inverted range) | Boundary | P1 | **[observed]** 200, stored as-is — no range check |
| BND-005 | Create | Very long name strings (e.g. 500 chars) | Boundary | P1 | **[observed]** 200, stored verbatim full-length (probed 2026-10-03) |
| BND-006 | Get | Very large ID (`9999999999`) | Boundary | P1 | **[observed]** 404 `Not Found` (probed 2026-10-03) |
| BND-007 | Create | Minimal payload (only required-feeling fields) | Boundary | P1 | **[observed]** any missing core field (`firstname`/`lastname`/`totalprice`/`depositpaid`/`bookingdates`) → 500 (probed 2026-10-03) |

## Contracts & schemas — `CON-`

| ID | Area | Scenario | Type | Priority | Expected |
| --- | --- | --- | --- | --- | --- |
| CON-001 | Contract | Status-code matrix matches inventory table (all endpoints) | Contract | P0 | **[observed]** per `api-inventory.md` §2, incl. 201-ping / 201-delete / 403 / 404 / 405 |
| CON-002 | Contract | `Content-Type` per family (JSON vs `text/plain`) | Contract | P0 | **[observed]** JSON on data endpoints; `text/plain` on ping/errors/delete |
| CON-003 | Contract | Auth response schema (`token` xor `reason`, never both) | Contract | P0 | **[observed]** shape; `jsonschema` in pytest, schema assert in Postman |
| CON-004 | Contract | Booking object schema (types, nested `bookingdates`, optional `additionalneeds`) | Contract | P0 | **[observed]** shape incl. `null`-coercion traps asserted in `NEG-004…006` |
| CON-005 | Contract | Create-response schema (`bookingid` int + `booking`) | Contract | P0 | **[observed]** shape from live `1198`-style responses |
| CON-006 | Contract | `Accept: application/xml` negotiation surprise documented | Contract | P1 | **[observed]** XML markup with `text/html` Content-Type on `GET`; clients must pin JSON Accept |

## End-to-end workflow — `E2E-`

| ID | Area | Scenario | Type | Priority | Expected |
| --- | --- | --- | --- | --- | --- |
| E2E-001 | Workflow | Full lifecycle: auth → create → get → put → get → patch → get → delete → get(404), asserting every hop | Workflow | P0 | **[observed]** each hop individually verified 2026-10-03; chained run to be proven in Phases 8/10 |
| E2E-002 | Workflow | Lifecycle with Basic auth (instead of token) | Workflow | P1 | **[observed]** full Basic chain greens in Newman folder 08 (probed + collection-verified 2026-10-03) |

## Coverage summary

- Total: **56 scenarios** (3 HLTH + 9 AUTH + 12 BOOK + 5 FILT + 12 NEG + 7 BND + 6 CON + 2 E2E).
- P0: 18 (all happy paths, auth enforcement, contracts that gate CI, lifecycle).
- P1: 38 (negative / boundary / filter-depth / negotiation nuances).
- All 56 scenarios carry **[observed]** expectations pinned across Phases 1,
  4/5, and 10. Volatile-host re-verification remains standard practice before
  any new assertion is written.
- Traceability: requirement → this ID → Postman test (Phase 5–10) → pytest
  (Phase 12–16) → CI (Phase 18) lands in `docs/traceability-matrix.md`
  (Phase 22). IDs are frozen from here — automation references them, never
  renames them.
