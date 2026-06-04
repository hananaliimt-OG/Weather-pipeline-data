import json
import urllib3
import boto3
import uuid
from datetime import datetime
import os

# Initialize the AWS service clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Target resources
BUCKET_NAME = 'openweather-pipeline-data-hanan'
TABLE_NAME = 'weather_pipeline_log'

def lambda_handler(event, context):
    # 1. Initialize tracking variables
    execution_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    table = dynamodb.Table(TABLE_NAME)
    
    # 2. Write initial "IN_PROGRESS" log to DynamoDB
    try:
        table.put_item(
            Item={
                'execution_id': execution_id,
                'timestamp': timestamp,
                'pipeline_name': 'weather_data_ingestion',
                'status': 'IN_PROGRESS',
                'city': 'Elur'
            }
        )
    except Exception as e:
        print(f"Failed to write initial log to DynamoDB: {str(e)}")

    # 3. Fetch data from OpenWeather API
    http = urllib3.PoolManager()

    LAT = os.environ['LAT']
    LON = os.environ['LON']
    API_KEY = os.environ['API_KEY']
    

    api_url =f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric" # Keep your existing API URL config here
    
    try:
        response = http.request('GET', api_url)
        data = json.loads(response.data.decode('utf-8'))
        
        # 4. Upload raw file to S3
        file_name = f"raw_weather_data/weather_{execution_id}.json"
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=json.dumps(data)
        )
        
        # 5. Update DynamoDB log to "SUCCESS"
        table.update_item(
            Key={'execution_id': execution_id, 'timestamp': timestamp},
            UpdateExpression="set #st = :s",
            ExpressionAttributeNames={'#st': 'status'},
            ExpressionAttributeValues={':s': 'SUCCESS'}
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps('Data ingested and logged successfully!')
        }
        
    except Exception as e:
        # 6. Update DynamoDB log to "FAILED" if anything breaks
        table.update_item(
            Key={'execution_id': execution_id, 'timestamp': timestamp},
            UpdateExpression="set #st = :s, error_message = :e",
            ExpressionAttributeNames={'#st': 'status'},
            ExpressionAttributeValues={':s': 'FAILED', ':e': str(e)}
        )
        
        return {
            'statusCode': 500,
            'body': json.dumps(f'Pipeline failed: {str(e)}')
        }
