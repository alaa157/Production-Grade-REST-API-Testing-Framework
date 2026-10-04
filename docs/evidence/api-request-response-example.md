# Example API request/response — full lifecycle (live, 2026-10-04)

> Transcript of real calls against `https://restful-booker.herokuapp.com`
> (token redacted to length; booking ID was live at capture time and has
> since been deleted as part of the transcript itself).

## 1. Authenticate — `POST /auth`

```http
POST /auth HTTP/1.1
Content-Type: application/json

{"username": "admin", "password": "password123"}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8

{"token": "<15-char hex>"}
```

Observed: `200`, JSON, exactly one key (`token`). Failure modes return the
same `200` with `{"reason": "Bad credentials"}` instead — see `AUTH-002…005`
and defect D-003.

## 2. Create — `POST /booking`

```http
POST /booking HTTP/1.1
Content-Type: application/json
Accept: application/json

{
  "firstname": "Evidence",
  "lastname": "Showcase",
  "totalprice": 150,
  "depositpaid": true,
  "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-05"},
  "additionalneeds": "Breakfast"
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8

{"bookingid": 2264, "booking": {
  "firstname": "Evidence",
  "lastname": "Showcase",
  "totalprice": 150,
  "depositpaid": true,
  "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-05"},
  "additionalneeds": "Breakfast"
}}
```

## 3. Retrieve — `GET /booking/2264`

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8

{"firstname": "Evidence", ..., "additionalneeds": "Breakfast"}
```

Observed: **round-trip equal** — `GET` body identical to the created
`booking` object (`BOOK-002`, the data-integrity anchor asserted on every
create/update/patch test).

## 4. Delete — `DELETE /booking/2264`

```http
DELETE /booking/2264 HTTP/1.1
Cookie: token=<token>
```

```http
HTTP/1.1 201 Created
Content-Type: text/plain; charset=utf-8

Created
```

Observed: `201` + `Created` (`text/plain`), **not** 200/204 + JSON — the
contract quirk pinned in `BOOK-010` / D-005. Follow-up `GET` returns `404`
`Not Found` (the verify-gone proof, `NEG-012`).
