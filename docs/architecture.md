# Architecture (placeholder — diagrams: Phase 25)

> Status: skeleton created in Phase 0.

Planned:

```mermaid
flowchart TD
    A[RESTful Booker API] --> B[Postman Collection]
    A --> C[Python API Tests]
    B --> D[Newman]
    C --> E[Pytest]
    D --> F[GitHub Actions]
    E --> F
    F --> G[Test Reports]
    F --> H[CI Pass / Fail]
```

Repository separation: `docs/` (documentation), `postman/` (collections,
environments, schemas), `tests/` + `src/` (Python automation), `.github/`
(CI), `reports/` (generated artifacts, git-ignored except `.gitkeep`).
