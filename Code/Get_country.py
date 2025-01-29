import pandas as pd

# 读取原始表格数据（包含国家名称和三字母代码的表）
file_path = "F:/MCM/2025COMAP/Data/summerOly_athletes.csv"  # 替换为实际文件路径
original_df = pd.read_csv(file_path)

# 提取第三列（国家名称）和第四列（三字母代码）作为键值对
country_to_code = pd.DataFrame({
    "Country": original_df.iloc[:, 2],  # 第三列：国家名称
    "NOC": original_df.iloc[:, 3]      # 第四列：三字母缩写
}).dropna()  # 删除空值

# 读取目标表格（需要添加三字母代码的表）
target_file_path = "F:/MCM/2025COMAP/Data/summerOly_medal_counts.csv"  # 替换为目标文件路径
target_df = pd.read_csv(target_file_path)
for col in target_df.columns:
    target_df[col] = target_df[col].astype(str).str.rstrip("?")
# 确保国家名称列为第二列
target_df["Country"] = target_df.iloc[:, 1]  # 提取目标表第二列作为国家名称列

# 初始化第八列为空
target_df.insert(7, "NOC", None)  # 第八列位置插入一个新列 "NOC"
for col in original_df.columns:
    original_df[col] = original_df[col].astype(str).str.rstrip("?")

# 遍历目标表并匹配三字母缩写
for index, row in target_df.iterrows():
    country_name = row["Country"]
    matched_code = country_to_code[country_to_code["Country"] == country_name]["NOC"]
    if not matched_code.empty:
        target_df.at[index, "NOC"] = matched_code.values[0]

# 保存结果
output_file_path = "F:/MCM/2025COMAP/Data/NOC_medal_counts.csv"  # 替换为输出文件路径
target_df.to_csv(output_file_path, index=False)

print("操作完成，三字母代码已添加至第八列。结果保存至:", output_file_path)
