import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
input_file = f"{data_path}/without_age_Participants_2020_with_TOPSIS.csv"  # 输入文件
output_file = f"{data_path}/NOC_Sport_Summary.csv"  # 输出文件

# 读取数据
data = pd.read_csv(input_file)

# 按 NOC 和 Sport 分组，计算汇总数据
summary = data.groupby(["NOC", "Sport"]).agg(
    Gold_Medals=("Gold_Medals", "sum"),  # 金牌总数
    Silver_Medals=("Silver_Medals", "sum"),  # 银牌总数
    Bronze_Medals=("Bronze_Medals", "sum"),  # 铜牌总数
    Total_Medals=("Total_Medals", "sum"),  # 总奖牌数
    Participation_Count=("Participation_Count", "sum"),  # 参赛次数总和
    TOPSIS_Score_Sum=("TOPSIS Score", "sum")  # TOPSIS Score 总和
).reset_index()

# 保存结果
summary.to_csv(output_file, index=False)
print(f"汇总结果已保存至：{output_file}")