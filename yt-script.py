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
NUM_OF_RESULTS = os.getenv('NUM_OF_RESULTS')
CLIENT_SECRETS_FILE = os.getenv('CLIENT_SECRET_FILE')
API_KEY = os.getenv('YOUTUBE_API_KEY')
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

if not CLIENT_SECRETS_FILE and not API_KEY:
    print("エラー: 認証情報が見つかりません。.envファイルを確認してください。")
    print("CLIENT_SECRET_FILE または YOUTUBE_API_KEY が正しく設定されているか確認してください。")
    sys.exit(1)

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
        maxResults=NUM_OF_RESULTS
    )
    response = request.execute()

    video_ids = [item['id']['videoId'] for item in response['items']]
    
    videos_request = youtube.videos().list(
        part='snippet,statistics',
        id=','.join(video_ids)
    )
    videos_response = videos_request.execute()

    return videos_response['items']

# 動画情報の成型
def format_video_info(video):
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
    tags = video['snippet'].get('tags')
    tags_str = ', '.join(tags) if tags else "タグなし"
    
    return {
        "title": title,
        "date": formatted_date,
        "channel": channel,
        "views": views,
        "likes": likes,
        "comments": comments,
        "tags": tags_str
    }

# 出力
def process_results(videos, query, save_to_file=False):
    print("---")
    print(f"検索キーワード: {query}")
    print("---")

    filename = None
    if save_to_file:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"search_results_{now}.txt"
        file = open(filename, "w", encoding="utf-8")
        file.write(f"検索キーワード: {query}\n")
        file.write("---\n")

    for video in videos:
        video_info = format_video_info(video)
        # 表示処理
        print(f"タイトル: {video_info['title']}")
        print(f"投稿日時: {video_info['date']}")
        print(f"投稿者: {video_info['channel']}")
        print(f"再生数: {video_info['views']}")
        print(f"高評価数: {video_info['likes']}")
        print(f"コメント数: {video_info['comments']}")
        print(f"タグ: {video_info['tags']}")
        print("---")
        # 書き込み処理
        if save_to_file:
            file.write(f"タイトル: {video_info['title']}\n")
            file.write(f"投稿日時: {video_info['date']}\n")
            file.write(f"投稿者: {video_info['channel']}\n")
            file.write(f"再生数: {video_info['views']}\n")
            file.write(f"高評価数: {video_info['likes']}\n")
            file.write(f"コメント数: {video_info['comments']}\n")
            file.write(f"タグ: {video_info['tags']}\n")
            file.write("---\n")

    if save_to_file:
        file.close()
        print(f"検索結果を {filename} に保存しました。")

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
    
    # 結果の処理（表示とファイル保存）
    process_results(videos, query, save_to_file=True)

if __name__ == "__main__":
    main()
