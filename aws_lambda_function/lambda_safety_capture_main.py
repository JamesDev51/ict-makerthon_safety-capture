import json
from telegram import Bot
import asyncio
import boto3
import os


def lambda_handler(event, context):
    body=json.loads(event['body'])
    
    LOCATION = body['location']
    S3_BUCKET = body['bucket']
    S3_KEY= body['key']
    model_response=send_s3_image_to_rekognition(S3_BUCKET, S3_KEY)
    
    no_helmet_cnt=0
    # 감지된 레이블 출력
    for label in model_response['CustomLabels']:
        name=label['Name']
        confidence=label['Confidence']
        print(f"{name} : {confidence}")
        
        #로직 추가
    #텔레그램 메시지 발송
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def send_s3_image_to_rekognition(s3_bucket,s3_key):
    # Rekognition 클라이언트 생성
    SERVICE='rekognition'
    AWS_REGION_CUSTOM=os.getenv("AWS_REGION_CUSTOM")
    REKOGNITION_MODEL=os.getenv("REKOGNITION_MODEL")
    REKOGNITION_MIN_CONFIDENCE=int(os.getenv("REKOGNITION_MIN_CONFIDENCE"))
    
    rekognition = boto3.client(SERVICE, region_name=AWS_REGION_CUSTOM)
    
    # Rekognition의 detect_custom_labels API 호출
    response = rekognition.detect_custom_labels(
        Image={
            'S3Object': {
                'Bucket': s3_bucket,
                'Name': s3_key,
            }
        },
        MinConfidence=REKOGNITION_MIN_CONFIDENCE,
        ProjectVersionArn=REKOGNITION_MODEL
    )

    return response

def send_telegram_message(message):

    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    bot = Bot(token=TOKEN)

    async def send_message():
        await bot.send_message(chat_id=CHAT_ID, text=message)

    # Create a new event loop
    loop = asyncio.get_event_loop()

    try:
        # Run the async function
        loop.run_until_complete(send_message())
    finally:
        # Close the loop
        loop.close()

def put_s3_image_url_to_sqs(s3_link):

    SERVICE='sqs'
    SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")

    sqs = boto3.client(SERVICE)


    #SQS Queue에 메시지 전송하기
    response = sqs.send_message(
        QueueUrl=SQS_QUEUE_URL,
        DelaySeconds=10,
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
