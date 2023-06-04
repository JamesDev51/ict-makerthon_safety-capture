import boto3
from PIL import Image, ImageDraw
import os
from io import BytesIO

from dotenv import load_dotenv
load_dotenv()

# S3 클라이언트 생성
s3 = boto3.client('s3')

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

    # 그려진 이미지 업로드        
    NEW_S3_KEY = f"visualize_bb_{S3_KEY}"
    upload_image_to_s3(NEW_S3_KEY, temp_file)
    
    #다 쓴 이미지 삭제
    os.remove(temp_file)
    
    visualized_image_s3_url=f"https://{S3_BUCKET}/{NEW_S3_KEY}"
    return visualized_image_s3_url
    
    

# 실행
if __name__ == '__main__':
    S3_BUCKET = os.getenv("S3_BUCKET")
    
    image_key = 'esp32_cam_images/b6d23ffe-cbc5-41a1-b64c-0f18f44c2374.jpg'
    labels = {"CustomLabels": 
        [
                {
                "Name": "no_helmet", 
                    "Confidence": 92.5530014038086, 
                    "Geometry": 
                        {
                            "BoundingBox": {
                                "Width": 0.25422000885009766, 
                                "Height": 0.397460013628006, 
                                "Left": 0.3990899920463562, 
                                "Top": 0.19565999507904053
                                }}}
            ], 
        "ResponseMetadata": {"RequestId": "0aea66cc-eb9c-4ff2-a7af-2bd5390a068d", "HTTPStatusCode": 200, "HTTPHeaders": {"x-amzn-requestid": "0aea66cc-eb9c-4ff2-a7af-2bd5390a068d", "content-type": "application/x-amz-json-1.1", "content-length": "205", "date": "Sat, 03 Jun 2023 04:34:25 GMT"}, "RetryAttempts": 0}}

                # {
                # "Name": "no_helmet", 
                #     "Confidence": 92.5530014038086, 
                #     "Geometry": 
                #         {
                #             "BoundingBox": {
                #                 "Width": 0.25422000885009766, 
                #                 "Height": 0.397460013628006, 
                #                 "Left": 0.3990899920463562, 
                #                 "Top": 0.19565999507904053
                #                 }}}
    
    
    visualize_bounding_boxes(S3_BUCKET, image_key, labels)