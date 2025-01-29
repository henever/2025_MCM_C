import pandas as pd

# 创建DataFrame
file_path = "F:/MCM/2025COMAP/Data/NOC_medal_counts.csv"
df = pd.read_csv(file_path)

# 按国家分组，计算金、银、铜牌和总奖牌数
result = df.groupby(["NOC","Name"]).agg({
    'Gold': 'sum',
    'Silver': 'sum',
    'Bronze': 'sum'
}).reset_index()

# 计算总奖牌数
result['Total'] = result['Gold'] + result['Silver'] + result['Bronze']

# 打印结果

output_file_path = "F:/MCM/2025COMAP/Data/NOC_medal.csv"
result.to_csv(output_file_path, index=False)