import pandas as pd

# 读取数据
# 假设 summerOly_athletes.csv 是原始数据文件
data = pd.read_csv("F:/MCM/2025COMAP/Data/summerOly_athletes.csv")

# 检查数据结构
print(data.head())

# 确保数据中 "Medal" 列只有有效值（Gold, Silver, Bronze, No medal）
data["Medal"] = data["Medal"].fillna("No medal")  # 填补缺失值为 No medal

# 筛选 2020 年和 2024 年的参赛运动员
# filtered_data = data[data["Year"].isin([2020, 2024])]

# 按运动员聚合，统计每个运动员的奖牌情况
athlete_medals = data.groupby(["NOC", "Name"]).agg(
    Total_Medals=("Medal", lambda x: (x != "No medal").sum()),  # 总奖牌数（非 No medal 值计数）
    Gold_Medals=("Medal", lambda x: (x == "Gold").sum()),       # 金牌数
    Silver_Medals=("Medal", lambda x: (x == "Silver").sum()),   # 银牌数
    Bronze_Medals=("Medal", lambda x: (x == "Bronze").sum()),    # 铜牌数
    Total_Competitions=("Medal", "size") # 参赛次数
).reset_index()

# 检查结果
# print(athlete_medals.head())



# 保存结果到文件
athlete_medals.to_csv("F:/MCM/2025COMAP/Data/athlete_models_compet.csv", index=False)

# 检查按国家的聚合结果
# print(country_medals.head())
