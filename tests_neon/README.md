# Neon / FastAPI / ML Tests

These tests do **not** use JSON Server.

They test:

- FastAPI in-process using `TestClient`
- Neon PostgreSQL
- Database schema
- ML `model.pkl`
- ML prediction
- Recommendation engine
- Emission calculations
- Saved recommendations
- End-to-end Neon -> emissions -> ML -> Neon flow

## Install test dependencies

```powershell
python -m pip install pytest python-dotenv httpx
```

`psycopg`, FastAPI, pandas, joblib and scikit-learn should already be installed by the backend.

## Run

From the project root:

```powershell
$env:PYTHONPATH="$PWD;$PWD\backend"
pytest tests_neon -v
```

You do NOT need to run Uvicorn in a second terminal.

## Important

Your project root `.env` must contain:

```env
DATA_BACKEND=db
DATABASE_URL=postgresql://...
```

## UUID route

If this test fails with `422`:

```text
test_factory_by_uuid
```

check `backend/api/factories.py`.

Because Neon IDs are UUIDs, factory path parameters should be strings:

```python
@router.get("/{factory_id}")
async def get_factory(factory_id: str):
    ...
```

The same applies to update/delete routes when they use UUID IDs.
