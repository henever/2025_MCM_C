import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
athletes_file = f"{data_path}/summerOly_athletes.csv"  # 运动员数据文件
participants_file = f"{data_path}/medals_2024_with_participants_medals.csv"  # 2024年奖牌数据文件

# 设置截止年份
cutoff_year = 2024  # 可以调整这个值

# 读取数据
athletes_data = pd.read_csv(athletes_file)
participants_data = pd.read_csv(participants_file)

# 筛选出截止到指定年份的数据
filtered_data = athletes_data[athletes_data["Year"] <= cutoff_year]

# 按 Sport 分组，统计历史上所有国家在该项目中获得的总奖牌数量
total_medals_by_sport = filtered_data.groupby("Sport")["Medal"].value_counts().unstack(fill_value=0)
total_medals_by_sport = total_medals_by_sport.rename(columns={
    "Gold": "Total_Gold",
    "Silver": "Total_Silver",
    "Bronze": "Total_Bronze",
    "No medal": "Total_No_Medal"
}).reset_index()

# 将总奖牌数量合并到 participants_data 中
merged_data = pd.merge(participants_data, total_medals_by_sport, on="Sport", how="left")

# 计算四种奖牌的比例
merged_data["Gold_Ratio"] = merged_data["Gold Medals"] / merged_data["Total_Gold"]
merged_data["Silver_Ratio"] = merged_data["Silver Medals"] / merged_data["Total_Silver"]
merged_data["Bronze_Ratio"] = merged_data["Bronze Medals"] / merged_data["Total_Bronze"]
merged_data["No_Medal_Ratio"] = merged_data["No Medals"] / merged_data["Total_No_Medal"]

# 将缺失值填充为 0（如果某个项目没有奖牌数据）
merged_data = merged_data.fillna({
    "Gold_Ratio": 0,
    "Silver_Ratio": 0,
    "Bronze_Ratio": 0,
    "No_Medal_Ratio": 0
})

# 保存结果到原文件
merged_data.to_csv(participants_file, index=False)
print(f"结果已保存至：{participants_file}")