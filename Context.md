PROJECT CONTEXT — CARBONWISE / ASTER HACKOUT FULL BACKEND
Date: 12 Sep 2026

I am working on a CarbonWise hackathon project.

Project folder on Windows:
C:\Users\Asus\Desktop\Projects\aster-hackout

Git branch:
FullBackend

==================================================
1. CURRENT ARCHITECTURE
==================================================

The project originally used JSON Server, but JSON Server has now been completely removed.

CURRENT ARCHITECTURE:

React / Vite Frontend
        |
        v
FastAPI Backend
        |
        +--------------------+
        |                    |
        v                    v
Emission Service       Recommendation Engine
        |                    |
        v                    v
Neon PostgreSQL       Random Forest ML Model
        |                    |
        +---------+----------+
                  |
                  v
           Neon PostgreSQL

JSON Server is NO LONGER USED.

Removed:
- json-server-api/
- db.json
- package.json for JSON Server
- routes.json
- backend/services/json_api.py / JSON backend logic
- tests/test_json_server.py
- DATA_BACKEND switching
- JSON_SERVER_URL configuration

The backend should use Neon PostgreSQL exclusively.

==================================================
2. PROJECT STRUCTURE
==================================================

Important structure is approximately:

aster-hackout/
│
├── .env
├── .env.example
├── .gitignore
├── pytest.ini
├── README_CarbonWise.md
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   │
│   ├── api/
│   │   ├── emissions.py
│   │   ├── energy.py
│   │   ├── factories.py
│   │   ├── logistics.py
│   │   ├── materials.py
│   │   ├── recommendations.py
│   │   ├── simulations.py
│   │   └── waste.py
│   │
│   └── services/
│       ├── data_api.py
│       ├── db_api.py
│       ├── emission_service.py
│       ├── recommendation_service.py
│       └── simulation_service.py
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
└── tests_neon/
    ├── __init__.py
    ├── conftest.py
    ├── test_database.py
    ├── test_e2e.py
    ├── test_emissions.py
    ├── test_fastapi.py
    ├── test_ml_model.py
    ├── test_recommendation_engine.py
    ├── test_recommendations_api.py
    └── README.md

==================================================
3. ENVIRONMENT
==================================================

.env contains the real Neon connection string and MUST NOT be committed.

Current configuration should essentially be:

DATABASE_URL=<real Neon PostgreSQL connection URL>
FRONTEND_URL=http://localhost:5173

.env.example contains safe placeholders.

.gitignore ignores:
.env
Python cache files
pytest cache
etc.

If .env was ever tracked, use:
git rm --cached .env

Never expose or commit the actual Neon password.

==================================================
4. NEON / DATABASE
==================================================

Using Neon PostgreSQL.

Python driver:
psycopg 3

Installed using:

python -m pip install "psycopg[binary]"

It should also exist in backend/requirements.txt.

db_api.py uses async psycopg.

Important connection pattern:

import psycopg
from psycopg.rows import dict_row
from config import DATABASE_URL

async def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")

    return await psycopg.AsyncConnection.connect(
        DATABASE_URL,
        row_factory=dict_row
    )

Allowed database tables:

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

18 tables total.

data_api.py should now use db_api.py directly.
There should be NO JSON/DB backend switching.

==================================================
5. IMPORTANT DATABASE CONSTRAINTS
==================================================

carbon_results:
UNIQUE(reporting_period_id, calculation_version)

emission_sources:
UNIQUE(result_id, rank)

recommendations.emission_source_id:
foreign key -> emission_sources.id

IMPORTANT:
Do NOT delete emission_sources during recalculation because
recommendations may reference them.

The emission service therefore updates existing source rows in place.

During reranking it can temporarily move existing ranks to values such as
100+ to avoid the UNIQUE(result_id, rank) constraint, then assign the
correct final ranks.

==================================================
6. CURRENT DEMO DATA
==================================================

User UUID:
39f9cb32-8f69-4650-bb95-aacf6e921c69

Factory UUID:
963b9cdf-7c11-48d6-98b0-904dbfe6b613

Factory:
CarbonWise Demo Factory
Industry: Manufacturing
Ahmedabad, Gujarat, India
Employees: 250
Production capacity: 10000 tonnes/year

Reporting period UUID:
e3866bf8-246b-4f31-bf05-b62128ab9f9e

Period:
2026-01-01 -> 2026-12-31
status: completed

ENERGY:
125000 kWh Electricity
15% renewable
source: Grid

WASTE:
1000 kg Industrial Waste
500 recycled
200 recovered
300 disposed

LOGISTICS:
Truck
850 km
120 tonnes
25 trips
Diesel

MATERIAL:

Material UUID:
6515de97-e5f9-4b31-beb8-6d0a3ea96ca2

Steel
Code: MAT-STEEL-001
Carbon factor: 1.85 kgCO2e/kg
Usage: 50000 kg
Recycled content: 20%

==================================================
7. CURRENT CARBON CALCULATION
==================================================

Carbon result UUID:
8fb1e2e2-1608-4a3a-864b-88405cf34558

Current emissions:

Electricity:
35000 kgCO2e

Fuel:
0 kgCO2e

Raw material:
92500 kgCO2e

Transport:
255000 kgCO2e

Waste:
500 kgCO2e

TOTAL:
383000 kgCO2e

NET:
383000 kgCO2e

Carbon intensity:
38.3 kgCO2e/unit

calculation_version:
1.0

==================================================
8. EMISSION SOURCE RANKING
==================================================

Current ranking:

1. Transport
   255000 kgCO2e
   ~66.58%
   critical

2. Raw Material
   92500 kgCO2e
   ~24.15%
   high

3. Electricity
   35000 kgCO2e
   ~9.14%
   medium

4. Waste
   500 kgCO2e
   ~0.13%
   low

5. Fuel
   0
   0%
   low

Severity logic:

>= 50% -> critical
>= 20% -> high
>= 5% -> medium
else -> low

==================================================
9. EMISSIONS API
==================================================

Important endpoint:

POST
/api/emissions/{factory_id}/calculate

The endpoint runs BOTH:

1. emission calculation
2. ML recommendation generation

Conceptually:

emission_result = await calculate_factory_emissions(factory_id)

recommendation_result =
    await create_recommendations_for_factory(factory_id)

return {
    "emissions": emission_result,
    "recommendations": recommendation_result
}

==================================================
10. ML RECOMMENDATION ENGINE
==================================================

The recommendation engine is a separate Python package:

recommendation_engine/

Entry point:

from .services.recommendation_engine import generate_recommendations

def run_recommendation_engine(emissions, ranked_sources):
    return generate_recommendations(emissions, ranked_sources)

The backend recommendation service imports:

from recommendation_engine.main import run_recommendation_engine

The backend converts DB emission values to:

emissions = {
    "electricity": ...,
    "diesel": ...,
    "raw_material": ...,
    "waste": ...,
    "transport": ...
}

Then passes emissions and ranked sources to the ML engine.

==================================================
11. ML MODEL
==================================================

Current selected model:
RandomForestRegressor

Model file:
recommendation_engine/ml/model.pkl

Dataset:
recommendation_engine/ml/dataset.csv

Dataset size:
13,000 rows

Generated from:
1000 synthetic factories × 13 interventions

Dataset is SYNTHETIC / DEMO data.
It is NOT scientifically validated real industrial data.

Dataset columns:

factory_id
intervention_id
electricity_emission
diesel_emission
raw_material_emission
waste_emission
transport_emission
cost
savings
feasibility
co2_reduction

Current model input features are 8:

electricity_emission
diesel_emission
raw_material_emission
waste_emission
transport_emission
cost
savings
feasibility

IMPORTANT:
intervention_id currently exists in the dataset but is NOT used as a
model feature.

==================================================
12. MODEL TRAINING RESULTS
==================================================

Training command:

python -m recommendation_engine.ml.train

Models tested:

Linear Regression
R² = 0.2600
MAE = 11097.86

Random Forest
R² = 0.7960
MAE = 4644.55

Gradient Boosting
R² = 0.6835
MAE = 6974.72

Extra Trees
R² = 0.7881
MAE = 5178.55

Selected:
Random Forest

Random Forest configuration approximately:

RandomForestRegressor(
    n_estimators=300,
    max_depth=12,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

==================================================
13. ML PREDICTOR
==================================================

ml_predictor.py loads model.pkl using joblib.

It constructs a pandas DataFrame containing the 8 model features.

Prediction should be prevented from becoming negative, e.g.:

predicted_reduction = max(0, float(prediction[0]))

==================================================
14. POSSIBLE ML IMPROVEMENTS LATER
==================================================

Current validation uses rows generated from synthetic factories.

A more rigorous evaluation should use GroupKFold grouped by factory_id
so rows from the same synthetic factory don't leak between training and
validation.

Another future improvement:

Use intervention_id as a categorical ML feature using:
Pipeline
+
ColumnTransformer
+
OneHotEncoder

Currently intervention identity is indirectly represented only by
cost/savings/feasibility and the relevant emission values.

Do NOT make these changes unless I specifically ask.

==================================================
15. 13 ML INTERVENTIONS
==================================================

renewable_electricity
source: electricity
cost: 50000
savings: 18000
feasibility: 0.85
rate: 0.28

energy_efficiency
electricity
25000
12000
0.95
0.18

smart_energy_management
electricity
18000
8500
0.88
0.12

fuel_efficiency
diesel
20000
9000
0.90
0.20

fuel_switching
diesel
45000
14000
0.70
0.25

recycled_material
raw_material
15000
7000
0.80
0.20

material_efficiency
raw_material
20000
9000
0.85
0.24

sustainable_material_substitution
raw_material
30000
10000
0.72
0.22

waste_recovery
waste
10000
3000
0.85
0.30

waste_recycling
waste
14000
4500
0.88
0.25

industrial_symbiosis
waste
12000
6000
0.65
0.35

transport_optimization
transport
12000
5000
0.75
0.16

electric_transport
transport
60000
15000
0.60
0.30

==================================================
16. RECOMMENDATION ENGINE LOGIC
==================================================

Candidate generator considers interventions corresponding to the TOP 3
ranked emission sources.

ROI:

ROI = savings / cost

Final score:

score =
    0.50 * co2_score
  + 0.30 * roi_score
  + 0.20 * feasibility

CO2 reduction and ROI are min-max normalized.

Top 3 recommendations are returned.

==================================================
17. CURRENT ML OUTPUT EXAMPLE
==================================================

A successful current run produced approximately:

electric_transport

predicted CO2 reduction:
68484.2483

cost:
60000

savings:
15000

ROI:
0.25

feasibility:
0.60

score:
0.62


transport_optimization

predicted reduction:
26434.5352

cost:
12000

savings:
5000

ROI:
0.41667

feasibility:
0.75

score:
0.52155


recycled_material

predicted reduction:
16944.5887

cost:
15000

savings:
7000

ROI:
0.46667

feasibility:
0.80

score:
0.51872

This proves the ML model is genuinely being invoked by the backend.

==================================================
18. TEMPORARY ML -> DATABASE INTERVENTION MAPPING
==================================================

The database currently has generic intervention rows such as:

Energy Efficiency Upgrade
Solar Power Installation
Diesel Usage Reduction
Recycled Steel Substitution
Logistics Route Optimization
Waste Recycling Improvement

The 13 ML interventions are temporarily mapped to these generic DB rows.

Examples:

renewable_electricity
-> Solar Power Installation

energy_efficiency
-> Energy Efficiency Upgrade

smart_energy_management
-> Energy Efficiency Upgrade

fuel_efficiency / fuel_switching
-> Diesel Usage Reduction

recycled_material / material_efficiency /
sustainable_material_substitution
-> Recycled Steel Substitution

transport_optimization / electric_transport
-> Logistics Route Optimization

waste interventions
-> Waste Recycling Improvement

Because multiple ML interventions can map to the same DB intervention,
sometimes only two DB recommendation rows are saved even when the ML
engine returns three recommendations.

FUTURE FIX:
Seed all 13 interventions individually into Neon and ideally add:

engine_key VARCHAR(100) UNIQUE

Then remove this temporary many-to-one mapping.

Do not do this automatically unless I ask.

==================================================
19. TEST SUITE
==================================================

Old JSON Server tests were removed.

Current tests are in:

tests_neon/

There are 23 tests.

Run:

pytest tests_neon -v

CURRENT RESULT:

23 passed
1 warning
~101 seconds

Everything passed:

Neon connection
database tables
factory exists
E2E flow
emission calculation
emission source ranking
percentage calculation
FastAPI root
health
factory endpoints
model file
model loading
model features
non-negative prediction
recommendation engine
required fields
scores
ROI
sorting
zero-source behavior
ML recommendation generation API
saved recommendations API

==================================================
20. WINDOWS ASYNCIO TEST FIX
==================================================

Originally tests failed because psycopg AsyncConnection does not support
Windows ProactorEventLoop.

pytest/TestClient was using ProactorEventLoop.

pytest.ini now uses:

[pytest]
asyncio_mode = auto

tests_neon/conftest.py also applies the Windows Selector event loop policy
before FastAPI imports.

After this fix:
23/23 tests pass.

==================================================
21. TEST WARNING
==================================================

There is one non-failing warning:

StarletteDeprecationWarning:
Using `httpx` with `starlette.testclient` is deprecated;
install `httpx2` instead.

This is currently harmless.

Do NOT make risky dependency changes just to remove this warning unless
I ask.

==================================================
22. RUNNING FASTAPI
==================================================

When running from the project root, imports previously required:

$env:PYTHONPATH="$PWD;$PWD\backend"

python -m uvicorn backend.main:app --reload --port 8000

The API runs on port 8000.

Frontend expected:
http://localhost:5173

==================================================
23. FACTORY ROUTE NOTE
==================================================

Factory IDs are UUID strings.

GET factory route uses a string ID.

If PUT/DELETE still have:

factory_id: int

they should eventually be changed to:

factory_id: str

because Neon factory IDs are UUIDs.

Also avoid broad:

except Exception:
    raise HTTPException(404, ...)

because it can hide actual database errors as "Factory not found".

==================================================
24. GIT / JSON SERVER REMOVAL
==================================================

Branch:
FullBackend

Before commit, all 23 tests passed.

JSON Server files staged/deleted included:

json-server-api/README.md
json-server-api/db.json
json-server-api/package-lock.json
json-server-api/package.json
json-server-api/routes.json

Old tests removed:

tests/test_e2e.py
tests/test_fastapi.py
tests/test_json_server.py
tests/test_recommendation_engine.py

New files included:

backend/services/db_api.py
pytest.ini
tests_neon/*

Commit successfully created:

1e474cd

Commit message:

Remove JSON Server and use Neon PostgreSQL exclusively

Commit stats:

42 files changed
16132 insertions
4979 deletions

The last command executed was:

git push origin FullBackend

The pasted output ended immediately after that command, so the final
push success output was not shown.

To verify:

git status

Expected:

On branch FullBackend
Your branch is up to date with 'origin/FullBackend'.
nothing to commit, working tree clean

Also:

git log -1 --oneline

should show:

1e474cd Remove JSON Server and use Neon PostgreSQL exclusively

==================================================
25. VERIFY JSON SERVER IS COMPLETELY GONE
==================================================

Can run:

git grep -ni -E "json-server|json_server|json_api|localhost:3000|DATA_BACKEND|JSON_SERVER_URL"

Ideally it should produce no active JSON Server references.

JSON Server should NOT be reintroduced.

==================================================
26. IMPORTANT DEVELOPMENT RULES FOR THIS PROJECT
==================================================

1. Neon PostgreSQL is the ONLY backend datastore.
2. Do not reintroduce JSON Server.
3. Factory/database IDs are UUID strings.
4. Keep .env out of Git.
5. Never expose the Neon password.
6. Preserve emission_source IDs because recommendations reference them.
7. Run tests after backend changes:
   pytest tests_neon -v
8. Current baseline is 23 passing tests.
9. Random Forest is the current selected ML model.
10. model.pkl is actually being used by the recommendation engine.
11. The training dataset is synthetic/demo data.
12. Do not claim the model is scientifically validated.
13. Avoid large architectural changes unless requested.
14. When helping me, prefer incremental changes and give complete
    corrected files when I provide a file that needs modification.

==================================================
27. CURRENT STATUS
==================================================

Neon PostgreSQL       WORKING
FastAPI               WORKING
Emission calculation  WORKING
Emission ranking      WORKING
Random Forest model   WORKING
ML recommendation     WORKING
Recommendation API    WORKING
E2E integration       WORKING
Tests                  23/23 PASSING
JSON Server            REMOVED
Git commit             CREATED
Commit                 1e474cd
Branch                 FullBackend

The next chat should continue from this state.