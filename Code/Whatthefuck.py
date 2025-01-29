import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
medals_file = f"{data_path}/medals_2024.csv"  # 2024年奖牌数据文件
summary_file = f"{data_path}/NOC_Sport_Summary_2020_with_topsis.csv"  # 2020年项目汇总文件
output_file = f"{data_path}/medals_2024_with_topsis.csv"  # 输出文件

# 读取数据
medals_data = pd.read_csv(medals_file)
summary_data = pd.read_csv(summary_file)

# 合并 TOPSIS_Score_Sum, Host, Sport_topsis_score
merged_data = pd.merge(
    medals_data,
    summary_data[["NOC", "Sport", "TOPSIS_Score_Sum", "Host", "Sport_topsis_score"]],
    on=["NOC", "Sport"],
    how="left"  # 保留 medals_data 中的所有行
)

# 将缺失值填充为 0
merged_data["TOPSIS_Score_Sum"] = merged_data["TOPSIS_Score_Sum"].fillna(0)
merged_data["Host"] = merged_data["Host"].fillna(0)
merged_data["Sport_topsis_score"] = merged_data["Sport_topsis_score"].fillna(0)

# 保存结果
merged_data.to_csv(output_file, index=False)
print(f"结果已保存至：{output_file}")