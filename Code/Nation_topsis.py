import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
input_file = f"{data_path}/medals_2024_with_topsis.csv"  # 输入文件
output_file = f"{data_path}/medals_2024_with_country_topsis.csv"  # 输出文件

# 读取数据
data = pd.read_csv(input_file)

# 1. 将 TOPSIS_Score_Sum 和 Sport_topsis_score 中为 0 的值替换为 1e-10
data["TOPSIS_Score_Sum"] = data["TOPSIS_Score_Sum"].replace(0, 1e-10)
data["Sport_topsis_score"] = data["Sport_topsis_score"].replace(0, 1e-10)

# 2. 计算每个国家的 TOPSIS 分数
# 新增一列 TOPSIS_Product，表示 TOPSIS_Score_Sum * Sport_topsis_score
data["TOPSIS_Product"] = data["TOPSIS_Score_Sum"] * data["Sport_topsis_score"]

# 按国家分组，计算 TOPSIS_Product 的总和
# country_topsis = data.groupby("NOC")["TOPSIS_Product"].sum().reset_index()
# country_topsis = country_topsis.rename(columns={"TOPSIS_Product": "Country_TOPSIS_Score"})

# 将国家 TOPSIS 分数合并到原始数据中
# data = pd.merge(data, country_topsis, on="NOC", how="left")

# 3. 保存结果
data.to_csv(output_file, index=False)
print(f"结果已保存至：{output_file}")