import requests
import re
import pandas as pd
ans = 0
def get_birth_date_from_wikidata(name):
    """
    通过 Wikidata API 查询运动员的出生日期。
    :param name: 运动员姓名
    :param noc: 国家缩写 (NOC)
    :return: 运动员出生日期或 None
    """
    # 格式化姓名以符合 Wikidata 搜索
    name_query = name.replace(" ", "%20")
    query_url = f"https://www.wikidata.org/w/api.php?action=query&list=search&srsearch={name_query}&format=json"
    
    response = requests.get(query_url)
    if response.status_code != 200:
        print(f"Failed to search Wikidata for {name}.")
        return None
    
    # 获取搜索结果
    data = response.json()
    search_results = data.get("query", {}).get("search", [])
    
    for result in search_results:
        # 检查 NOC 是否在搜索结果的描述中
        # if noc.lower() in result.get("snippet", "").lower():
        # 获取实体 ID
        entity_id = result.get("title")
        
        # 查询实体详情以获取出生日期
        detail_url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
        detail_response = requests.get(detail_url)
        
        if detail_response.status_code != 200:
            continue
        
        detail_data = detail_response.json()
        claims = detail_data.get("entities", {}).get(entity_id, {}).get("claims", {})
        
        # 提取出生日期 (P569 是出生日期的属性代码)
        birth_date_data = claims.get("P569", [])
        if birth_date_data:
            birth_date = birth_date_data[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("time", "")
            birth_year = extract_year(birth_date)
            return birth_year
    
    print(f"No matching result found for {name}  on Wikidata.")
    return None

def extract_year(text):
    pattern = r'\b(?:18|19|20)\d{2}\b'
    result = re.findall(pattern, text)
    if len(result) >= 1:
        return result[0]
    return None

# 定义一个处理函数
def fetch_birth_year(name):
    global ans
    try:
        ans += 1
        percent = ans // 18876 * 100
        print(f"{ans} of 18876, {percent}%")
        return get_birth_date_from_wikidata(name)  # 获取出生年份
    except Exception as e:
        print(f"获取名字 {name} 的出生年份失败: {e}")
        return None  # 如果获取失败，返回 None
# 示例：查询运动员出生日期
file_path = "F:/MCM/2025COMAP/Data/test_athlete_medals_summary_arrangeby_NOC_2020_2024.csv"
df = pd.read_csv(file_path)

#for index, row in df.iterrows():
#    name = row["Name"]  # 假设名字在 'Name' 列
#    try:
#        birth_year = get_birth_date_from_wikidata(name)  # 获取出生年份
#        df.at[index, "Birth_Year"] = birth_year  # 更新 DataFrame
#    except Exception as e:
#        print(f"获取名字 {name} 的出生年份失败: {e}")
#        df.at[index, "Birth_Year"] = None  # 如果获取失败，设置为 None
df["Birth_Year"] = df["Name"].apply(fetch_birth_year)

df.to_csv("F:/MCM/2025COMAP/Data/athlete_birth.csv",index=False)
print("Done")
