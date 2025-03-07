import sys
sys.path.insert(0, "./lib")

import json
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import requests
from dotenv import load_dotenv

# スコープは事前に設定されたものを仮定
SCOPES = ['https://www.googleapis.com/auth/photoslibrary']

load_dotenv()

def load_credentials():
    """既存のトークンをロードし、必要ならリフレッシュ"""
    creds = None
    if os.path.exists('ci/token.json'):
        creds = Credentials.from_authorized_user_file('ci/token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("トークンが期限切れです。リフレッシュ中...")
            creds.refresh(Request())
        else:
            raise Exception("token.json が無効です。再認証が必要です。")
    
        # 更新されたトークンを保存
        with open('ci/token.json', 'w') as token_file:
            token_file.write(creds.to_json())
            print("リフレッシュ済みのトークンを保存しました。")
    return creds

def get_album_photos(album_id, creds):
    """指定したアルバム内の写真のURLを取得"""
    url = 'https://photoslibrary.googleapis.com/v1/mediaItems:search'
    headers = {'Authorization': f'Bearer {creds.token}'}
    payload = {'albumId': album_id, 'pageSize': 100}  # 1回のリクエストで最大100件取得

    all_photos = []
    next_page_token = None

    while True:
        if next_page_token:
            payload['pageToken'] = next_page_token

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            break

        data = response.json()
        items = data.get('mediaItems', [])
        for item in items:
            # Base URL とファイル名を取得
            base_url = item.get('baseUrl')
            filename = item.get('filename')
            print(f"Photo: {filename}, URL: {base_url}")
            all_photos.append({'filename': filename, 'url': base_url})

        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break

    return all_photos

def save_photos_to_json(photo_data, output_file='src/data/google_photos.json'):
    """写真データをJSON形式で保存"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(photo_data, f, ensure_ascii=False, indent=4)
    print(f"Saved photo data to {output_file}")

def main():
    creds = load_credentials()

    # 環境変数からアルバムIDを取得
    album_id = os.getenv('ALBUM_ID')
    if not album_id:
        raise Exception("ALBUM_ID 環境変数が設定されていません。")

    # アルバム内の写真URLを取得
    photo_urls = get_album_photos(album_id, creds)
    print(f"Total photos found: {len(photo_urls)}")

    # JSONファイルに保存
    save_photos_to_json(photo_urls)

if __name__ == '__main__':
    main()
