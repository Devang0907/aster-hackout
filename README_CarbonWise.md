# CarbonWise

**CarbonWise** is an AI-powered industrial carbon-emission analysis and recommendation backend built for Aster Hackout 2026.

The current backend uses:

- **FastAPI** for HTTP APIs
- **Neon PostgreSQL** as the primary database
- **psycopg 3** for asynchronous PostgreSQL access
- **scikit-learn** for ML-based CO2-reduction prediction
- **Random Forest** as the currently selected recommendation model
- **pytest** for database, API, ML, emission, recommendation, and end-to-end tests

---

## 1. Current Architecture

```text
React / Vite frontend
        |
        v
     FastAPI
        |
        +-----------------------------+
        |                             |
        v                             v
backend/services/data_api.py   Recommendation Engine
        |                             |
        v                             +--> candidate generation
backend/services/db_api.py            +--> Random Forest prediction
        |                             +--> ROI calculation
        v                             +--> feasibility scoring
 Neon PostgreSQL                      +--> final ranking
        ^                             |
        |                             v
        +------ saved recommendations +
```

The main flow for emission analysis is:

```text
Factory data in Neon
        |
        v
Emission calculation
        |
        v
Carbon result + ranked emission sources
        |
        v
ML recommendation engine
        |
        v
Predicted CO2 reduction + ROI + feasibility + score
        |
        v
Top recommendations
        |
        v
Saved back to Neon
```

---

## 2. Project Structure

```text
aster-hackout/
|
|-- .env                  # local secrets; never commit
|-- .env.example          # safe configuration template
|-- .gitignore
|-- pytest.ini
|-- README.md
|-- README_CarbonWise.md
|
|-- backend/
|   |-- main.py
|   |-- config.py
|   |-- requirements.txt
|   |
|   |-- api/
|   |   |-- emissions.py
|   |   |-- energy.py
|   |   |-- factories.py
|   |   |-- logistics.py
|   |   |-- materials.py
|   |   |-- recommendations.py
|   |   |-- simulations.py
|   |   `-- waste.py
|   |
|   `-- services/
|       |-- data_api.py
|       |-- db_api.py
|       |-- emission_service.py
|       |-- recommendation_service.py
|       `-- simulation_service.py
|
|-- recommendation_engine/
|   |-- main.py
|   |
|   |-- data/
|   |   `-- interventions.py
|   |
|   |-- ml/
|   |   |-- dataset.csv
|   |   |-- model.pkl
|   |   `-- train.py
|   |
|   |-- models/
|   |   `-- recommendation_model.py
|   |
|   `-- services/
|       |-- candidate_generator.py
|       |-- ml_predictor.py
|       |-- recommendation_engine.py
|       `-- score_calculator.py
|
|-- tests_neon/
|   |-- conftest.py
|   |-- test_database.py
|   |-- test_fastapi.py
|   |-- test_ml_model.py
|   |-- test_recommendation_engine.py
|   |-- test_emissions.py
|   |-- test_recommendations_api.py
|   `-- test_e2e.py
|
```

---

## 3. Requirements

Recommended:

- Python 3.11+
- Git
- A Neon PostgreSQL database

Check versions:

```powershell
python --version
git --version
```

Install project dependencies:

```powershell
python -m pip install -r backend\requirements.txt
```

The backend requires packages including:

```text
fastapi
uvicorn
psycopg[binary]
pandas
joblib
scikit-learn
python-dotenv
pytest
httpx
```

---

## 4. Environment Configuration

Copy the example file:

```powershell
Copy-Item .env.example .env
```

Configure `.env`:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require
FRONTEND_URL=http://localhost:5173
```

### Important

- Never commit `.env`.
- Never put the real Neon password in `.env.example`.
- `.env.example` should contain placeholders only.
- The root `.gitignore` already excludes `.env` and `.env.*`, while allowing `.env.example`.

If `.env` was ever committed before adding it to `.gitignore`, ignoring it is not enough. Remove it from Git tracking once:

```powershell
git rm --cached .env
```

Then rotate the exposed database password if the secret was pushed to a remote repository.

---

## 5. Start the FastAPI Backend

From the project root in PowerShell:

```powershell
$env:PYTHONPATH="$PWD;$PWD\backend"
python -m uvicorn backend.main:app --reload --port 8000
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

---

## 6. Neon Database

CarbonWise currently uses the following PostgreSQL tables:

```text
users
factories
reporting_periods
materials
material_alternatives
factory_material_usage
energy_usage
waste_streams
logistics
emission_factors
ml_pipeline_runs
carbon_results
emission_sources
interventions
recommendations
simulations
carbon_credit_results
audit_logs
```

Database access goes through:

```text
backend/services/data_api.py
        |
        v
backend/services/db_api.py
        |
        v
Neon PostgreSQL
```

Application API code uses `data_api.py`, which delegates directly to the Neon PostgreSQL database service.

---

## 7. Emission Calculation

Run an emission calculation with:

```http
POST /api/emissions/{factory_id}/calculate
```

The emission service calculates categories including:

- Electricity
- Fuel
- Raw materials
- Transport
- Waste

It stores or updates:

- `carbon_results`
- `emission_sources`

Emission sources are ranked from highest to lowest contribution.

Example flow:

```text
Electricity data -----+
Material usage -------+
Waste ----------------+--> emission_service.py --> carbon_results
Logistics ------------+                           emission_sources
Emission factors -----+
```

---

## 8. ML Recommendation Engine

The recommendation engine is called by the FastAPI recommendation service.

```text
Carbon result
    |
    v
Emission vector
    |
    v
Ranked sources
    |
    v
Candidate interventions
    |
    v
model.pkl
    |
    v
Predicted CO2 reduction
    |
    +--> ROI
    +--> feasibility
    `--> recommendation score
             |
             v
          Top 3
```

Current model inputs:

```text
electricity_emission
diesel_emission
raw_material_emission
waste_emission
transport_emission
cost
savings
feasibility
```

The current trained model was selected by comparing multiple regressors and is stored at:

```text
recommendation_engine/ml/model.pkl
```

The model file is intentionally committed because the application needs it at runtime.

---

## 9. Retrain the ML Model

Training data:

```text
recommendation_engine/ml/dataset.csv
```

Train from the project root:

```powershell
python -m recommendation_engine.ml.train
```

The training script compares supported models using cross-validation and writes the selected model to:

```text
recommendation_engine/ml/model.pkl
```

Restart FastAPI after retraining because the model is loaded when the prediction module is imported.

---

## 10. Testing

The current Neon-based tests are in:

```text
tests_neon/
```

They run against the FastAPI, Neon PostgreSQL, and ML stack.

Run all current backend tests:

```powershell
$env:PYTHONPATH="$PWD;$PWD\backend"
pytest tests_neon -v
```

The suite covers:

- Neon connection
- expected PostgreSQL tables
- factory data
- FastAPI routes
- emission calculation
- emission-source ranking
- ML model loading
- ML predictions
- recommendation scoring
- ROI calculation
- recommendation API
- saved recommendations
- full Neon -> emissions -> ML -> Neon flow

Current verified result:

```text
23 passed
```

### Windows event-loop configuration

`psycopg.AsyncConnection` cannot use Windows' `ProactorEventLoop` in this test setup. `tests_neon/conftest.py` therefore uses `WindowsSelectorEventLoopPolicy` on Windows.

`pytest.ini` contains:

```ini
[pytest]
asyncio_mode = auto
```

---

## 11. Main API Endpoints

Common endpoints include:

```text
GET  /health
GET  /api/factories/
GET  /api/factories/{factory_id}
POST /api/emissions/{factory_id}/calculate
GET  /api/recommendations/{factory_id}
POST /api/recommendations/{factory_id}/generate
```

Additional APIs exist for energy, materials, waste, logistics, and simulations.

Use Swagger for the complete route list:

```text
http://127.0.0.1:8000/docs
```

---

## 12. Git Safety Before Committing

Check the active branch:

```powershell
git branch
```

Inspect changes:

```powershell
git status
```

Verify that `.env` is ignored:

```powershell
git check-ignore -v .env
```

Stage the project:

```powershell
git add .
```

Check staged files **before committing**:

```powershell
git status
```

The real `.env` must not appear under "Changes to be committed".

Commit example:

```powershell
git commit -m "Migrate backend to Neon and integrate ML recommendations"
```

Push the FullBackend branch:

```powershell
git push origin FullBackend
```

---

## 14. Security Notes

Never commit:

```text
.env
real database passwords
API keys
private tokens
local credential files
```

Safe to commit:

```text
.env.example
recommendation_engine/ml/model.pkl
recommendation_engine/ml/dataset.csv
tests_neon/
pytest.ini
```

Before pushing to a public remote, always review:

```powershell
git diff --cached
```

---

# CarbonWise Backend Status

```text
FastAPI                 OK
Neon PostgreSQL         OK
Emission calculation    OK
Emission ranking        OK
Random Forest ML        OK
Recommendation engine   OK
Saved recommendations   OK
End-to-end tests         OK
```
