import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
import random
# 定义一个全局变量，用于记录完成的任务数
completed_tasks = 0
total_tasks = 0
# 创建带有重试策略的 Session
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

def get_birth_date_from_wikidata(name):
    name_query = name.replace(" ", "%20")
    query_url = f"https://www.wikidata.org/w/api.php?action=query&list=search&srsearch={name_query}&format=json"
    
    try:
        response = session.get(query_url, timeout=5)
        if response.status_code != 200:
            return None

        data = response.json()
        search_results = data.get("query", {}).get("search", [])
        for result in search_results:
            entity_id = result.get("title")
            detail_url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
            detail_response = session.get(detail_url, timeout=5)

            if detail_response.status_code != 200:
                continue

            detail_data = detail_response.json()
            claims = detail_data.get("entities", {}).get(entity_id, {}).get("claims", {})
            birth_date_data = claims.get("P569", [])
            if birth_date_data:
                birth_date = birth_date_data[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("time", "")
                return extract_year(birth_date)
    except Exception as e:
        print(f"Error fetching data for {name}: {e}")
    return None

def extract_year(text):
    """从日期字符串中提取年份"""
    pattern = r'\b(?:18|19|20)\d{2}\b'
    result = re.findall(pattern, text)
    if result:
        return result[0]
    return None

def fetch_birth_year(name):
    """用于线程的任务函数"""
    global completed_tasks
    try:
        year = get_birth_date_from_wikidata(name)
        return year
    finally:
        # 记录完成的任务数
        completed_tasks += 1
        print(f"Progress: {completed_tasks}/{total_tasks} tasks completed.")
# 读取已有的文件
file_path = "F:/MCM/2025COMAP/Data/athlete_birth.csv"
df = pd.read_csv(file_path)

# 筛选出出生年份为空的人名
missing_birth_years = df[df["Birth_Year"].isna()]["Name"].tolist()

# 定义每块的大小（例如：每块包含 100 个名字）
chunk_size = 100
chunks = [missing_birth_years[i:i + chunk_size] for i in range(0, len(missing_birth_years), chunk_size)]

# 获取出生年份的函数
def fetch_and_update_birth_year(chunk):
    updated_names = []
    for name in chunk:
        try:
            birth_year = get_birth_date_from_wikidata(name)  # 重新获取出生年份
            if birth_year:
                updated_names.append((name, birth_year))
            else:
                print(f"Could not find birth year for {name}.")
        except Exception as e:
            print(f"Error fetching data for {name}: {e}")
    
    return updated_names

# 使用线程池来并行处理
def update_birth_years_in_parallel(chunks):
    with ThreadPoolExecutor(max_workers=32) as executor:
        future_to_chunk = {executor.submit(fetch_and_update_birth_year, chunk): chunk for chunk in chunks}
        for future in as_completed(future_to_chunk):
            try:
                updated_names = future.result()
                # 更新 DataFrame 中对应的出生年份
                for name, birth_year in updated_names:
                    df.loc[df["Name"] == name, "Birth_Year"] = birth_year
            except Exception as e:
                print(f"Error during processing chunk: {e}")

# 更新缺失出生年份
update_birth_years_in_parallel(chunks)

# 保存更新后的 DataFrame 到新的 CSV 文件
df.to_csv("F:/MCM/2025COMAP/Data/athlete_birth_updated.csv", index=False)
print("Done! The updated data is saved.")
