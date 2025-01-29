import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
medal_2024_file = f"{data_path}/medal_rankings_2024.csv"  # 2024 年奖牌榜
medal_2028_file = f"{data_path}/medal_rankings_2028_sorted.csv"  # 2028 年奖牌榜
output_file = f"{data_path}/progress_report_weighted.txt"  # 输出文件

# 读取数据
medal_2024 = pd.read_csv(medal_2024_file)
medal_2028 = pd.read_csv(medal_2028_file)

# 合并 2024 和 2028 年数据
merged_data = pd.merge(
    medal_2024[["NOC", "Gold", "Silver", "Bronze", "Total"]],
    medal_2028[["NOC", "Gold", "Silver", "Bronze", "Total"]],
    on="NOC",
    suffixes=("_2024", "_2028")
)

# 定义权重
gold_weight = 5
silver_weight = 3
bronze_weight = 2
total_weight = 0.6  # 总奖牌数权重
medal_structure_weight = 0.4  # 奖牌结构权重

# 计算加权奖牌总数
def calculate_weighted_total(gold, silver, bronze):
    return (gold * gold_weight) + (silver * silver_weight) + (bronze * bronze_weight)

merged_data["Weighted_Total_2024"] = calculate_weighted_total(
    merged_data["Gold_2024"], merged_data["Silver_2024"], merged_data["Bronze_2024"]
)
merged_data["Weighted_Total_2028"] = calculate_weighted_total(
    merged_data["Gold_2028"], merged_data["Silver_2028"], merged_data["Bronze_2028"]
)

# 计算总奖牌数变化率
merged_data["Total_Change_Rate"] = (
    (merged_data["Total_2028"] - merged_data["Total_2024"]) / merged_data["Total_2024"]
) * 100

# 计算奖牌结构变化率
merged_data["Medal_Structure_Change_Rate"] = (
    (merged_data["Weighted_Total_2028"] - merged_data["Weighted_Total_2024"]) / merged_data["Weighted_Total_2024"]
) * 100

# 计算综合进步率
merged_data["Overall_Progress_Rate"] = (
    (merged_data["Total_Change_Rate"] * total_weight) +
    (merged_data["Medal_Structure_Change_Rate"] * medal_structure_weight)
)

# 生成报告
report_increase = []  # 增加的国家
report_decrease = []  # 减少的国家
zero_to_nonzero = []  # 奖牌数从 0 变为非 0 的国家

for _, row in merged_data.iterrows():
    noc = row["NOC"]
    gold_2024, gold_2028 = row["Gold_2024"], row["Gold_2028"]
    silver_2024, silver_2028 = row["Silver_2024"], row["Silver_2028"]
    bronze_2024, bronze_2028 = row["Bronze_2024"], row["Bronze_2028"]
    total_2024, total_2028 = row["Total_2024"], row["Total_2028"]
    overall_progress_rate = row["Overall_Progress_Rate"]

    # 奖牌变化详情
    medal_details = (
        f"Golden_Medals : {gold_2024} -> {gold_2028}\n"
        f"Silver_Medals : {silver_2024} -> {silver_2028}\n"
        f"Bronze_Medals : {bronze_2024} -> {bronze_2028}"
    )

    # 处理奖牌数从 0 变为非 0 的情况
    if total_2024 == 0 and total_2028 > 0:
        zero_to_nonzero.append(f"{noc} gained {total_2028} medals")
        continue

    # 增加的国家
    if overall_progress_rate > 0:
        report_increase.append(
            f"{noc} increased {overall_progress_rate:.2f}%\n"
            f"{medal_details}\n"
        )
    # 减少的国家
    elif overall_progress_rate < 0:
        report_decrease.append(
            f"{noc} decreased {abs(overall_progress_rate):.2f}%\n"
            f"{medal_details}\n"
        )
    # 无变化的国家
    else:
        report_decrease.append(
            f"{noc} no change (0.00%)\n"
            f"{medal_details}\n"
        )

# 按综合进步率排序
report_increase_sorted = sorted(
    report_increase,
    key=lambda x: float(x.split("\n")[0].split()[-1].replace("%", "")),
    reverse=True
)
report_decrease_sorted = sorted(
    report_decrease,
    key=lambda x: float(x.split("\n")[0].split()[-1].replace("%", "").replace("(", "").replace(")", "")),
    reverse=True
)

# 合并报告
final_report = report_increase_sorted + report_decrease_sorted

# 添加奖牌数从 0 变为非 0 的国家
if zero_to_nonzero:
    final_report.append("\nCountries that gained medals from zero:")
    final_report.extend(zero_to_nonzero)

# 保存报告
with open(output_file, "w", encoding="utf-8") as f:
    for line in final_report:
        f.write(line + "\n")

print(f"加权进步报告已保存至：{output_file}")