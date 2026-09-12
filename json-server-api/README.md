# Carbon Management JSON Server API

This is a JSON Server mock API matching the PostgreSQL schema supplied by the project.

## Run

```powershell
cd json-server-api
npm install
npm start
```

Server:
`http://localhost:3000`

## API prefix

Use `/api/...` routes from `routes.json`.

Examples:

- GET `/api/users`
- GET `/api/factories`
- GET `/api/factories/33333333-3333-3333-3333-333333333333`
- GET `/api/reporting-periods?factory_id=33333333-3333-3333-3333-333333333333`
- GET `/api/interventions`
- GET `/api/recommendations?factory_id=33333333-3333-3333-3333-333333333333`
- POST `/api/factories`
- PATCH `/api/recommendations/<id>`

## Important

JSON Server provides CRUD and filtering, but it does NOT enforce PostgreSQL foreign keys, CHECK constraints, enum constraints, immutable-history triggers, or authentication.

Use this as a frontend/integration mock. Keep the supplied PostgreSQL schema as the production database contract.

## Frontend example

```js
const API = "http://localhost:3000/api";

const response = await fetch(`${API}/factories`);
const factories = await response.json();

await fetch(`${API}/recommendations`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    factory_id: "33333333-3333-3333-3333-333333333333",
    result_id: "result-id",
    intervention_id: "intervention-id",
    priority: 1,
    recommendation_score: 92,
    status: "new"
  })
});
```

## Resource mapping

users -> /api/users
factories -> /api/factories
reporting_periods -> /api/reporting-periods
materials -> /api/materials
material_alternatives -> /api/material-alternatives
factory_material_usage -> /api/material-usage
energy_usage -> /api/energy-usage
waste_streams -> /api/waste-streams
logistics -> /api/logistics
emission_factors -> /api/emission-factors
carbon_results -> /api/carbon-results
emission_sources -> /api/emission-sources
interventions -> /api/interventions
recommendations -> /api/recommendations
simulations -> /api/simulations
ml_pipeline_runs -> /api/ml-pipeline-runs
carbon_credit_results -> /api/carbon-credit-results
audit_logs -> /api/audit-logs
