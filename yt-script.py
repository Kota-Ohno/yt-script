import sys
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

# 環境変数を読み込み
load_dotenv()

# 定数設定
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# 認証情報読み込み
CLIENT_SECRETS_FILE = os.getenv('CLIENT_SECRET_FILE')
API_KEY = os.getenv('YOUTUBE_API_KEY')
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# 認証方法選択
def select_auth_method():
    while True:
        choice = input("認証方法を選択してください(1: API KEY, 2: OAuth): ")
        if choice in ['1', '2']:
            return choice
        print("無効な入力です。半角で1または2を入力してください。")

# 認証
def get_authenticated_service(auth_method):
    if auth_method == '1':
        return build(API_SERVICE_NAME, API_VERSION, developerKey=API_KEY)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_local_server(port=0)
        return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

# 動画検索
def search_videos(youtube, query):
    request = youtube.search().list(
        q=query,
        type='video',
        part='id,snippet',
        maxResults=10
    )
    response = request.execute()

    video_ids = [item['id']['videoId'] for item in response['items']]
    
    videos_request = youtube.videos().list(
        part='snippet,statistics',
        id=','.join(video_ids)
    )
    videos_response = videos_request.execute()

    return videos_response['items']

# 検索結果表示
def display_results(videos, query):
    print("---")
    print(f"検索キーワード: {query}")
    print("---")
    for video in videos:
        # 動画情報抽出
        title = video['snippet']['title']
        published_at_str = video['snippet']['publishedAt']
        published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
        jst = timezone(timedelta(hours=9))
        published_at_jst = published_at.astimezone(jst)
        formatted_date = published_at_jst.strftime('%Y年%m月%d日 %H時%M分')
        channel = video['snippet']['channelTitle']
        views = video['statistics']['viewCount']
        likes = video['statistics']['likeCount']
        comments = video['statistics']['commentCount']
        tags = video['snippet'].get('tags') # タグが存在しない場合、getメソッドでないとエラーが発生する
        tags_str = ', '.join(tags) if tags else "タグなし"
        
        # 動画情報表示
        print(f"タイトル: {title}")
        print(f"投稿日時: {formatted_date}")
        print(f"投稿者: {channel}")
        print(f"再生数: {views}")
        print(f"高評価数: {likes}")
        print(f"コメント数: {comments}")
        print(f"タグ: {tags_str}")
        print("---")

def main():
    # 引数処理
    if len(sys.argv) < 2:
        print("使用方法: python yt-script.py <検索キーワード>")
        sys.exit(1)

    # 認証
    auth_method = select_auth_method()
    youtube = get_authenticated_service(auth_method)

    # 検索キーワード結合
    query = ' '.join(sys.argv[1:])

    # 検索
    videos = search_videos(youtube, query)
    
    # 表示
    display_results(videos, query)

if __name__ == "__main__":
    main()
