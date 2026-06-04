# Weather-pipeline-data

### Progress Update: Phase 1 — Data Sourcing, Serverless Compute, and Object Storage

Built the foundational ingestion layer of the data pipeline, focusing on automated API data retrieval, environment variable security, and scalable cloud storage configuration.

#### Key Milestones Achieved

* **API Integration:** Established connectivity with the OpenWeather Map API to source real-time regional weather metrics, including temperature, humidity, wind data, and localized descriptions.
* **Serverless Compute Infrastructure:** Developed and deployed an AWS Lambda function running a Python runtime environment. This serverless script handles the programmatic HTTP requests to the external API, processes the payload response, and formats the output into structured JSON files.
* **Secure Credential Management:** Implemented AWS Lambda Environment Variables to securely store API authentication keys, preventing hardcoded credentials within the source code repo.
* **Data Lake Landing Zone:** Provisioned an Amazon S3 bucket (`openweather-pipeline-data-hanan`) with a dedicated directory structure (`raw_weather_data/`) to act as the primary, high-durability landing zone for the incoming raw JSON objects.
* **Automated Scheduling:** Configured an Amazon EventBridge Rule (CloudWatch Event) acting as a cron-job trigger to systematically invoke the Lambda function at fixed intervals, achieving hands-free data collection.

#### Architecture Framework Completed in Phase 1
* OpenWeather API -> HTTP Request -> AWS Lambda (Python Compute) -> Secure Parameter Store -> Amazon S3 Object Storage (Raw JSON).

### Progress Update: May 18, 2026 — Phase 2: Snowflake Data Warehouse Integration

Established the secure data highway and continuous ingestion pipeline connecting Amazon S3 to Snowflake, focusing on cross-cloud security and semi-structured data transformation.

#### Key Milestones Achieved

* **Cross-Cloud Authentication:** Created an AWS IAM Trust Policy paired with a Snowflake Storage Integration object. This enables secure, credentialless authentication between the two cloud environments via Amazon Resource Names (ARNs) and External IDs.
* **External Staging:** Configured a Snowflake External Stage referencing the specific S3 landing zone directory, allowing Snowflake to map and read the raw cloud object files directly.
* **Semi-Structured JSON Parsing:** Developed and optimized a custom SQL extraction script using flattening logic. By deploying a specific JSON File Format template, the pipeline resolves truncation variances and cleanly parses nested variants (such as temperature, coordinates, and array-based weather descriptions) into explicit data types.
* **Continuous Ingestion Infrastructure:** Provisioned the target analytical relational table (`weather_data_final`) and wrapped the data-flattening query inside a automated **Snowpipe** definition. This establishes a passive serverless listener tied to an internal Amazon SQS notification channel.

#### Architecture Framework Completed Today
* AWS Lambda -> Amazon S3 (Raw JSON Object) -> Snowflake Storage Integration -> Snowflake External Stage -> Snowpipe Ingestion Compiler -> Structured Target Table.


##  Today's Sprint: Ingestion Security, Audit Logging & Warehouse Ingestion

Today, the pipeline architecture was upgraded from a basic script into a secure, production-ready backend system. The focus was on implementing configuration security, an asynchronous audit logging layer, and end-to-end telemetry verification.

### What Was Built & Implemented Today:

#### 1. Configuration Security (Production Standard)
* Abstracted all sensitive API credentials and geographic coordinates (`LAT`, `LON`, `API_KEY`) out of the codebase.
* Migrated the ingestion engine to interface with secrets exclusively via secure **AWS Lambda Environment Variables** using Python’s `os.environ` module, preventing private keys from being exposed in source control.

#### 2. Live NoSQL Audit Ledger (DynamoDB Integration)
* Provisioned an AWS DynamoDB tracking table (`weather_pipeline_log`) using a combination of `execution_id` (UUIDv4 Partition Key) and a `timestamp` (Sort Key).
* Enabled **DynamoDB Streams (New Image)** to capture real-time change data capture (CDC) logs for downstream alerting.
* Upgraded the Python Lambda script using `boto3` to dynamically handle database states:
  * Drops an initial heartbeat record flagged as `IN_PROGRESS` before fetching API data.
  * Electronically updates the state to `SUCCESS` upon successful S3 archival.
  * Captures runtime execution exceptions and logs them as `FAILED` with explicit error traces if any breakages occur.

#### 3. IAM Security & Permission Orchestration
* Resolved real-time cloud security barriers (`AccessDeniedException`).
* Configured identity-based execution policies on the Lambda IAM Role, explicitly allowing granular NoSQL interactions (`dynamodb:PutItem`, `dynamodb:UpdateItem`).

#### 4. Warehouse Verification & Data Cleaning Layer
* Verified end-to-end data telemetry across the entire AWS-to-Snowflake bridge, confirming live records automatically load via Snowpipe notifications.
* Engineered an analytical data-cleaning query inside Snowflake using window functions (`ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`) to automatically identify, rank, and strip out duplicate ingestion entries, serving a clean data layer for reporting.

---

## Project Status and Validation Milestone

The complete end-to-end event-driven architecture was fully validated, live-tested, and deployed on June 4, 2026. The pipeline is 100% operational, self-monitoring, and verified across all integrated cloud systems.

### Ingestion and Storage Layer Validation
* **Compute Triggering:** Manual and cron-scheduled Amazon EventBridge execution vectors were verified for the primary ingestion Lambda function.
* **Storage Ingestion:** Successfully initiated communication with the OpenWeather API, dropping structured JSON payloads into the target Amazon S3 object landing zone with clean timestamp tracking.
* **Transaction Ledger Auditing:** Confirmed transactional writes to the Amazon DynamoDB ledger table (`weather_pipeline_log`). Each execution successfully records unique UUID execution IDs, accurate epoch timestamps, and system operational states (`SUCCESS` or `FAILED`).

### Automated Warehousing and Snowpipe Validation
* **Event Notification Bridge:** S3 event routing to the Snowpipe SQS queue was verified. Ingestion occurs natively within seconds of file arrival without manual intervention.
* **Analytical Ingestion Verification:** Validated structural data landing inside the Snowflake environment. Running the primary tracking queries inside `WEATHER_DB.PUBLIC.WEATHER_DATA_FINAL` confirmed successful execution of the schema-on-read pipeline, converting the semi-structured JSON `VARIANT` payloads into relational datasets:

```sql
SELECT * FROM WEATHER_DB.PUBLIC.WEATHER_DATA_FINAL 
ORDER BY recorded_at DESC 
LIMIT 5;

