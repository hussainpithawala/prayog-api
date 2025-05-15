# app/repositories/cassandra/dependencies.py
from app.repositories.cassandra.experiment_sampling_condition_repository import ExperimentSamplingConditionRepository

def get_condition_repo() -> ExperimentSamplingConditionRepository:
    return ExperimentSamplingConditionRepository()