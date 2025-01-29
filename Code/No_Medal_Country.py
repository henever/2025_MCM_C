import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
input_file = f"{data_path}/country_medals_summary_sorted.csv"  # 请替换为你的文件名
output_file = f"{data_path}/Non_Winning_Countries.csv"  # 输出文件名

# 读取数据
data = pd.read_csv(input_file)

# 按国家分组，计算每个国家的总奖牌数
grouped_data = data.groupby('NOC').agg({
    'Bronze': 'sum',
    'Gold': 'sum',
    'Silver': 'sum',
    'Total_Medals': 'sum',
    'Year': 'count',  # 参赛次数
    'No medal': 'sum'  # 未获奖次数
}).reset_index()

# 筛选出至今仍未获奖的国家
non_winning_countries = grouped_data[grouped_data['Total_Medals'] == 0].copy()

# 初始化存储结果的列表
results = []

# 遍历每个未获奖的国家
for noc in non_winning_countries['NOC']:
    country_data = data[data['NOC'] == noc].sort_values(by='Year')  # 按年份排序

    # 找到第一次获得 No medal 的年份
    first_no_medal_year = country_data[country_data['No medal'] > 0]['Year'].min()

    if pd.isna(first_no_medal_year):  # 如果没有 No medal 记录，跳过
        continue

    # 排除第一次获得 No medal 之前的年份
    country_data = country_data[country_data['Year'] >= first_no_medal_year]

    # 计算参赛次数和未获奖次数
    years_before = len(country_data)
    no_medal_before = country_data['No medal'].sum()

    # 生成结果
    result = {
        'NOC': noc,
        'Bronze': 0,  # 未获奖国家，奖牌数为 0
        'Silver': 0,
        'Gold': 0,
        'Total_Medals': 0,
        'Years_Before_Medals': years_before,
        'No_Medal_Before_Medals': no_medal_before,
        'Logistic': 0,  # 未获奖国家，Logistic 为 0
        'Hans': 'False'
    }
    results.append(result)

# 将结果转换为 DataFrame
result_df = pd.DataFrame(results)

# 选择需要的列
result_df = result_df[[
    'NOC', 'Bronze', 'Silver', 'Gold', 'Total_Medals',
    'Years_Before_Medals', 'No_Medal_Before_Medals', 'Logistic', 'Hans'
]]

# 保存结果
result_df.to_csv(output_file, index=False, encoding='utf-8')
print(f"未获奖国家的数据已保存至：{output_file}")