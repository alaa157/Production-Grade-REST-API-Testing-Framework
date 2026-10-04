# Defect Summary — RESTful Booker (Phase 21)

> All entries below describe **genuinely observed behavior** probed live
> against `https://restful-booker.herokuapp.com` on 2026-10-03. Automation
> coverage varies by finding and is stated in each evidence section; D-006 is
> documented from a manual probe and is not CI-gated. Nothing here is invented
> to look impressive: where the API's
> contract is merely surprising but self-consistent, the entry is marked
> `Contract quirk` rather than `Defect`. Expected results state what a
> conventional REST API would do; actual results state what this demo API
> verifiably does. Re-verify on a volatile shared host before citing any
> entry externally.

Environment (all entries): public demo host
`https://restful-booker.herokuapp.com`, no setup beyond a live booking where
noted. Evidence pointers use request names from
`postman/collections/restful-booker-api.postman_collection.json` and test
functions from `tests/api/`.

---

## D-001 — Missing required field crashes with 500 (not 400)

- **Severity:** Medium · **Priority:** P1 · **Status:** Observed, automated
- **Type:** Defect (server-side validation missing)
- **Endpoint / Method:** `POST /booking`
- **Preconditions:** None.
- **Steps to reproduce:**
  1. `POST /booking` with `Content-Type: application/json` and a valid
     payload minus any one of `firstname`, `lastname`, `totalprice`,
     `depositpaid`, `bookingdates`.
  2. Observe status and body.
- **Request:** `{"lastname":"X", ...}` (any single core field omitted).
- **Expected result:** `400 Bad Request` with a validation message.
- **Actual result:** `500 Internal Server Error` (`text/plain`).
  Probed 2026-10-03 for all five fields.
- **Evidence:** Postman `03 - Booking - Create / CreateBooking - missing
  firstname gives 500`, `07 - Negative Tests / NEG missing lastname 500`,
  `NEG missing bookingdates 500`; pytest
  `test_create_without_required_field_returns_observed_500[firstname|lastname|totalprice|depositpaid|bookingdates]`
  in `tests/api/test_booking_negative.py`.
- **Impact:** Clients get no actionable validation feedback; 5xx risks
  alert fatigue and masks real outages. Tests assert the **observed 500**
  with a contract-opinion note — they do not demand 400 the API never
  promised.

## D-002 — Wrong-type scalars silently coerced instead of rejected

- **Severity:** Medium · **Priority:** P1 · **Status:** Observed, automated
- **Type:** Defect (validation / data-integrity risk)
- **Endpoint / Method:** `POST /booking`
- **Preconditions:** None.
- **Steps to reproduce:**
  1. `POST /booking` with `"totalprice": "not-a-number"` → observe
     stored `"totalprice": null`.
  2. `POST /booking` with `"depositpaid": "yes"` → observe stored `true`.
  3. `POST /booking` with `"bookingdates": {"checkin": "not-a-date", ...}`
     → observe stored `"0NaN-aN-aN"` (JS-Date artifact).
- **Expected result:** `400` (or at minimum echo of a validated type).
- **Actual result:** `200` in all three cases with the coerced values above.
- **Evidence:** Postman `CreateBooking - string price coerced to null`,
  `NEG string boolean coerced true`, `NEG bad date artifact`; pytest
  `test_create_records_observed_type_coercion[...]`,
  `test_create_with_invalid_date_records_observed_artifact`.
- **Impact:** Corrupt data (`null` price, impossible date string) can enter
  the system silently. Flagged for any consumer of this API style; tests pin
  the coerced values verbatim so a future stricter API visibly breaks them.

## D-003 — Failed authentication returns 200 (not 401/403)

- **Severity:** Low-Medium · **Priority:** P1 · **Status:** Observed, automated
- **Type:** Contract quirk (consistent, but traps naive assertions)
- **Endpoint / Method:** `POST /auth`
- **Preconditions:** None.
- **Steps to reproduce:**
  1. `POST /auth` with wrong password, unknown user, `{}` body, or
     `{"username":"","password":""}`.
  2. Observe status and body.
- **Expected result:** `401 Unauthorized` (conventional).
- **Actual result:** `200` + `{"reason":"Bad credentials"}`, no `token`
  field — identical shape for all four failure modes.
- **Evidence:** Postman `07 - Negative Tests / CreateToken - invalid
  password|invalid user|missing body|empty credentials`; pytest
  `test_authenticate_with_invalid_credentials_reports_bad_credentials[...]`
  (4 params) in `tests/api/test_auth.py`; contract `CON-003`.
- **Impact:** Any check that asserts on status alone passes a failed login
  as success. Both harnesses assert on the **body** (`reason` present,
  `token` absent). Documented as the canonical example of why this project
  pins observed contracts.

## D-004 — No value validation on the leniency envelope

- **Severity:** Low (Medium for price) · **Priority:** P1 · **Status:**
  Observed; automation coverage varies by case
- **Type:** Risk area (lenient-by-design demo API, documented not fixed)
- **Endpoint / Method:** `POST /booking`
- **Preconditions:** None.
- **Steps to reproduce:** create bookings with `totalprice` `0` / `-50` /
  `999999999`, `checkout` before `checkin`, `firstname: ""`, 500-char
  names, unknown extra field `"surprise"`, `"additionalneeds": null`.
- **Expected result:** At least negative prices, inverted ranges, and
  empty names rejected or normalized per a stated rule.
- **Actual result:** The listed probes returned `200`; supported booking
  values were stored as submitted, the unknown extra field was dropped, and
  the null optional field remained null. The 500-character-name case is
  automated in pytest only; the other listed cases are covered in Postman
  and/or pytest as identified below.
- **Evidence:** Postman `NEG empty firstname stored`, `NEG extra field
  dropped`, `NEG null additionalneeds`, `BND zero|negative|huge price
  stored`, `BND inverted dates stored`; pytest
  `test_create_with_empty_firstname_is_stored_verbatim`,
  `test_create_with_boundary_price_is_stored_as_is[0|-50|999999999]`,
  `test_create_with_inverted_dates_is_stored_without_range_check`,
  `test_create_with_very_long_name_is_stored_verbatim`,
  `test_create_ignores_unknown_field`,
  `test_create_preserves_null_optional_field`. Postman covers the empty-name,
  boundary-price, inverted-date, unknown-field, and null-optional cases; the
  500-character case is pytest-only.
- **Impact:** Consumers cannot rely on the API to enforce business rules;
  validation must live client-side. Tests pin verbatim storage so any
  future tightening is caught.

## D-005 — Success and error status codes defy convention (201/403/404/405)

- **Severity:** Low · **Priority:** P1 · **Status:** Observed, automated
- **Type:** Contract quirk (self-consistent, pinned)
- **Endpoints:**
  - `GET /ping` → `201` + `Created` (`text/plain`), not 200.
  - `DELETE /booking/{id}` success → `201` + `Created` (`text/plain`),
    not 200/204 + JSON.
  - `GET /booking/abc` (malformed ID) → `404`, not 400.
  - Re-`DELETE` of the same ID → `405 Method Not Allowed`, not 404.
  - Write without/invalid token → `403 Forbidden` (`text/plain`) on
    `PUT`/`PATCH`/`DELETE` alike.
- **Steps to reproduce:** see `docs/api-inventory.md` §2 and the evidence
  pointers below; each is a single request with the stated method/ID/token.
- **Expected result:** Conventional codes (200 ping, 200/204 delete,
  400 malformed ID, 404 double delete).
- **Actual result:** Codes as listed — verified 2026-10-03.
- **Evidence:** Postman `01 - Health`, `06 - Booking - Delete` (all five
  requests), `GetBooking - malformed ID 404`; pytest `test_health.py`
  (both tests), `test_delete_removes_booking`, `test_redelete_returns_405`,
  `test_get_invalid_booking_id_returns_404`, `*_without_valid_auth_*`
  / `*_invalid_token_*` in `test_booking_update.py`,
  `test_booking_delete.py`, `test_booking_negative.py`.
- **Impact:** Low for a demo host, high as a lesson: contract tests must
  assert the **documented-observed** code, with an "expected-if-RESTful"
  note for reviewers, never the assumed one.

## D-006 — `Accept: application/xml` returns XML as `text/html`

- **Severity:** Info · **Priority:** P1 · **Status:** Observed, documented
- **Type:** Contract quirk
- **Endpoint / Method:** `GET /booking/{id}` with
  `Accept: application/xml`.
- **Steps to reproduce:** `GET` a live booking with
  `Accept: application/xml`; observe XML markup served with
  `Content-Type: text/html; charset=utf-8`.
- **Expected result:** Either `406` or XML served as `application/xml`.
- **Actual result:** `200` XML body with `text/html` content type.
- **Evidence:** Manual live probe recorded in `docs/api-inventory.md` §1 and
  scenario `CON-006`. It is documentation-only: no automated request asserts
  XML response negotiation. JSON clients pin `Accept: application/json`.
- **Impact:** Content-negotiation surprise for generic HTTP clients;
  mitigated by pinning `Accept` explicitly everywhere.

## D-007 — Missing/invalid `Content-Type` on writes surfaces as 500

- **Severity:** Low · **Priority:** P1 · **Status:** Observed, automated
- **Type:** Risk area (server doesn't distinguish client header error)
- **Endpoint / Method:** `POST /booking` (also `PUT`/`PATCH` malformed-JSON
  path returns the cleaner `400`).
- **Steps to reproduce:**
  1. `POST /booking` with JSON body but `Content-Type: text/plain` →
     `500` (Postman probe).
  2. `POST /booking` with JSON body and no `Content-Type` (raw `requests`
     call) → `500` (pytest `test_request_headers.py`).
  3. Contrast: syntactically malformed JSON **with** JSON content type →
     `400 Bad Request`.
- **Expected result:** `415` or `400` naming the header problem.
- **Actual result:** `500 Internal Server Error` for cases 1–2.
- **Evidence:** Postman `CreateBooking - wrong Content-Type gives 500`;
  pytest `test_booking_create_without_content_type_returns_observed_server_error`
  (`tests/api/test_request_headers.py`),
  `test_create_with_malformed_json_returns_400`; scenario `NEG-008`/`NEG-011`.
- **Impact:** Misleading 5xx on a client mistake. Note: Newman auto-sets
  `Content-Type`, so the truly-omitted-header case is covered in pytest
  only — stated explicitly so nobody chases it in Postman.

---

## Methodology note (anti-fabrication)

1. Probes ran against the live host (`requests`, curl-equivalent) before
   any assertion was written (Rule 2 — verify the API).
2. Each discrepancy was recorded in `docs/test-scenarios.md` with an
   **[observed]** tag; whether it is automated, and in which harness, is
   called out in the evidence above.
3. Where automation exists, it asserts observed behavior; contract opinions
   live in notes, never in pass/fail logic (so a future API fix shows up as a
   clean, explainable failure, not a hidden pass).
4. No defects were invented for portfolio effect. If this were a real client
   engagement, D-001 and D-002 would be filed as bugs; D-003–D-007 would
   ship as documented contract quirks with reproduction steps.
