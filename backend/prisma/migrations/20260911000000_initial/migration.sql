-- Initial PostgreSQL/Neon schema. Prisma owns table/column/index definitions;
-- the CHECK constraints and integrity triggers below cover invariants that the
-- Prisma schema language cannot express.
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TYPE "user_role" AS ENUM ('admin', 'factory_owner', 'factory_manager');
CREATE TYPE "reporting_period_status" AS ENUM ('draft', 'submitted', 'processing', 'completed', 'failed');
CREATE TYPE "emission_severity" AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE "recommendation_status" AS ENUM ('new', 'viewed', 'accepted', 'rejected', 'implemented');
CREATE TYPE "pipeline_run_status" AS ENUM ('queued', 'running', 'completed', 'failed');

CREATE TABLE "users" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "full_name" VARCHAR(150) NOT NULL,
    "email" VARCHAR(255) NOT NULL,
    "role" "user_role" NOT NULL,
    "phone" VARCHAR(20),
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    CONSTRAINT "users_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "users_email_key" UNIQUE ("email")
);

CREATE TABLE "factories" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "owner_id" UUID NOT NULL,
    "manager_id" UUID,
    "name" VARCHAR(200) NOT NULL,
    "industry_type" VARCHAR(100) NOT NULL,
    "description" TEXT,
    "address" TEXT,
    "city" VARCHAR(100) NOT NULL,
    "state" VARCHAR(100) NOT NULL,
    "country" VARCHAR(100) NOT NULL DEFAULT 'India',
    "latitude" DECIMAL(10,7),
    "longitude" DECIMAL(10,7),
    "employees" INTEGER,
    "production_capacity" DECIMAL(20,6),
    "production_unit" VARCHAR(50),
    "established_year" INTEGER,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    CONSTRAINT "factories_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "factories_manager_id_key" UNIQUE ("manager_id"),
    CONSTRAINT "factories_employees_check" CHECK ("employees" IS NULL OR "employees" >= 0),
    CONSTRAINT "factories_production_capacity_check" CHECK ("production_capacity" IS NULL OR "production_capacity" >= 0),
    CONSTRAINT "factories_latitude_check" CHECK ("latitude" IS NULL OR "latitude" BETWEEN -90 AND 90),
    CONSTRAINT "factories_longitude_check" CHECK ("longitude" IS NULL OR "longitude" BETWEEN -180 AND 180)
);

CREATE TABLE "reporting_periods" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "factory_id" UUID NOT NULL,
    "period_start" DATE NOT NULL,
    "period_end" DATE NOT NULL,
    "status" "reporting_period_status" NOT NULL DEFAULT 'draft',
    "submitted_by_id" UUID,
    "submitted_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    CONSTRAINT "reporting_periods_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "reporting_periods_factory_dates_key" UNIQUE ("factory_id", "period_start", "period_end"),
    CONSTRAINT "reporting_periods_dates_check" CHECK ("period_end" >= "period_start")
);

CREATE TABLE "materials" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "name" VARCHAR(200) NOT NULL,
    "material_code" VARCHAR(50),
    "material_type" VARCHAR(100) NOT NULL,
    "category" VARCHAR(100),
    "subcategory" VARCHAR(100),
    "grade" VARCHAR(100),
    "description" TEXT,
    "carbon_factor" DECIMAL(20,8),
    "carbon_unit" VARCHAR(50),
    "carbon_factor_source" TEXT,
    "carbon_factor_version" VARCHAR(50),
    "recycled_content_possible" BOOLEAN NOT NULL DEFAULT false,
    "recyclable" BOOLEAN NOT NULL DEFAULT false,
    "hazardous" BOOLEAN NOT NULL DEFAULT false,
    "sustainability_score" DECIMAL(7,4),
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    CONSTRAINT "materials_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "materials_material_code_key" UNIQUE ("material_code"),
    CONSTRAINT "materials_carbon_factor_check" CHECK ("carbon_factor" IS NULL OR "carbon_factor" >= 0),
    CONSTRAINT "materials_sustainability_score_check" CHECK ("sustainability_score" IS NULL OR "sustainability_score" BETWEEN 0 AND 100)
);

CREATE TABLE "material_alternatives" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "material_id" UUID NOT NULL,
    "alternative_material_id" UUID NOT NULL,
    "substitution_percentage" DECIMAL(7,4),
    "carbon_reduction_percentage" DECIMAL(7,4),
    "cost_difference_percentage" DECIMAL(9,4),
    "availability_score" DECIMAL(7,4),
    "compatibility_score" DECIMAL(7,4),
    "notes" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    CONSTRAINT "material_alternatives_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "material_alternatives_pair_key" UNIQUE ("material_id", "alternative_material_id"),
    CONSTRAINT "material_alternatives_distinct_check" CHECK ("material_id" <> "alternative_material_id"),
    CONSTRAINT "material_alternatives_substitution_check" CHECK ("substitution_percentage" IS NULL OR "substitution_percentage" BETWEEN 0 AND 100),
    CONSTRAINT "material_alternatives_carbon_reduction_check" CHECK ("carbon_reduction_percentage" IS NULL OR "carbon_reduction_percentage" BETWEEN 0 AND 100),
    CONSTRAINT "material_alternatives_cost_difference_check" CHECK ("cost_difference_percentage" IS NULL OR "cost_difference_percentage" BETWEEN 0 AND 100),
    CONSTRAINT "material_alternatives_availability_check" CHECK ("availability_score" IS NULL OR "availability_score" BETWEEN 0 AND 100),
    CONSTRAINT "material_alternatives_compatibility_check" CHECK ("compatibility_score" IS NULL OR "compatibility_score" BETWEEN 0 AND 100)
);

CREATE TABLE "factory_material_usage" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "factory_id" UUID NOT NULL,
    "reporting_period_id" UUID NOT NULL,
    "material_id" UUID NOT NULL,
    "quantity" DECIMAL(20,6) NOT NULL,
    "unit" VARCHAR(30) NOT NULL,
    "recycled_percentage" DECIMAL(7,4) NOT NULL DEFAULT 0,
    "supplier_name" VARCHAR(200),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    CONSTRAINT "factory_material_usage_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "factory_material_usage_quantity_check" CHECK ("quantity" >= 0),
    CONSTRAINT "factory_material_usage_recycled_check" CHECK ("recycled_percentage" BETWEEN 0 AND 100)
);

CREATE TABLE "energy_usage" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "factory_id" UUID NOT NULL,
    "reporting_period_id" UUID NOT NULL,
    "energy_type" VARCHAR(100) NOT NULL,
    "quantity" DECIMAL(20,6) NOT NULL,
    "unit" VARCHAR(30) NOT NULL,
    "renewable_percentage" DECIMAL(7,4) NOT NULL DEFAULT 0,
    "source" VARCHAR(100),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    CONSTRAINT "energy_usage_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "energy_usage_quantity_check" CHECK ("quantity" >= 0),
    CONSTRAINT "energy_usage_renewable_check" CHECK ("renewable_percentage" BETWEEN 0 AND 100)
);

CREATE TABLE "waste_streams" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "factory_id" UUID NOT NULL,
    "reporting_period_id" UUID NOT NULL,
    "waste_type" VARCHAR(100) NOT NULL,
    "quantity" DECIMAL(20,6) NOT NULL,
    "unit" VARCHAR(30) NOT NULL,
    "treatment_method" VARCHAR(100),
    "recycled_quantity" DECIMAL(20,6) NOT NULL DEFAULT 0,
    "recovered_quantity" DECIMAL(20,6) NOT NULL DEFAULT 0,
    "disposed_quantity" DECIMAL(20,6) NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    CONSTRAINT "waste_streams_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "waste_streams_quantities_nonnegative_check" CHECK (
        "quantity" >= 0 AND "recycled_quantity" >= 0 AND "recovered_quantity" >= 0 AND "disposed_quantity" >= 0
    ),
    CONSTRAINT "waste_streams_total_check" CHECK (
        "recycled_quantity" + "recovered_quantity" + "disposed_quantity" <= "quantity"
    )
);

CREATE TABLE "logistics" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "factory_id" UUID NOT NULL,
    "reporting_period_id" UUID NOT NULL,
    "transport_type" VARCHAR(100) NOT NULL,
    "mode" VARCHAR(50) NOT NULL,
    "distance_km" DECIMAL(20,6) NOT NULL,
    "weight_tonnes" DECIMAL(20,6),
    "trips" INTEGER,
    "fuel_type" VARCHAR(50),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    CONSTRAINT "logistics_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "logistics_distance_check" CHECK ("distance_km" >= 0),
    CONSTRAINT "logistics_weight_check" CHECK ("weight_tonnes" IS NULL OR "weight_tonnes" >= 0),
    CONSTRAINT "logistics_trips_check" CHECK ("trips" IS NULL OR "trips" >= 0)
);

CREATE TABLE "emission_factors" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "category" VARCHAR(100) NOT NULL,
    "activity" VARCHAR(200) NOT NULL,
    "factor" DECIMAL(20,8) NOT NULL,
    "unit" VARCHAR(50) NOT NULL,
    "source" TEXT NOT NULL,
    "source_url" TEXT,
    "region" VARCHAR(100),
    "country" VARCHAR(100),
    "version" VARCHAR(50) NOT NULL,
    "valid_from" DATE,
    "valid_until" DATE,
    "uncertainty_percentage" DECIMAL(7,4),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    CONSTRAINT "emission_factors_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "emission_factors_factor_check" CHECK ("factor" >= 0),
    CONSTRAINT "emission_factors_uncertainty_check" CHECK ("uncertainty_percentage" IS NULL OR "uncertainty_percentage" BETWEEN 0 AND 100),
    CONSTRAINT "emission_factors_dates_check" CHECK ("valid_from" IS NULL OR "valid_until" IS NULL OR "valid_until" >= "valid_from")
);

CREATE TABLE "carbon_results" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "factory_id" UUID NOT NULL,
    "reporting_period_id" UUID NOT NULL,
    "pipeline_run_id" UUID,
    "total_co2e" DECIMAL(20,6) NOT NULL,
    "electricity_co2e" DECIMAL(20,6) NOT NULL DEFAULT 0,
    "fuel_co2e" DECIMAL(20,6) NOT NULL DEFAULT 0,
    "material_co2e" DECIMAL(20,6) NOT NULL DEFAULT 0,
    "transport_co2e" DECIMAL(20,6) NOT NULL DEFAULT 0,
    "waste_co2e" DECIMAL(20,6) NOT NULL DEFAULT 0,
    "renewable_offset" DECIMAL(20,6) NOT NULL DEFAULT 0,
    "net_co2e" DECIMAL(20,6) NOT NULL,
    "carbon_intensity" DECIMAL(20,8),
    "carbon_intensity_unit" VARCHAR(100),
    "calculation_version" VARCHAR(50) NOT NULL,
    "ml_model_version" VARCHAR(100),
    "calculated_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "carbon_results_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "carbon_results_pipeline_run_id_key" UNIQUE ("pipeline_run_id"),
    CONSTRAINT "carbon_results_period_version_key" UNIQUE ("reporting_period_id", "calculation_version"),
    CONSTRAINT "carbon_results_nonnegative_check" CHECK (
        "total_co2e" >= 0 AND "electricity_co2e" >= 0 AND "fuel_co2e" >= 0 AND
        "material_co2e" >= 0 AND "transport_co2e" >= 0 AND "waste_co2e" >= 0 AND
        "renewable_offset" >= 0 AND "net_co2e" >= 0 AND ("carbon_intensity" IS NULL OR "carbon_intensity" >= 0)
    ),
    CONSTRAINT "carbon_results_ml_trace_check" CHECK ("ml_model_version" IS NULL OR "pipeline_run_id" IS NOT NULL)
);

CREATE TABLE "emission_sources" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "result_id" UUID NOT NULL,
    "source_type" VARCHAR(100) NOT NULL,
    "source_name" VARCHAR(200) NOT NULL,
    "source_reference_id" UUID,
    "emissions_co2e" DECIMAL(20,6) NOT NULL,
    "percentage" DECIMAL(7,4) NOT NULL,
    "severity" "emission_severity" NOT NULL,
    "rank" INTEGER NOT NULL,
    "explanation" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "emission_sources_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "emission_sources_result_rank_key" UNIQUE ("result_id", "rank"),
    CONSTRAINT "emission_sources_emissions_check" CHECK ("emissions_co2e" >= 0),
    CONSTRAINT "emission_sources_percentage_check" CHECK ("percentage" BETWEEN 0 AND 100),
    CONSTRAINT "emission_sources_rank_check" CHECK ("rank" > 0)
);

CREATE TABLE "interventions" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "name" VARCHAR(200) NOT NULL,
    "category" VARCHAR(100) NOT NULL,
    "description" TEXT NOT NULL,
    "intervention_type" VARCHAR(100),
    "applicable_industries" JSONB,
    "estimated_cost_min" DECIMAL(20,2),
    "estimated_cost_max" DECIMAL(20,2),
    "expected_co2_reduction_percentage" DECIMAL(7,4),
    "expected_energy_reduction_percentage" DECIMAL(7,4),
    "expected_waste_reduction_percentage" DECIMAL(7,4),
    "payback_months_min" DECIMAL(12,2),
    "payback_months_max" DECIMAL(12,2),
    "feasibility_score" DECIMAL(7,4),
    "technology_readiness" DECIMAL(7,4),
    "implementation_complexity" VARCHAR(50),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    CONSTRAINT "interventions_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "interventions_cost_check" CHECK (
        ("estimated_cost_min" IS NULL OR "estimated_cost_min" >= 0) AND
        ("estimated_cost_max" IS NULL OR "estimated_cost_max" >= 0) AND
        ("estimated_cost_min" IS NULL OR "estimated_cost_max" IS NULL OR "estimated_cost_max" >= "estimated_cost_min")
    ),
    CONSTRAINT "interventions_percentages_check" CHECK (
        ("expected_co2_reduction_percentage" IS NULL OR "expected_co2_reduction_percentage" BETWEEN 0 AND 100) AND
        ("expected_energy_reduction_percentage" IS NULL OR "expected_energy_reduction_percentage" BETWEEN 0 AND 100) AND
        ("expected_waste_reduction_percentage" IS NULL OR "expected_waste_reduction_percentage" BETWEEN 0 AND 100)
    ),
    CONSTRAINT "interventions_payback_check" CHECK (
        ("payback_months_min" IS NULL OR "payback_months_min" >= 0) AND
        ("payback_months_max" IS NULL OR "payback_months_max" >= 0) AND
        ("payback_months_min" IS NULL OR "payback_months_max" IS NULL OR "payback_months_max" >= "payback_months_min")
    ),
    CONSTRAINT "interventions_scores_check" CHECK (
        ("feasibility_score" IS NULL OR "feasibility_score" BETWEEN 0 AND 100) AND
        ("technology_readiness" IS NULL OR "technology_readiness" BETWEEN 0 AND 100)
    )
);

CREATE TABLE "recommendations" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "factory_id" UUID NOT NULL,
    "result_id" UUID NOT NULL,
    "intervention_id" UUID NOT NULL,
    "material_id" UUID,
    "alternative_material_id" UUID,
    "emission_source_id" UUID,
    "priority" INTEGER NOT NULL,
    "recommendation_score" DECIMAL(7,4),
    "estimated_co2_reduction" DECIMAL(20,6),
    "estimated_cost" DECIMAL(20,2),
    "estimated_annual_savings" DECIMAL(20,2),
    "payback_months" DECIMAL(12,2),
    "feasibility_score" DECIMAL(7,4),
    "confidence_score" DECIMAL(7,4),
    "ai_explanation" TEXT,
    "status" "recommendation_status" NOT NULL DEFAULT 'new',
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    CONSTRAINT "recommendations_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "recommendations_priority_check" CHECK ("priority" > 0),
    CONSTRAINT "recommendations_amounts_check" CHECK (
        ("estimated_co2_reduction" IS NULL OR "estimated_co2_reduction" >= 0) AND
        ("estimated_cost" IS NULL OR "estimated_cost" >= 0) AND
        ("estimated_annual_savings" IS NULL OR "estimated_annual_savings" >= 0) AND
        ("payback_months" IS NULL OR "payback_months" >= 0)
    ),
    CONSTRAINT "recommendations_scores_check" CHECK (
        ("recommendation_score" IS NULL OR "recommendation_score" BETWEEN 0 AND 100) AND
        ("feasibility_score" IS NULL OR "feasibility_score" BETWEEN 0 AND 100) AND
        ("confidence_score" IS NULL OR "confidence_score" BETWEEN 0 AND 100)
    )
);

CREATE TABLE "simulations" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "factory_id" UUID NOT NULL,
    "base_result_id" UUID NOT NULL,
    "name" VARCHAR(200) NOT NULL,
    "assumptions" JSONB NOT NULL,
    "baseline_co2e" DECIMAL(20,6) NOT NULL,
    "resulting_co2e" DECIMAL(20,6) NOT NULL,
    "co2_reduction" DECIMAL(20,6) NOT NULL,
    "co2_reduction_percentage" DECIMAL(7,4) NOT NULL,
    "estimated_cost" DECIMAL(20,2),
    "estimated_savings" DECIMAL(20,2),
    "payback_months" DECIMAL(12,2),
    "created_by_id" UUID NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    CONSTRAINT "simulations_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "simulations_values_check" CHECK (
        "baseline_co2e" >= 0 AND "resulting_co2e" >= 0 AND "co2_reduction" >= 0 AND
        "co2_reduction_percentage" BETWEEN 0 AND 100 AND
        ("estimated_cost" IS NULL OR "estimated_cost" >= 0) AND
        ("estimated_savings" IS NULL OR "estimated_savings" >= 0) AND
        ("payback_months" IS NULL OR "payback_months" >= 0)
    )
);

CREATE TABLE "ml_pipeline_runs" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "factory_id" UUID NOT NULL,
    "reporting_period_id" UUID NOT NULL,
    "pipeline_version" VARCHAR(100) NOT NULL,
    "model_version" VARCHAR(100),
    "status" "pipeline_run_status" NOT NULL DEFAULT 'queued',
    "started_at" TIMESTAMPTZ(6),
    "completed_at" TIMESTAMPTZ(6),
    "error_message" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "ml_pipeline_runs_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "ml_pipeline_runs_dates_check" CHECK ("started_at" IS NULL OR "completed_at" IS NULL OR "completed_at" >= "started_at")
);

CREATE TABLE "carbon_credit_results" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "factory_id" UUID NOT NULL,
    "reporting_period_id" UUID NOT NULL,
    "gross_emissions" DECIMAL(20,6) NOT NULL,
    "eligible_reductions" DECIMAL(20,6) NOT NULL DEFAULT 0,
    "verified_reductions" DECIMAL(20,6) NOT NULL DEFAULT 0,
    "carbon_credits" DECIMAL(20,6) NOT NULL DEFAULT 0,
    "methodology" VARCHAR(200),
    "verification_status" VARCHAR(50),
    "calculated_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "carbon_credit_results_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "carbon_credit_results_nonnegative_check" CHECK (
        "gross_emissions" >= 0 AND "eligible_reductions" >= 0 AND "verified_reductions" >= 0 AND "carbon_credits" >= 0
    )
);

CREATE TABLE "audit_logs" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID,
    "factory_id" UUID,
    "action" VARCHAR(100) NOT NULL,
    "entity_type" VARCHAR(100) NOT NULL,
    "entity_id" UUID,
    "metadata" JSONB,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "audit_logs_pkey" PRIMARY KEY ("id")
);

-- Foreign keys use RESTRICT for tenant and historical records. Optional actor/
-- manager references use SET NULL so deactivation/deletion cannot orphan history.
ALTER TABLE "factories" ADD CONSTRAINT "factories_owner_id_fkey" FOREIGN KEY ("owner_id") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "factories" ADD CONSTRAINT "factories_manager_id_fkey" FOREIGN KEY ("manager_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "reporting_periods" ADD CONSTRAINT "reporting_periods_factory_id_fkey" FOREIGN KEY ("factory_id") REFERENCES "factories"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "reporting_periods" ADD CONSTRAINT "reporting_periods_submitted_by_id_fkey" FOREIGN KEY ("submitted_by_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "material_alternatives" ADD CONSTRAINT "material_alternatives_material_id_fkey" FOREIGN KEY ("material_id") REFERENCES "materials"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "material_alternatives" ADD CONSTRAINT "material_alternatives_alternative_id_fkey" FOREIGN KEY ("alternative_material_id") REFERENCES "materials"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "factory_material_usage" ADD CONSTRAINT "factory_material_usage_factory_id_fkey" FOREIGN KEY ("factory_id") REFERENCES "factories"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "factory_material_usage" ADD CONSTRAINT "factory_material_usage_period_id_fkey" FOREIGN KEY ("reporting_period_id") REFERENCES "reporting_periods"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "factory_material_usage" ADD CONSTRAINT "factory_material_usage_material_id_fkey" FOREIGN KEY ("material_id") REFERENCES "materials"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "energy_usage" ADD CONSTRAINT "energy_usage_factory_id_fkey" FOREIGN KEY ("factory_id") REFERENCES "factories"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "energy_usage" ADD CONSTRAINT "energy_usage_period_id_fkey" FOREIGN KEY ("reporting_period_id") REFERENCES "reporting_periods"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "waste_streams" ADD CONSTRAINT "waste_streams_factory_id_fkey" FOREIGN KEY ("factory_id") REFERENCES "factories"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "waste_streams" ADD CONSTRAINT "waste_streams_period_id_fkey" FOREIGN KEY ("reporting_period_id") REFERENCES "reporting_periods"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "logistics" ADD CONSTRAINT "logistics_factory_id_fkey" FOREIGN KEY ("factory_id") REFERENCES "factories"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "logistics" ADD CONSTRAINT "logistics_period_id_fkey" FOREIGN KEY ("reporting_period_id") REFERENCES "reporting_periods"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "carbon_results" ADD CONSTRAINT "carbon_results_factory_id_fkey" FOREIGN KEY ("factory_id") REFERENCES "factories"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "carbon_results" ADD CONSTRAINT "carbon_results_period_id_fkey" FOREIGN KEY ("reporting_period_id") REFERENCES "reporting_periods"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "emission_sources" ADD CONSTRAINT "emission_sources_result_id_fkey" FOREIGN KEY ("result_id") REFERENCES "carbon_results"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "recommendations" ADD CONSTRAINT "recommendations_factory_id_fkey" FOREIGN KEY ("factory_id") REFERENCES "factories"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "recommendations" ADD CONSTRAINT "recommendations_result_id_fkey" FOREIGN KEY ("result_id") REFERENCES "carbon_results"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "recommendations" ADD CONSTRAINT "recommendations_intervention_id_fkey" FOREIGN KEY ("intervention_id") REFERENCES "interventions"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "recommendations" ADD CONSTRAINT "recommendations_material_id_fkey" FOREIGN KEY ("material_id") REFERENCES "materials"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "recommendations" ADD CONSTRAINT "recommendations_alternative_material_id_fkey" FOREIGN KEY ("alternative_material_id") REFERENCES "materials"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "recommendations" ADD CONSTRAINT "recommendations_emission_source_id_fkey" FOREIGN KEY ("emission_source_id") REFERENCES "emission_sources"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "simulations" ADD CONSTRAINT "simulations_factory_id_fkey" FOREIGN KEY ("factory_id") REFERENCES "factories"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "simulations" ADD CONSTRAINT "simulations_base_result_id_fkey" FOREIGN KEY ("base_result_id") REFERENCES "carbon_results"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "simulations" ADD CONSTRAINT "simulations_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "ml_pipeline_runs" ADD CONSTRAINT "ml_pipeline_runs_factory_id_fkey" FOREIGN KEY ("factory_id") REFERENCES "factories"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "ml_pipeline_runs" ADD CONSTRAINT "ml_pipeline_runs_period_id_fkey" FOREIGN KEY ("reporting_period_id") REFERENCES "reporting_periods"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "carbon_results" ADD CONSTRAINT "carbon_results_pipeline_run_id_fkey" FOREIGN KEY ("pipeline_run_id") REFERENCES "ml_pipeline_runs"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "carbon_credit_results" ADD CONSTRAINT "carbon_credit_results_factory_id_fkey" FOREIGN KEY ("factory_id") REFERENCES "factories"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "carbon_credit_results" ADD CONSTRAINT "carbon_credit_results_period_id_fkey" FOREIGN KEY ("reporting_period_id") REFERENCES "reporting_periods"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "audit_logs" ADD CONSTRAINT "audit_logs_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "audit_logs" ADD CONSTRAINT "audit_logs_factory_id_fkey" FOREIGN KEY ("factory_id") REFERENCES "factories"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- Required and high-value query-path indexes.
CREATE INDEX "users_email_idx" ON "users"("email");
CREATE INDEX "users_role_idx" ON "users"("role");
CREATE INDEX "factories_owner_id_idx" ON "factories"("owner_id");
CREATE INDEX "factories_manager_id_idx" ON "factories"("manager_id");
CREATE INDEX "factories_industry_type_idx" ON "factories"("industry_type");
CREATE INDEX "factories_city_idx" ON "factories"("city");
CREATE INDEX "factories_state_idx" ON "factories"("state");
CREATE INDEX "reporting_periods_factory_id_idx" ON "reporting_periods"("factory_id");
CREATE INDEX "reporting_periods_status_idx" ON "reporting_periods"("status");
CREATE INDEX "reporting_periods_start_idx" ON "reporting_periods"("period_start");
CREATE INDEX "reporting_periods_end_idx" ON "reporting_periods"("period_end");
CREATE INDEX "materials_name_idx" ON "materials"("name");
CREATE INDEX "materials_type_idx" ON "materials"("material_type");
CREATE INDEX "material_alternatives_material_id_idx" ON "material_alternatives"("material_id");
CREATE INDEX "material_alternatives_alternative_id_idx" ON "material_alternatives"("alternative_material_id");
CREATE INDEX "factory_material_usage_factory_id_idx" ON "factory_material_usage"("factory_id");
CREATE INDEX "factory_material_usage_period_id_idx" ON "factory_material_usage"("reporting_period_id");
CREATE INDEX "factory_material_usage_material_id_idx" ON "factory_material_usage"("material_id");
CREATE INDEX "factory_material_usage_factory_period_idx" ON "factory_material_usage"("factory_id", "reporting_period_id");
CREATE INDEX "energy_usage_factory_id_idx" ON "energy_usage"("factory_id");
CREATE INDEX "energy_usage_period_id_idx" ON "energy_usage"("reporting_period_id");
CREATE INDEX "energy_usage_factory_period_idx" ON "energy_usage"("factory_id", "reporting_period_id");
CREATE INDEX "waste_streams_factory_id_idx" ON "waste_streams"("factory_id");
CREATE INDEX "waste_streams_period_id_idx" ON "waste_streams"("reporting_period_id");
CREATE INDEX "waste_streams_factory_period_idx" ON "waste_streams"("factory_id", "reporting_period_id");
CREATE INDEX "logistics_factory_id_idx" ON "logistics"("factory_id");
CREATE INDEX "logistics_period_id_idx" ON "logistics"("reporting_period_id");
CREATE INDEX "logistics_factory_period_idx" ON "logistics"("factory_id", "reporting_period_id");
CREATE INDEX "emission_factors_category_idx" ON "emission_factors"("category");
CREATE INDEX "emission_factors_activity_idx" ON "emission_factors"("activity");
CREATE INDEX "emission_factors_country_idx" ON "emission_factors"("country");
CREATE INDEX "emission_factors_region_idx" ON "emission_factors"("region");
CREATE INDEX "emission_factors_version_idx" ON "emission_factors"("version");
CREATE INDEX "carbon_results_factory_id_idx" ON "carbon_results"("factory_id");
CREATE INDEX "carbon_results_period_id_idx" ON "carbon_results"("reporting_period_id");
CREATE INDEX "carbon_results_calculated_at_idx" ON "carbon_results"("calculated_at");
CREATE INDEX "emission_sources_result_id_idx" ON "emission_sources"("result_id");
CREATE INDEX "emission_sources_rank_idx" ON "emission_sources"("rank");
CREATE INDEX "interventions_category_idx" ON "interventions"("category");
CREATE INDEX "interventions_name_idx" ON "interventions"("name");
CREATE INDEX "recommendations_factory_id_idx" ON "recommendations"("factory_id");
CREATE INDEX "recommendations_result_id_idx" ON "recommendations"("result_id");
CREATE INDEX "recommendations_priority_idx" ON "recommendations"("priority");
CREATE INDEX "recommendations_status_idx" ON "recommendations"("status");
CREATE INDEX "recommendations_intervention_id_idx" ON "recommendations"("intervention_id");
CREATE INDEX "simulations_factory_id_idx" ON "simulations"("factory_id");
CREATE INDEX "simulations_base_result_id_idx" ON "simulations"("base_result_id");
CREATE INDEX "simulations_created_by_id_idx" ON "simulations"("created_by_id");
CREATE INDEX "ml_pipeline_runs_factory_id_idx" ON "ml_pipeline_runs"("factory_id");
CREATE INDEX "ml_pipeline_runs_period_id_idx" ON "ml_pipeline_runs"("reporting_period_id");
CREATE INDEX "ml_pipeline_runs_status_idx" ON "ml_pipeline_runs"("status");
CREATE INDEX "carbon_credit_results_factory_id_idx" ON "carbon_credit_results"("factory_id");
CREATE INDEX "carbon_credit_results_period_id_idx" ON "carbon_credit_results"("reporting_period_id");
CREATE INDEX "audit_logs_user_id_idx" ON "audit_logs"("user_id");
CREATE INDEX "audit_logs_factory_id_idx" ON "audit_logs"("factory_id");
CREATE INDEX "audit_logs_created_at_idx" ON "audit_logs"("created_at");
CREATE INDEX "audit_logs_entity_type_idx" ON "audit_logs"("entity_type");
CREATE INDEX "audit_logs_entity_id_idx" ON "audit_logs"("entity_id");

-- Database-level role correctness for factory associations.
CREATE FUNCTION "check_factory_user_roles"() RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM "users" WHERE "id" = NEW."owner_id" AND "role" = 'factory_owner') THEN
        RAISE EXCEPTION 'factory owner_id must reference a factory_owner';
    END IF;
    IF NEW."manager_id" IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM "users" WHERE "id" = NEW."manager_id" AND "role" = 'factory_manager'
    ) THEN
        RAISE EXCEPTION 'factory manager_id must reference a factory_manager';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER "factories_check_user_roles"
BEFORE INSERT OR UPDATE OF "owner_id", "manager_id" ON "factories"
FOR EACH ROW EXECUTE FUNCTION "check_factory_user_roles"();

CREATE FUNCTION "prevent_incompatible_user_role_change"() RETURNS TRIGGER AS $$
BEGIN
    IF NEW."role" <> OLD."role" THEN
        IF EXISTS (SELECT 1 FROM "factories" WHERE "owner_id" = NEW."id") AND NEW."role" <> 'factory_owner' THEN
            RAISE EXCEPTION 'cannot change role while user owns factories';
        END IF;
        IF EXISTS (SELECT 1 FROM "factories" WHERE "manager_id" = NEW."id") AND NEW."role" <> 'factory_manager' THEN
            RAISE EXCEPTION 'cannot change role while user manages a factory';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER "users_prevent_incompatible_role_change"
BEFORE UPDATE OF "role" ON "users"
FOR EACH ROW EXECUTE FUNCTION "prevent_incompatible_user_role_change"();

-- Protect factory tenancy from mismatched redundant factory_id values. Keeping
-- factory_id directly on operational rows makes authorization and future RLS
-- simple; these triggers ensure it always agrees with the parent object.
CREATE FUNCTION "check_reporting_period_factory"() RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM "reporting_periods"
        WHERE "id" = NEW."reporting_period_id" AND "factory_id" = NEW."factory_id"
    ) THEN
        RAISE EXCEPTION 'reporting period does not belong to factory';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER "factory_material_usage_check_tenant" BEFORE INSERT OR UPDATE OF "factory_id", "reporting_period_id" ON "factory_material_usage" FOR EACH ROW EXECUTE FUNCTION "check_reporting_period_factory"();
CREATE TRIGGER "energy_usage_check_tenant" BEFORE INSERT OR UPDATE OF "factory_id", "reporting_period_id" ON "energy_usage" FOR EACH ROW EXECUTE FUNCTION "check_reporting_period_factory"();
CREATE TRIGGER "waste_streams_check_tenant" BEFORE INSERT OR UPDATE OF "factory_id", "reporting_period_id" ON "waste_streams" FOR EACH ROW EXECUTE FUNCTION "check_reporting_period_factory"();
CREATE TRIGGER "logistics_check_tenant" BEFORE INSERT OR UPDATE OF "factory_id", "reporting_period_id" ON "logistics" FOR EACH ROW EXECUTE FUNCTION "check_reporting_period_factory"();
CREATE TRIGGER "carbon_results_check_tenant" BEFORE INSERT OR UPDATE OF "factory_id", "reporting_period_id" ON "carbon_results" FOR EACH ROW EXECUTE FUNCTION "check_reporting_period_factory"();
CREATE TRIGGER "ml_pipeline_runs_check_tenant" BEFORE INSERT OR UPDATE OF "factory_id", "reporting_period_id" ON "ml_pipeline_runs" FOR EACH ROW EXECUTE FUNCTION "check_reporting_period_factory"();
CREATE TRIGGER "carbon_credit_results_check_tenant" BEFORE INSERT OR UPDATE OF "factory_id", "reporting_period_id" ON "carbon_credit_results" FOR EACH ROW EXECUTE FUNCTION "check_reporting_period_factory"();

CREATE FUNCTION "check_carbon_result_pipeline_trace"() RETURNS TRIGGER AS $$
BEGIN
    IF NEW."pipeline_run_id" IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM "ml_pipeline_runs"
        WHERE "id" = NEW."pipeline_run_id"
          AND "factory_id" = NEW."factory_id"
          AND "reporting_period_id" = NEW."reporting_period_id"
          AND (NEW."ml_model_version" IS NULL OR "model_version" = NEW."ml_model_version")
    ) THEN
        RAISE EXCEPTION 'pipeline run does not match carbon result factory, period, or model version';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER "carbon_results_check_pipeline_trace" BEFORE INSERT OR UPDATE OF "factory_id", "reporting_period_id", "pipeline_run_id", "ml_model_version" ON "carbon_results" FOR EACH ROW EXECUTE FUNCTION "check_carbon_result_pipeline_trace"();

CREATE FUNCTION "check_result_factory"() RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM "carbon_results" WHERE "id" = NEW."base_result_id" AND "factory_id" = NEW."factory_id") THEN
        RAISE EXCEPTION 'base result does not belong to factory';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER "simulations_check_tenant" BEFORE INSERT OR UPDATE OF "factory_id", "base_result_id" ON "simulations" FOR EACH ROW EXECUTE FUNCTION "check_result_factory"();

CREATE FUNCTION "check_recommendation_trace"() RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM "carbon_results" WHERE "id" = NEW."result_id" AND "factory_id" = NEW."factory_id") THEN
        RAISE EXCEPTION 'carbon result does not belong to recommendation factory';
    END IF;
    IF NEW."emission_source_id" IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM "emission_sources" WHERE "id" = NEW."emission_source_id" AND "result_id" = NEW."result_id"
    ) THEN
        RAISE EXCEPTION 'emission source does not belong to recommendation result';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER "recommendations_check_trace" BEFORE INSERT OR UPDATE OF "factory_id", "result_id", "emission_source_id" ON "recommendations" FOR EACH ROW EXECUTE FUNCTION "check_recommendation_trace"();

-- Audit logs are append-only even if an application bug tries to mutate them.
CREATE FUNCTION "reject_audit_log_mutation"() RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'audit_logs are append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER "audit_logs_no_update" BEFORE UPDATE ON "audit_logs" FOR EACH ROW EXECUTE FUNCTION "reject_audit_log_mutation"();
CREATE TRIGGER "audit_logs_no_delete" BEFORE DELETE ON "audit_logs" FOR EACH ROW EXECUTE FUNCTION "reject_audit_log_mutation"();

-- Recalculations create new versioned rows. Previously calculated results and
-- published factors cannot be silently rewritten or removed.
CREATE FUNCTION "reject_immutable_history_mutation"() RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION '% history is immutable; create a new version instead', TG_TABLE_NAME;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER "carbon_results_no_update" BEFORE UPDATE ON "carbon_results" FOR EACH ROW EXECUTE FUNCTION "reject_immutable_history_mutation"();
CREATE TRIGGER "carbon_results_no_delete" BEFORE DELETE ON "carbon_results" FOR EACH ROW EXECUTE FUNCTION "reject_immutable_history_mutation"();
CREATE TRIGGER "emission_factors_no_update" BEFORE UPDATE ON "emission_factors" FOR EACH ROW EXECUTE FUNCTION "reject_immutable_history_mutation"();
CREATE TRIGGER "emission_factors_no_delete" BEFORE DELETE ON "emission_factors" FOR EACH ROW EXECUTE FUNCTION "reject_immutable_history_mutation"();
CREATE TRIGGER "reporting_periods_no_delete" BEFORE DELETE ON "reporting_periods" FOR EACH ROW EXECUTE FUNCTION "reject_immutable_history_mutation"();
CREATE TRIGGER "emission_sources_no_update" BEFORE UPDATE ON "emission_sources" FOR EACH ROW EXECUTE FUNCTION "reject_immutable_history_mutation"();
CREATE TRIGGER "emission_sources_no_delete" BEFORE DELETE ON "emission_sources" FOR EACH ROW EXECUTE FUNCTION "reject_immutable_history_mutation"();
CREATE TRIGGER "recommendations_no_delete" BEFORE DELETE ON "recommendations" FOR EACH ROW EXECUTE FUNCTION "reject_immutable_history_mutation"();
CREATE TRIGGER "simulations_no_delete" BEFORE DELETE ON "simulations" FOR EACH ROW EXECUTE FUNCTION "reject_immutable_history_mutation"();
CREATE TRIGGER "ml_pipeline_runs_no_delete" BEFORE DELETE ON "ml_pipeline_runs" FOR EACH ROW EXECUTE FUNCTION "reject_immutable_history_mutation"();
CREATE TRIGGER "carbon_credit_results_no_delete" BEFORE DELETE ON "carbon_credit_results" FOR EACH ROW EXECUTE FUNCTION "reject_immutable_history_mutation"();
