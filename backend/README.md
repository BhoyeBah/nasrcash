# NasrCash Backend

FastAPI backend for the NasrCash MVP (sandbox mode) — see `../CAHIER_DES_CHARGES_NASRCASH.md`
and `../NASRCASH_TECH_SPEC.md` for the full product and technical specification.

## Local development

```bash
cp .env.example .env
docker compose up -d postgres redis
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Health check: `GET /health`

## Tests

Tests run against a real Postgres database (`nasrcash_test`) — no sqlite shortcuts,
since ledger/money correctness needs to be verified against the real engine.

```bash
createdb -O nasrcash nasrcash_test   # once
pytest
```

## Architecture

- **Modular monolith**: each business domain lives in `app/modules/<name>/` with its
  own `router.py`, `service.py`, `models.py`, `schemas.py`.
- **Sandbox-first**: external providers (Mobile Money, card issuing, FX) are accessed
  only through abstract interfaces in `app/modules/providers/`; the `Mock*` implementations
  are the only ones wired up until real partnerships are integrated.
- **Ledger is the source of truth**: `app/modules/ledger` implements an append-only,
  double-entry `LedgerService`. Cached balance columns on `wallets`/`card_balances` are
  projections, never written to directly.
- **Idempotent money operations**: every monetary operation carries a `reference` key;
  replaying a request must not double-write.
