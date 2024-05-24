from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# AWS credentials and region
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_REGION')

# Create a DynamoDB resource
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

# DynamoDB table
table_name = 'TemperatureData'
table = dynamodb.Table(table_name)

@app.route('/temperature', methods=['POST'])
def store_temperature():
    try:
        # Get temperature data from request
        data = request.json
        temperature = data.get('temperature')
        print("Received temperature:", temperature)
        timestamp = datetime.now().isoformat()
        print("Current timestamp:", timestamp)
        table.put_item(
            Item={
                'timestamp': timestamp,
                'temperature': temperature
            }
        )
        print("Temperature stored successfully:", temperature)
        return jsonify({"message": f"Temperature {temperature} stored successfully at {timestamp}"}), 200

    except (NoCredentialsError, PartialCredentialsError) as e:
        return jsonify({"error": "Credentials not available"}), 500
    except ClientError as e:
        return jsonify({"error": f"Client error: {e.response['Error']['Message']}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=5000)
