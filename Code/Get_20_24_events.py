import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
input_file = f"{data_path}/summerOly_athletes.csv"  # 输入文件
output_file_2020 = f"{data_path}/sport_participation_2020.csv"  # 2020年输出文件
output_file_2024 = f"{data_path}/sport_participation_2024.csv"  # 2024年输出文件

# 读取数据
df = pd.read_csv(input_file)

# 过滤2020年和2024年的数据
df_2020 = df[df["Year"] == 2020]
df_2024 = df[df["Year"] == 2024]

# 定义函数，统计每个年份的 Sport 参与人数
def calculate_participation(df, year):
    # 按 NOC 和 Sport 分组，统计参与人数
    participation = df.groupby(["NOC", "Sport"])["Name"].nunique().reset_index()
    participation = participation.rename(columns={"Name": "Participant Count"})
    
    # 按 NOC 和 Sport 排序
    participation = participation.sort_values(by=["NOC", "Sport"])
    
    # 保存到文件
    output_file = f"{data_path}/sport_participation_{year}.csv"
    participation.to_csv(output_file, index=False)
    print(f"{year}年的 Sport 参与人数统计已保存至：{output_file}")

# 统计2020年和2024年的 Sport 参与人数
calculate_participation(df_2020, 2020)
calculate_participation(df_2024, 2024)