import json
from telegram import Bot
from PIL import Image, ImageDraw
from io import BytesIO
import asyncio
import boto3
import os

# Rekognition 클라이언트 생성
AWS_REGION_CUSTOM=os.getenv("AWS_REGION_CUSTOM")
REKOGNITION_MODEL=os.getenv("REKOGNITION_MODEL")
REKOGNITION_MIN_CONFIDENCE=int(os.getenv("REKOGNITION_MIN_CONFIDENCE"))
rekognition = boto3.client('rekognition', region_name=AWS_REGION_CUSTOM)

#SQS 클라이언트 생성 
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
sqs = boto3.client('sqs')

#S3 클라이언트 생성
S3_BUCKET = os.getenv("S3_BUCKET")
s3 = boto3.client('s3')


def lambda_handler(event, context):
    body=json.loads(event['body'])
    
    S3_BUCKET = body['S3_BUCKET']
    S3_KEY= body['S3_KEY']
    print(f"S3 BUCKET : {S3_BUCKET}, S3 KEY : {S3_KEY}")
    
    model_response=send_s3_image_to_rekognition(S3_BUCKET, S3_KEY)
    
    no_helmet_cnt=0
    
    if 'CustomLabels' in model_response:
        print("label 분석")
        # 감지된 레이블 출력
        for label in model_response['CustomLabels']:
            name=label['Name']
            confidence=label['Confidence']
            print(f"{name} : {confidence}")
            if name=="no_helmet": no_helmet_cnt+=1
        
        
        
    #모델이 있든 없든 일단은 비주얼라이징 처리하기
    visualized_image_s3_url=visualize_bounding_boxes(S3_BUCKET, S3_KEY, model_response)
    
    #sqs 큐에 넣기
    put_s3_image_url_to_sqs(visualized_image_s3_url) 
    
    # no_helmet_cnt가 0보다 크면 텔레그램 메시지 발송
    print(f"no_helmet_cnt : {no_helmet_cnt}")
    if no_helmet_cnt:
        telegram_message=f'''
            안전모 미착용 근무자 적발되었습니다. \n
            사진을 확인하시려면 다음 링크를 클릭해주세요. \n\n
            사진 확인하기 📸 : {visualized_image_s3_url}
        '''
        print(f"telegram message : {telegram_message}")
        send_telegram_message(telegram_message)

        
    return {
        'statusCode': 200,
        'body': json.dumps(model_response) 
    }

def send_s3_image_to_rekognition(s3_bucket,s3_key):
    
    try:
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
    except Exception:
        message="AWS rekognition safety capture model is not available now"
        print(message)
        response=dict()
        response["message"]=message 

    return response



def send_telegram_message(message):

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    async def send_message():
        await telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    # Create a new event loop
    loop = asyncio.get_event_loop()
    
    retry_count = 1
    while(retry_count<=3):
        try:
            loop.run_until_complete(send_message())
            print("Sent TELEGRAM successfully")
            return True
        except Exception as e:
            print("TELEGRAM SEND FAILED ")
            print(f"try count is {_retry_count}/3")
            retry_count += 1
            time.sleep(3)
            if retry_count==4:
                print(e)
                print("CONNECTION FAILED, ALL THREE ATTEMPTS FAILED.")
            continue
    loop.close()
    
def put_s3_image_url_to_sqs(s3_link):

    #SQS Queue에 메시지 전송하기
    response = sqs.send_message(
        QueueUrl=SQS_QUEUE_URL,
        DelaySeconds=0,
        MessageGroupId='visualized-image',
        MessageAttributes={
            'S3Link': {
                'DataType': 'String',
                'StringValue': s3_link
            }
        },
        MessageBody=(
            s3_link
        )
    )

    print(f" SQS meesage id : {response['MessageId']}")
    return '메시지 전송을 완료했습니다.'

# 이미지 다운로드 함수
def download_image(S3_BUCKET, S3_KEY):
    try:
        response = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        image_data = response['Body'].read()
        return image_data
    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        return None

# 이미지 업로드 함수
def upload_image_to_s3(S3_KEY, image_data):
    try:
        response = s3.upload_file(image_data, Bucket=S3_BUCKET, Key=S3_KEY)
        
        print("Image uploaded successfully")
    except Exception as e:
        print(f"Error uploading image: {str(e)}")

# 이미지에 박스 그리기 함수
def draw_boxes_on_image(image_data, labels):
    image = Image.open(BytesIO(image_data))
    draw = ImageDraw.Draw(image)
    width=1600
    height=1200
    
    for label in labels['CustomLabels']:
        name = label['Name']
        geometry = label['Geometry']
        box = (
            geometry['BoundingBox']['Left'] * width,
            geometry['BoundingBox']['Top'] * height,
            (geometry['BoundingBox']['Left'] + geometry['BoundingBox']['Width']) * width,
            (geometry['BoundingBox']['Top'] + geometry['BoundingBox']['Height']) * height
        )
        
        # 박스 색상 설정
        if name == 'no_helmet':
            box_color = 'red'
        elif name == 'yes_helmet':
            box_color = 'lime'
        else:
            box_color = 'white'
        
        # 박스 그리기
        draw.rectangle(box, outline=box_color, width=10)
    
    # 그려진 이미지 반환
    output_image = Image.new('RGB', image.size)
    output_image.paste(image)
    
    return output_image

# 메인 함수
def visualize_bounding_boxes(S3_BUCKET, S3_KEY, bb_labels):
    
    # 이미지 다운로드
    image_data = download_image(S3_BUCKET, S3_KEY)
    print("image_data : ",image_data[:10])
    
    if image_data is None:
        print("원본 이미지 데이터가 존재하지 않습니다.")
        return
    
    temp_file = '/tmp/output_image.jpg'
    if 'CustomLabels' not in bb_labels or not bb_labels['CustomLabels']:
        print("바운딩 박스레이블이 존재하지 않습니다. 그대로 업로드합니다.")
        with open(temp_file, 'wb') as file:
            file.write(image_data)
        
    else:
        # 박스 그리기
        output_image = draw_boxes_on_image(image_data, bb_labels)
        print("바운딩 박스레이블 이미지에 그리기 완료")
        
        # output_image를 메모리 상에 임시 파일로 저장
        output_image.save(temp_file)

    if os.path.exists(temp_file):
        print("temp 파일 정상 생성됨")
    else:
        print("temp 파일 안 만들어짐")

    # 그려진 이미지 업로드        
    NEW_S3_KEY = f"visualize_bb_{S3_KEY}"
    upload_image_to_s3(NEW_S3_KEY, temp_file)
    
    #다 쓴 이미지 삭제
    os.remove(temp_file)
    
    visualized_image_s3_url=f"https://{S3_BUCKET}.s3.ap-northeast-2.amazonaws.com/{NEW_S3_KEY}"
    return visualized_image_s3_url
