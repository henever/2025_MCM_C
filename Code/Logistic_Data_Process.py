import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
input_file = f"{data_path}/country_medals_summary_sorted.csv"  # 请替换为你的文件名
output_file = f"{data_path}/Filtered_Countries.csv"  # 输出文件名

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

# 筛选出总奖牌数小于等于 3 的国家
filtered_countries = grouped_data[grouped_data['Total_Medals'] <= 3].copy()

# 初始化新表格的列
filtered_countries['Years_Before_Medals'] = 0
filtered_countries['No_Medal_Before_Medals'] = 0
filtered_countries['Logistic'] = 0
filtered_countries['Logistic汉字'] = '否'

# 遍历每个筛选出的国家
for index, row in filtered_countries.iterrows():
    noc = row['NOC']
    country_data = data[data['NOC'] == noc].sort_values(by='Year')  # 按年份排序

    # 找到第一次获奖的年份
    first_medal_year = country_data[country_data['Total_Medals'] > 0]['Year'].min()

    if pd.isna(first_medal_year):  # 如果仍未获奖
        filtered_countries.at[index, 'Years_Before_Medals'] = len(country_data)  # 参赛次数
        filtered_countries.at[index, 'No_Medal_Before_Medals'] = country_data['No medal'].sum()  # 未获奖次数
        filtered_countries.at[index, 'Logistic'] = 0  # 未获奖
        filtered_countries['Logistic汉字'] = '否'
    else:  # 如果已获奖
        before_medal_data = country_data[country_data['Year'] < first_medal_year]  # 获奖前的数据
        filtered_countries.at[index, 'Years_Before_Medals'] = len(before_medal_data)  # 参赛次数
        filtered_countries.at[index, 'No_Medal_Before_Medals'] = before_medal_data['No medal'].sum()  # 未获奖次数
        filtered_countries.at[index, 'Logistic'] = 1  # 已获奖
        filtered_countries['Logistic汉字'] = '是'

# 选择需要的列
result = filtered_countries[[
    'NOC', 'Bronze', 'Silver', 'Gold', 'Total_Medals',
    'Years_Before_Medals', 'No_Medal_Before_Medals', 'Logistic', 'Logistic汉字'
]]

# 保存结果
result.to_csv(output_file, index=False, encoding='utf-8')
print(f"筛选后的数据已保存至：{output_file}")