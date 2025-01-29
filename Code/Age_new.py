import requests
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
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

# 文件路径和读取数据
file_path = "F:/MCM/2025COMAP/Data/athlete_medals_summary_arrangeby_NOC_2020_2024.csv"
df = pd.read_csv(file_path)

# 初始化出生年份列
df["Birth_Year"] = None

# 提取姓名列表
names = df["Name"].tolist()
total_tasks = len(names)

# 使用线程池并发处理
max_workers = 64 # 设置线程数
results = []
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    # 提交所有任务
    future_to_name = {executor.submit(fetch_birth_year, name): name for name in names}

    # 等待任务完成并收集结果
    for future in as_completed(future_to_name):
        name = future_to_name[future]
        try:
            birth_year = future.result()
            results.append((name, birth_year))
        except Exception as e:
            print(f"Error processing {name}: {e}")

# 将结果写回 DataFrame
result_dict = dict(results)
df["Birth_Year"] = df["Name"].map(result_dict)

# 保存结果到文件
output_path = "F:/MCM/2025COMAP/Data/athlete_birth_new.csv"
df.to_csv(output_path, index=False)
print("All tasks completed. Results saved to:", output_path)
