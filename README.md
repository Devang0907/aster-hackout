![CarbonLoop Landing Page](frontend/public/image.png)

# Industrial Emission Leak-Point Detector Backend

FastAPI + PostgreSQL + Prisma Client Python backend for factory-scoped emissions data,
leak-point results, circular interventions, recommendations, and what-if simulations.

## Important runtime note

This repository intentionally uses **Prisma Client Python 0.15.0** because that is a hard
project requirement. The upstream Python client is archived and no longer maintained. Its
last release officially supports Python 3.12, so this project pins Python to `>=3.12,<3.13`.
Evaluate this dependency risk before a long-lived production launch; replacing the ORM would
be a separate architecture decision and is not done here.

The generator enables Prisma Client Python's experimental Decimal support. This is required to
preserve the precision mandated by the data model; exercise Decimal query paths in staging when
upgrading any runtime dependency.

## Project structure

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
│   │   ├── carbon.py
│   │   ├── common.py
│   │   ├── energy.py
│   │   ├── factory.py
│   │   ├── logistics.py
│   │   ├── material.py
│   │   ├── recommendation.py
│   │   ├── simulation.py
│   │   ├── user.py
│   │   └── waste.py
│   ├── security/authentication.py
│   ├── services/
│   │   ├── admin.py
│   │   ├── authorization.py
│   │   ├── errors.py
│   │   ├── factories.py
│   │   ├── operational.py
│   │   ├── recommendations.py
│   │   ├── reporting.py
│   │   └── simulations.py
│   └── main.py
├── prisma/
│   ├── migrations/
│   │   ├── migration_lock.toml
│   │   └── 20260911000000_initial/migration.sql
│   ├── schema.prisma
│   └── seed.py
├── tests/
│   ├── test_authorization.py
│   └── test_schema_contract.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## Local development

Install CPython 3.12, PostgreSQL, and platform build prerequisites. From `backend/`:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the application and test dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Create the local environment file without committing it:

```powershell
Copy-Item .env.example .env
```

On macOS/Linux use `cp .env.example .env`. Set `DATABASE_URL` to a PostgreSQL database, for
example `postgresql://app:password@localhost:5432/emissions`. Then generate the async Python
client and apply the checked-in migration:

```bash
python -m prisma generate --schema prisma/schema.prisma
python -m prisma migrate deploy --schema prisma/schema.prisma
python prisma/seed.py
```

To add the removable demo tenant for API and frontend verification:

```powershell
python prisma/seed.py --demo-tenant
```

The demo users use these fixed IDs so local development authentication can reference them:

- Admin: `00000000-0000-0000-0000-000000000001`
- Factory owner: `00000000-0000-0000-0000-000000000002`
- Factory manager: `00000000-0000-0000-0000-000000000003`

Remove only the demo tenant later with:

```powershell
python prisma/seed.py --cleanup-demo
```

This cleanup does not remove the reference materials, alternatives, interventions, or demo
emission factors.

For later schema changes in development:

```bash
python -m prisma migrate dev --name describe_change --schema prisma/schema.prisma
python -m prisma generate --schema prisma/schema.prisma
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Verify it:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/health/db
```

Run tests:

```bash
pytest
```

The checked-in tests cover the Pydantic validation, authorization behavior, the exact
18-model contract, and the required migration-level foreign keys, checks, uniqueness, and
immutability protections.

## Authentication and authorization

The default `AUTH_MODE=jwt` validates an HMAC JWT with `sub` (the user's UUID) and `exp`.
`JWT_SECRET`, and optionally issuer/audience, must be supplied by the deployment secret store.
The `sub` is looked up in `users`; inactive or missing users are denied. No password is stored.

`AUTH_MODE=development_header` accepts `X-User-Id` only for isolated local development. The
configuration refuses to start with this mode when `APP_ENV=production`.

Authorization has two deliberately separate paths:

- Admin endpoints select only allow-listed user/factory metadata. They never call operational
  services. Admins receive no operationally accessible factory IDs and are explicitly denied
  by `assert_factory_operational_access`.
- Owners are scoped by `factory.ownerId == current_user.id`. They may own multiple factories,
  register a factory, change its metadata, and create/assign its manager account.
- Managers are scoped by `factory.managerId == current_user.id`. PostgreSQL's unique constraint
  on `factories.manager_id` limits each manager to one factory. A factory has one nullable scalar
  manager field, so it also has at most one manager.

Unknown and cross-tenant factory IDs both return the same `404`, reducing object-enumeration
leakage. The database additionally checks that owner and manager references have the correct
user role and that repeated `factory_id` values agree with their reporting period/result.

The current JWT implementation is an integration seam, not an identity provider. When an
external provider is selected, replace token verification with that provider's verified signing
keys/claims while keeping its UUID subject synchronized to `users.id`.

## API surface

- `GET /health` and `GET /health/db`
- `/api/v1/admin/*`: metadata-only user/factory listing and active-state management
- `/api/v1/factories`: accessible factory listing, owner registration, metadata changes, manager assignment
- `/api/v1/factories/{factoryId}/reporting-periods`: create/list/submit periods
- `/api/v1/factories/{factoryId}/{material-usage|energy-usage|waste-streams|logistics}`: confidential data entry/listing
- `/api/v1/factories/{factoryId}/carbon-results`: versioned results with leak points
- `/api/v1/factories/{factoryId}/recommendations`: traceable recommendation listing/status changes
- `/api/v1/factories/{factoryId}/simulations`: JSON-assumption what-if scenarios
- `/api/v1/catalogs/{materials|material-alternatives|interventions|emission-factors}`: authenticated read-only catalogs

The frontend-facing API currently contains 23 route paths. Calculation and ML persistence is
available through internal services in `app/services/calculations.py`; it is intentionally not
exposed as a public owner/manager endpoint.

## Data model: all 18 models

1. **User** — external-auth-compatible UUID identity, role, contact/basic status; no password.
2. **Factory** — basic factory metadata, exactly one owner, and zero/one unique manager.
3. **ReportingPeriod** — unique factory/date window with submission and processing lifecycle.
4. **Material** — version-aware material master data and sustainability properties.
5. **MaterialAlternative** — directed, unique, non-self material substitution edge.
6. **FactoryMaterialUsage** — confidential period material amount and supplier data.
7. **EnergyUsage** — confidential energy activity and renewable share.
8. **WasteStream** — confidential period waste and bounded disposition quantities.
9. **Logistics** — confidential distance, freight, trip, mode, and fuel activity.
10. **EmissionFactor** — append-only, explicitly versioned factor catalog.
11. **CarbonResult** — immutable calculation-version snapshot tied to a reporting period and,
    for ML output, the exact pipeline run.
12. **EmissionSource** — ranked leak points for one carbon result.
13. **Intervention** — reusable circular/sustainability action catalog with JSON applicability.
14. **Recommendation** — result/intervention output, optionally traced to source and material pair.
15. **Simulation** — flexible JSON assumptions and preserved baseline/result economics.
16. **MlPipelineRun** — pipeline/model version, lifecycle, timing, and failure trace.
17. **CarbonCreditResult** — separate, non-authoritative estimate of reductions/credits.
18. **AuditLog** — database-enforced append-only record of significant actions.

## Relationships and deletion policy

- `User -> Factory` is one-to-many for ownership. `User -> managed Factory` is optional one-to-one
  through the unique nullable manager foreign key.
- `Factory -> ReportingPeriod/operational/result/recommendation/simulation/run/credit` is
  one-to-many. Every confidential query begins with its direct `factoryId`.
- `MaterialAlternative` has two named foreign keys to `Material`, producing source and target
  collections without ambiguity.
- `CarbonResult -> EmissionSource` is one-to-many. Recommendation links the factory, result,
  intervention, and optional source/material/alternative. A database trigger ensures the source
  belongs to the stated result.
- `MlPipelineRun -> CarbonResult` is optional one-to-one. When `mlModelVersion` is present the
  result must reference a run with the same factory, period, and model version, exposing that
  run's immutable `pipelineVersion`.
- Simulation references an immutable base result and its creator; a trigger ensures the base
  result belongs to the stated factory.

Users and factories use `isActive` for soft deletion. Required tenant and historical foreign keys
use `RESTRICT`; an owner/factory/reporting period cannot be physically deleted out from under
history. Optional manager, submitter, and audit actor/factory references use `SET NULL`, preserving
the dependent record. Carbon results and emission factors reject updates/deletes at the database
level—recalculation or correction requires a new version. Reporting periods, emission sources,
recommendations, simulations, ML runs, and credit results reject deletes. Audit logs reject all
updates/deletes. No normal API exposes physical deletion.

## PostgreSQL checks not expressible by Prisma schema

The initial SQL migration adds checks for dates, coordinates, non-negative quantities/costs,
bounded percentages/scores, waste allocations, ranks, range ordering, and distinct alternative
materials. It also adds triggers for:

- owner/manager role correctness;
- one-manager-one-factory compatibility during role changes;
- factory/reporting-period/result tenant consistency;
- recommendation result/source trace consistency;
- carbon-result pipeline/factory/period/model trace consistency;
- immutable carbon result and factor history;
- append-only audit logs.

Do not regenerate and replace the initial migration without carrying these statements forward.

## Neon production setup

1. Create a Neon project/database and a least-privilege application role.
2. In Neon **Connect**, copy a TLS connection string. Keep it in the platform secret manager, not
   source control. It must contain `sslmode=require` (Neon may also supply
   `channel_binding=require`).
3. For migration deployment, prefer the direct non-pooler connection string. Set it temporarily
   as `DATABASE_URL` in the migration job and run:

   ```bash
   python -m prisma migrate deploy --schema prisma/schema.prisma
   python -m prisma generate --schema prisma/schema.prisma
   ```

4. For the running API, use Neon's pooled connection string when connection concurrency warrants
   it. Prisma Client Python embeds an older Prisma engine; verify pooler behavior in staging and
   fall back to the direct string if compatibility issues occur.
5. Generate the Prisma client during the immutable build, fail deployment if migration deploy
   fails, use separate database roles/environments, rotate credentials, restrict CORS, disable
   debug mode, and never run `migrate dev` against production.
6. Run `GET /health/db` as the readiness probe after deployment.

Official references: [Neon connection pooling](https://neon.com/docs/connect/connection-pooling),
[Neon Python connection strings](https://neon.com/docs/guides/python), and
[Prisma Client Python CLI](https://prisma-client-py.readthedocs.io/en/stable/reference/command-line/).

## Future PostgreSQL RLS

Application authorization is **not** PostgreSQL Row Level Security. The schema is RLS-ready
because tenant-owned operational records carry `factory_id`. A later rollout can set transaction-
local request context and define policies, for example:

```sql
BEGIN;
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
COMMIT;
```

`SET LOCAL`/transaction-local context is essential with pooled connections so identity cannot
leak between requests. Add equivalent policies to every operational table, use a runtime role
that cannot bypass RLS, force RLS where appropriate, and keep admin operational policies absent.
Integration tests must exercise RLS before enabling it in production.

## Carbon-credit disclaimer

`carbon_credit_results` stores estimates separately from emissions. Seed data and calculated
values are not official, verified, certified, or tradable carbon credits. A recognized methodology
and external verification workflow must be implemented before making such claims.

## ER diagram

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

    CarbonResult ||--o{ EmissionSource : identifies
    CarbonResult ||--o{ Recommendation : generates
    CarbonResult ||--o{ Simulation : baseline_for
    MlPipelineRun |o--o| CarbonResult : produces
    Intervention ||--o{ Recommendation : proposes
    EmissionSource |o--o{ Recommendation : motivates
```

## Assumptions

- Factory-owner identities are provisioned by an external identity/admin workflow; manager
  provisioning here accepts that provider's UUID and never accepts or stores a password.
- Operational data is mutable only while its reporting period is `draft`; submitting locks entry.
- An emission-factor correction is a new version, and a recalculation uses a new
  `calculationVersion`. Duplicate result versions for one period are rejected.
- `costDifferencePercentage` is constrained to `0..100` exactly as requested, even though some
  domains represent cost decreases as negative values.
- Decimal units are stored with each activity. Unit conversion and the actual carbon/ML pipeline
  are separate domain components and are not fabricated by this database/API foundation.
- Seed emission factors are conspicuously demo-only and carry 100% uncertainty. Replace them with
  sourced, reviewed, versioned factors before real calculations.
