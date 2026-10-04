# Traceability Matrix (Phase 22)

> Requirement → Scenario (`docs/test-scenarios.md`) → Postman request
> (folder/request in
> `postman/collections/restful-booker-api.postman_collection.json`) →
> pytest (`tests/`) → CI. Scenario IDs are frozen (Phase 3); automation
> references them, never renames them. Postman names are quoted verbatim;
> pytest entries are `file::function[param]` where parametrized.
> CI: `P` = `postman-tests.yml` (Newman, whole collection),
> `Y` = `api-tests.yml` (pytest, whole suite) — both run on
> `push` / `pull_request` / `workflow_dispatch` and fail closed.

Legend: Priority **P0** = happy path / auth enforcement / lifecycle /
gating contract; **P1** = negative / boundary / filter-depth / nuance.
`—` in the pytest column is an explicit, accepted gap (covered in Postman;
reason in the Notes column) — never an oversight.

## Health

| Requirement | Scenario | Postman (folder 01) | Pytest | Pri | CI | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Health endpoint reachable | HLTH-001 | HealthCheck - GET ping | `test_health.py::test_get_ping_returns_201_created` | P0 | P+Y | 201 pinned, not 200 |
| Headers-only health check | HLTH-002 | HealthCheck - HEAD ping | `test_health.py::test_head_ping_returns_201_with_empty_body` | P1 | P+Y | |
| Health response contract | HLTH-003 | HealthCheck - GET ping (Content-Type + latency guard) | `test_health.py::test_get_ping_returns_201_created` (status/body/CT) | P1 | P+Y | Latency guard is client-side smoke only |

## Authentication

| Requirement | Scenario | Postman | Pytest | Pri | CI | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Valid credentials yield usable token | AUTH-001 | 02 - Authentication / CreateToken - valid credentials; 08 E2E auth | `test_auth.py::test_authenticate_with_valid_credentials_returns_usable_token` | P0 | P+Y | Token proven by authorizing a write |
| Wrong password rejected | AUTH-002 | 07 / CreateToken - invalid password | `test_auth.py::..._reports_bad_credentials[wrong_password]` | P1 | P+Y | 200 + reason, not 401 (D-003) |
| Unknown user rejected | AUTH-003 | 07 / CreateToken - invalid user | `..._reports_bad_credentials[unknown_user]` | P1 | P+Y | Same shape as AUTH-002 |
| Empty body rejected | AUTH-004 | 07 / CreateToken - missing body | `..._reports_bad_credentials[empty_body]` | P1 | P+Y | |
| Empty-string credentials rejected | AUTH-005 | 07 / CreateToken - empty credentials | `..._reports_bad_credentials[empty_strings]` | P1 | P+Y | |
| Cookie-token authorizes writes | AUTH-006 | 05 / UpdateBooking PUT - with token; 06 / DeleteBooking - with token 201 | `test_auth.py` write-proof + `test_booking_update.py::test_put_replaces_booking_and_persists`, `test_booking_delete.py::test_delete_removes_booking` | P0 | P+Y | |
| Basic auth authorizes writes | AUTH-007 | 08 E2E(Basic) update/delete chain | — | P1 | P | **Accepted gap (pytest):** alt mechanism proven in Postman; token path covers pytest. No regression risk accepted blindly — Basic chain greens in Newman |
| Missing-token write refused per method | AUTH-008 | 05 / PUT - without token 403; PATCH - without token 403; 06 / DeleteBooking - without token 403 | `test_booking_update.py::..._without_valid_auth...[missing]` (PUT+PATCH), `test_booking_delete.py::...[missing]` | P0 | P+Y | 403 each method |
| Invalid-token write refused | AUTH-009 | 05 / PUT - invalid token 403; PATCH - invalid token 403; 06 / invalid token 403 | `...[invalid]` params + `test_booking_negative.py::test_{put,patch,delete}_invalid_token_is_forbidden` | P1 | P+Y | |

## Booking functional

| Requirement | Scenario | Postman | Pytest | Pri | CI | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Create booking with valid payload | BOOK-001 | 03 / CreateBooking - valid payload | `test_booking_create.py::test_create_booking_returns_booking_id_and_matching_echo` | P0 | P+Y | Field-for-field echo |
| Create → GET round-trip identical | BOOK-002 | 04 / GetBooking - live ID round-trips; 08 E2E pairs | `test_booking_create.py::test_created_booking_round_trips_identically`; `test_booking_get.py::test_get_existing_booking_returns_created_payload` | P0 | P+Y | Data-integrity anchor |
| Retrieve existing booking | BOOK-003 | 04 / GetBooking - live ID round-trips | `test_booking_get.py::test_get_existing_booking_returns_created_payload` | P0 | P+Y | |
| Nonexistent ID | BOOK-004 | 07 / GetBooking - nonexistent ID 404 | `test_booking_get.py::test_get_nonexistent_booking_returns_404`; `test_booking_negative.py::test_get_invalid_booking_id_returns_404[999999]` | P1 | P+Y | 404 text/plain |
| Malformed ID | BOOK-005 | 07 / GetBooking - malformed ID 404 | `test_booking_get.py::test_get_malformed_booking_id_returns_404_not_400`; `...[abc]` | P1 | P+Y | 404 not 400 (D-005) |
| Authenticated full replace persists | BOOK-006 | 05 / UpdateBooking PUT - with token; 08 E2E full update | `test_booking_update.py::test_put_replaces_booking_and_persists` | P0 | P+Y | PUT echo + follow-up GET |
| PUT without/invalid token refused | BOOK-007 | 05 / PUT - without/invalid token 403 | `test_booking_update.py::test_put_without_valid_auth...[missing\|invalid]` + `test_booking_negative.py::test_put_invalid_token_is_forbidden` | P1 | P+Y | GET proves untouched |
| Authenticated partial update merges | BOOK-008 | 05 / PartialUpdate PATCH - with token; 08 E2E partial update | `test_booking_update.py::test_patch_merges_fields_and_persists` | P0 | P+Y | Merge + GET confirm |
| PATCH without/invalid token refused | BOOK-009 | 05 / PATCH - without/invalid token 403 | `test_booking_update.py::test_patch_without_valid_auth...[missing\|invalid]` + `test_booking_negative.py::test_patch_invalid_token_is_forbidden` | P1 | P+Y | |
| Authenticated delete removes booking | BOOK-010 | 06 / DeleteBooking - with token 201; GetBooking - verify gone 404 | `test_booking_delete.py::test_delete_removes_booking` | P0 | P+Y | 201 + verify-gone 404 |
| DELETE without/invalid token refused | BOOK-011 | 06 / DeleteBooking - without/invalid token 403 | `test_booking_delete.py::test_delete_without_valid_auth...[missing\|invalid]` + `test_booking_negative.py::test_delete_invalid_token_is_forbidden` | P1 | P+Y | GET proves survival |
| Re-delete same ID | BOOK-012 | 06 / DeleteBooking - re-delete 405 | `test_booking_delete.py::test_redelete_returns_405` | P1 | P+Y | 405 not 404 (D-005) |

## Listing / filtering

| Requirement | Scenario | Postman | Pytest | Pri | CI | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| List returns ID array | FILT-001 | 04 / GetBookingIds - list shape | `test_booking_get.py::test_list_bookings_returns_id_array_shape_only` | P0 | P+Y | Shape-only, never count |
| Filter by firstname narrows | FILT-002 | 04 / GetBookingIds - filter firstname | `test_booking_get.py::test_filter_by_firstname_narrows_results` | P1 | P+Y | |
| Filter by lastname narrows | FILT-003 | 04 / GetBookingIds - filter lastname | — | P1 | P | **Accepted gap (pytest):** same mechanism as FILT-002, proven in Postman |
| Date-window filter semantics | FILT-004 | 04 / GetBookingIds - filter date window | — | P1 | P | **Accepted gap (pytest):** data-dependent (`[]` observed); shape asserted in Postman |
| Combined filters narrow | FILT-005 | 04 / GetBookingIds - combined filter narrows | — | P1 | P | **Accepted gap (pytest):** AND-narrowing proven in Postman |

## Negative payloads

| Requirement | Scenario | Postman | Pytest | Pri | CI | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Missing firstname → 500 | NEG-001 | 03 / CreateBooking - missing firstname gives 500 | `test_booking_negative.py::test_create_without_required_field_returns_observed_500[firstname]` | P1 | P+Y | D-001 |
| Missing lastname → 500 | NEG-002 | 07 / NEG missing lastname 500 | `...[lastname]` | P1 | P+Y | D-001 |
| Missing bookingdates → 500 | NEG-003 | 07 / NEG missing bookingdates 500 | `...[bookingdates]` (+`[totalprice]`, `[depositpaid]` — BND-007 floor) | P1 | P+Y | D-001 |
| Wrong-type totalprice coerced null | NEG-004 | 03 / CreateBooking - string price coerced to null | `test_create_records_observed_type_coercion[totalprice-not-a-number-None]` | P1 | P+Y | D-002 |
| Wrong-type depositpaid coerced true | NEG-005 | 07 / NEG string boolean coerced true | `...[depositpaid-yes-True]` | P1 | P+Y | D-002 |
| Bad dates → artifact | NEG-006 | 07 / NEG bad date artifact | `test_create_with_invalid_date_records_observed_artifact` | P1 | P+Y | `0NaN-aN-aN` (D-002) |
| Empty-string names stored | NEG-007 | 07 / NEG empty firstname stored | `test_create_with_empty_firstname_is_stored_verbatim` | P1 | P+Y | D-004 |
| Malformed JSON → 400 | NEG-008 | 05 / PUT - malformed JSON 400; PATCH - malformed JSON 400; 07 / NEG malformed JSON 400 | `test_create_with_malformed_json_returns_400` (POST) | P1 | P+Y | PUT/PATCH-400 proven in Postman; POST-400 in pytest — jointly complete |
| Unknown extra field dropped | NEG-009 | 07 / NEG extra field dropped | `test_create_ignores_unknown_field` | P1 | P+Y | D-004 |
| Null optional stored null | NEG-010 | 07 / NEG null additionalneeds | `test_create_preserves_null_optional_field` | P1 | P+Y | D-004 |
| Missing/invalid Content-Type | NEG-011 | 07 / CreateBooking - wrong Content-Type gives 500 | `test_request_headers.py::test_booking_create_without_content_type_returns_observed_server_error` | P1 | P+Y | D-007; truly-omitted header is pytest-only (Newman auto-sets it) |
| GET just-deleted ID → 404 | NEG-012 | 06 / GetBooking - verify gone 404; 08 E2E verify-deletion ×2 | `test_booking_delete.py::test_delete_removes_booking` (verify-gone tail) | P0 | P+Y | The deletion proof |

## Boundary values

| Requirement | Scenario | Postman | Pytest | Pri | CI | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| totalprice 0 stored | BND-001 | 07 / BND zero price stored | `test_create_with_boundary_price_is_stored_as_is[0]` | P1 | P+Y | D-004 |
| totalprice −50 stored | BND-002 | 07 / BND negative price stored | `...[-50]` | P1 | P+Y | D-004 |
| totalprice 999999999 stored | BND-003 | 07 / BND huge price stored | `...[999999999]` | P1 | P+Y | D-004 |
| Inverted date range stored | BND-004 | 07 / BND inverted dates stored | `test_create_with_inverted_dates_is_stored_without_range_check` | P1 | P+Y | D-004 |
| 500-char name stored verbatim | BND-005 | — (pytest-probed 2026-10-03) | `test_create_with_very_long_name_is_stored_verbatim` | P1 | Y | **Accepted gap (Postman):** covered in pytest; collection omits it to avoid a 500-char literal in JSON |
| Very large ID → 404 | BND-006 | 07 / GetBooking - huge ID 404 | `test_booking_get.py` invalid-ID family (same 404 path; `999999`/`abc` params) | P1 | P+Y | `9999999999` in Postman, equivalents in pytest |
| Minimal payload floor (any core field missing → 500) | BND-007 | NEG missing-field set (03 + 07) | `test_create_without_required_field_returns_observed_500` (all 5 params) | P1 | P+Y | Shared with NEG-001…003 |

## Contracts & schemas

| Requirement | Scenario | Postman | Pytest | Pri | CI | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Status-code matrix per inventory | CON-001 | Every request asserts its observed code | Every test asserts its observed code | P0 | P+Y | `docs/api-inventory.md` §2 is the oracle |
| Content-Type per family | CON-002 | JSON vs `text/plain` asserted per request | Asserted in health/auth/negative/header tests | P0 | P+Y | JSON on data, text/plain on ping/errors/delete |
| Auth response schema | CON-003 | Schema assert on token issue | `validate_schema(..., "auth-schema.json")` in `test_auth.py` (success + all 4 failures) | P0 | P+Y | token-xor-reason; `tests/schemas/auth-schema.json` |
| Booking object schema | CON-004 | Inline `jsonSchema` on live retrieval | `validate_schema` on create/get/update paths (`tests/schemas/booking-schema.json`) | P0 | P+Y | Incl. coercion-trap awareness |
| Create-response schema | CON-005 | Inline `jsonSchema` on creation | Validated via bookingid + booking shape in create tests (`booking-response-schema.json`) | P0 | P+Y | |
| XML negotiation documented | CON-006 | — (manual probe, pinned Accept) | — | P1 | — | **Accepted gap (both):** docs-level scenario; mitigation (pin `Accept: application/json`) is implemented in client + collection. Not CI-gated by design |

## End-to-end workflow

| Requirement | Scenario | Postman (folder 08) | Pytest | Pri | CI | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Full lifecycle on token auth | E2E-001 | E2E auth → create → get → put → get → patch → get → delete → verify-gone (7 requests, every hop asserted) | Chained-test equivalents: create+round-trip, put-persist, patch-persist, delete+verify-gone | P0 | P+Y | Atomic lifecycle in Postman; hop-by-hop independence in pytest (Rule 8) |
| Full lifecycle on Basic auth | E2E-002 | E2E(Basic) create → put → patch → delete → verify-gone | — | P1 | P | **Accepted gap (pytest):** alt-auth chain proven in Newman; token chain + Basic single-write (AUTH-007 Postman) cover pytest |

## Coverage roll-up (observed, not projected)

- Scenarios: **56** (3 HLTH + 9 AUTH + 12 BOOK + 5 FILT + 12 NEG + 7 BND + 6 CON + 2 E2E); P0 **18**, P1 **38**.
- Postman: **57 requests** across 8 folders (every scenario has ≥1 request except BND-005/CON-006, noted above); **215 assertions** (last full Newman run, green).
- Pytest: **49 tests** collected (47 scenario tests + 2 fixture-hygiene meta-tests in `test_fixture_cleanup.py`, which guard the suite itself and trace to no scenario by design).
- CI: both workflows green-gated; any scenario failure fails its workflow (no `continue-on-error`; uploads use `if: always()` only).
- Gaps above are **accepted and stated** (Postman-only: FILT-003/004/005, AUTH-007, E2E-002, PUT/PATCH-400; pytest-only: BND-005; docs-level: CON-006). Zero unexplained gaps.
