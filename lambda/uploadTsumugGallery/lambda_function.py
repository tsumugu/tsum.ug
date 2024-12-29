import json
import base64
import hashlib
import boto3
import requests
from PIL import Image
from io import BytesIO

# AWS S3設定
S3_BUCKET = "tsumug-gallery"
S3_REGION = "ap-northeast-1"

# S3クライアント
s3_client = boto3.client("s3")

# サムネイルの最大サイズ設定
THUMBNAIL_SIZE = (600, 600)

def calculate_hash(image_data):
    """画像データからハッシュ値を計算する"""
    hasher = hashlib.md5()  # 必要に応じてSHA256などに変更可能
    hasher.update(image_data)
    return hasher.hexdigest()

def lambda_handler(event, context):

    # イベントデータからリクエストボディを取得
    try:
        data = json.loads(event['body'])
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Invalid JSON format"})
        }

    if not data or not isinstance(data, list):
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Invalid input format. Expected a list of objects."})
        }

    try:
        all_objects = s3_client.list_objects_v2(Bucket=S3_BUCKET)
    except Exception as e:
        print(f"Error listing objects in S3: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": "Failed to list objects in S3"})
        }

    # バケットにファイルが存在する場合
    existing_files = set()
    if 'Contents' in all_objects:
        for obj in all_objects['Contents']:
            existing_files.add(obj['Key'])

    results = []

    for image_info in data:
        filename = image_info.get("filename")
        image_url = image_info.get("url")+ "=d"

        if not filename or not image_url:
            continue  # 入力が不完全な場合はスキップ

        try:
            # 1. 画像をダウンロード
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image_data = response.content
            img = Image.open(BytesIO(image_data))

            # 2. ハッシュ値を計算
            hash_value = calculate_hash(image_data)

            print(filename, hash_value)

            # 3. S3キーを定義
            original_key = f"original/{hash_value}"
            thumbnail_key = f"thumbnail/{hash_value}"

            # 4. 既存ファイルがあるか確認
            if original_key in existing_files:
                # 元画像とサムネイルのURLを生成
                original_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{original_key}"
                thumbnail_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{thumbnail_key}"

                # 既存の結果を追加
                results.append({
                    "filename": filename,
                    "original_url": original_url,
                    "thumbnail_url": thumbnail_url
                })
                continue  # アップロードをスキップ

            # 5. 元画像をS3にアップロード
            original_buffer = BytesIO(image_data)
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=original_key,
                Body=original_buffer,
                ContentType=f"image/{img.format.lower()}"
            )

            # 6. サムネイルを生成（アスペクト比を維持してリサイズ）
            img.thumbnail(THUMBNAIL_SIZE)  # アスペクト比を維持
            thumbnail_buffer = BytesIO()
            img.save(thumbnail_buffer, format=img.format)
            thumbnail_buffer.seek(0)
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=thumbnail_key,
                Body=thumbnail_buffer,
                ContentType=f"image/{img.format.lower()}"
            )

            # 7. アップロード後のURLを生成
            original_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{original_key}"
            thumbnail_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{thumbnail_key}"

            # 8. 成功した場合のみ結果を追加
            results.append({
                "filename": filename,
                "original_url": original_url,
                "thumbnail_url": thumbnail_url
            })

        except Exception as e:
            # アップロードに失敗した場合はスキップ
            print(f"Error processing {filename}: {e}")

    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }
