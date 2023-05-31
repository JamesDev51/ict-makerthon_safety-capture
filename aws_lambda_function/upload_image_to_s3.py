import json
import uuid
import boto3
import base64
import os

from dotenv import load_dotenv
load_dotenv()


def upload_image_to_s3(image_data):
    SERVICE='s3'
    S3_BUCKET = os.getenv("S3_BUCKET")
    S3_FOLDER = os.getenv("S3_FOLDER")
    
    S3_KEY = S3_FOLDER + str(uuid.uuid4()) + '.jpg'
    
    s3 = boto3.client(SERVICE)
    
    url = s3.put_object(Bucket=S3_BUCKET, Key=S3_KEY, Body=image_data, ContentType='image/jpeg')
    print("s3_url : ",url)

    ret=dict()
    ret['S3_BUCKET']=S3_BUCKET
    ret['S3_KEY']=S3_KEY

    return ret

def main():
    # Use a local image file
    image_path = "bio.jpg"

    # Read the image file
    encoded_image = read_image_file(image_path)

    # Call the function to upload the image to S3
    response = upload_image_to_s3(encoded_image)

    print(response)
    
def read_image_file(file_path):
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

if __name__=="__main__":
    main()
    



