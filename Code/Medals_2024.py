import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
input_file = f"{data_path}/summerOly_athletes.csv"  # 输入文件
output_file = f"{data_path}/medals_2024.csv"  # 输出文件

# 读取数据
df = pd.read_csv(input_file)

# 筛选出 2024 年的数据
df_2024 = df[df["Year"] == 2024]

# 按 NOC 和 Sport 分组，统计奖牌数量
medal_counts = df_2024.groupby(["NOC", "Sport"])["Medal"].value_counts().unstack(fill_value=0)

# 重命名列
medal_counts = medal_counts.rename(columns={
    "Gold": "Gold Medals",
    "Silver": "Silver Medals",
    "Bronze": "Bronze Medals",
    "No medal": "No Medals"  # 如果需要统计无奖牌的情况
})

# 计算总奖牌数量（不包括 "No medal"）
medal_counts["Total Medals"] = medal_counts["Gold Medals"] + medal_counts["Silver Medals"] + medal_counts["Bronze Medals"]

# 重置索引
medal_counts = medal_counts.reset_index()

# 保存结果
medal_counts.to_csv(output_file, index=False)
print(f"2024年各国各项目奖牌数量已保存至：{output_file}")