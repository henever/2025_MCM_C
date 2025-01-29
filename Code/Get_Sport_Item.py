import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
athletes_file = f"{data_path}/summerOly_athletes.csv"  # 运动员参赛记录表
medals_file = f"{data_path}/athlete_medals_compet.csv"  # 运动员获奖记录表
output_file = f"{data_path}/athlete_medals_compet_with_sport.csv"  # 输出文件名

# 读取数据
athletes_data = pd.read_csv(athletes_file)  # 运动员参赛记录
medals_data = pd.read_csv(medals_file)  # 运动员获奖记录

# 确保运动员姓名和国家代码（NOC）在两个表中一致
# 假设运动员姓名列名为 'Name'，国家代码列名为 'NOC'，运动项目列名为 'Sport'
athletes_data['Name'] = athletes_data['Name'].str.strip().str.lower()
medals_data['Name'] = medals_data['Name'].str.strip().str.lower()

# 创建一个字典，存储每个运动员的运动项目
athlete_sport_dict = athletes_data.groupby(['Name', 'NOC'])['Sport'].first().to_dict()

# 在 medals_data 中添加运动项目列
medals_data['Sport'] = medals_data.apply(
    lambda row: athlete_sport_dict.get((row['Name'], row['NOC']), 'Unknown'), axis=1
)

# 保存结果
medals_data.to_csv(output_file, index=False, encoding='utf-8')
print(f"添加运动项目后的数据已保存至：{output_file}")