# SecureNotes — Make It Fast & Fair, Then Ship It (Weeks 16–17)

Student starter. The SecureNotes API is finished and secure; this lab is about
the front end and the pipeline around it.

- **Part A (Week 16):** make `app/static/` accessible (WCAG) and fast.
- **Part B (Week 17):** write `.github/workflows/ci.yml` so every push runs the checks.
- **Part C:** push, open a PR, watch the pipeline go green, peer review.

**Start with `TASKS.md`** — it lists every task in order and the exact command to
check each one.

## Quick start

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload     # http://127.0.0.1:8000/app/
pytest -q                         # the app's 12 tests pass; many checks start red
```

## Accounts

| username | password   | role  |
|----------|------------|-------|
| admin    | admin123   | admin |
| alice    | alicepass  | owns note 1 |
| bob      | bobpass    | owns note 2 |

## Keep the bcrypt pin

`requirements.txt` pins `bcrypt==4.0.1` on purpose — newer bcrypt breaks passlib.
Don't bump it.

## What you edit

```
app/static/index.html      <- Part A (TASKs 1, 2, 3, 5)
app/static/styles.css      <- Part A (TASK 4)
.github/workflows/ci.yml   <- Part B (TASKs 6, 7)
```

Everything else — the API in `app/main.py`, and the tests — stays as given.
Don't edit the tests; make them pass.
