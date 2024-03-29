import boto3
import os

from dotenv import load_dotenv
load_dotenv()


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

    print("response :",response)
    # 감지된 레이블 출력
    for label in response['CustomLabels']:
        print(label['Name'] + ' : ' + str(label['Confidence']))

    return response

def main():
    for i in range(10,26):
        print(f"test {i}")
        send_s3_image_to_rekognition("custom-labels-console-ap-northeast-2-0d6a663a62",f"esp32_cam_images/test{i}.jpg")
        print()

if __name__=="__main__":
    main()