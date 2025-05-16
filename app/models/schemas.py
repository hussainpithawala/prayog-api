# app/models/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Optional
import uuid

class ServiceBase(BaseModel):
    name: str
    active: bool = True

class ServiceCreate(ServiceBase):
    pass

class Service(ServiceBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class ExperimentBase(BaseModel):
    name: str
    service_id: uuid.UUID
    active: bool = True
    scheduled_start_date: Optional[datetime] = None

class ExperimentCreate(ExperimentBase):
    pass

class Experiment(ExperimentBase):
    id: uuid.UUID
    last_deactivated_at: Optional[datetime] = None
    last_activated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class ExperimentBucketBase(BaseModel):
    experiment_id: uuid.UUID
    bucket_name: str
    percentage_distribution: int

class ExperimentBucketCreate(ExperimentBucketBase):
    pass

class ExperimentBucket(ExperimentBucketBase):
    experiment_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class ExperimentSamplingConditionBase(BaseModel):
    model: str
    property: str
    value: str
    condition: str

class ExperimentSamplingConditionCreate(ExperimentSamplingConditionBase):
    criterion_id: uuid.UUID = None
    experiment_id: uuid.UUID

class ExperimentSamplingCondition(ExperimentSamplingConditionBase):
    id: uuid.UUID
    criterion_id: uuid.UUID
    experiment_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class ExperimentSamplingCriterionBase(BaseModel):
    sampling_model: str
    sampling_attribute: str

class ExperimentSamplingCriterionCreate(ExperimentSamplingCriterionBase):
    experiment_id: uuid.UUID

class ExperimentSamplingCriterion(ExperimentSamplingCriterionBase):
    id: uuid.UUID
    experiment_id: uuid.UUID
    conditions: List[ExperimentSamplingCondition] = []
    created_at: datetime
    updated_at: datetime

class ExperimentTerminationBase(BaseModel):
    termination_type: str
    termination_value: str

class ExperimentTerminationCreate(ExperimentTerminationBase):
    pass

class ExperimentTermination(ExperimentTerminationBase):
    experiment_id: uuid.UUID
    termination_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class BucketedSampleBase(BaseModel):
    sampled_value: str
    sampled_entity: str
    allocated_bucket: str

class BucketedSampleCreate(BucketedSampleBase):
    pass

class BucketedSample(BucketedSampleBase):
    experiment_id: uuid.UUID
    complete: bool = False
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime