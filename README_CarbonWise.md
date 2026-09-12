# CarbonWise

**CarbonWise** is an AI-powered industrial carbon-emission analysis and recommendation system built for Aster Hackout 2026.

The current backend uses:

- **FastAPI** for the application API
- **JSON Server** as a temporary/mock database API
- **Python recommendation engine** for emission-based recommendations
- **scikit-learn** for ML prediction
- **pytest** for backend and end-to-end testing

The project is structured so the JSON Server can later be replaced by a real database/API without rewriting the recommendation logic.

---

# 1. Project Structure

```text
aster-hackout/
│
├── .env
├── .env.example
├── .gitignore
├── README.md
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── start.bat
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── factories.py
│   │   ├── emissions.py
│   │   ├── recommendations.py
│   │   ├── simulations.py
│   │   ├── materials.py
│   │   ├── energy.py
│   │   ├── waste.py
│   │   └── logistics.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_api.py
│   │   ├── json_api.py
│   │   ├── emission_service.py
│   │   ├── recommendation_service.py
│   │   └── simulation_service.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── calculations.py
│       └── normalization.py
│
├── recommendation_engine/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── data/
│   │   └── interventions.py
│   │
│   ├── ml/
│   │   ├── dataset.csv
│   │   ├── model.pkl
│   │   └── train.py
│   │
│   ├── models/
│   │   └── recommendation_model.py
│   │
│   ├── services/
│   │   ├── candidate_generator.py
│   │   ├── ml_predictor.py
│   │   ├── recommendation_engine.py
│   │   └── score_calculator.py
│   │
│   └── utils/
│       └── normalization.py
│
├── json-server-api/
│   ├── db.json
│   ├── db.backup.json
│   ├── package.json
│   ├── package-lock.json
│   ├── routes.json
│   └── README.md
│
└── tests/
    ├── __init__.py
    ├── test_json_server.py
    ├── test_recommendation_engine.py
    ├── test_fastapi.py
    └── test_e2e.py
```

---

# 2. How CarbonWise Works

The current request flow is:

```text
UI
 │
 ▼
FastAPI
 │
 ▼
backend/services/data_api.py
 │
 ▼
backend/services/json_api.py
 │
 ▼
JSON Server
 │
 ▼
Emission data
 │
 ▼
Recommendation Engine
 │
 ├── Candidate generation
 ├── ML prediction
 ├── CO2 reduction estimation
 ├── ROI calculation
 ├── Feasibility calculation
 ├── Score calculation
 └── Ranking
 │
 ▼
Top recommendations
 │
 ▼
FastAPI
 │
 ▼
Saved to database API
 │
 ▼
Returned to UI
```

The recommendation engine is the source of truth for recommendation calculations.

FastAPI should **not duplicate** recommendation-engine logic.

FastAPI is responsible for:

- receiving HTTP requests
- reading factory/emission data
- calling the recommendation engine
- saving recommendation results
- returning JSON to the UI

The recommendation engine is responsible for:

- generating candidate interventions
- predicting emission reduction
- calculating ROI
- calculating feasibility
- scoring recommendations
- ranking recommendations
- returning the top recommendations

---

# 3. Requirements

Install:

- Python 3.11+
- Node.js + npm
- Git

Check versions:

```powershell
python --version
node --version
npm --version
git --version
```

---

# 4. Python Setup

Open PowerShell in the project root:

```powershell
cd C:\Users\Asus\Desktop\Projects\aster-hackout
```

Create a virtual environment if one does not already exist:

```powershell
python -m venv backend\venv
```

Activate it:

```powershell
.\backend\venv\Scripts\Activate.ps1
```

Install backend dependencies:

```powershell
pip install -r backend\requirements.txt
```

If pytest is not already installed:

```powershell
pip install pytest
```

---

# 5. Environment Variables

Create this file in the project root:

```text
.env
```

Example:

```env
DATA_BACKEND=json

JSON_SERVER_URL=http://localhost:3000

FRONTEND_URL=http://localhost:5173
```

Do not commit `.env`.

Use `.env.example` to document the required configuration:

```env
DATA_BACKEND=json
JSON_SERVER_URL=http://localhost:3000
DB_API_URL=http://localhost:9000
FRONTEND_URL=http://localhost:5173
```

---

# 6. Start the JSON Server

Open a new PowerShell terminal:

```powershell
cd C:\Users\Asus\Desktop\Projects\aster-hackout\json-server-api
```

Install packages if required:

```powershell
npm install
```

Start JSON Server:

```powershell
npm start
```

It should run at:

```text
http://localhost:3000
```

Example resources:

```text
http://localhost:3000/factories
http://localhost:3000/carbon_results
http://localhost:3000/recommendations
```

Keep this terminal open.

---

# 7. Start FastAPI

Open another PowerShell terminal.

Go to the project root:

```powershell
cd C:\Users\Asus\Desktop\Projects\aster-hackout
```

Activate the virtual environment:

```powershell
.\backend\venv\Scripts\Activate.ps1
```

Set the Python path:

```powershell
$env:PYTHONPATH = "$PWD;$PWD\backend"
```

Start FastAPI:

```powershell
python -m uvicorn backend.main:app --reload --port 8000
```

FastAPI should run at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

---

# 8. Important API Endpoints

## Health

```http
GET /health
```

Example:

```text
http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

---

## Factories

```http
GET /api/factories/
```

Get one factory:

```http
GET /api/factories/{factory_id}
```

Example factory ID:

```text
33333333-3333-3333-3333-333333333333
```

Example:

```text
http://localhost:8000/api/factories/33333333-3333-3333-3333-333333333333
```

---

## Recommendations

```http
GET /api/recommendations/{factory_id}
```

Example:

```text
http://localhost:8000/api/recommendations/33333333-3333-3333-3333-333333333333
```

The backend:

1. loads the factory
2. loads its carbon results
3. builds an emissions dictionary
4. ranks emission sources
5. calls the recommendation engine
6. saves generated recommendations
7. returns the final result

---

# 9. Recommendation Engine

You can test the recommendation engine independently.

From the project root:

```powershell
python -m recommendation_engine.main
```

Example emission input used by the project:

```python
{
    "electricity": 35000,
    "diesel": 10000,
    "raw_material": 3000,
    "waste": 500,
    "transport": 1000
}
```

The engine ranks sources by their emissions and returns up to three recommendations.

Current recommendation scoring uses:

```text
CO2 reduction     50%
ROI               30%
Feasibility       20%
```

The recommendation engine should remain separate from the FastAPI service.

---

# 10. Running Tests

Make sure both services are running first:

```text
JSON Server -> port 3000
FastAPI     -> port 8000
```

Then open a third terminal:

```powershell
cd C:\Users\Asus\Desktop\Projects\aster-hackout
```

Run all tests:

```powershell
pytest -v
```

Current test groups:

```text
test_json_server.py
test_recommendation_engine.py
test_fastapi.py
test_e2e.py
```

The end-to-end test verifies the complete flow:

```text
JSON Server
    ↓
FastAPI
    ↓
Emission data
    ↓
Recommendation Engine
    ↓
Recommendations
    ↓
JSON Server
```

---

# 11. Data Access Layer

The application should not directly depend on JSON Server.

Use:

```text
backend/services/data_api.py
```

as the common data-access layer.

Application code should import functions from:

```python
from services.data_api import (
    get_resource,
    get_resource_by_id,
    create_resource,
    update_resource,
    delete_resource
)
```

Do not directly import `json_api` inside normal route/service code.

Current flow:

```text
FastAPI
   ↓
data_api.py
   ↓
json_api.py
   ↓
JSON Server
```

Later:

```text
FastAPI
   ↓
data_api.py
   ↓
db_api.py
   ↓
Real database API
```

This allows the database implementation to change without changing the rest of the application.

---

# 12. Integrating a Real Database API

When the real database/API becomes available, create:

```text
backend/services/db_api.py
```

It should implement the same functions currently provided by `json_api.py`:

```python
async def get_resource(resource):
    ...

async def get_resource_by_id(resource, resource_id):
    ...

async def create_resource(resource, data):
    ...

async def update_resource(resource, resource_id, data):
    ...

async def delete_resource(resource, resource_id):
    ...
```

The function interface should stay the same even if the real API uses completely different URLs internally.

For example:

```python
import httpx

from config import DB_API_URL


async def get_resource(resource):

    async with httpx.AsyncClient() as client:

        response = await client.get(
            f"{DB_API_URL}/{resource}"
        )

        response.raise_for_status()

        return response.json()
```

The exact URL mapping should be changed to match the real backend API.

---

# 13. Switching Between JSON Server and the Real Database

Once `db_api.py` exists, `data_api.py` can become:

```python
from config import DATA_BACKEND


if DATA_BACKEND == "json":

    from services.json_api import (
        get_resource,
        get_resource_by_id,
        create_resource,
        update_resource,
        delete_resource
    )

elif DATA_BACKEND == "db":

    from services.db_api import (
        get_resource,
        get_resource_by_id,
        create_resource,
        update_resource,
        delete_resource
    )

else:

    raise ValueError(
        f"Unknown DATA_BACKEND: {DATA_BACKEND}"
    )
```

For local development:

```env
DATA_BACKEND=json
```

For the real API:

```env
DATA_BACKEND=db
DB_API_URL=https://your-real-api.example.com
```

No API route or recommendation-engine code should need to change.

---

# 14. If the Real Database Is Directly Accessible

If you receive direct PostgreSQL/MySQL access instead of a separate REST API, keep the same architecture:

```text
FastAPI
   ↓
data_api.py
   ↓
db_api.py
   ↓
PostgreSQL / MySQL
```

In that case, `db_api.py` would use something like:

```text
SQLAlchemy
psycopg
asyncpg
```

rather than `httpx`.

For example:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/carbonwise
```

Do not put this password in Git.

---

# 15. Integrating a Flask UI

If your team decides to use a **Flask UI instead of React**, Flask should act as the frontend/client.

Recommended architecture:

```text
Browser
   ↓
Flask UI
   ↓
FastAPI
   ↓
Services
   ↓
Database
   ↓
Recommendation Engine
```

Flask should **not access the recommendation engine directly**.

Flask should call FastAPI.

---

# 16. Example Flask UI Structure

A separate frontend can look like:

```text
flask-ui/
│
├── app.py
├── requirements.txt
│
├── templates/
│   ├── index.html
│   ├── factory.html
│   └── recommendations.html
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

Install Flask:

```powershell
pip install flask requests
```

Example `requirements.txt`:

```text
Flask
requests
```

---

# 17. Basic Flask Application

Example:

```python
from flask import Flask, render_template
import requests


app = Flask(__name__)


FASTAPI_URL = "http://localhost:8000"


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/factories")
def factories():

    response = requests.get(
        f"{FASTAPI_URL}/api/factories/"
    )

    response.raise_for_status()

    factories = response.json()

    return render_template(
        "factories.html",
        factories=factories
    )


@app.route("/recommendations/<factory_id>")
def recommendations(factory_id):

    response = requests.get(
        f"{FASTAPI_URL}/api/recommendations/{factory_id}"
    )

    response.raise_for_status()

    data = response.json()

    return render_template(
        "recommendations.html",
        data=data
    )


if __name__ == "__main__":
    app.run(
        debug=True,
        port=5000
    )
```

Start Flask:

```powershell
python app.py
```

It would normally run at:

```text
http://localhost:5000
```

---

# 18. Flask Recommendation Template Example

Example `templates/recommendations.html`:

```html
<!DOCTYPE html>

<html>

<head>
    <title>CarbonWise Recommendations</title>
</head>

<body>

    <h1>
        {{ data.factory.name }}
    </h1>

    <h2>Emission Sources</h2>

    <ul>

        {% for item in data.ranked_sources %}

        <li>
            {{ item.source }}:
            {{ item.emission }}
        </li>

        {% endfor %}

    </ul>

    <h2>Recommendations</h2>

    {% for recommendation in data.recommendations %}

    <div>

        <h3>
            {{ recommendation.name }}
        </h3>

        <p>
            Source:
            {{ recommendation.source }}
        </p>

        <p>
            Predicted CO2 Reduction:
            {{ recommendation.predicted_co2_reduction }}
        </p>

        <p>
            ROI:
            {{ recommendation.roi }}
        </p>

        <p>
            Score:
            {{ recommendation.score }}
        </p>

    </div>

    {% endfor %}

</body>

</html>
```

---

# 19. Full Architecture With Flask + Real Database

The final architecture can be:

```text
                 Browser
                    │
                    ▼
                Flask UI
                 :5000
                    │
                    ▼
                FastAPI
                 :8000
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     Data Services     Recommendation Engine
          │                   │
          ▼                   ├── ML Model
       db_api.py              ├── ROI
          │                   ├── Feasibility
          ▼                   └── Ranking
    Real Database/API
```

During development:

```text
Flask UI
   ↓
FastAPI
   ↓
data_api.py
   ↓
json_api.py
   ↓
JSON Server
```

During production:

```text
Flask UI
   ↓
FastAPI
   ↓
data_api.py
   ↓
db_api.py
   ↓
Real Database/API
```

---

# 20. Recommended Ports

```text
JSON Server     http://localhost:3000
Flask UI        http://localhost:5000
FastAPI         http://localhost:8000
```

If React is used instead of Flask:

```text
React/Vite      http://localhost:5173
FastAPI         http://localhost:8000
JSON Server     http://localhost:3000
```

---

# 21. Git

Current backend work can be kept on:

```text
FullBackend
```

Check branch:

```powershell
git branch
```

Commit changes:

```powershell
git add .
git commit -m "Update CarbonWise backend"
git push
```

Do not commit:

```text
.env
venv/
__pycache__/
.pytest_cache/
```

---

# 22. Development Rules

When extending CarbonWise, keep these rules:

1. UI communicates with FastAPI.
2. UI should not call the recommendation engine directly.
3. FastAPI handles HTTP/API responsibilities.
4. Recommendation calculations stay inside `recommendation_engine/`.
5. Database access goes through `data_api.py`.
6. `json_api.py` is only the temporary JSON Server implementation.
7. The future `db_api.py` should provide the same interface.
8. Secrets belong in `.env`, never in Git.
9. Factory IDs are UUID strings, not integers.
10. Run the test suite after backend changes.

---

# 23. Quick Start

### Terminal 1 — JSON Server

```powershell
cd C:\Users\Asus\Desktop\Projects\aster-hackout\json-server-api
npm start
```

### Terminal 2 — FastAPI

```powershell
cd C:\Users\Asus\Desktop\Projects\aster-hackout

.\backend\venv\Scripts\Activate.ps1

$env:PYTHONPATH = "$PWD;$PWD\backend"

python -m uvicorn backend.main:app --reload --port 8000
```

### Terminal 3 — Tests

```powershell
cd C:\Users\Asus\Desktop\Projects\aster-hackout

pytest -v
```

### Optional Terminal 4 — Flask UI

```powershell
cd flask-ui
python app.py
```

---

# CarbonWise

**AI-Powered Industrial Emission Leak-Point Detector & Circular Alternative Recommender**

The main goal of the architecture is to keep the UI, API layer, data layer, and recommendation engine separate so every part can be replaced or improved independently.
