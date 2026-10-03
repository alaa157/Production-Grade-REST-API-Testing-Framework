# Test Plan — RESTful Booker API Testing

> Phase 2. Implements the strategy (`docs/test-strategy.md`) against the
> verified inventory (`docs/api-inventory.md`, 2026-10-03). Scenario IDs below
> are defined in `docs/test-scenarios.md` (Phase 3); automation mapping lands
> in the traceability matrix (Phase 22).

## 1. Overview

Validate the public RESTful Booker API's functional, negative, boundary,
contract, authentication, and workflow behavior through a dual-automation
suite (Postman/Newman + pytest), gated in CI. Success = all P0 scenarios
green in both surfaces with evidence, all P1 discrepancies dispositioned.

## 2. In scope / out of scope

Per strategy §1–§2. In one line: JSON CRUD + auth + filtering + contracts on
the public host, in two harnesses; no perf/security-penetration/UI work.

## 3. Functional areas & planned coverage

### 3.1 Health check (`GET/HEAD /ping`)

- `HLTH-001` (P0, smoke): `GET /ping` → **201**, body `Created`
  (`text/plain`). Pins the counter-intuitive but observed contract.
- `HLTH-002` (P1): `HEAD /ping` → 201, empty body.
- `HLTH-003` (P1, contract): `Content-Type` is `text/plain`; latency sanity
  (client-side guard only, no SLA).

### 3.2 Authentication (`POST /auth`, token usage)

- `AUTH-001` (P0, positive): valid `admin`/`password123` → 200 + `token`
  (non-empty string); token authenticates a write.
- `AUTH-002…005` (P1, negative): wrong password, unknown user, `{}` body,
  empty-string credentials → **200 + `{"reason":"Bad credentials"}`**, no
  token field. Assert body, not status (the trap this area exists to catch).
- `AUTH-006` (P0): Cookie-token write succeeds (`PUT` 200).
- `AUTH-007` (P1): Basic-auth write succeeds (`PUT` 200) — alternative
  mechanism must not regress.
- `AUTH-008/009` (P0/P1): missing-token and invalid-token writes →
  **403** `Forbidden` (`PUT`, `PATCH`, `DELETE` each covered in `BOOK-`
  scenarios; auth matrix asserts the code mapping once per method).

### 3.3 Booking creation (`POST /booking`)

- `BOOK-001` (P0): valid payload → 200 + `{bookingid, booking}`; echo matches
  request field-for-field (data integrity anchor).
- `CON-005` (P0, contract): create-response validates against the
  booking-response schema (`bookingid` integer + full `booking` object).
- `NEG-001` (P1): missing `firstname` → observed **500** (documents crash;
  Phase 21 dispositions whether to assert 500-as-observed or demand 400).
- `NEG-002…009`: wrong-type price (`null` coercion), missing `lastname` /
  `bookingdates`, empty strings, malformed JSON (400), extra unknown field
  (ignored), `null` optional (stored null). Each asserts observed behavior
  with a contract-opinion note.
- `BND-` boundary set (§3.9) reuses the create endpoint.

### 3.4 Booking retrieval (`GET /booking/{id}`, list)

- `BOOK-002` (P0): create → immediate `GET` returns identical payload.
- `BOOK-003` (P0): retrieve an existing booking by ID.
- `BOOK-004/005` (P1, negative): nonexistent ID (`999999`) and malformed ID
  (`abc`) → **404** `Not Found` (`text/plain`).
- `FILT-001` (P0): list → 200, array of `{bookingid}` (shape-only; never
  exact count — shared data volatile, ~968 observed).
- `FILT-002…005` (P1): `firstname` filter narrows; `lastname` filter;
  `checkin`/`checkout` window (observed `[]` for one window — asserts
  shape + documents data-dependence); combined filters (AND/OR question
  explicitly probed, outcome recorded either way).

### 3.5 Full update (`PUT /booking/{id}`)

- `BOOK-006` (P0): authenticated full replace → 200, echo equals replacement;
  follow-up `GET` confirms persistence.
- `BOOK-007` (P1, negative): `PUT` without token → 403; invalid token → 403.
- `CON-` contract: `PUT` response validates against booking schema; wrong-ID
  `PUT` (nonexistent) behavior probed and pinned (outcome recorded in
  scenarios; re-verified at automation time since host state shifts).

### 3.6 Partial update (`PATCH /booking/{id}`)

- `BOOK-008` (P0): authenticated `PATCH {"firstname":…}` → 200, field merged,
  all other fields preserved (verified live); `GET` confirms.
- `BOOK-009` (P1): `PATCH` without/invalid token → 403.

### 3.7 Deletion (`DELETE /booking/{id}`)

- `BOOK-010` (P0): authenticated delete → **201** `Created` (`text/plain`);
  follow-up `GET` → 404 (verify-gone — the actual deletion proof).
- `BOOK-011` (P1): delete without/invalid token → 403, booking still
  retrievable (auth did not half-apply).
- `BOOK-012` (P1): re-delete same ID → observed **405** (pinned + dispositioned).

### 3.8 Filtering (see §3.4, IDs `FILT-001…005`)

### 3.9 Negative behavior

Payload and header failures (`NEG-001…011`), post-delete verification
(`NEG-012`), authentication failures (`AUTH-002…005`, `AUTH-008/009`),
nonexistent/malformed IDs (`BOOK-004/005`), re-delete (`BOOK-012`), and XML
negotiation (`CON-006`) cover the negative behavior. Rule: send invalid →
capture verbatim → assert observed → attach contract opinion → route to defect
review. Never reshape the request to force the expected code.

### 3.10 Response validation & data integrity

- Every create/update/patch test performs a `GET` round-trip comparison
  (request vs stored vs re-fetched).
- `CON-001…006` (contract): status codes per inventory table; `Content-Type`
  per endpoint family (JSON vs `text/plain`); required fields; field types
  (with coercion traps explicitly asserted: price-null, boolean-true,
  date-artifact); booking/auth/create-response/list schemas.
- Full lifecycle `E2E-001` (P0): auth → create → get → put → get → patch →
  get → delete → get(404), asserting at each hop.

## 4. Test types & levels

Smoke (`HLTH-001`, `AUTH-001`, `BOOK-001/002/003`, `E2E-001` spine) runs first and
fast; functional/positive proves happy paths; negative/boundary prove the
leniency envelope; contract/schema prove wire shape; auth proves both
mechanisms + all 403 paths; workflow proves statefulness. Levels: per-endpoint
component tests (independent, self-creating data) + one stateful workflow.
`pytest -m` markers select each type; Postman folders 01–08 mirror them.

## 5. Schedule & milestones (plan-order, no dates fabricated)

`0 skeleton (done) → 1 inventory (done) → 2 strategy+plan (this doc) → 3
scenarios → 4 test-data → 5–10 Postman → 11 Newman → 12–16 pytest → 17 config
→ 18–19 CI+gates → 20 reporting → 21 defect review → 22 traceability → 23–25
README/presentation/diagrams → 26–28 quality/failure-sim/audit → 29–30
deliverables/DoD.` Each phase ends in a runnable, committable state
(Rule 1); automation phases re-verify any volatile-host assumption before
pinning it.

## 6. Resources & responsibilities

Single-QA portfolio project: one engineer owns design, automation, CI, docs,
and defect review. Review checkpoints: post-inventory (contract questions
frozen), post-scenario (IDs frozen — automation references them), pre-CI
(quality review per Phase 26 checklist).

## 7. Entry / exit criteria

- Entry: inventory verified; host reachable; `pip install` + collection
  skeleton runnable (Phase 0 validation passed: 7/7 placeholders skip).
- Exit (test-cycle): 100% of P0 scenarios pass in both harnesses in CI;
  100% of executed P1 scenarios have evidence + disposition (pass, or
  fail-with-defect-entry); JUnit + HTML artifacts published; no skipped
  scenario without a stated reason; README coverage counts match observed
  runs only.

## 8. Risks & mitigations

| Risk (evidence) | Mitigation |
| --- | --- |
| Shared-host volatility (IDs/counts shift; `/1` 404'd) | Self-created data, unique names, no hardcoded IDs/counts; workflow-scoped cleanup |
| Over-lenient validation hides bugs (200 + coercion ×6 probes) | Assert coerced values verbatim; flag each as defect-candidate |
| Misleading statuses (auth 200, delete 201, re-delete 405) | Pin observed codes; add "expected-if-restful" notes for reviewers |
| Filter semantics unknown (`[]` on date window) | Probe-and-record scenarios; shape-only asserts where data-dependent |
| Reset wipes chained IDs mid-run | Create-then-immediately-use; re-create on 404 with retry-once in workflow only |
| XML negotiation surprise | Pin `Accept: application/json` everywhere; one explicit XML-behavior scenario |

## 9. Deliverables of this plan

Scenarios (`test-scenarios.md`), test data (`test-data.md`), Postman
collection + environment + schemas, pytest suite + schemas, CI workflows +
reports, defect summary, traceability matrix, README + diagrams — acceptance
per Phase 30 Definition of Done.
