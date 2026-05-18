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
