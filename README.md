# Real-Time Event-Driven Weather Data Pipeline

An enterprise-grade, event-driven data engineering pipeline designed to automate the ingestion, transaction auditing, and relational analytics of live meteorological data using AWS Serverless Infrastructure and the Snowflake Cloud Data Platform. 

The architecture features programmatic data ingestion, decoupled transaction logging, zero-copy automated data warehouse loading via Snowpipe, active schema-on-read transformation, and an independent real-time asynchronous error monitoring stream.

---

## System Architecture and Data Flow

The system is engineered across four distinct, fully decoupled architectural layers to enforce high availability, strict fault isolation, and structural elasticity:

1. **Orchestration Layer:** Amazon EventBridge triggers the primary ingestion compute layer via a scheduled cron rule configured to run on a deterministic time interval.
2. **Ingestion and Auditing Layer:** The primary AWS Lambda function (Python 3.12) executes a secure HTTPS GET request to the OpenWeather API endpoint. Upon receiving the payload, it writes the raw data as a JSON object into an Amazon S3 landing bucket. Simultaneously, it logs runtime execution metadata—including a unique UUID execution ID, runtime timestamp, and operation status—into an Amazon DynamoDB transactional ledger.
3. **Automated Warehousing Layer (Snowpipe):** An S3 Event Notification publishes an event to an SQS queue managed natively by Snowflake Snowpipe immediately upon object creation in the S3 landing bucket. Snowpipe consumes the message queue asynchronously, provisions transient compute resources, and runs a COPY INTO command to load the raw JSON object directly into a landing table (`WEATHER_DATA_RAW`) formatted with a Snowflake VARIANT data type.
4. **Asynchronous Stream Auditing Layer:** An active DynamoDB Stream continuously tracks modifications to the logging ledger. A secondary Alerting AWS Lambda function is bound directly to this stream. Using native Lambda event source mapping and a JSON filter pattern, the function remains dormant during SUCCESS states but activates instantaneously upon a FAILED status log to extract error traces for downstream engineering triage.

---

## Core Infrastructure Tech Stack
* **Cloud Infrastructure Provider:** Amazon Web Services (AWS)
  * **Serverless Compute:** AWS Lambda (Python 3.12 deployment packages)
  * **Object Storage:** Amazon S3 (Simple Storage Service)
  * **NoSQL Transactional Ledger:** Amazon DynamoDB + DynamoDB Streams
  * **Event Orchestration:** Amazon EventBridge (CloudWatch Events Engine)
  * **Access Control:** AWS Identity and Access Management (IAM Least-Privilege Execution Policies)
* **Cloud Data Platform:** Snowflake
  * **Continuous Loading Ingestion:** Snowpipe (Auto-Ingest SQS Architecture)
  * **Compute Resources:** Virtual Warehouses (Configured with automated suspension parameters)
  * **Semi-Structured Processing:** SQL JSON Notation (Schema-on-Read Evaluation)
* **Programming Languages:** Python, Standard Structured Query Language (SQL)

---

## Project Repository Structure
```text
├── src/
│   ├── ingestion_lambda.py   # Core ET/L handler executing API requests, S3 staging, and audit logging
│   └── alerting_lambda.py    # Asynchronous stream-processor isolated for real-time failure notification
├── sql/
│   └── snowflake_setup.sql   # Complete database, warehouse, table, stage, and pipe DDL/DML scripts
└── README.md                 # Technical system documentation and deployment blueprint
