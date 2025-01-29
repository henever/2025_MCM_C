import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
summary_file = f"{data_path}/NOC_Sport_Summary_2020.csv"  # 国家-项目汇总文件
topsis_file = f"{data_path}/Sport_Topsis_Results.csv"  # 体育项目 TOPSIS 结果文件
output_file = f"{data_path}/NOC_Sport_Summary_2020_with_Topsis.csv"  # 输出文件

# 读取数据
summary_data = pd.read_csv(summary_file)
topsis_data = pd.read_csv(topsis_file)

# 合并 Sport_topsis_score
merged_data = pd.merge(
    summary_data,
    topsis_data[["NOC", "Sport", "Score"]],  # 需要 NOC 和 Sport 都匹配
    on=["NOC", "Sport"],  # 按 NOC 和 Sport 列进行匹配
    how="left"  # 保留 summary_data 中的所有行
)

# 重命名 Score 列为 Sport_topsis_score
merged_data = merged_data.rename(columns={"Score": "Sport_topsis_score"})

# 保存结果
merged_data.to_csv(output_file, index=False)
print(f"结果已保存至：{output_file}")