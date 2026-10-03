# Technique Reference — test-case-designer

Quick reference for constructing each test design technique artifact.
Claude loads this file when it needs mechanical details during Phase 2.5 or Phase 3.

---

## Layer 1: Scenario-Based Testing

### Flow Types to Identify

| Flow Type | Description | Example |
|---|---|---|
| Main success path | The happy path — all inputs valid, system behaves as designed | User logs in with correct credentials |
| Alternate path | Valid but non-default route through the feature | User logs in via SSO instead of password |
| Exception path | System handles invalid input or error state gracefully | User enters wrong password 3× → account locked |

### Scenario Case Template

For each flow, write one row:
- **Preconditions**: system state required before starting
- **Steps**: numbered actions (keep to 3–7 steps)
- **Expected Result**: observable system output

### Smoke Selection Rule

Mark the primary main-success-path case as `Smoke ✓`. Typically 1–3 cases per module. Smoke cases must be independently runnable (no dependency on prior test execution).

---

## Layer 2: Equivalence Partitioning + Boundary Value

### Equivalence Class Construction

For each input field, define:

| Class Type | Rule | Example (age field, valid range 18–120) |
|---|---|---|
| Valid equivalence class | Values the system accepts normally | age = 25 |
| Invalid equivalence class (below) | Values below the valid range | age = 10 |
| Invalid equivalence class (above) | Values above the valid range | age = 150 |
| Invalid equivalence class (type) | Wrong data type or format | age = "abc" |
| Invalid equivalence class (empty) | Null or empty input | age = "" |

### Boundary Value Points

For a numeric field with valid range [min, max], test these 6 points:

| Point | Formula | Example (18–120) |
|---|---|---|
| Just below minimum | min − 1 | 17 |
| Minimum | min | 18 |
| Just above minimum | min + 1 | 19 |
| Just below maximum | max − 1 | 119 |
| Maximum | max | 120 |
| Just above maximum | max + 1 | 121 |

For string length fields (min_len to max_len), apply the same formula to character counts.

### Equivalence Class Table Format (for Phase 2.5)

| Field | Valid Class | Invalid Class(es) | Boundary Points |
|---|---|---|---|
| Username | 1–32 alphanumeric chars | Empty, >32 chars, special chars | 1 char, 32 chars, 33 chars |
| Password | 8–64 chars, any printable | Empty, <8 chars, >64 chars | 7 chars, 8 chars, 64 chars, 65 chars |

---

## Layer 3: Decision Table

### Construction Steps

1. List all conditions (inputs that affect behavior) as rows
2. List all actions (system outputs/behaviors) as rows below conditions
3. Create one column per unique combination of condition values
4. Fill in Y/N (or specific values) for each condition per column
5. Fill in the resulting action for each column
6. **Collapse**: merge columns with identical actions → reduces test cases

### Decision Table Template

```
| Condition / Action     | Rule 1 | Rule 2 | Rule 3 | Rule 4 |
|------------------------|--------|--------|--------|--------|
| C1: User authenticated | Y      | Y      | N      | N      |
| C2: Cart not empty     | Y      | N      | Y      | N      |
|------------------------|--------|--------|--------|--------|
| A1: Proceed to payment | ✓      |        |        |        |
| A2: Show empty cart    |        | ✓      |        |        |
| A3: Redirect to login  |        |        | ✓      | ✓      |
```

### Collapsing Rules

- Two columns with the same action set can be merged if one condition value differs and the other conditions are identical
- Use `—` (don't care) for the differing condition in the merged column

---

## Layer 4: Orthogonal Array (Pairwise)

### When to Use

Trigger: 3 or more parameters, each with 2 or more values. Do NOT use for 1–2 parameters — use full Cartesian product instead.

### Script Invocation

```bash
python scripts/allpairs.py \
  --input '{"parameters": {"param1": ["v1","v2"], "param2": ["v1","v2","v3"], "param3": ["v1","v2"]}}'
```

Note: The script is located in the skill's `scripts/` directory. Use `python` command directly (ensure Python is in your PATH).

### Factor-Level Extraction Table (for Phase 2.5)

List parameters and their values before running the script:

| Factor (Parameter) | Levels (Values) | Count |
|---|---|---|
| Browser | Chrome, Firefox, Safari | 3 |
| OS | Windows, macOS, Linux | 3 |
| Language | EN, ZH | 2 |

Cartesian product = 3 × 3 × 2 = **18 cases**. AllPairs reduces this to ≈9 cases with full pairwise coverage.

### Using Script Output

Each row from allpairs.py output becomes one test case row:
- `Technique` column: `Orthogonal`
- `Test Level`: `UI` (or adjust based on what the parameters control)
- `Steps`: "Configure [param1]=[v1], [param2]=[v2], [param3]=[v3], then execute the target action"
- `Expected Result`: same for all orthogonal rows unless a specific combination has a known different outcome

---

## Layer 5: Workflow / State Transition

### State Transition Diagram (Mermaid format for Phase 2.5)

```
stateDiagram-v2
    [*] --> Draft
    Draft --> PendingReview : submit()
    PendingReview --> Approved : approve()
    PendingReview --> Rejected : reject()
    Approved --> Published : publish()
    Rejected --> Draft : revise()
    Published --> [*]
```

### Test Case Types for State Transitions

| Type | Description | Example |
|---|---|---|
| Valid transition | Execute each arrow in the diagram | Draft → PendingReview via submit() |
| Invalid transition | Attempt a transition not shown in diagram | Draft → Published directly (should fail) |
| Skip-step attempt | Jump over an intermediate state | Draft → Approved without PendingReview |
| Boundary state | Test entry and exit of each state node | Verify system shows "Pending" status after submit() |

### Coverage Rule

Every state node must appear in at least one test case as: (a) entry point and (b) exit point.

---

## Layer 6: Error Guessing

### Standard Error Guessing Checklist

Apply these to every module regardless of other layers:

| Category | Test Ideas |
|---|---|
| **Empty / Null** | Leave required fields blank; submit with all fields empty |
| **Extreme values** | Maximum integer (2^31−1), minimum integer, very long strings (1000+ chars) |
| **Special characters** | `<script>alert(1)</script>`, `' OR 1=1--`, `../../../etc/passwd`, `\0`, emoji |
| **Wrong type** | Enter letters in numeric fields, numbers in date fields |
| **Wrong sequence** | Skip a step, go back and resubmit, double-submit a form |
| **Concurrent actions** | Open same resource in two tabs, submit simultaneously |
| **Network/timing** | Disconnect mid-operation, very slow response (if testable) |
| **Boundary of business rules** | Values at exact policy limits (e.g. max items in cart) |

### Risk-Ordered Output

In Phase 2.5 Error Guessing Analysis section, sort defect-prone areas by risk:
1. 🔴 High: Security inputs (XSS, SQLi), authentication bypass attempts, data corruption paths
2. 🟡 Medium: Business rule violations, state corruption, double-submit
3. 🟢 Low: UI edge cases, cosmetic issues under extreme inputs

---

## RTM Template (for Phase 2.5 Section 11)

| Requirement ID | Requirement Summary | Test Case IDs | Coverage Status |
|---|---|---|---|
| REQ-001 | User can log in with valid credentials | TC-001, TC-002 | ✅ Covered |
| REQ-002 | Account locks after 3 failed attempts | TC-015, TC-016 | ✅ Covered |
| REQ-003 | Password reset sends email within 60s | TC-031 | ✅ Covered |

> Test Case IDs column is blank during Phase 2.5 and backfilled after Phase 4 completes.

---

## Risk Level Definitions

| Level | Assign when | P1 density | P2 density |
|---|---|---|---|
| 🔴 High | New feature, historically buggy area, complex conditional logic, security-related | ≥3 cases | ≥2 cases |
| 🟡 Medium | Modified existing feature, moderate complexity, non-critical data | ≥2 cases | ≥1 case |
| 🟢 Low | Stable unchanged area, display-only, low user impact | ≥1 case | discretionary |

---

## Test Level Definitions

| Level | Assign when | Automation potential |
|---|---|---|
| `UI` | Verification requires browser/app interaction | Selenium, Cypress, Appium |
| `API` | Can verify via HTTP request without UI | REST-assured, Postman, pytest |
| `DB` | Must query database to verify correct persistence | SQL query in test teardown |
| `Logic` | Pure business rule, no I/O needed | Unit test framework |

One case may have multiple levels: `UI/DB` means both UI interaction and DB state verification are required.
