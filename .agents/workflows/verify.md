---
description: Run lint/tests for backend & frontend and report pass/fail with logs.
---

---
description: Run lint/tests for backend & frontend and report pass/fail with logs.
---

# /verify

## Backend verify (FastAPI)
1) Ensure venv is active (if needed, activate it)
2) Run:
- `python -m pytest -q`

## Frontend verify (Vue3)
1) Go to frontend directory
2) Install deps if needed, then test:
- `npm test`  (or `npm run test` depending on package.json)

## Smoke check (optional but recommended)
- Ensure backend exposes GET /health
- Run:
  - `python -m uvicorn backend.main:app --port 8000`
  - In another terminal: `curl http://127.0.0.1:8000/health`
- Stop server after check

## Output
- Summarize:
  - Which commands ran
  - What failed (if anything)
  - Which files were touched to fix it