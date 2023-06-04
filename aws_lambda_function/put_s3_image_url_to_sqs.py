import boto3
import os

def put_s3_image_url_to_sqs(s3_link):

    SERVICE='sqs'
    SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")

    sqs = boto3.client(SERVICE)


    #SQS Queue에 메시지 전송하기
    response = sqs.send_message(
        QueueUrl=SQS_QUEUE_URL,
        DelaySeconds=0,
        MessageAttributes={
            'S3Link': {
                'DataType': 'String',
                'StringValue': s3_link
            }
        },
        MessageBody=(
            '안전포착 S3 URL 전송'
        )
    )

    print(f" SQS meesage id : {response['MessageId']}")
    return '메시지 전송을 완료했습니다.'
