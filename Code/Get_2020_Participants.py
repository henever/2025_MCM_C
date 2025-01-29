import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
input_file = f"{data_path}/summerOly_athletes.csv"  # 输入文件
output_file = f"{data_path}/Participants_2020.csv"  # 输出文件

# 读取数据
df = pd.read_csv(input_file)

# 筛选出参加了2020年奥运会的选手
participants_2020 = df[df["Year"] == 2020]["Name"].unique()

# 筛选出这些选手的所有历史记录（截止到2020年）
df_filtered = df[df["Name"].isin(participants_2020) & (df["Year"] <= 2020)]

# 按 Name, NOC, Sport 分组，统计比赛次数和奖牌数量
grouped = df_filtered.groupby(["Name", "NOC", "Sport"]).agg(
    Participation_Count=("Medal", "size"),  # 比赛次数
    Gold_Medals=("Medal", lambda x: (x == "Gold").sum()),  # 金牌数量
    Silver_Medals=("Medal", lambda x: (x == "Silver").sum()),  # 银牌数量
    Bronze_Medals=("Medal", lambda x: (x == "Bronze").sum()),  # 铜牌数量
).reset_index()

# 计算总奖牌数量
grouped["Total_Medals"] = grouped["Gold_Medals"] + grouped["Silver_Medals"] + grouped["Bronze_Medals"]

# 保存到文件
grouped.to_csv(output_file, index=False)
print(f"结果已保存至：{output_file}")