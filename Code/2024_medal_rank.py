import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
athletes_file = f"{data_path}/summerOly_athletes.csv"  # 运动员数据文件
output_file = f"{data_path}/2024_medal_rankings.csv"  # 输出文件

# 读取数据
athletes_data = pd.read_csv(athletes_file)

# 筛选出 2024 年的数据
athletes_2024 = athletes_data[athletes_data["Year"] == 2024]

# 按国家分组，统计奖牌总数
medal_totals = athletes_2024.groupby("NOC")["Medal"].value_counts().unstack(fill_value=0)

# 重命名列
medal_totals = medal_totals.rename(columns={
    "Gold": "Gold",
    "Silver": "Silver",
    "Bronze": "Bronze"
})

# 计算总奖牌数
medal_totals["Total"] = medal_totals["Gold"] + medal_totals["Silver"] + medal_totals["Bronze"]

# 按总奖牌数（降序）、金牌数（降序）、银牌数（降序）、铜牌数（降序）排序
medal_totals = medal_totals.sort_values(
    by=["Total", "Gold", "Silver", "Bronze"],
    ascending=[False, False, False, False]
).reset_index()

# 保存奖牌总榜
medal_totals.to_csv(output_file, index=False)

print(f"2024 年各国总奖牌榜已保存至：{output_file}")
print("2024 年各国总奖牌榜：")
print(medal_totals)