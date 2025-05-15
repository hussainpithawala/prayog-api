-- # Keyspace creation
CREATE KEYSPACE IF NOT EXISTS experimentation
WITH replication = {'class': 'NetworkTopologyStrategy', 'replication_factor': 3};

USE experimentation;

-- # Services table
CREATE TABLE services (
    id UUID PRIMARY KEY,
    name TEXT,
    active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) WITH additional_write_policy = '99p';

CREATE MATERIALIZED VIEW services_by_name AS
    SELECT * FROM services
    WHERE name IS NOT NULL AND id IS NOT NULL
    PRIMARY KEY (name, id);

-- # Experiments table - optimized for service-based queries
CREATE TABLE experiments (
    id UUID PRIMARY KEY,
    service_id UUID,
    name TEXT,
    active BOOLEAN,
    last_deactivated_at TIMESTAMP,
    last_activated_at TIMESTAMP,
    scheduled_start_date TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
) WITH CLUSTERING ORDER BY (id ASC);

-- # Secondary index for experiment name lookup
CREATE MATERIALIZED VIEW experiments_by_name AS
    SELECT * FROM experiments
    WHERE name IS NOT NULL AND service_id IS NOT NULL AND id IS NOT NULL
    PRIMARY KEY (name, service_id, id);

-- # Bucket definitions - denormalized with experiment
CREATE TABLE experiment_buckets (
    id UUID,
    experiment_id UUID,
    bucket_name TEXT PRIMARY KEY ,
    percentage_distribution INT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY ((id), experiment_id, bucket_name)
) WITH CLUSTERING ORDER BY (bucket_name ASC);

-- # Sampling criteria with denormalized conditions
-- Main criteria table
CREATE TABLE IF NOT EXISTS experimentation.experiment_sampling_criteria (
    id UUID,
    experiment_id UUID,
    sampling_model TEXT,
    sampling_attribute TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY ((experiment_id), id)
) WITH CLUSTERING ORDER BY (id ASC);

-- Conditions table
CREATE TABLE IF NOT EXISTS experimentation.experiment_sampling_conditions (
    id UUID,
    criterion_id UUID,
    experiment_id UUID,
    model TEXT,
    property TEXT,
    value TEXT,
    condition TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY ((criterion_id), id)
) WITH CLUSTERING ORDER BY (id ASC);

-- Materialized view remains the same
CREATE MATERIALIZED VIEW IF NOT EXISTS experimentation.conditions_by_experiment AS
    SELECT * FROM experiment_sampling_conditions
    WHERE experiment_id IS NOT NULL AND criterion_id IS NOT NULL AND id IS NOT NULL
    PRIMARY KEY ((experiment_id), criterion_id, id);

-- # Bucketed samples - optimized for time-based access
CREATE TABLE bucketed_samples (
    experiment_id UUID,
    sampled_entity TEXT,
    sampled_value TEXT,
    allocated_bucket TEXT,
    complete BOOLEAN,
    completed_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY ((experiment_id, sampled_entity), sampled_value, created_at)
) WITH CLUSTERING ORDER BY (sampled_value ASC, created_at DESC);

-- # Terminations - denormalized with experiment
CREATE TABLE experiment_terminations (
    experiment_id UUID,
    termination_id UUID,
    termination_type TEXT,
    termination_value TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY ((experiment_id), termination_id)
) WITH CLUSTERING ORDER BY (termination_id ASC);