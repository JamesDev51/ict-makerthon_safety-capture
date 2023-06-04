import boto3
import os
import json


def lambda_handler(event, context):
    
    SERVICE='sqs'
    SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")

    #SQS CLIENT 생성
    sqs = boto3.client(SERVICE)


    #S3 이미지 링크들
    s3_urls = []

    #SQS 큐에서 메시지 받아오기
    while True:
        messages = sqs.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            AttributeNames=[
                'All'
            ],
            MaxNumberOfMessages=10,  
            VisibilityTimeout=30,
            WaitTimeSeconds=0
        )

        if 'Messages' in messages:  #Messages가 있을 때까지 받아오기
            for message in messages['Messages']: 
                print("message : ",message)
                s3_url = message['Body']
                print("s3 url : " , s3_url)
                s3_urls.append(s3_url)

                #큐에서 메시지 지우기
                sqs.delete_message(
                    QueueUrl=SQS_QUEUE_URL,
                    ReceiptHandle=message['ReceiptHandle']
                )
        else:
            print('SQS 큐가 비어 있습니다.')
            break

    return {
        'statusCode': 200,
        'body': json.dumps(s3_urls)
    }
