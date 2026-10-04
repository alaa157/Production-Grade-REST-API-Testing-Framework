# Portfolio Audit (Phase 28)

> Refreshed 2026-10-04 after reviewing the current README, docs, test suite,
> workflow definitions, and latest hosted green runs. Findings distinguish
> observed evidence from configuration-based inference.

| Question | Verdict |
| --- | --- |
| Recruiter understands it in 30 seconds? | **Yes.** Title + 2 CI badges + 4-line summary + verified-counts note are above the fold; coverage table gives numbers without scrolling far. |
| Developer can clone and run it? | **Yes.** `run_tests.sh` creates venv + installs + runs; `run_postman.sh` degrades cleanly (`npm ci` hint if Newman missing). Config needs no secrets. |
| Actual testing skill demonstrated? | **Yes.** 56 frozen scenarios across 8 types; observed (not assumed) contracts; dual-harness agreement as the correctness bar. |
| Tests meaningful? | **Yes** (see `docs/quality-review.md` — zero vacuous asserts by grep). |
| Negative testing evident? | **Yes.** 24 scenarios + dedicated Postman folder 07 + D-001…D-007. |
| Schema validation implemented? | **Yes.** 4 strict contracts × 2 harnesses, with a worked example (`docs/evidence/schema-validation-example.md`). |
| Authentication handled? | **Yes.** Both mechanisms, all 403 paths per method, body-based failure asserts. |
| CI automation present? | **Yes.** Both workflows have successful hosted runs and fail-closed test steps. Local red-path simulations are recorded; a deliberately failing hosted run has not been observed (`docs/failure-simulation.md`). |
| Reproducible? | **Yes.** Pinned installs, env-var config, no hardcoded live IDs or volatile result counts. |
| README shows business value? | **Yes.** Defect impacts, honesty note on host volatility, evidence-first presentation. |
| Looks maintained, not tutorial? | **Mostly.** One grep hit for "placeholder" is a legitimate history note (`test-plan.md:145`). No lorem/TODO/FIXME anywhere. |

## Fixes applied in this phase

- Corrected lifecycle docs to show GET verification after PUT and PATCH.
- Tightened malformed-ID and re-delete tests to check observed response body
  and content type as well as status.
- Replaced the stale claim about uncommitted phases with current evidence and
  explicit open limitations.

## Known leftovers (not hidden)

1. **Hosted failure run pending.** The deliberate red paths have only been
   run locally; verify that a test failure marks a GitHub Actions job red.
2. **Manual screenshots pending.** Shot list in `docs/evidence/README.md`;
   text evidence stands alone until a human captures them.
3. **`docs/installed-agent-skills.md`** is agent-tooling inventory, not
   portfolio content, and is deliberately unlinked from the README's doc
   guide. Left in place (tooling-owned); ignore it in reviews.
