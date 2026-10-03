# Installed Agent Skills

Inventory of agent skills installed into `/workspaces/testing2/.opencode/skills/` for opencode.
All skills are `SKILL.md`-based (folder name matches frontmatter `name`); they load via opencode's
progressive disclosure (name+description at startup, full body on activation).

**Totals:** 41 installed · 41 discovered by opencode (verified) · 1 pre-existing built-in (`customize-opencode`).

## Installed skills

| Skill | Source repo | Category | Purpose | Status |
|---|---|---|---|---|
| test-planning | petrkindlmann/qa-skills | QA / Test Management | Sprint/release test plan: scenario decomposition, coverage mapping, effort estimation, risk prioritization | Installed |
| test-strategy | petrkindlmann/qa-skills | QA / Test Management | Multi-quarter QA strategy: test pyramid, entry/exit criteria, quality KPIs, tool selection, CI scaling | Installed |
| test-case-management | petrkindlmann/qa-skills | QA / Test Management | Author manual/hybrid test cases in TestRail, Xray, Zephyr Scale, Qase from user stories | Installed |
| test-case-designer | ll0v0ll/test-case-designer | QA / Test Design | Systematic test design: equivalence partitioning, BVA, decision tables, pairwise (bundled `allpairs.py`), state transition, error guessing; outputs analysis doc + 10-column test case table | Installed |
| exploratory-testing | petrkindlmann/qa-skills | QA / Test Design | Structured exploratory sessions: SBTM, charters, HICCUPS/FW HICCUPS heuristics, findings → automated tests | Installed |
| test-gap-audit | github/awesome-copilot | QA / Test Design | Read-only audit for missing/weak/stale/mis-scoped test coverage across a repo or named scope | Installed |
| bug-reproduction | petrkindlmann/qa-skills | QA / Test Design | Turn vague bug reports into verified minimal repro + failing regression test (minimize/isolate, git bisect) | Installed |
| coverage-analysis | petrkindlmann/qa-skills | QA / Test Design | Meaningful coverage: gap analysis by risk, coverage ratchet in CI, mutation testing, no vanity metrics | Installed |
| release-readiness | petrkindlmann/qa-skills | QA / Release | Evidence-based go/no-go: checklists, smoke suites, staged rollout, rollback criteria, post-deploy verification | Installed |
| api-testing | petrkindlmann/qa-skills | QA / Automation | REST/GraphQL API tests (Playwright APIRequestContext, Supertest): schema validation, auth, CRUD, pagination, perf asserts | Installed |
| contract-testing | petrkindlmann/qa-skills | QA / Automation | Consumer-driven contracts with Pact-JS v16: broker, can-i-deploy gate, webhooks, OpenAPI/Ajv schemas | Installed |
| database-testing | petrkindlmann/qa-skills | QA / Automation | DB integrity, forward/backward migrations, constraints, seed data, drift, query perf; Testcontainers | Installed |
| ci-cd-integration | petrkindlmann/qa-skills | QA / Automation | CI/CD test pipelines: GitHub Actions/GitLab CI, sharding, flaky quarantine, coverage gates, OIDC deploy | Installed |
| playwright-automation | petrkindlmann/qa-skills | QA / Automation | Production-grade Playwright TS: POM, fixtures, locators, parallelism, sharding, AI "do not" list | Installed |
| cypress-automation | petrkindlmann/qa-skills | QA / Automation | Cypress TS E2E/component suites: cy.intercept, cy.session, cy.origin, fixtures, Cloud, CI | Installed |
| accessibility-testing | petrkindlmann/qa-skills | QA / Automation | WCAG 2.2 AA: axe-core + Playwright, keyboard/screen-reader audits, ADA/EAA/Section 508 mapping | Installed |
| security-testing | petrkindlmann/qa-skills | QA / Automation | OWASP Top 10 (2025): ZAP DAST, OSV-Scanner/SBOM, Semgrep SAST, JWT/OAuth/RBAC tests, XSS/CSRF patterns | Installed |
| webapp-testing | anthropics/skills | QA / Automation | Playwright toolkit for local web apps: verify frontend, debug UI, screenshots, browser logs | Installed |
| skill-creator | anthropics/skills | Agent meta | Create/improve skills, run evals, benchmark and optimize skill descriptions | Installed |
| test-driven-development | obra/superpowers | Software Engineering | Red-green-refactor discipline: write failing test before implementation | Installed |
| systematic-debugging | obra/superpowers | Software Engineering | Structured debugging loop for any bug/failure before proposing fixes | Installed |
| verification-before-completion | obra/superpowers | Software Engineering | Run verification commands and confirm output before claiming work complete/passing | Installed |
| code-review-and-quality | addyosmani/skills | Software Engineering | Multi-axis code review before merging any change | Installed |
| git-workflow-and-versioning | addyosmani/skills | Software Engineering | Branching, atomic commits, conflict resolution, PR handling, versioning | Installed |
| documentation-and-adrs | addyosmani/skills | Software Engineering | ADRs and documentation for API changes, features, design decisions | Installed |
| security-and-hardening | addyosmani/skills | Software Engineering | OWASP Top 10 hardening of inputs, auth, data storage, integrations | Installed |
| api-and-interface-design | addyosmani/skills | Software Engineering | Stable REST/GraphQL endpoints, type contracts, module boundaries | Installed |
| github-actions-hardening | github/awesome-copilot | Software Engineering | Actions threat model: script injection, mutable refs, over-scoped tokens | Installed |
| security-review | github/awesome-copilot | Software Engineering | AI-reasoning codebase security scan (data-flow tracing, beyond pattern matching) | Installed |
| refactor | github/awesome-copilot | Software Engineering | Behavior-preserving refactoring: extract functions, god-function breakup, code smells | Installed |
| documentation-writer | github/awesome-copilot | Software Engineering | Diátaxis-based technical documentation | Installed |
| architecture-blueprint-generator | github/awesome-copilot | Software Engineering | Generates architectural blueprints/diagrams from detected stack and patterns | Installed |
| multi-stage-dockerfile | github/awesome-copilot | Software Engineering | Optimized multi-stage Dockerfiles for any language | Installed |
| javascript-typescript-jest | github/awesome-copilot | Software Engineering | Jest best practices: mocking, async, snapshots, React Testing Library | Installed |
| shell-scripting | mitch-avis/agent-skills | Software Engineering | Production Bash/PowerShell: strict mode, quoting, traps, ShellCheck/shfmt, Bats/Pester (8 reference files) | Installed |
| gh-fix-ci | openai/skills | Software Engineering | Debug/fix failing GitHub Actions PR checks via `gh` (fix only after approval) | Installed |
| fastapi | fastapi/fastapi | Framework / Stack | Official FastAPI conventions: Pydantic, dependencies, SSE, frontend serving | Installed |
| pytest-skill | lambdatest/skills | Framework / Stack | Production pytest: fixtures, parametrize, markers, mocking, conftest patterns | Installed |
| selenium-skill | lambdatest/skills | Framework / Stack | Selenium WebDriver tests in Java/Python/JS/C#/Ruby/PHP + cross-browser cloud | Installed |
| newman-script-helper | lambdatest/skills | QA / Automation | Correct Newman CLI flags/reporters for running Postman collections | Installed |
| web-design-guidelines | vercel (Vercel skill pack) | Framework / Stack | Review UI code against Web Interface Guidelines (a11y, UX, design) | Installed |

## Source repositories

- https://github.com/petrkindlmann/qa-skills
- https://github.com/anthropics/skills
- https://github.com/obra/superpowers
- https://github.com/addyosmani/skills
- https://github.com/LambdaTest/skills
- https://github.com/github/awesome-copilot
- https://github.com/openai/skills
- https://github.com/ll0v0ll/test-case-designer
- https://github.com/mitch-avis/agent-skills
- https://github.com/fastapi/fastapi (skill in `backend/.opencode/skill/fastapi/`)
- Vercel web-design-guidelines skill pack

All skills were inspected before copying (frontmatter validity, content quality, relative-link
integrity, security-pattern scan — flagged matches were legitimate security-guidance text).

## Rejected candidates (reasons)

| Candidate | Reason |
|---|---|
| openai/skills full set (all folders) | Repo archived/deprecated in favor of OpenAI plugins; only `gh-fix-ci` taken (unique, relevant) |
| anthropics/skills document skills (docx, pdf, xlsx, pptx, docx) | Document generation, not SWE/QA scope |
| anthropics/skills mcp-builder, slack-gif-creator, canvas-design | Out of scope (MCP authoring/design) |
| cloudflare/skills | Cloudflare-platform-specific |
| LambdaTest playwright-skill, cicd-pipeline-skill | Duplicates of qa-skills playwright-automation / ci-cd-integration |
| qa-skills cypress-automation vs LambdaTest cypress | Kept qa-skills version (TypeScript, more current) |
| obra/superpowers writing-plans, brainstorming | Planning/meta skills; overlaps opencode built-ins — not SWE/QA core |
| addyosmani ci-cd-and-automation, debugging-and-error-recovery, test-driven-development | Duplicate coverage (qa-skills ci-cd-integration, superpowers TDD/debugging) |
| mattpocock/skills (tdd, code-review, improve-codebase-architecture) | Claude-Code-specific (`disable-model-invocation`, `Skill tool` calls, GLOSSARY.md/ADR conventions); duplicates superpowers/addyosmani skills |
| proffesor-for-testing/agentic-qe | Tightly coupled to its custom qe-agent framework (FleetManager/Task calls) |
| skill-tools, agentskill-sh/learn, review-skill | Tooling/meta for skills, not SWE/QA capability skills |
| mitch-avis non-shell skills (python*, rust*, docker, cicd, kubernetes…) | Would bloat inventory; overlaps already-installed skills; shell-scripting only (unique gap) |

## Remaining gaps

- **Performance/load testing** — no dedicated skill (k6, JMeter, Locust).
- **Mobile/native app testing** — Appium/XCUITest not covered.
- **TypeScript/JavaScript general** — Jest covered; Vitest-specific skill not installed (Jest guidance largely transfers).
- **Test case management platforms** — TestRail/Xray/Zephyr covered for authoring; no skill for API-driven execution/reporting from those platforms.
- **Requirements traceability beyond test-case-designer's RTM** — no DOORS/Polarion-style ALM integration skill.

## Verification

- Structural validation: 41/41 have valid YAML frontmatter, `name` == folder name, description
  present and specific, no broken relative links, no duplicate names, description < 1024 chars.
- opencode discovery: `opencode debug skill` output (64 KB truncation — sampled repeatedly until
  stable, 80 iterations) contains all 41 installed names plus built-in `customize-opencode`
  (42 unique); zero installed skills missing.
- Note: config only loads at startup — restart opencode to pick up this inventory.
