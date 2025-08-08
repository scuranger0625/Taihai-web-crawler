import requests
import time
import pandas as pd  

url = "http://search.people.cn/search-platform/front/search"
headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "http://search.people.cn",
    "Referer": "http://search.people.cn/s/?keyword=%E5%8F%B0%E6%B5%B7&st=0&_=1754549601226",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
}

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
        time.sleep(1)
    return all_results

# --- 抓取所有新聞 ---
results = fetch_news(max_pages=291)

# --- 挑選重點欄位並存為 CSV ---
def clean_html_tag(text):
    """去除 <em> 這種 HTML 標籤"""
    import re
    return re.sub(r'<.*?>', '', text) if isinstance(text, str) else text

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
df.to_csv("taihai_news.csv", index=False, encoding='utf-8-sig')  # 用 utf-8-sig Excel 也能開

print(f"已存成 taihai_news.csv，總共 {len(df)} 筆資料。")
