# yt-script

## 要件
- コマンドラインで検索キーワードを引数にとるスクリプト
- Youtubeの動画を検索キーワードをもとに検索し、リストで出力する
- 出力する項目はタイトル・投稿日時・投稿者・再生数・高評価数・コメント数
- 検索にはYouTube Data Apiを用いる
- pythonにて実装

## 参考としたサイトのURL
- https://developers.google.com/youtube/v3/docs/search?hl=ja
- https://developers.google.com/youtube/v3/code_samples/code_snippets?hl=ja
- https://github.com/googleapis/google-api-python-client
- https://developers.google.com/youtube/v3/guides/authentication?hl=ja
- https://dev.classmethod.jp/articles/oauth2-youtube-data-api/
- https://stackoverflow.com/questions/75602866/google-oauth-attributeerror-installedappflow-object-has-no-attribute-run-co
- https://qiita.com/tanitanistudio/items/7526d2d28626b1b5af2a
- https://note.nkmk.me/python-dict-get/


## 操作方法
### 1. python3環境を準備する
- python公式：[https://www.python.org/downloads/]から、Python version 3.xxのファイルをダウンロードし、インストールすることでpython3の環境を構築する
- 以下のコマンドをターミナルで入力し、必要なライブラリをインストールする

```
pip install google-api-python-client python-dotenv google-auth-oauthlib python-dotenv datetime
```
### 2.認証情報の用意
以下のいずれかの認証情報を用意する
#### 2.1 YouTube API KEYの場合
- [https://engineering.webstudio168.jp/2022/09/youtube-data-api-getapikeys/]を参考に、YouTube API KEYを作成する
- .envファイルの以下の部分にAPIキーの文字列を記述する
```
YOUTUBE_API_KEY="APIキーの文字列"
```
#### 2.2 Oauth 2.0の場合
- [https://dev.classmethod.jp/articles/oauth2-youtube-data-api/]を参考に、OAuth 2.0の認証情報を作成したうえで、認証情報のjsonファイルをダウンロードする
- yt-script.pyと同階層のディレクトリにjsonファイルを配置し、.envファイルの以下の部分にファイル名を記述する
```
CLIENT_SECRET_FILE="ファイル名"
```

### 3. スクリプトの実行
- yt-script.pyの階層でターミナルを開き、以下のコマンドを入力してスクリプトを実行する
```
python yt-script.py keyword1 keyword2 ...
```
- 以下のメッセージが表示されるので、用意した認証方法に合わせて1か2を入力する
```
認証方法を選択してください(1: API Key, 2: OAuth): 
```
