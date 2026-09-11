# Industrial Emission Leak-Point Detector & Circular Alternative Recommender

## Project specification and implementation context

This document is the consolidated source of context for the current project. It captures the
product intent, required technology choices, domain rules, database architecture, API behavior,
authorization model, operational assumptions, setup workflow, and current implementation status.

The implemented backend is located in `D:\Aster_Hackout\backend`.

## 1. Product purpose

The application helps SMEs and factories:

- collect factory operational data for defined reporting periods;
- calculate and preserve historical carbon-emission results;
- identify and rank major emission leak points;
- recommend circular interventions, material alternatives, recycling loops, process changes,
  energy optimization, and logistics improvements;
- run what-if simulations without requiring a new database column for every assumption;
- preserve calculation, emission-factor, ML-model, and recommendation traceability;
- keep carbon-credit estimates separate from carbon-emission calculations.

## 2. Required technology stack

The backend uses:

- Python 3.12;
- FastAPI;
- PostgreSQL;
- Neon PostgreSQL for production;
- Prisma ORM for Python (`prisma-client-py`);
- Pydantic v2;
- asynchronous Prisma database access;
- Prisma schema and Prisma migrations;
- UUID primary keys;
- environment-based configuration.

The backend must not use SQLAlchemy, SQLModel, Django ORM, Tortoise ORM, or Prisma Client JS.

### Prisma Python compatibility constraint

The upstream Prisma Client Python project is archived and no longer maintained. Its final release,
0.15.0, officially targets Python through 3.12 and requires the generator's experimental Decimal
support for Prisma `Decimal` fields. Consequently:

- `pyproject.toml` pins Python to `>=3.12,<3.13`;
- Prisma Client Python is pinned to `0.15.0`;
- `enable_experimental_decimal = true` is set in `prisma/schema.prisma`;
- dependency upgrades must be validated carefully in staging.

## 3. Roles and access rules

There are exactly three application roles.

### Admin

Admins may:

- access basic user information;
- access basic factory metadata;
- see factory name, industry, city, state, country, owner/manager association, active status,
  and timestamps;
- update platform-level active status metadata.

Admins must not access confidential operational data, including:

- energy consumption;
- raw-material quantities or supplier information;
- waste quantities;
- logistics data;
- internal production information;
- detailed calculation inputs;
- normal factory-scoped results, recommendations, or simulations through operational services.

The admin API uses explicit field allowlists. Operational authorization rejects admins even if
they know a factory UUID.

### Factory owner

A factory owner may:

- own multiple factories;
- register factories;
- update owned-factory metadata;
- create and assign one manager account per factory;
- enter and read material, energy, waste, and logistics data;
- create and submit reporting periods;
- view carbon results and ranked emission sources;
- view and update recommendation status;
- create and view simulations;
- view historical results.

Owners are authorized only where `factory.ownerId == current_user.id`.

### Factory manager

A factory manager may:

- manage exactly one factory;
- enter and read operational data for that factory;
- create and submit reporting periods for that factory;
- view its carbon results, emission sources, recommendations, and simulations;
- create simulations for that factory.

Managers are authorized only where `factory.managerId == current_user.id`.

The one-manager-one-factory rule is enforced with a PostgreSQL unique constraint on the nullable
`factories.manager_id` column. A factory has one scalar `managerId`, so it cannot contain multiple
managers.

### Cross-tenant behavior

- Every confidential operation is scoped by authenticated user and factory UUID.
- Unknown and unauthorized factory UUIDs both return `404`, reducing object-enumeration leakage.
- The backend never relies on frontend authorization.
- Database triggers ensure redundant `factoryId` values agree with their reporting-period/result
  references.

## 4. Authentication design

Passwords are never stored.

User UUIDs are designed to match an external identity-provider subject UUID. The current
authentication integration supports:

- `AUTH_MODE=jwt`: the default mode, validating an HMAC JWT with required `sub` and `exp` claims;
- optional JWT issuer and audience validation;
- `AUTH_MODE=development_header`: accepts `X-User-Id` for isolated local development only.

The application rejects `development_header` mode when `APP_ENV=production`.

After token validation, the UUID subject is loaded from `users`. Missing or inactive users are
denied. When an external provider is selected, its signature/JWKS verification should replace the
current HMAC verification while retaining the same database-backed user and authorization model.

## 5. Database principles

- `prisma/schema.prisma` is the schema source of truth.
- PostgreSQL tables and columns use snake_case through consistent Prisma `@map` and `@@map` usage.
- Application-facing Prisma fields use camelCase.
- All primary keys are PostgreSQL UUIDs generated with `gen_random_uuid()`.
- Precision-sensitive quantities, emissions, percentages, scores, costs, and savings use Decimal.
- Flexible assumptions and metadata use PostgreSQL JSONB.
- Timestamps use `TIMESTAMPTZ(6)`.
- Dates use PostgreSQL `DATE`.
- Users and factories use `isActive` for soft deletion.
- Historical relations use restrictive deletes.
- Optional manager/actor references use `SET NULL` where preserving the dependent record is safer.
- Audit logs are append-only at the database level.
- Carbon results and emission factors are immutable; corrections require a new version.
- Reporting periods, emission sources, recommendations, simulations, ML runs, and carbon-credit
  results cannot be physically deleted.
- Operational tables carry `factoryId` to make authorization and future RLS straightforward.

## 6. Database models

The schema contains exactly 18 models and the initial migration creates exactly 18 tables.

### 6.1 User (`users`)

Fields:

- `id` UUID primary key;
- `fullName` VARCHAR(150);
- `email` VARCHAR(255), unique;
- `role` PostgreSQL enum: `admin`, `factory_owner`, `factory_manager`;
- `phone` VARCHAR(20), nullable;
- `isActive` boolean, default true;
- `createdAt`, `updatedAt` timezone-aware timestamps.

Relations include owned factories, optionally managed factory, submitted periods, created
simulations, and audit logs.

### 6.2 Factory (`factories`)

Fields include owner/manager UUIDs, name, industry type, description, address, city, state,
country, coordinates, employees, production capacity/unit, established year, active status, and
timestamps.

Rules and checks:

- exactly one owner;
- zero or one manager;
- manager UUID is unique across factories;
- referenced owner must have role `factory_owner`;
- referenced manager must have role `factory_manager`;
- employees and production capacity cannot be negative;
- latitude is between -90 and 90;
- longitude is between -180 and 180.

### 6.3 ReportingPeriod (`reporting_periods`)

Defines a factory reporting window with start/end dates, status, submitter, submission time, and
timestamps.

Statuses: `draft`, `submitted`, `processing`, `completed`, `failed`.

Rules:

- end date is not before start date;
- exact factory/start/end duplicates are rejected;
- operational input can be modified only while the period is `draft`;
- a submitted period records submitter and UTC submission time.

### 6.4 Material (`materials`)

Master material catalog containing code, type, category, grade, description, optional versioned
carbon-factor metadata, recycling properties, hazard flag, sustainability score, active status,
and timestamps.

Carbon factors cannot be negative. Sustainability scores are bounded to 0–100.

### 6.5 MaterialAlternative (`material_alternatives`)

A directed self-referencing relationship between an original material and an alternative.

It stores substitution percentage, carbon reduction, cost difference, availability,
compatibility, notes, and timestamps.

Rules:

- a material cannot be its own alternative;
- the `(materialId, alternativeMaterialId)` pair is unique;
- percentages and scores are bounded to 0–100.

### 6.6 FactoryMaterialUsage (`factory_material_usage`)

Confidential material usage for a factory and reporting period, including material, quantity,
unit, recycled percentage, supplier name, and timestamps.

Quantity cannot be negative and recycled percentage is bounded to 0–100.

### 6.7 EnergyUsage (`energy_usage`)

Confidential factory energy activity containing reporting period, energy type, quantity, unit,
renewable share, source, and timestamps.

Quantity cannot be negative and renewable percentage is bounded to 0–100.

### 6.8 WasteStream (`waste_streams`)

Confidential waste activity containing reporting period, waste type, total quantity, unit,
treatment method, recycled/recovered/disposed quantities, and timestamps.

All quantities are non-negative. Recycled, recovered, and disposed quantities together cannot
exceed total quantity.

### 6.9 Logistics (`logistics`)

Confidential transport activity containing reporting period, transport type, mode, distance,
weight, trips, fuel type, and timestamps.

Distance, weight, and trips cannot be negative.

### 6.10 EmissionFactor (`emission_factors`)

Central factor catalog containing category, activity, factor, unit, source, URL, geography,
version, validity dates, uncertainty, and timestamps.

Rules:

- factor is non-negative;
- uncertainty is bounded to 0–100;
- valid-until is not before valid-from;
- records cannot be updated or deleted—corrections create new versions.

### 6.11 CarbonResult (`carbon_results`)

Immutable historical result containing factory, reporting period, optional exact pipeline run,
total and category-specific CO2e, renewable offset, net CO2e, optional intensity,
`calculationVersion`, optional `mlModelVersion`, and calculation timestamp.

Rules:

- emission values are non-negative;
- `(reportingPeriodId, calculationVersion)` is unique;
- ML output with a model version must include `pipelineRunId`;
- the linked pipeline run must match factory, period, and model version;
- results cannot be updated or deleted; recalculation creates a new version.

### 6.12 EmissionSource (`emission_sources`)

Immutable ranked leak point for a carbon result containing source type/name/reference, emissions,
percentage, severity, rank, explanation, and timestamp.

Severities: `low`, `medium`, `high`, `critical`.

Rules:

- emissions are non-negative;
- percentage is bounded to 0–100;
- rank is positive and unique within a result.

### 6.13 Intervention (`interventions`)

Master intervention catalog containing name, category, description, optional type, JSONB industry
applicability, cost range, expected reduction percentages, payback range, feasibility/readiness
scores, complexity, and timestamps.

Costs/payback cannot be negative, maximum ranges cannot be below minimums, and percentages/scores
are bounded to 0–100.

### 6.14 Recommendation (`recommendations`)

Recommendation-engine output linking a factory, carbon result, intervention, optional original
material, alternative material, and emission source. It stores priority, scores, estimated
reduction/cost/savings/payback, explanation, status, and timestamps.

Statuses: `new`, `viewed`, `accepted`, `rejected`, `implemented`.

Rules:

- priority is positive;
- values are non-negative;
- scores are bounded to 0–100;
- the result must belong to the stated factory;
- an optional emission source must belong to the stated result;
- recommendations cannot be deleted, although status may be updated.

### 6.15 Simulation (`simulations`)

What-if scenario containing factory, immutable base result, name, JSONB assumptions, baseline and
resulting CO2e, reduction, percentage, optional economics, creator, and timestamps.

The assumptions object is intentionally flexible. Values cannot be negative and percentage is
bounded to 0–100. The base result must belong to the stated factory. Simulations cannot be
deleted.

### 6.16 MlPipelineRun (`ml_pipeline_runs`)

Reproducibility record containing factory, reporting period, pipeline version, optional model
version, lifecycle status, timing, error message, and creation timestamp.

Statuses: `queued`, `running`, `completed`, `failed`.

Completion cannot precede start. Runs cannot be deleted. An ML carbon result may reference exactly
one run, and one run may produce at most one carbon result.

### 6.17 CarbonCreditResult (`carbon_credit_results`)

Separate estimate containing factory, reporting period, gross emissions, eligible reductions,
verified reductions, estimated credits, methodology, verification status, and timestamps.

Values cannot be negative. These records do not imply official verification or tradability and
cannot be deleted.

### 6.18 AuditLog (`audit_logs`)

Append-only record containing optional user/factory references, action, entity type/UUID, JSONB
metadata, and creation timestamp.

Database triggers reject all updates and deletes.

## 7. Important relationships

- `User 1 -> many Factory` through ownership.
- `User 0..1 -> 0..1 Factory` through unique manager assignment.
- `Factory 1 -> many ReportingPeriod`.
- `Factory` has many material usages, energy usages, waste streams, logistics entries, carbon
  results, recommendations, simulations, pipeline runs, carbon-credit results, and audit logs.
- `ReportingPeriod` has many operational records, carbon results, pipeline runs, and credit results.
- `Material` has many factory usages and participates on both sides of `MaterialAlternative`.
- `CarbonResult` has many emission sources and recommendations.
- `MlPipelineRun 0..1 -> 0..1 CarbonResult`.
- `Recommendation` belongs to an intervention and optionally links a source material, replacement
  material, and emission source.
- `Simulation` belongs to a factory, base result, and creator.

## 8. PostgreSQL integrity beyond Prisma syntax

The initial migration includes CHECK constraints and triggers that Prisma schema syntax cannot
fully express:

- bounded coordinates, percentages, and scores;
- non-negative quantities, emissions, costs, savings, payback, distance, weight, and trips;
- reporting and factor date ordering;
- waste disposition totals;
- non-self material alternatives;
- role-correct owner and manager references;
- protection against incompatible role changes while a user owns/manages a factory;
- operational record/reporting-period factory consistency;
- carbon-result/pipeline-run factory, period, and model consistency;
- recommendation factory/result/source consistency;
- simulation factory/base-result consistency;
- immutable historical data;
- append-only audit logs.

## 9. API structure

The API currently exposes 19 OpenAPI paths.

### Health

- `GET /health` returns `{ "status": "ok" }`.
- `GET /health/db` runs a Prisma/PostgreSQL `SELECT 1` check and returns 503 if unavailable.

### Admin metadata

- `GET /api/v1/admin/users`
- `GET /api/v1/admin/factories`
- `PATCH /api/v1/admin/users/{user_id}/active?active=true|false`
- `PATCH /api/v1/admin/factories/{factory_id}/active?active=true|false`

These endpoints expose metadata allowlists only.

### Factories and manager assignment

- `GET /api/v1/factories`
- `POST /api/v1/factories`
- `PATCH /api/v1/factories/{factory_id}`
- `POST /api/v1/factories/{factory_id}/manager`

Only owners may register/update factories and create/assign manager accounts.

### Reporting periods

- `GET /api/v1/factories/{factory_id}/reporting-periods`
- `POST /api/v1/factories/{factory_id}/reporting-periods`
- `POST /api/v1/factories/{factory_id}/reporting-periods/{period_id}/submit`

### Operational data

Each resource supports scoped create and list operations:

- `/api/v1/factories/{factory_id}/material-usage`
- `/api/v1/factories/{factory_id}/energy-usage`
- `/api/v1/factories/{factory_id}/waste-streams`
- `/api/v1/factories/{factory_id}/logistics`

Lists may be filtered by `reporting_period_id`.

### Results, recommendations, and simulations

- `GET /api/v1/factories/{factory_id}/carbon-results`
- `GET /api/v1/factories/{factory_id}/recommendations`
- `PATCH /api/v1/factories/{factory_id}/recommendations/{recommendation_id}`
- `GET /api/v1/factories/{factory_id}/simulations`
- `POST /api/v1/factories/{factory_id}/simulations`

Carbon/pipeline result creation is intended for an internal calculation/ML worker rather than a
normal owner/manager endpoint.

## 10. Application structure

```text
backend/
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   └── routes/
│   │       ├── admin.py
│   │       ├── factories.py
│   │       ├── health.py
│   │       ├── insights.py
│   │       ├── operational.py
│   │       └── reporting.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── repositories/helpers.py
│   ├── schemas/
│   ├── security/authentication.py
│   ├── services/
│   └── main.py
├── prisma/
│   ├── migrations/20260911000000_initial/migration.sql
│   ├── migrations/migration_lock.toml
│   ├── schema.prisma
│   └── seed.py
├── tests/
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

The FastAPI lifespan connects one process-wide asynchronous Prisma client at startup and
disconnects it at shutdown. Requests reuse that client; they do not open a new connection each
time.

## 11. Configuration

Configuration is loaded with Pydantic Settings from environment variables and an uncommitted
`.env` file.

Important variables:

```env
DATABASE_URL="postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require"
APP_ENV="development"
DEBUG="false"
AUTH_MODE="jwt"
JWT_SECRET="replace-with-a-long-random-secret"
JWT_ALGORITHM="HS256"
JWT_AUDIENCE=""
JWT_ISSUER=""
CORS_ORIGINS=[]
```

Database credentials, JWT secrets, Neon hosts, and API keys must never be committed or hardcoded.

## 12. Local setup

Use CPython 3.12. From `D:\Aster_Hackout\backend`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Set a valid PostgreSQL `DATABASE_URL`, then run:

```powershell
python -m prisma generate --schema prisma/schema.prisma
python -m prisma migrate deploy --schema prisma/schema.prisma
python prisma/seed.py
uvicorn app.main:app --reload
```

For a new development migration:

```powershell
python -m prisma migrate dev --name describe_change --schema prisma/schema.prisma
python -m prisma generate --schema prisma/schema.prisma
```

Never run `migrate dev` against production.

## 13. Neon production setup

1. Create a Neon project, database, and least-privilege application role.
2. Store the Neon connection string in the deployment secret manager as `DATABASE_URL`.
3. Require TLS with `sslmode=require`; retain `channel_binding=require` when Neon supplies it.
4. Prefer a direct/non-pooler connection string for the migration job.
5. Run `python -m prisma migrate deploy --schema prisma/schema.prisma`.
6. Generate the Prisma Python client during the immutable application build.
7. Use a pooled runtime connection where concurrency warrants it, but validate the archived
   Prisma Python engine's pooler compatibility in staging.
8. Run `/health/db` as the readiness check.
9. Use separate credentials/databases for development, staging, tests, and production.

No live Neon migration has been executed because this workspace does not contain production
database credentials.

## 14. Seed data

The seed script creates these materials:

- Virgin Polyester and Recycled Polyester;
- Cotton and Organic Cotton;
- Nylon and Recycled Nylon;
- Steel and Recycled Steel;
- Aluminum and Recycled Aluminum;
- Plastic and Recycled Plastic.

It creates example directed material alternatives and these interventions:

- Solar Installation;
- Energy Efficiency;
- Recycled Material Substitution;
- Waste Recovery;
- Electrification;
- Process Optimization;
- Water Recycling;
- Material Reuse;
- Packaging Reduction.

Seed emission factors are deliberately labeled `DEMO/EXAMPLE DATA — NOT AN OFFICIAL EMISSION
FACTOR`, use version `demo-v1`, and carry 100% uncertainty. They must be replaced with reviewed,
properly sourced, versioned factors before real calculations.

## 15. Testing and verification

Run:

```powershell
pytest
ruff check app prisma tests
```

The current suite contains 20 tests covering:

- exactly 18 models;
- admin role validation;
- owners with multiple factories;
- one-manager-one-factory database uniqueness;
- required factory/reporting/material/result/intervention relationships;
- percentage, quantity, date, alternative, and waste-allocation validation;
- simulation JSON preservation;
- audit-log creation and append-only protection;
- owner isolation;
- manager isolation;
- admin denial from confidential services;
- immutable historical results, recommendations, ML runs, and factors.

Current verification status:

- Prisma 5.17 schema validation: passed;
- Prisma Client Python 0.15.0 generation: passed;
- Pydantic/authorization/schema tests: 20 passed;
- Ruff: passed;
- FastAPI import and OpenAPI generation: passed with 19 paths;
- live PostgreSQL/Neon migration: not run because no database URL was supplied.

## 16. Future Row Level Security

FastAPI authorization is not PostgreSQL Row Level Security. The schema is prepared for later RLS
because operational records carry `factory_id`.

A future implementation should:

- start a database transaction for each protected operation;
- set transaction-local `app.user_id` and `app.user_role` settings;
- create policies that join each operational row's `factory_id` to an owned or managed factory;
- omit admin operational policies;
- use a runtime database role that cannot bypass RLS;
- use `FORCE ROW LEVEL SECURITY` where appropriate;
- test every policy directly against PostgreSQL;
- ensure transaction-local settings cannot leak through a pooled connection.

Illustrative policy shape:

```sql
SELECT set_config('app.user_id', :user_id, true);
SELECT set_config('app.user_role', :role, true);

ALTER TABLE energy_usage ENABLE ROW LEVEL SECURITY;

CREATE POLICY energy_usage_factory_access ON energy_usage
USING (
  current_setting('app.user_role', true) IN ('factory_owner', 'factory_manager')
  AND EXISTS (
    SELECT 1
    FROM factories f
    WHERE f.id = energy_usage.factory_id
      AND (
        f.owner_id = current_setting('app.user_id', true)::uuid
        OR f.manager_id = current_setting('app.user_id', true)::uuid
      )
  )
);
```

This is a future design, not a claim that RLS is currently enabled.

## 17. Carbon-credit disclaimer

Carbon-credit calculations remain separate from carbon-emission results. Stored credit values do
not imply that credits are certified, officially verified, registered, or tradable. Those claims
require a recognized methodology, evidence workflow, and external verification/certification.

## 18. Important implementation assumptions

- Owners/admins are provisioned through an external identity or controlled administration flow.
- Manager creation receives the external provider's UUID and never receives a password.
- Operational records are editable only in draft reporting periods.
- Submitting a reporting period locks normal data entry for that period.
- Emission-factor corrections create new factor versions.
- Carbon recalculation creates a new `calculationVersion` rather than overwriting history.
- ML-generated results link to the exact pipeline run.
- `costDifferencePercentage` is constrained to 0–100 as originally required, even though some
  financial domains represent a cost reduction with a negative percentage.
- Units are stored alongside activities; unit conversion and the actual calculation/ML worker are
  separate components and are not fabricated by this backend foundation.
- The `.env` file is local/deployment state and is intentionally excluded from source control.

## 19. ER diagram

```mermaid
erDiagram
    User ||--o{ Factory : owns
    User |o--o| Factory : manages
    User |o--o{ ReportingPeriod : submits
    User ||--o{ Simulation : creates
    User |o--o{ AuditLog : acts

    Factory ||--o{ ReportingPeriod : has
    Factory ||--o{ FactoryMaterialUsage : records
    Factory ||--o{ EnergyUsage : records
    Factory ||--o{ WasteStream : records
    Factory ||--o{ Logistics : records
    Factory ||--o{ CarbonResult : calculates
    Factory ||--o{ Recommendation : receives
    Factory ||--o{ Simulation : models
    Factory ||--o{ MlPipelineRun : executes
    Factory ||--o{ CarbonCreditResult : estimates
    Factory |o--o{ AuditLog : scopes

    ReportingPeriod ||--o{ FactoryMaterialUsage : contains
    ReportingPeriod ||--o{ EnergyUsage : contains
    ReportingPeriod ||--o{ WasteStream : contains
    ReportingPeriod ||--o{ Logistics : contains
    ReportingPeriod ||--o{ CarbonResult : versions
    ReportingPeriod ||--o{ MlPipelineRun : executes
    ReportingPeriod ||--o{ CarbonCreditResult : estimates

    Material ||--o{ FactoryMaterialUsage : used_as
    Material ||--o{ MaterialAlternative : source
    Material ||--o{ MaterialAlternative : alternative
    Material |o--o{ Recommendation : original
    Material |o--o{ Recommendation : replacement

    MlPipelineRun |o--o| CarbonResult : produces
    CarbonResult ||--o{ EmissionSource : identifies
    CarbonResult ||--o{ Recommendation : generates
    CarbonResult ||--o{ Simulation : baseline_for
    Intervention ||--o{ Recommendation : proposes
    EmissionSource |o--o{ Recommendation : motivates
```
