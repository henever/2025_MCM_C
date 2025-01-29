import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
participants_file = f"{data_path}/Participants_2020.csv"  # 2020年参赛选手数据文件
medals_file = f"{data_path}/medals_2024_with_topsis.csv"  # 2024年奖牌数据文件
output_file = f"{data_path}/medals_2024_with_participants_medals.csv"  # 输出文件

# 读取数据
participants_data = pd.read_csv(participants_file)
medals_data = pd.read_csv(medals_file)

# 按 NOC 和 Sport 分组，统计每个国家每个项目的所有参赛选手四种奖牌数量
participants_medals = participants_data.groupby(["NOC", "Sport"]).agg({
    "Gold_Medals": "sum",  # 金牌总数
    "Silver_Medals": "sum",  # 银牌总数
    "Bronze_Medals": "sum"  # 铜牌总数
    # "No_Medals": "sum"  # 无奖牌总数
}).reset_index()

# 重命名列
participants_medals = participants_medals.rename(columns={
    "Gold Medals": "Participants_Gold",
    "Silver Medals": "Participants_Silver",
    "Bronze Medals": "Participants_Bronze"
    # "No Medals": "Participants_No_Medal"
})

# 将参赛选手的奖牌数据合并到 2024 年奖牌数据中
merged_data = pd.merge(medals_data, participants_medals, on=["NOC", "Sport"], how="left")

# 将缺失值填充为 0（如果没有参赛选手的奖牌数据）
merged_data = merged_data.fillna({
    "Participants_Gold": 0,
    "Participants_Silver": 0,
    "Participants_Bronze": 0
    # "Participants_No_Medal": 0
})

# 保存结果
merged_data.to_csv(output_file, index=False)
print(f"结果已保存至：{output_file}")