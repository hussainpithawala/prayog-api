# app/dependencies.py
from app.repositories.cassandra.condition_repository import ExperimentSamplingConditionRepository
from app.repositories.cassandra.service_repository import ServiceRepository
from app.repositories.cassandra.experiment_repository import ExperimentRepository
from app.repositories.cassandra.bucket_repository import BucketRepository
from app.repositories.cassandra.sample_repository import BucketedSampleRepository
from app.repositories.cassandra.criterion_repository import ExperimentSamplingCriterionRepository


def get_service_repository() -> ServiceRepository:
    return ServiceRepository()


def get_experiment_repository() -> ExperimentRepository:
    return ExperimentRepository()


def get_bucket_repository() -> BucketRepository:
    return BucketRepository()


def get_experiment_sampling_criterion_repository() -> ExperimentSamplingCriterionRepository:
    return ExperimentSamplingCriterionRepository()


def get_bucketed_sample_repository() -> BucketedSampleRepository:
    return BucketedSampleRepository()

def get_criterion_repository() -> ExperimentSamplingCriterionRepository:
    return ExperimentSamplingCriterionRepository()

def get_condition_repository() -> ExperimentSamplingConditionRepository:
    return ExperimentSamplingConditionRepository()

def get_sample_repository() -> BucketedSampleRepository:
    return BucketedSampleRepository()