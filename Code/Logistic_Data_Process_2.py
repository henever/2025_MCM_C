import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
input_file = f"{data_path}/country_medals_summary_sorted.csv"  # 请替换为你的文件名
output_file = f"{data_path}/Filtered_Countries_1_4.csv"  # 输出文件名

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
filtered_countries = grouped_data[grouped_data['Total_Medals'] <= 4].copy()

# 初始化存储结果的列表
results = []

# 遍历每个筛选出的国家
for noc in filtered_countries['NOC']:
    country_data = data[data['NOC'] == noc].sort_values(by='Year')  # 按年份排序

    # 找到第一次参赛的年份
    first_participation_year = country_data['Year'].min()

    # 找到第一次获奖的年份
    first_medal_year = country_data[country_data['Total_Medals'] > 0]['Year'].min()

    if pd.isna(first_medal_year):  # 如果仍未获奖，跳过
        continue
    else:  # 如果已获奖
        # 获奖前的数据（排除第一次参赛之前的年份）
        before_medal_data = country_data[(country_data['Year'] < first_medal_year) & 
                                         (country_data['Year'] >= first_participation_year)]

        # 获取前一次和前两次奥运会的数据
        previous_olympics = before_medal_data.tail(1)  # 获取最后两届奥运会的数据

        # 遍历前一次和前两次奥运会
        for i, olympic_data in previous_olympics.iterrows():
            # 计算参赛次数和未获奖次数（排除第一次参赛之前的年份）
            years_before = len(before_medal_data[before_medal_data['Year'] < olympic_data['Year']])
            no_medal_before = before_medal_data[before_medal_data['Year'] < olympic_data['Year']]['No medal'].sum()

            result = {
                'NOC': noc,
                'Bronze': olympic_data['Bronze'],
                'Silver': olympic_data['Silver'],
                'Gold': olympic_data['Gold'],
                'Total_Medals': olympic_data['Total_Medals'],
                'Years_Before_Medals': years_before,
                'No_Medal_Before_Medals': no_medal_before,
                'Logistic': 0,  # 获奖前的奥运会，Logistic 为 0
                'Hans': 'False'
            }
            results.append(result)

        # 添加第一次获奖的数据
        first_medal_data = country_data[country_data['Year'] == first_medal_year].iloc[0]
        years_before = len(before_medal_data)
        no_medal_before = before_medal_data['No medal'].sum()

        result = {
            'NOC': noc,
            'Bronze': first_medal_data['Bronze'],
            'Silver': first_medal_data['Silver'],
            'Gold': first_medal_data['Gold'],
            'Total_Medals': first_medal_data['Total_Medals'],
            'Years_Before_Medals': years_before,
            'No_Medal_Before_Medals': no_medal_before,
            'Logistic': 1,  # 第一次获奖，Logistic 为 1
            'Hans': 'True'
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
print(f"筛选后的数据已保存至：{output_file}")