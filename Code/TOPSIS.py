import pandas as pd
import numpy as np

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
input_file = f"{data_path}/cutoff_medal_summary.csv"  # 请替换为你的文件名
output_file = f"{data_path}/Participants_Topsis_Results.csv"

# 读取数据
data = pd.read_csv(input_file)

# 需要用于分析的列
columns_to_analyze = [
    "Gold_Medals", "Silver_Medals", "Bronze_Medals", "Total_Medals",
    "Country_Event_Participation", "Parti_to_Gold", "Parti_to_Silver",
    "Parti_to_Bronze", "Parti_to_Medal", "Participate_Rate"
]

# 初始化存储结果
results = []

# 遍历每个国家
for noc in data["NOC"].unique():
    # 筛选该国家的数据
    country_data = data[data["NOC"] == noc].copy()

    # 提取用于 TOPSIS 的数据
    topsis_matrix = country_data[columns_to_analyze].values

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

    # 检查 country_data 是否为空
    if len(country_data) > 0:
    # 计算熵
        p_safe = p[:, ~zero_sum_columns] + epsilon  # 避免 log(0)
        entropy = -np.nansum(p[:, ~zero_sum_columns] * np.log(p_safe), axis=0) / np.log(len(country_data))
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

    # 将结果添加到 DataFrame
    country_data["Score"] = scores

    # 处理非有限值
    country_data["Score"] = country_data["Score"].fillna(0)  # 填充 NaN
    country_data["Score"] = country_data["Score"].replace([np.inf, -np.inf], 0)  # 替换 inf

    # 计算排名
    country_data["Rank"] = country_data["Score"].rank(ascending=False).astype(int)  # 排名

    # 保存每个国家的结果
    results.append(country_data)

# 合并所有结果
final_results = pd.concat(results, ignore_index=True)

# 输出到文件
final_results.to_csv(output_file, index=False)
print(f"分析结果已保存至：{output_file}")