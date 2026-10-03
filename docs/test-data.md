# Test Data Strategy (Phase 4)

> Factories: `src/test_data.py`. Ground truth: `docs/api-inventory.md`
> (live-verified 2026-10-03). Scenario IDs: `docs/test-scenarios.md`.

## 1. Principles

1. **Generate, don't hardcode.** Every booking a test touches is created by
   that test (or its fixture) via `valid_booking_payload()` /
   `unique_booking_payload()`. No committed booking IDs — `/booking/1` was
   already 404 on 2026-10-03, and the shared host shifts IDs constantly.
2. **Unique where it matters.** Workflow and filter-narrowing tests use
   `unique_booking_payload(prefix=…)` (`"<prefix>-<HHMMSS>-<rand6>"` first
   names) so a run can pick its own bookings out of cross-traffic with
   `GET /booking?firstname=…` without ever asserting exact list counts.
3. **Secrets never committed.** Usernames, passwords, base URL, and timeout
   resolve at runtime from env vars (`src/config.py` ← `.env` locally, CI
   secrets in CI). `.env.example` holds only the public demo defaults.
4. **Invalid data asserts reality.** Each invalid/boundary entry carries an
   `expected_note` with the *observed* behavior. Tests pin the observed
   contract and attach a contract-opinion note for the Phase 21 defect
   review — they never reshape the request to force the "nice" status code.

## 2. Valid data (`valid_booking_payload`, `valid_booking_variants`)

Standard booking (mirrors the documented shape, all types strict):

```python
{
    "firstname": "John",
    "lastname": "Doe",
    "totalprice": 150,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-05"},
    "additionalneeds": "Breakfast",
}
```

Variants (`valid_booking_variants()`): `standard`, `deposit_false`
(`depositpaid: False`), `no_additional_needs` (`additionalneeds: None` —
accepted, stored `null`), `high_price` (9999), `long_stay` (June 2026 window),
`alt_names` (Sally Brown / Lunch). Covers BOOK-001/002/003/006/008/010,
E2E-001, and the AUTH-006/007 write-proofs. Any field overridable, including
partially nested `bookingdates` (merged, not replaced).

## 3. Invalid data (`invalid_booking_payloads()` → NEG scenarios)

| Key | Mutation | Observed (2026-10-03) | Scenarios |
| --- | --- | --- | --- |
| `missing_firstname` | delete `firstname` | **500** Internal Server Error | NEG-001 |
| `missing_lastname` | delete `lastname` | **500** (probed 2026-10-03) | NEG-002 |
| `missing_bookingdates` | delete `bookingdates` | **500** (probed 2026-10-03; `totalprice`/`depositpaid` also 500) | NEG-003 |
| `price_as_string` | `totalprice: "not-a-number"` | 200, `totalprice: null` | NEG-004 |
| `deposit_as_string` | `depositpaid: "yes"` | 200, `true` | NEG-005 |
| `bad_date_format` | `checkin: "not-a-date"` | 200, `"0NaN-aN-aN"` | NEG-006 |
| `empty_firstname` | `firstname: ""` | 200, stored `""` | NEG-007 |
| `extra_unknown_field` | `surprise: "hello"` | 200, silently dropped | NEG-009 |
| `null_additional_needs` | `additionalneeds: null` | 200, stored `null` | NEG-010 |

Plus, outside factory form (handled per-protocol, not per-payload):
malformed raw JSON → 400 (NEG-008, observed); `text/plain` `Content-Type` →
500 in the Postman collection, and omitted `Content-Type` with a JSON body →
500 in `tests/api/test_request_headers.py` (NEG-011, probed raw 2026-10-03);
verify-gone `GET` after delete → 404 (NEG-012, observed). Postman/Newman
automatically adds a `Content-Type` for raw request bodies, so the omission
case uses `requests` to ensure the header is genuinely absent.

## 4. Boundary data (`boundary_booking_payloads()` → BND scenarios)

| Key | Value | Observed | Scenario |
| --- | --- | --- | --- |
| `zero_price` | `totalprice: 0` | 200, stored `0` | BND-001 |
| `negative_price` | `totalprice: -50` | 200, stored `-50` | BND-002 |
| `huge_price` | `totalprice: 999999999` | 200, stored as-is | BND-003 |
| `inverted_dates` | checkout before checkin | 200, stored as-is | BND-004 |
| `long_name` | 500-char firstname | 200, stored verbatim (probed 2026-10-03) | BND-005 |

Large-ID retrieval (`9999999999` → 404, BND-006, probed) and the
required-field floor (any missing core field → 500, BND-007, probed) are
asserted with static expectations; no pre-fabrication risk remains.

## 5. Authentication data (`auth_payloads()` → AUTH scenarios)

Five bodies: `valid` (credentials resolved from `API_USERNAME` and
`API_PASSWORD` via `src/config.py`, with optional explicit overrides),
`wrong_password`, `unknown_user`, `empty_body` (`{}`), and `empty_strings`.
Observed contract reminder: all four failure shapes return **200 +
`{"reason":"Bad credentials"}`** — tests assert the body, and the valid case
additionally proves the token authorizes a write (AUTH-001/006). Token and
created IDs travel via Postman variables
(`token`, `bookingId`) / pytest fixtures (`auth_token`, `created_booking`),
never via files.

## 6. Lifecycle & cleanup

- Create → capture live ID → use immediately → delete → verify-gone (404).
  Only `E2E-002` (full Basic-auth chain) still carries `[pin at automation]`;
  everything else was probed live in Phase 1 and Phase 4/5 (2026-10-03).
- Failed runs may orphan bookings on the shared host; this is harmless
  (periodic server reset) and preferable to cross-test deletes. Workflow tests
  use unique names so orphans never collide with later runs.
- List/filter tests assert shapes only (`array of {bookingid}`, narrowing
  direction), never totals — ~968 entries observed, volatile by design.
