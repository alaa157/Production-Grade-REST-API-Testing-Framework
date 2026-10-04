# Example schema validation (live contract, quoted verbatim)

## The contract — `tests/schemas/auth-schema.json`

( byte-identical copy of `postman/schemas/auth-schema.json` )

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Auth response",
  "description": "POST /auth returns exactly one of the success token shape or the failure reason shape.",
  "oneOf": [
    {
      "type": "object",
      "required": ["token"],
      "properties": {
        "token": { "type": "string", "minLength": 1 }
      },
      "additionalProperties": false
    },
    {
      "type": "object",
      "required": ["reason"],
      "properties": {
        "reason": { "type": "string", "enum": ["Bad credentials"] }
      },
      "additionalProperties": false
    }
  ]
}
```

Why this shape matters: the API returns `200` for **both** success and
failure, so status-code checks are worthless here. The schema enforces the
real discriminator — `token` xor `reason`, never both — which is exactly the
trap `AUTH-002…005` exist to catch (defect D-003).

## The assertion — pytest (`tests/api/test_auth.py`)

```python
response = _auth(api_client, auth_payloads()[credentials])

assert response.status_code == 200
validate_schema(response.json(), "auth-schema.json")
assert response.json() == {"reason": "Bad credentials"}
```

`validate_schema` (`tests/schema_validation.py`) resolves same-directory
`$ref`s locally and fails with `<path>: <message>` per violation, so a
contract break names the missing property or wrong type instead of dumping a
blob.

## The Postman mirror

The same contract is asserted inline on the token-issue responses via
`pm.response.to.have.jsonSchema()` against the embedded copy — one contract,
two harnesses. The remaining three contracts (`booking`, `booking-response`,
`booking-list`) follow the identical pattern; see `docs/traceability-matrix.md`
rows `CON-003…005`.
