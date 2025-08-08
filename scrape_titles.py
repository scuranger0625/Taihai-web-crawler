import requests
import time
import pandas as pd
from tabulate import tabulate
import re

# === API 設定 ===
url = "http://search.people.cn/search-platform/front/search"
headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "http://search.people.cn",
    "Referer": "http://search.people.cn/s/?keyword=%E5%8F%B0%E6%B5%B7&st=0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
}

# === 清除 HTML 標籤 ===
def clean_html_tag(text):
    return re.sub(r'<.*?>', '', text) if isinstance(text, str) else text

# === 抓取函數 ===
def fetch_news(keyword="台海", max_pages=2):
    all_results = []
    for page in range(1, max_pages + 1):
        payload = {
            "key": keyword,
            "page": page,
            "limit": 10,
            "hasTitle": True,
            "hasContent": True,
            "isFuzzy": True,
            "type": 0,
            "sortType": 2,
            "startTime": 0,
            "endTime": 0
        }
        response = requests.post(url, headers=headers, json=payload, verify=False)
        if response.status_code == 200:
            data = response.json()
            records = data.get("data", {}).get("records", [])
            print(f"✅ Page {page}: 抓到 {len(records)} 筆")
            all_results.extend(records)
        else:
            print(f"❌ Page {page}: 失敗，狀態碼 {response.status_code}")
        time.sleep(1)  # 避免過快請求被封
    return all_results

if __name__ == "__main__":
    # 抓取所有新聞
    results = fetch_news(max_pages=291)

    # 處理欄位
    data = [
        {
            "title": clean_html_tag(item.get("title", "")),
            "url": item.get("url", ""),
            "originName": item.get("originName", ""),
            "editor": item.get("editor", ""),
            "displayTime": item.get("displayTime", ""),
            "content": clean_html_tag(item.get("content", "")),
        }
        for item in results
    ]

    df = pd.DataFrame(data)

    # 在終端顯示前 20 筆標題
    print(tabulate(df[["title"]].head(20), headers="keys", tablefmt="github", showindex=False))

    # 存成 Parquet（snappy 壓縮）
    df.to_parquet("taihai_news.parquet", engine="pyarrow", compression="snappy")
    print(f"📦 已存成 taihai_news.parquet，總共 {len(df)} 筆資料。")
