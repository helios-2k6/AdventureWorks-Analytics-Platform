# Working Standards for Data & Integration Projects

## 1. Objective

This document defines a common working standard for all projects related to data, integration, ETL, data platforms, automation, and general data processing systems. The goal is to ensure:

- code is easy to extend over time
- code is easy to review and maintain
- responsibilities of each module are clear
- code is easy to test and debug
- business logic is not tied to a specific source
- different projects can evolve under the same architectural standard

---

## 2. Core principles

### 2.1. Separate responsibilities clearly
Every project should be organized into clear layers:

1. Infrastructure / Core
   - configuration
   - logger
   - base utilities
   - environment handling
   - shared constants

2. Connectors / Adapters
   - database connector
   - API connector
   - file connector
   - storage connector
   - message queue connector

3. Services / Business Logic
   - ingestion service
   - validation service
   - transformation service
   - mapping service
   - enrichment service

4. Orchestration / Jobs
   - pipeline runner
   - batch process
   - workflow orchestrator
   - scheduled job

5. Entry point
   - application bootstrap
   - runner / command initializer
   - only invokes classes that are already designed for the task

### 2.2. Do not put business logic inside main.py
The `main.py` file or any entrypoint should only:

- initialize the application
- inject dependencies
- call the runner / job
- start the workflow

`main.py` should not contain:

- raw query logic
- data transformation logic
- validation logic
- business process logic
- parser logic

---

## 3. Mandatory OOP requirements

### 3.1. All processing logic must belong to a class or service
Each function should be encapsulated in a clear class or service.

Examples:

- `SQLServerConnector` -> manages database connections
- `ApiConnector` -> manages API requests
- `DataValidator` -> validates data
- `IngestionJob` -> orchestrates the pipeline
- `Transformer` -> transforms data

### 3.2. `main.py` should only call classes
Every time you write code, check whether:

- `main.py` is invoking procedural functions directly
- if so, move the logic into a class or service

Correct example:

```python
from src.app.app import App

if __name__ == "__main__":
    app = App()
    app.run()
```

Incorrect example:

```python
from scripts.pipeline import run_pipeline

if __name__ == "__main__":
    run_pipeline()
```

If `run_pipeline()` contains business logic, it should live inside a class such as `DataPipelineJob`.

---

## 4. Distinguish clearly: Connection, Test, and Process

This is a mandatory standard for every project.

### 4.1. Connection layer
Responsibility: create and manage connections to a source or target system.

Examples:

- `DatabaseConnector`
- `SQLServerConnector`
- `PostgreSQLConnector`
- `ApiConnector`
- `S3Connector`
- `KafkaConnector`

It should only do:

- initialize clients/sessions
- connect/disconnect
- execute queries or requests
- handle timeouts, credentials, and environment configuration

It should not do:

- business validation
- data transformation
- business logic
- domain-specific checks

### 4.2. Test / health-check layer
Responsibility: verify that a source or system is ready and usable.

Examples:

- `ConnectionHealthChecker`
- `DatabaseHealthChecker`
- `ApiHealthChecker`

Its responsibilities include:

- checking credentials
- pinging or testing a query / GET /health
- verifying tables, schemas, or endpoints are available
- returning status as `OK` / `FAIL`

### 4.3. Process / orchestration layer
Responsibility: coordinate a specific workflow.

Examples:

- `IngestionJob`
- `LoadJob`
- `ValidationJob`
- `TransformationJob`
- `PipelineRunner`

Its responsibilities include:

- calling connectors
- calling validators
- calling transformers
- coordinating the sequence of steps
- handling retries, logging, and error summaries

### 4.4. Rule to avoid confusion
- If the code is meant to “open a connection” => use a connector class
- If the code is meant to “test whether the connection works” => use a health checker
- If the code is meant to “read data, transform it, validate it, and load it” => use a job/service

---

## 5. Standard package organization

### 5.1. Recommended package structure

```text
src/
  app/
    app.py
    main.py
  core/
    config.py
    logger.py
    settings.py
  connectors/
    base_connector.py
    sql_server_connector.py
    postgres_connector.py
    api_connector.py
    s3_connector.py
  services/
    health_check_service.py
    validator_service.py
    ingestion_service.py
    transformation_service.py
  jobs/
    ingest_job.py
    pipeline_job.py
  domain/
    sales/
      extractor.py
      transformer.py
      validator.py
```

### 5.2. Avoid this structure

```text
scripts/
  ingest.py
  validate.py
  transform.py
  main.py
```

If `scripts/` only contains thin wrappers or CLI bootstrap code, that is acceptable.

If `scripts/` contains real business processing logic, the project is mixing procedural scripts with an object-oriented architecture.

---

## 6. Design for extensibility across all data sources

### 6.1. Expand from SQL to API, file, storage, or queue systems
Business logic must not be tied to one specific source type.

Incorrect example:

```python
if source == "sql":
    query = ...
elif source == "api":
    response = requests.get(...)
```

Correct example:

```python
class BaseConnector:
    def connect(self):
        raise NotImplementedError

    def read(self):
        raise NotImplementedError

    def write(self, data):
        raise NotImplementedError
```

Then implement specific classes such as:

- `SQLServerConnector(BaseConnector)`
- `ApiConnector(BaseConnector)`
- `PostgreSQLConnector(BaseConnector)`
- `S3Connector(BaseConnector)`

After that, business logic only calls:

```python
source_connector.read()
```

### 6.2. Purpose of abstraction
- the source should not affect the workflow
- new sources can be added without breaking business logic
- the code follows interfaces instead of a single concrete implementation
- easier testing and mocking at the interface level

---

## 7. Mandatory code review rules

### 7.1. During each review, ask these questions

- Is `main.py` only calling classes/services?
- Is business logic hidden inside procedural scripts?
- Is connection logic mixed with validation logic?
- Is source abstraction being used properly?
- Are jobs/orchestration and services separated clearly?
- Are packages overloaded with too many responsibilities?
- Are functions too long and doing too many things?

### 7.2. Review checklist

- [ ] `main.py` does not contain business logic
- [ ] connector classes are separated from process logic
- [ ] validation is separated from connection logic
- [ ] classes have clear names and single responsibilities
- [ ] package names follow functional responsibilities
- [ ] there is abstraction around data sources
- [ ] the code is testable and not dependent on a specific implementation

---

## 8. Naming conventions

### 8.1. Class names
- `DatabaseConnector`
- `ApiConnector`
- `DataValidator`
- `IngestionJob`
- `Transformer`
- `PipelineRunner`

### 8.2. File names
- `database_connector.py`
- `api_connector.py`
- `data_validator.py`
- `ingestion_job.py`

### 8.3. Function names
- `connect()`
- `disconnect()`
- `execute_query()`
- `validate_schema()`
- `run()`
- `load()`

Function names should be verbs and clearly describe the action.

---

## 9. Standard team workflow

### 9.1. Every task should follow four steps

1. analyze the requirement
2. identify the correct layer
   - connector / service / job / app
3. design the class and interface
4. implement the code according to the pattern

### 9.2. After coding, verify the following

- which module owns which responsibility
- whether the entrypoint calls the correct class
- whether adding a new source is easy
- whether the code is easy to test
- whether duplicate logic exists

### 9.3. Each task must be clearly described

- which layer it belongs to
- which class handles it
- input and output
- dependencies
- expected result

---

## 10. Important notes

### 10.1. Do not put too many responsibilities in one file
A file should not contain all of the following at once:

- connection logic
- transformation logic
- validation logic
- pipeline orchestration
- CLI entrypoint

### 10.2. Do not overload `main.py`
If `main.py` becomes long and contains business logic, it should be split into classes.

### 10.3. Do not use source-specific logic in the business pipeline
The workflow should not know whether the source is SQL, API, file, or queue.

### 10.4. Every project should define its structure before writing code
The architecture should be planned before implementation.

---

## 11. Conclusion

If a project follows this standard, it will be easier to:

- extend with new data sources
- refactor without breaking existing behavior
- review code faster
- test more effectively
- maintain more efficiently

In short:

- `connector` = connection
- `health check` = connectivity test
- `service/job` = business logic execution
- `main.py` = launcher, not business logic
- `package structure` = functional separation and clarity

---

## 12. Final checklist

Before merging code, ask yourself:

- [ ] Is the main file only orchestrating?
- [ ] Are classes/services being used instead of procedural functions?
- [ ] Is the connection layer separated from the process layer?
- [ ] Is validation separated from connectors?
- [ ] Will adding a new source break the business logic?
- [ ] Is the package structure organized by functionality?
- [ ] Is the code easy to test independently?

If all answers are “yes,” the code meets the general design standard for data projects.
