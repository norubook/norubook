import os
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path


jst = timezone(timedelta(hours=9))

NIGHT_START_HOUR = 21
NIGHT_END_HOUR = 5

# --- 設定項目 ---
GITHUB_USERNAME = "norubook" # あなたのGitHubユーザー名に書き換えてください

'''
# GitHub APIにアクセスするためのトークン。GitHub Actionsから安全に受け取ります。
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN') 
# ---

# APIリクエスト用のヘッダー
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

def get_user_events():
    """ユーザーの公開イベントを取得する"""
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/events"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching events: {response.status_code}")
        return []
'''    
TOKEN = os.getenv('GITHUB_PAT')
if not TOKEN:
    print("❌ エラー: 環境変数 'GITHUB_PAT' が設定されていません。")
    print("GitHubでパーソナルアクセストークンを作成し、設定してください。")
    exit()

# 2. 正しいリクエストヘッダーを作成
headers = {
    # 'Authorization'ヘッダーでトークンを送信します
    "Authorization": f"Bearer {TOKEN}",
    # 'User-Agent'ヘッダーでアプリケーション名を指定します（あなたのGitHubユーザー名などでOK）
    "User-Agent": "norubook" ,
    "Accept":"application/vnd.github.v3+json"
}

# 3. GitHub APIのエンドポイント（URL）
url = f'https://api.github.com/users/{GITHUB_USERNAME}/events'

print("GitHubから公開イベントを取得します...")
'''
# 4. 実際にリクエストを送信
response = requests.get(url, headers=headers)

# 5. 結果を確認
if response.status_code == 200:
    print("✅ 成功！イベント情報を取得しました。")
    # 取得したデータ（JSON形式）を表示（長すぎるので最初の1件だけ表示）
    events = response.json()
    if events:
        print(events)#[0])
else:
    print(f"😭 失敗しました。ステータスコード: {response.status_code}")
    print(f"エラー内容: {response.json()}")
'''

# 夜間プッシュの情報を格納するリスト
night_pushes = []

print("APIからイベントデータを取得中...")
response = requests.get(url, headers=headers)

if response.status_code == 200:
    events = response.json()
    print(f"取得したイベント数: {len(events)}件")

    for event in events:
        # 1. プッシュイベントかどうかをチェック
        if event['type'] == 'PushEvent':
            # 2. 作成日時(UTC)の文字列を取得
            timestamp_utc_str = event['created_at']
            
            # 3. 文字列をdatetimeオブジェクトに変換
            #    'Z'をUTCのオフセット'+00:00'に置換する必要がある
            timestamp_utc = datetime.fromisoformat(timestamp_utc_str.replace('Z', '+00:00'))
            
            # 4. JSTに変換
            timestamp_jst = timestamp_utc.astimezone(jst)
            
            # 5. 時間が夜の範囲内かチェック
            #    例: 21時以降 または 5時より前
            if timestamp_jst.hour >= NIGHT_START_HOUR or timestamp_jst.hour < NIGHT_END_HOUR:
                
                # 抽出したい情報を辞書にまとめてリストに追加
                push_info = {
                    'repo': event['repo']['name'],
                    'pushed_at_jst': timestamp_jst.strftime('%Y-%m-%d %H:%M:%S'),
                    'commits': len(event['payload']['commits'])
                }
                night_pushes.append(push_info)

    print("\n--- 夜間のプッシュ活動 ---")
    if night_pushes:
        for push in night_pushes:
            print(f"リポジトリ: {push['repo']}, プッシュ日時: {push['pushed_at_jst']}, コミット数: {push['commits']}")
    else:
        print("夜間のプッシュ活動は見つかりませんでした。")

else:
    print(f"APIリクエストに失敗しました: {response.status_code}")
    print(response.json())




def check_morning_coder_achievement(events):
    """「朝活コーダー」アチーブementをチェックする"""
    morning_commits = 0
    # 過去30日間のコミットをチェック
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    for event in events:
        if event['type'] == 'PushEvent':
            event_time = datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            if event_time > thirty_days_ago:
                # JSTに変換 (UTC+9時間)
                jst_hour = (event_time + timedelta(hours=9)).hour
                if 5 <= jst_hour < 9: # 朝5時～8時台
                    morning_commits += len(event['payload']['commits'])
    
    if morning_commits >= 10:
        # 条件達成！バッジのMarkdownを返す
        return "![Morning Coder](https://img.shields.io/badge/Achievement-Morning%20Coder-blue) - 朝5時から9時の間に10回以上コミットしました！"
    return None

def check_night_coder_achievement(events):
    """「夜活コーダー」アチーブementをチェックする"""
    morning_commits = 0
    # 過去30日間のコミットをチェック
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    for event in events:
        if event['type'] == 'PushEvent':
            event_time = datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            if event_time > thirty_days_ago:
                # JSTに変換 (UTC+9時間)
                jst_hour = (event_time + timedelta(hours=9)).hour
                if 20 <= jst_hour < 23 | 0<= jst_hour < 5: # 20～5時台
                    morning_commits += len(event['payload']['commits'])
    
    if morning_commits >= 1:
        # 条件達成！バッジのMarkdownを返す
        return "![Night Coder](https://img.shields.io/badge/Achievement-Morning%20Coder-blue) - 20時から5時の間に1回以上コミットしました！"
    return None


def update_readme(achievements):
    """READMEファイルを更新する"""
    program_path = Path(__file__).resolve()
    readme_path = program_path.parent.parent/ "README.md"
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()

    # 目印の間を書き換える
    start_marker = "<-->"
    end_marker = "><><"

    start_index = readme_content.find(start_marker)
    end_index = readme_content.find(end_marker)

    if start_index == -1 or end_index == -1:
        print("Error: Markers not found in README.md")
        return

    # 新しいアチーブメントリストを作成
    if achievements:
        new_content = "\n".join(f"- {ach}" for ach in achievements)
    else:
        new_content = "まだアチーブメントはありません。これからが楽しみ！"

    # READMEの内容を組み立てる
    new_readme = (
        readme_content[:start_index + len(start_marker)] +
        "\n" + new_content + "\n" +
        readme_content[end_index:]
    )

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_readme)
    print("README.md has been updated!")


if __name__ == "__main__":
    unlocked_achievements = []
    
    print("Fetching GitHub events...")
    #events = get_user_events()

    # --- アチーブメント判定処理 ---
    # ここに新しいアチーブメントのチェック関数を追加していきます
    print("Checking achievement...")
    morning_coder = check_morning_coder_achievement(events)
    if morning_coder:
        unlocked_achievements.append(morning_coder)
    night_coder = check_night_coder_achievement(events)
    if night_coder:
        unlocked_achievements.append(night_coder)
    
    # 他のアチーブメントチェックもここに追加...
    #
    # ---

    print(f"Unlocked achievements: {len(unlocked_achievements)}")
    update_readme(unlocked_achievements)