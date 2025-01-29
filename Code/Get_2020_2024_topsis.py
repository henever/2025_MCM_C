import pandas as pd

# 读取数据
file_path = 'F:/MCM/2025COMAP/Data/summerOly_athletes.csv'
df = pd.read_csv(file_path)

# 读取 Highlighted_Data.csv 中的 Name 列
# highlighted_names = pd.read_excel('F:/MCM/2025COMAP/Data/Highlighted_Data.xlsx')['Name'].tolist()

# 筛选出名字在 Highlighted_Data.csv 中的选手
# df = df[df['Name'].isin(highlighted_names)]

# 获取2020年和2024年参赛过的选手名单
participants_2020 = df[df['Year'] == 2020]['Name'].unique()
participants_2024 = df[df['Year'] == 2024]['Name'].unique()

# 合并2020年和2024年参赛选手名单
participants = set(participants_2020).union(set(participants_2024))

# 筛选出这些选手的所有历史记录
df_filtered = df[df['Name'].isin(participants)]

# 定义函数，统计截止到某年的奖牌数量和参赛次数
def calculate_medals(df, year):
    # 过滤出截止到指定年份的数据
    df_filtered = df[df['Year'] <= year]
    
    # 按 Name, NOC, Sport 分组，统计奖牌数量
    medal_counts = df_filtered.groupby(['Name', 'NOC', 'Sport'])['Medal'].value_counts().unstack(fill_value=0)
    medal_counts = medal_counts.rename(columns={
        'Gold': 'Gold Medals',
        'Silver': 'Silver Medals',
        'Bronze': 'Bronze Medals',
        'No medal': 'No Medals'  # 如果需要统计无奖牌的情况
    })
    
    # 计算总奖牌数量（不包括 "No medal"）
    medal_counts['Total Medals'] = medal_counts['Gold Medals'] + medal_counts['Silver Medals'] + medal_counts['Bronze Medals']
    
    # 统计参赛次数
    participation_counts = df_filtered.groupby(['Name', 'NOC', 'Sport']).size().reset_index(name='Participation Count')
    
    # 合并奖牌数量和参赛次数
    summary = pd.merge(medal_counts.reset_index(), participation_counts, on=['Name', 'NOC', 'Sport'], how='left')
    
    # 添加截止年份列
    summary['Cutoff Year'] = year
    
    return summary

# 统计截止到2020年和2024年的奖牌数量和参赛次数
df_2020 = calculate_medals(df_filtered, 2020)
df_2024 = calculate_medals(df_filtered, 2024)

# 合并两部分数据
combined_df = pd.concat([df_2020, df_2024], ignore_index=True)

# 排序：按 Cutoff Year, NOC, Sport, Name 排序
combined_df = combined_df.sort_values(by=['Cutoff Year', 'NOC', 'Sport', 'Name'])

# 保存到文件
output_path = 'F:/MCM/2025COMAP/Data/without_age_cutoff_medal_summary.csv'
combined_df.to_csv(output_path, index=False)

print(f"生成的表格已保存到 {output_path}")