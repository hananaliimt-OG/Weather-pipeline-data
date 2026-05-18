# Weather-pipeline-data

### Progress Update: May 18, 2026 — Phase 2: Snowflake Data Warehouse Integration

Established the secure data highway and continuous ingestion pipeline connecting Amazon S3 to Snowflake, focusing on cross-cloud security and semi-structured data transformation.

#### Key Milestones Achieved

* **Cross-Cloud Authentication:** Created an AWS IAM Trust Policy paired with a Snowflake Storage Integration object. This enables secure, credentialless authentication between the two cloud environments via Amazon Resource Names (ARNs) and External IDs.
* **External Staging:** Configured a Snowflake External Stage referencing the specific S3 landing zone directory, allowing Snowflake to map and read the raw cloud object files directly.
* **Semi-Structured JSON Parsing:** Developed and optimized a custom SQL extraction script using flattening logic. By deploying a specific JSON File Format template, the pipeline resolves truncation variances and cleanly parses nested variants (such as temperature, coordinates, and array-based weather descriptions) into explicit data types.
* **Continuous Ingestion Infrastructure:** Provisioned the target analytical relational table (`weather_data_final`) and wrapped the data-flattening query inside a automated **Snowpipe** definition. This establishes a passive serverless listener tied to an internal Amazon SQS notification channel.

#### Architecture Framework Completed Today
* AWS Lambda -> Amazon S3 (Raw JSON Object) -> Snowflake Storage Integration -> Snowflake External Stage -> Snowpipe Ingestion Compiler -> Structured Target Table.
