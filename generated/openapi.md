# Experiment API

API for managing experiment samples

# Base URL


| URL | Description |
|-----|-------------|


# APIs

## POST /api/v1/services

Create Service





### Request Body

[ServiceCreate](#servicecreate)







### Responses

#### 201


Successful Response


[Service](#service)







#### 422


Validation Error


[HTTPValidationError](#httpvalidationerror)







## GET /api/v1/services

List Services



### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| active_only | boolean | False |  |


### Responses

#### 200


Successful Response


array







#### 422


Validation Error


[HTTPValidationError](#httpvalidationerror)







## GET /api/v1/services/{service_id}

Get Service



### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| service_id | string | True |  |


### Responses

#### 200


Successful Response


[Service](#service)







#### 422


Validation Error


[HTTPValidationError](#httpvalidationerror)







## POST /api/v1/services/{service_id}/experiments

Create Experiment



### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| service_id | string | True |  |


### Request Body

[ExperimentCreate](#experimentcreate)







### Responses

#### 200


Successful Response


[Experiment](#experiment)







#### 422


Validation Error


[HTTPValidationError](#httpvalidationerror)







## GET /api/v1/services/{service_id}/experiments

List Experiments



### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| service_id | string | True |  |
| active_only | boolean | False |  |


### Responses

#### 200


Successful Response


array







#### 422


Validation Error


[HTTPValidationError](#httpvalidationerror)







## POST /api/v1/experiments/{experiment_id}/criteria

Create Criterion



### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| experiment_id | string | True |  |


### Request Body

[Body_create_criterion_api_v1_experiments__experiment_id__criteria_post](#body_create_criterion_api_v1_experiments__experiment_id__criteria_post)







### Responses

#### 200


Successful Response


[ExperimentSamplingCriterion](#experimentsamplingcriterion)







#### 422


Validation Error


[HTTPValidationError](#httpvalidationerror)







## GET /api/v1/experiments/{experiment_id}/criteria

List Criteria



### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| experiment_id | string | True |  |


### Responses

#### 200


Successful Response


array







#### 422


Validation Error


[HTTPValidationError](#httpvalidationerror)







## POST /api/v1/criteria/{criterion_id}/conditions

Create Condition



### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| criterion_id | string | True |  |


### Request Body

[ExperimentSamplingConditionCreate](#experimentsamplingconditioncreate)







### Responses

#### 200


Successful Response


[ExperimentSamplingCondition](#experimentsamplingcondition)







#### 422


Validation Error


[HTTPValidationError](#httpvalidationerror)







## GET /api/v1/criteria/{criterion_id}/conditions

List Conditions



### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| criterion_id | string | True |  |


### Responses

#### 200


Successful Response


array







#### 422


Validation Error


[HTTPValidationError](#httpvalidationerror)







## POST /api/v1/experiments/{experiment_id}/buckets

Create Bucket



### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| experiment_id | string | True |  |


### Request Body

[ExperimentBucketCreate](#experimentbucketcreate)







### Responses

#### 200


Successful Response


[ExperimentBucket](#experimentbucket)







#### 422


Validation Error


[HTTPValidationError](#httpvalidationerror)







## GET /api/v1/experiments/{experiment_id}/buckets

List Buckets



### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| experiment_id | string | True |  |


### Responses

#### 200


Successful Response


array







#### 422


Validation Error


[HTTPValidationError](#httpvalidationerror)







## POST /api/v1/experiments/{experiment_id}/samples

Create Sample



### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| experiment_id | string | True |  |


### Request Body

[BucketedSampleCreate](#bucketedsamplecreate)







### Responses

#### 200


Successful Response


[BucketedSample](#bucketedsample)







#### 422


Validation Error


[HTTPValidationError](#httpvalidationerror)







## GET /api/v1/experiments/{experiment_id}/samples

List Samples



### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| experiment_id | string | True |  |
| limit | integer | False |  |


### Responses

#### 200


Successful Response


array







#### 422


Validation Error


[HTTPValidationError](#httpvalidationerror)







## POST /api/v1/experiments/{experiment_id}/samples/{sample_id}/complete

Mark Sample Complete



### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| sample_id | string | True |  |


### Responses

#### 200


Successful Response


[BucketedSample](#bucketedsample)







#### 422


Validation Error


[HTTPValidationError](#httpvalidationerror)







## GET /health

Health Check





### Responses

#### 200


Successful Response








# Components



## Body_create_criterion_api_v1_experiments__experiment_id__criteria_post



| Field | Type | Description |
|-------|------|-------------|
| criterion |  |  |
| conditions | array |  |


## BucketedSample



| Field | Type | Description |
|-------|------|-------------|
| experiment_id | string |  |
| sampled_value | string |  |
| sampled_entity | string |  |
| allocated_bucket | string |  |
| id | string |  |
| complete | boolean |  |
| completed_at |  |  |
| created_at | string |  |
| updated_at | string |  |


## BucketedSampleCreate



| Field | Type | Description |
|-------|------|-------------|
| experiment_id | string |  |
| sampled_value | string |  |
| sampled_entity | string |  |
| allocated_bucket | string |  |


## Experiment



| Field | Type | Description |
|-------|------|-------------|
| name | string |  |
| service_id | string |  |
| active | boolean |  |
| scheduled_start_date |  |  |
| id | string |  |
| last_deactivated_at |  |  |
| last_activated_at |  |  |
| created_at | string |  |
| updated_at | string |  |


## ExperimentBucket



| Field | Type | Description |
|-------|------|-------------|
| experiment_id | string |  |
| bucket_name | string |  |
| percentage_distribution | integer |  |
| created_at | string |  |
| updated_at | string |  |


## ExperimentBucketCreate



| Field | Type | Description |
|-------|------|-------------|
| experiment_id | string |  |
| bucket_name | string |  |
| percentage_distribution | integer |  |


## ExperimentCreate



| Field | Type | Description |
|-------|------|-------------|
| name | string |  |
| service_id | string |  |
| active | boolean |  |
| scheduled_start_date |  |  |


## ExperimentSamplingCondition



| Field | Type | Description |
|-------|------|-------------|
| model | string |  |
| property | string |  |
| value | string |  |
| condition | string |  |
| id | string |  |
| criterion_id | string |  |
| experiment_id | string |  |
| created_at | string |  |
| updated_at | string |  |


## ExperimentSamplingConditionCreate



| Field | Type | Description |
|-------|------|-------------|
| model | string |  |
| property | string |  |
| value | string |  |
| condition | string |  |
| criterion_id | string |  |
| experiment_id | string |  |


## ExperimentSamplingCriterion



| Field | Type | Description |
|-------|------|-------------|
| sampling_model | string |  |
| sampling_attribute | string |  |
| id | string |  |
| experiment_id | string |  |
| conditions | array |  |
| created_at | string |  |
| updated_at | string |  |


## ExperimentSamplingCriterionCreate



| Field | Type | Description |
|-------|------|-------------|
| sampling_model | string |  |
| sampling_attribute | string |  |
| experiment_id | string |  |


## HTTPValidationError



| Field | Type | Description |
|-------|------|-------------|
| detail | array |  |


## Service



| Field | Type | Description |
|-------|------|-------------|
| name | string |  |
| active | boolean |  |
| id | string |  |
| created_at | string |  |
| updated_at | string |  |


## ServiceCreate



| Field | Type | Description |
|-------|------|-------------|
| name | string |  |
| active | boolean |  |


## ValidationError



| Field | Type | Description |
|-------|------|-------------|
| loc | array |  |
| msg | string |  |
| type | string |  |
