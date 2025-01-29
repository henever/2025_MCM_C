import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
participants_2020_file = f"{data_path}/Participants_2020.csv"  # 2020年参赛选手文件
topsis_results_file = f"{data_path}/without_age_participants_topsis_results.csv"  # TOPSIS 结果文件
output_file = f"{data_path}/without_age_Participants_2020_with_TOPSIS.csv"  # 输出文件

# 读取数据
participants_2020 = pd.read_csv(participants_2020_file)
topsis_results = pd.read_csv(topsis_results_file)

# 确保 participants_2020 中的 Name 是唯一的
participants_2020 = participants_2020.drop_duplicates(subset=["Name"], keep="first")

# 确保 topsis_results 中的 Name 是唯一的
topsis_results = topsis_results.drop_duplicates(subset=["Name"], keep="first")

# 合并 TOPSIS Score 到 Participants_2020
merged_data = pd.merge(
    participants_2020,
    topsis_results[["Name", "TOPSIS Score"]],
    on="Name",
    how="left"
)

# 按国家和项目分组，计算 TOPSIS Score 的总和
topsis_sum = merged_data.groupby(["NOC", "Sport"])["TOPSIS Score"].sum().reset_index()
topsis_sum = topsis_sum.rename(columns={"TOPSIS Score": "TOPSIS Score Sum"})

# 将 TOPSIS Score Sum 合并到 Participants_2020
final_data = pd.merge(
    merged_data,
    topsis_sum,
    on=["NOC", "Sport"],
    how="left"
)

# 计算参赛次数
participation_count = merged_data.groupby(["NOC", "Sport", "Name"]).size().reset_index(name="Participation Count")

# 将参赛次数合并到最终数据
final_data = pd.merge(
    final_data,
    participation_count,
    on=["NOC", "Sport", "Name"],
    how="left"
)

# 按 NOC, Sport, Name 排序
final_data = final_data.sort_values(by=["NOC", "Sport", "Name"])

# 保存结果
final_data.to_csv(output_file, index=False)
print(f"结果已保存至：{output_file}")