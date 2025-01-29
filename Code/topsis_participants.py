import pandas as pd
import numpy as np

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
input_file = f"{data_path}/without_age_cutoff_medal_summary.csv"  # 输入文件
output_file = f"{data_path}/without_age_participants_topsis_results.csv"  # 输出文件

# 读取数据
data = pd.read_csv(input_file)

# 需要用于 TOPSIS 分析的列
columns_to_analyze = [
    "Gold Medals", "Silver Medals", "Bronze Medals", "Total Medals", "Participation Count"
]

# 提取用于 TOPSIS 的数据
topsis_matrix = data[columns_to_analyze].values

# 1. 数据标准化
column_sums = (topsis_matrix**2).sum(axis=0)  # 计算每列的平方和
zero_sum_columns = column_sums == 0  # 检查哪些列的平方和为 0

# 初始化标准化矩阵
norm_matrix = np.zeros_like(topsis_matrix, dtype=float)

# 对非零列进行标准化
norm_matrix[:, ~zero_sum_columns] = topsis_matrix[:, ~zero_sum_columns] / np.sqrt(column_sums[~zero_sum_columns])

# 2. 计算熵权
column_sums = norm_matrix.sum(axis=0)  # 计算每列的和
zero_sum_columns = column_sums == 0  # 检查哪些列的和为 0
epsilon = 1e-10

# 初始化 p 矩阵
p = np.zeros_like(norm_matrix, dtype=float)

# 对非零列计算占比
p[:, ~zero_sum_columns] = norm_matrix[:, ~zero_sum_columns] / column_sums[~zero_sum_columns]

# 初始化权重
weights = np.zeros(norm_matrix.shape[1])

# 计算熵
p_safe = p[:, ~zero_sum_columns] + epsilon  # 避免 log(0)
entropy = -np.nansum(p[:, ~zero_sum_columns] * np.log(p_safe), axis=0) / np.log(len(data))
weights[~zero_sum_columns] = (1 - entropy) / (1 - entropy).sum()  # 熵权

# 3. 加权归一化矩阵
weighted_matrix = norm_matrix * weights

# 4. 计算理想解和负理想解
ideal_solution = weighted_matrix.max(axis=0)  # 理想解
negative_ideal_solution = weighted_matrix.min(axis=0)  # 负理想解

# 5. 计算各方案到理想解和负理想解的距离
distance_to_ideal = np.sqrt(((weighted_matrix - ideal_solution)**2).sum(axis=1))
distance_to_negative = np.sqrt(((weighted_matrix - negative_ideal_solution)**2).sum(axis=1))

# 6. 计算综合得分 (C*)
scores = distance_to_negative / (distance_to_ideal + distance_to_negative)

# 将 TOPSIS 结果添加到原始数据中
data["TOPSIS Score"] = scores
data["TOPSIS Rank"] = data["TOPSIS Score"].rank(ascending=False).astype(int)  # 排名

# 保存结果
data.to_csv(output_file, index=False)
print(f"TOPSIS 分析结果已保存至：{output_file}")