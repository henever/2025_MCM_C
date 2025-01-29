import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
input_file = f"{data_path}/NOC_Sport_Summary_2020.csv"  # 输入文件
check_file = f"{data_path}/check.csv"  # 检查文件
output_file = f"{data_path}/filtered_Participants_2020_with_TOPSIS.csv"  # 输出文件

# 读取数据
data = pd.read_csv(input_file)
check_data = pd.read_csv(check_file)

# 获取需要删除的国家（check2 值为 1 的 NOC）
nocs_to_remove = check_data[check_data["check2"] == 1]["NOC"].unique()

# 过滤掉这些国家的数据
filtered_data = data[~data["NOC"].isin(nocs_to_remove)]

# 保存结果
filtered_data.to_csv(output_file, index=False)
print(f"过滤后的结果已保存至：{output_file}")