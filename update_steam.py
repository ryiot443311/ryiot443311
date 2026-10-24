import os
import json
import urllib.request
import re

# GitHub Secretsから環境変数を取得
API_KEY = os.environ.get("STEAM_API_KEY")
STEAM_ID = os.environ.get("STEAM_ID")

if not API_KEY or not STEAM_ID:
    print("API Key or Steam ID is missing.")
    exit(1)

# Steam APIエンドポイント
url = f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={API_KEY}&steamid={STEAM_ID}&format=json"

try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
    games = data.get("response", {}).get("games", [])
except Exception as e:
    print(f"Failed to fetch data: {e}")
    games = []

# Markdownテーブルのヘッダーを作成
markdown_list = [
    "| Game | Recent (2 Weeks) | Total Playtime |\n",
    "|:---|:---:|:---:|\n"
]

# 最近遊んだゲーム上位3つを抽出
for game in games[:3]:
    name = game["name"]
    appid = game["appid"]
    recent_hrs = round(game.get("playtime_2weeks", 0) / 60, 1)
    total_hrs = round(game.get("playtime_forever", 0) / 60, 1)
    
    # Steam公式CDNからゲームのバナー画像を取得
    img_url = f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg"

    markdown_list.append(
        f"| <img src='{img_url}' width='150'><br>**{name}** | {recent_hrs} hrs | {total_hrs} hrs |\n"
    )

if not games:
    markdown_list.append("| (No recent games) | - | - |\n")

new_content = "".join(markdown_list)

# README.mdを読み込み、指定コメントの間を正規表現で書き換える
with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

readme = re.sub(
    r"(<!-- STEAM-STATS:START -->).*?(<!-- STEAM-STATS:END -->)",
    f"\\1\n{new_content}\\2",
    readme,
    flags=re.DOTALL
)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
