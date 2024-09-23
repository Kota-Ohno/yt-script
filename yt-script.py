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
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# 環境変数を読み込み
NUM_OF_RESULTS = int(os.getenv('NUM_OF_RESULTS', 10))
CLIENT_SECRETS_FILE = os.getenv('CLIENT_SECRET_FILE')
API_KEY = os.getenv('YOUTUBE_API_KEY')


# 認証情報の検証
def validate_auth_info():
    if not API_KEY and not CLIENT_SECRETS_FILE:
        print("エラー: 認証情報が見つかりません。.envファイルを確認してください。")
        print("YOUTUBE_API_KEY または CLIENT_SECRET_FILE が正しく設定されているか確認してください。")
        sys.exit(1)
    elif not API_KEY and CLIENT_SECRETS_FILE:
        print("警告: API KEYが設定されていません。OAuthのみ使用可能です。")
        return ['2']
    elif API_KEY and not CLIENT_SECRETS_FILE:
        print("警告: CLIENT_SECRET_FILEが設定されていません。API KEYのみ使用可能です。")
        return ['1']
    else:
        return ['1', '2']

# エラーハンドリング
def safe_api_call(func):
    try:
        return func()
    except Exception as e:
        print(f"APIエラーが発生しました: {e}")
        sys.exit(1)

# 動画検索
def search_videos(youtube, query):
    def _search():
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
        return videos_request.execute()['items']

    return safe_api_call(_search)

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
def process_results(videos, query, should_save_to_file=False):
    print("---")
    print(f"検索キーワード: {query}")
    print("---")

    content = f"検索キーワード: {query}\n---\n"

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
        
        # コンテンツ追加
        content += f"タイトル: {video_info['title']}\n"
        content += f"投稿日時: {video_info['date']}\n"
        content += f"投稿者: {video_info['channel']}\n"
        content += f"再生数: {video_info['views']}\n"
        content += f"高評価数: {video_info['likes']}\n"
        content += f"コメント数: {video_info['comments']}\n"
        content += f"タグ: {video_info['tags']}\n"
        content += "---\n"

    if should_save_to_file:
        filename = generate_filename()
        save_to_file(filename, content)

# ファイル保存関数
def save_to_file(filename, content):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"検索結果を {filename} に保存しました。")
    except IOError as e:
        print(f"ファイル保存中にエラーが発生しました: {e}")

# ファイル名生成関数
def generate_filename():
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"search_results_{now}.txt"

# 認証方法選択
def select_auth_method(available_methods):
    if len(available_methods) == 1:
        return available_methods[0]
    
    while True:
        choice = input("認証方法を選択してください(1: API KEY, 2: OAuth): ")
        if choice in available_methods:
            return choice
        print("無効な入力です。半角で1または2を入力してください。")

# 認証
def get_authenticated_service(auth_method):
    if auth_method == '1':
        return build(API_SERVICE_NAME, API_VERSION, developerKey=API_KEY)
    else:
        try:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
            return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
        except FileNotFoundError:
            print(f"エラー: CLIENT_SECRETS_FILE '{CLIENT_SECRETS_FILE}' が見つかりません。")
            print("ファイルパスが正しいか確認してください。")
            sys.exit(1)
        except Exception as e:
            print(f"認証中に予期せぬエラーが発生しました: {e}")
            sys.exit(1)

def main():
    available_methods = validate_auth_info()

    if len(sys.argv) < 2:
        print("使用方法: python yt-script.py <検索キーワード>")
        sys.exit(1)

    # 認証
    auth_method = select_auth_method(available_methods)
    try:
        youtube = get_authenticated_service(auth_method)
    except SystemExit:
        # get_authenticated_serviceでエラーが発生した場合、プログラムを終了
        return

    # 検索キーワード結合
    query = ' '.join(sys.argv[1:])

    # 検索
    videos = search_videos(youtube, query)
    
    # 結果の処理（表示とファイル保存）
    process_results(videos, query, should_save_to_file=True)

if __name__ == "__main__":
    main()
