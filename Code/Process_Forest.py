import pandas as pd

# 读取原始数据
file_path = "F:/MCM/2025COMAP/Data/summerOly_athletes.csv"  # 替换为您的文件路径
df = pd.read_csv(file_path)

# 确保数据包含必要列
required_columns = {'Year', 'NOC', 'Medal'}
if not required_columns.issubset(df.columns):
    raise ValueError(f"CSV 文件必须包含以下列: {required_columns}")



# 计算每个国家每年三种奖牌和总奖牌数量
summary = df.groupby(['NOC', 'Year'])['Medal'].value_counts().unstack(fill_value=0).reset_index()

# 确保包含 'Gold', 'Silver', 'Bronze' 列
for medal_type in ['Gold', 'Silver', 'Bronze']:
    if medal_type not in summary.columns:
        summary[medal_type] = 0

summary['Total_Medals'] = summary[['Gold', 'Silver', 'Bronze']].sum(axis=1)

# 获取所有国家列表，包括无奖牌国家
all_countries = df['NOC'].unique()

# 确保所有国家出现在每年数据中，即使没有奖牌
all_years = df['Year'].unique()
expanded_data = pd.DataFrame([(noc, year) for noc in all_countries for year in all_years], columns=['NOC', 'Year'])
summary = pd.merge(expanded_data, summary, on=['NOC', 'Year'], how='left').fillna(0)

# 转换奖牌列为整数类型
for col in ['Gold', 'Silver', 'Bronze', 'Total_Medals']:
    summary[col] = summary[col].astype(int)

# 添加 "Medals_Last_3_Years" 列
recent_years = [2016, 2020, 2024]  # 最近三届奥运会的年份


# 按 NOC 和 Year 排序
summary = summary.sort_values(by=['NOC', 'Year']).reset_index(drop=True)

summary['Medals_Last_3_Years'] = summary.groupby('NOC').apply(
    lambda group: group['Total_Medals'][group['Year'].isin(recent_years)].sum() > 0

).astype(int).reset_index(drop=True)
# 添加 "More_Than_3_Medals" 列
summary['More_Than_3_Medals'] = summary.groupby('NOC')['Total_Medals'].transform(lambda x: 1 if x.max() >= 3 else 0)
# 保存到新的 CSV 文件
output_path = "F:/MCM/2025COMAP/Data/country_medals_summary_sorted.csv"  # 替换为您希望保存的文件路径
summary.to_csv(output_path, index=False)

print(f"结果已保存至: {output_path}")
