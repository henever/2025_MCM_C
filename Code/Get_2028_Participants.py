import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
topsis_file = f"{data_path}/participants_topsis_results.csv"  # TOPSIS 结果文件
participation_file = f"{data_path}/sport_participation_2024.csv"  # 2024年参赛人数文件
birth_file = f"{data_path}/athlete_birth_new.csv"  # 出生年份文件
output_file = f"{data_path}/Participants_2028.csv"  # 输出文件

# 读取数据
topsis_data = pd.read_csv(topsis_file)
participation_data = pd.read_csv(participation_file)
birth_data = pd.read_csv(birth_file)

# 合并 TOPSIS 数据和出生年份数据
merged_data = pd.merge(topsis_data, birth_data[["Name", "Birth_Year"]], on="Name", how="left")

# 排除出生年份缺失的选手
merged_data = merged_data.dropna(subset=["Birth_Year"])

# 计算 2028 年时的年龄
merged_data["Age_in_2028"] = 2028 - merged_data["Birth_Year"]

# 筛选出年龄不超过 40 岁的选手
filtered_data = merged_data[merged_data["Age_in_2028"] <= 40]

# 处理重复参赛的选手
# 假设数据中有 Year 列表示参赛年份
# 如果某个选手在 2020 年和 2024 年都参赛，则删除 2020 年的记录
filtered_data = filtered_data.sort_values(by=["Name", "Birth_Year"], ascending=[True, False])
filtered_data = filtered_data.drop_duplicates(subset=["Name"], keep="first")

# 初始化结果存储
results = []

# 遍历每个国家和项目
for _, row in participation_data.iterrows():
    noc = row["NOC"]
    sport = row["Sport"]
    num = row["Participant Count"]
    
    # 筛选出该国家该项目的选手
    candidates = filtered_data[(filtered_data["NOC"] == noc) & (filtered_data["Sport"] == sport)]
    
    # 按 TOPSIS 分数从高到低排序
    candidates = candidates.sort_values(by="TOPSIS Score", ascending=False)
    
    # 选取前 num 个符合条件的选手
    selected = candidates.head(num)
    
    # 添加到结果中
    results.append(selected)

# 合并所有结果
final_results = pd.concat(results, ignore_index=True)

# 按国家、项目、排名排序
final_results = final_results.sort_values(by=["NOC", "Sport", "TOPSIS Rank"])

# 保存结果
final_results.to_csv(output_file, index=False)
print(f"筛选结果已保存至：{output_file}")