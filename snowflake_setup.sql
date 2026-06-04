-- ============================================================================
-- STEP 1: STORAGE, WAREHOUSE & DATABASE ARCHITECTURE
-- ============================================================================

-- Create a dedicated virtual warehouse for data compute tasks
CREATE OR REPLACE WAREHOUSE COMPUTE_WH 
WITH WAREHOUSE_SIZE = 'XSMALL' 
AUTO_SUSPEND = 60 
AUTO_RESUME = TRUE;

-- Create the main relational data database
CREATE DATABASE IF NOT EXISTS WEATHER_DB;
USE DATABASE WEATHER_DB;
USE SCHEMA PUBLIC;


-- ============================================================================
-- STEP 2: STAGING TABLES (RAW VARIANT STORAGE)
-- ============================================================================

-- Create a raw landing table to safely harbor semi-structured JSON strings
CREATE OR REPLACE TABLE WEATHER_DATA_RAW (
    raw_json VARIANT,
    ingested_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);


-- ============================================================================
-- STEP 3: FILE FORMAT CONFIGURATION (JSON SCHEMALESS ANALYSIS)
-- ============================================================================

-- Create a dedicated file format to properly handle JSON data properties
CREATE OR REPLACE FILE FORMAT JSON_FILE_FORMAT
    TYPE = 'JSON'
    STRIP_OUTER_ARRAY = TRUE
    IGNORE_UTF8_ERRORS = TRUE;


-- ============================================================================
-- STEP 4: EXTERNAL STAGE CONFIGURATION (AWS S3 BRIDGE)
-- ============================================================================

-- Establish a secure external pointer tracking the live AWS S3 landing bucket
-- Note: Replace with your actual S3 bucket path and AWS IAM integration/credentials
CREATE OR REPLACE STAGE WEATHER_S3_STAGE
    URL = 's3://your-weather-data-bucket-name/'
    FILE_FORMAT = JSON_FILE_FORMAT;


-- ============================================================================
-- STEP 5: AUTOMATED INGESTION PIPELINE (SNOWPIPE)
-- ============================================================================

-- Create the continuous loading pipe that triggers instantly upon S3 events
CREATE OR REPLACE PIPE WEATHER_SNOWPIPE
AUTO_INGEST = TRUE
AS
COPY INTO WEATHER_DB.PUBLIC.WEATHER_DATA_RAW
FROM @WEATHER_DB.PUBLIC.WEATHER_S3_STAGE;


-- ============================================================================
-- STEP 6: ANALYTICAL VIEW / FINAL DESTINATION TABLE (RELATIONAL SCHEMA)
-- ============================================================================

-- Create the final structured relational table parsed from the raw variant data
CREATE OR REPLACE TABLE WEATHER_DATA_FINAL (
    city_name STRING,
    country STRING,
    temperature_celsius FLOAT,
    weather_condition STRING,
    humidity INT,
    wind_speed FLOAT,
    recorded_at TIMESTAMP_NTZ
);

-- Flatten and load structural items from the raw JSON payload into final table
-- This mirrors the logic executing inside your production workflows
INSERT INTO WEATHER_DATA_FINAL
SELECT 
    raw_json:name::STRING as city_name,
    raw_json:sys.country::STRING as country,
    (raw_json:main.temp::FLOAT - 273.15) as temperature_celsius, -- Convert Kelvin to Celsius
    raw_json:weather[0].main::STRING as weather_condition,
    raw_json:main.humidity::INT as humidity,
    raw_json:wind.speed::FLOAT as wind_speed,
    TO_TIMESTAMP_NTZ(raw_json:dt::INT) as recorded_at
FROM WEATHER_DATA_RAW;


-- ============================================================================
-- STEP 7: MONITORING & MAINTENANCE COMMANDS
-- ============================================================================

-- Show active status parameters of the data channels
SHOW PIPES;
SHOW STAGES;

-- Fetch the exact automated IAM/SQS string needed for AWS Event Notifications
SELECT SYSTEM$PIPE_STATUS('WEATHER_SNOWPIPE');

-- Verify live record rows landed cleanly
SELECT * FROM WEATHER_DATA_FINAL 
ORDER BY recorded_at DESC 
LIMIT 5;
