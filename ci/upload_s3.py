import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# 定数定義
INPUT_FILE = "src/data/google_photos.json"  # 入力JSONファイル
OUTPUT_FILE = "src/data/photos.json"        # 出力JSONファイル
API_URL = "https://9deksw1dhh.execute-api.ap-northeast-1.amazonaws.com/default"
HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": os.getenv('UPLOAD_KEY')
}
CHUNK_SIZE = 5  # 1回のリクエストで送信するデータ数

def chunk_data(data, chunk_size):
    """データを指定されたサイズで分割"""
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

def main():
    # JSONファイルの読み取り
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as infile:
            data = json.load(infile)
    except Exception as e:
        print(f"入力ファイルの読み取りエラー: {e}")
        return

    # 分割したデータをAPIに送信
    all_responses = []
    for index, chunk in enumerate(chunk_data(data, CHUNK_SIZE)):
        try:
            print(f"リクエスト送信中: チャンク {index + 1}/{(len(data) + CHUNK_SIZE - 1) // CHUNK_SIZE}")
            response = requests.post(API_URL, headers=HEADERS, json=chunk)
            response.raise_for_status()
            all_responses.extend(response.json())
        except requests.exceptions.RequestException as e:
            print(f"リクエストエラー (チャンク {index + 1}): {e}")
            continue

    # 全てのレスポンスデータをJSONファイルに保存
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
            json.dump(all_responses, outfile, indent=4, ensure_ascii=False)
        print(f"全てのレスポンスデータを'{OUTPUT_FILE}'に保存しました。")
    except Exception as e:
        print(f"出力ファイルの書き込みエラー: {e}")

if __name__ == "__main__":
    main()