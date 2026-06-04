import json
import logging

# Set up logging for CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Received stream event: {json.dumps(event)}")
    
    # Loop through the batch of records sent by the DynamoDB stream
    for record in event.get('Records', []):
        # We only care about NEW data added or updated in the table
        if record['eventName'] in ['INSERT', 'MODIFY']:
            new_image = record['dynamodb'].get('NewImage', {})
            
            # Extract values safely from DynamoDB's structured JSON format
            execution_id = new_image.get('execution_id', {}).get('S', 'UNKNOWN_ID')
            pipeline_status = new_image.get('status', {}).get('S', 'UNKNOWN_STATUS')
            
            # Check if the pipeline run explicitly failed
            if pipeline_status == "FAILED":
                error_message = new_image.get('error_message', {}).get('S', 'No error details provided.')
                timestamp = new_image.get('timestamp', {}).get('S', 'N/A')
                
                # CRITICAL ALERT TRIGGER
                logger.error(
                    f"🚨 PIPELINE FAILURE ALERT 🚨\n"
                    f"Execution ID: {execution_id}\n"
                    f"Timestamp: {timestamp}\n"
                    f"Error Details: {error_message}"
                )
                
                # NOTE: This is where you would hook up an SNS topic, 
                # a Slack webhook, or send an email in a full production environment.
            else:
                logger.info(f"Execution {execution_id} processed normally with status: {pipeline_status}")
                
    return {
        'statusCode': 200,
        'body': json.dumps('Stream processing complete!')
    }
