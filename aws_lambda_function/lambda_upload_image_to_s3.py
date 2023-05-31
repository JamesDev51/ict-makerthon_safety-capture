import json
import base64
import os
import uuid
import boto3

def lambda_handler(event, context):
    body=json.loads(event['body'])
    base64_image = body['image']
    image_data = base64.b64decode(base64_image)
    
    # Call the function to upload the image to S3
    response = upload_image_to_s3(image_data)
    
    print(response)
    
    
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

def upload_image_to_s3(image_data):
    SERVICE='s3'
    S3_BUCKET = os.getenv("S3_BUCKET")
    S3_FOLDER = os.getenv("S3_FOLDER")
    
    S3_KEY = S3_FOLDER + str(uuid.uuid4()) + '.jpg'
    
    s3 = boto3.client(SERVICE)
    
    s3.put_object(Bucket=S3_BUCKET, Key=S3_KEY, Body=image_data, ContentType='image/jpeg')
    

    ret=dict()
    ret['S3_BUCKET']=S3_BUCKET
    ret['S3_KEY']=S3_KEY

    return ret