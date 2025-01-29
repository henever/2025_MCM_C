import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
input_file = f"{data_path}/medals_2024_with_topsis.csv"  # 输入文件
output_file = f"{data_path}/medals_2024_with_topsis_filtered.csv"  # 输出文件

# 读取数据
data = pd.read_csv(input_file)

# 删除运动员 TOPSIS Score 和项目 TOPSIS Score 均为 0 的项目
filtered_data = data[~((data["TOPSIS_Score_Sum"] == 0) & (data["Sport_topsis_score"] == 0))]

# 保存结果
filtered_data.to_csv(output_file, index=False)
print(f"过滤后的数据已保存至：{output_file}")