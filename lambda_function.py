import json
import os
import urllib.request
from datetime import datetime
import boto3

# Initialize the S3 client
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # 1. Configuration - pulling details from the OpenWeather API
    # We will use Kochi/Thrissur region metrics for your pipeline testing!
    LAT = "10.0261" 
    LON = "76.3125"
    API_KEY = os.environ.get('OPENWEATHER_API_KEY')
    BUCKET_NAME = "openweather-pipeline-data-hanan"
    
    # Construct the OpenWeather API URL (Current Weather Data)
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
    
    try:
        # 2. Fetch data from OpenWeather API
        with urllib.request.urlopen(url) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode())
                
                # 3. Create a unique timestamped filename for S3 tracking
                current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                file_name = f"raw_weather_data/{current_time}.json"
                
                # 4. Upload the raw JSON payload directly into S3
                s3_client.put_object(
                    Bucket=BUCKET_NAME,
                    Key=file_name,
                    Body=json.dumps(data),
                    ContentType='application/json'
                )
                
                return {
                    'statusCode': 200,
                    'body': json.dumps(f"Successfully ingested weather data to S3: {file_name}")
                }
            else:
                return {
                    'statusCode': response.getcode(),
                    'body': json.dumps("Failed to fetch data from OpenWeather API")
                }
                
    except Exception as e:
        print(f"Error encountered: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Internal Pipeline Error: {str(e)}")
        }
