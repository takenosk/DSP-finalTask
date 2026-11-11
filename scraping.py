import requests
from bs4 import BeautifulSoup
import time

# 取得したリポジトリを保存するリスト
all_repositories = []

page = 1
while True:
    url = f"https://github.com/orgs/google/repositories?page={page}"

    res = requests.get(url)

    res.raise_for_status()

    print(f"{page}ページ目を取得しました")
    time.sleep(1)  

    with open("github.html", "w", encoding="utf-8") as f:
        f.write(res.text)

    print("Googleのリポジトリ一覧HTMLを保存しました")

    # アクセス間隔を保存するための待機
    time.sleep(1)

    html_soup = BeautifulSoup(res.text, "html.parser")

    repositories = html_soup.select('ul[role="list"] > li[aria-label]')

    for a in html_soup.select("a[href]"):
        if a.get_text(" ", strip=True).lower() == "next":
            print("次のページリンク:", a.get("href"))

    if len(repositories) == 0:
        print("取得を終了します")
        break

    print(f"{page}ページ目:{len(repositories)}件")

    page += 1
    time.sleep(1)  
    print(f"取得件数: {len(repositories)}")

    # 各リポジトリから必要な情報を取得
    for repo in repositories:
        name_element = repo.select_one('[data-listview-item-title-container="true"] a')

        # 主要言語
        language_element = repo.select_one('span[class*="PrimaryLanguageName"]')

        # スター数
        star_element = repo.select_one('a[href$="/stargazers"]')

        name = name_element.get_text(strip=True) if name_element else None
        language = language_element.get_text(strip=True) if language_element else None
        stars = star_element.get_text(strip=True) if star_element else None

        all_repositories.append((name, language, stars))
        print(name, language, stars)

    if page < 3:
        time.sleep(1)  # 次のページにアクセスする前に1秒待機
print(f"合計取得件数: {len(all_repositories)}件")

import sqlite3

conn = sqlite3.connect("github_repositories.db")
cursor = conn.cursor()

# テーブル作成
cursor.execute("""
CREATE TABLE IF NOT EXISTS repositories (
    name TEXT PRIMARY KEY,
    language TEXT,
    stars TEXT
)
""")

cursor.executemany("""
INSERT OR REPLACE INTO repositories (name,language,stars)
VALUES(?,?,?)
""", all_repositories)
conn.commit()

cursor.execute("SELECT COUNT(*) FROM repositories")
print("DB保存件数:", cursor.fetchone()[0])

cursor.execute("SELECT * FROM repositories LIMIT 10")

for row in cursor.fetchall():
    print(row)

conn.close()