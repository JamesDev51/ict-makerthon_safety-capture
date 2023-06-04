import json
import base64
import os
import uuid
import boto3

def lambda_handler(event, context):
    print(event)
    base64_image=event['body']
    image_data = base64.b64decode(base64_image)
    
    head = "--UploadImage\r\nContent-Disposition: form-data; name=\"imageFile\"; filename=\"esp32-cam.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n"
    tail = "\r\n--UploadImage--\r\n"
    image_data=strip_header_and_tail(image_data,head,tail)
    
    print("base64 decoded done")
    
    response = upload_image_to_s3(image_data)
    
    print(response)
    
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
    
def strip_header_and_tail(image_data, head, tail):
    head = head.encode('utf-8')
    tail = tail.encode('utf-8')
    start_index = image_data.find(head) + len(head)
    end_index = image_data.find(tail)
    stripped_data = image_data[start_index:end_index]
    return stripped_data

def upload_image_to_s3(image_data):
    SERVICE='s3'
    S3_BUCKET = os.getenv("S3_BUCKET")
    S3_FOLDER = os.getenv("S3_FOLDER")
    
    S3_KEY = S3_FOLDER + str(uuid.uuid4()) + '.jpg'
    
    s3 = boto3.client(SERVICE)
    
    metadata = {
    'Content-Type': 'image/jpeg',
    'Cache-Control': 'max-age=3600'
    }
    
    
    s3.put_object(Bucket=S3_BUCKET, Key=S3_KEY, Body=image_data, ContentType='image/jpeg', Metadata=metadata)
    
    ret=dict()
    ret['S3_BUCKET']=S3_BUCKET
    ret['S3_KEY']=S3_KEY

    return ret