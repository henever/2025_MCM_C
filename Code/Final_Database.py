import pandas as pd

# 读取历史奥运会数据
historical_data_path = "F:/MCM/2025COMAP/Data/summerOly_athletes.csv"
historical_data = pd.read_csv(historical_data_path)

# 读取2028年奥运会参赛队员数据
participants_data_path = "F:/MCM/2025COMAP/Data/Participants_2028.csv"  # 假设你的2028年数据文件名是这个
participants_data = pd.read_csv(participants_data_path)

# 1. 对每个国家中的每个项目所有参赛队员的 Bronze Medals, Gold Medals, Silver Medals 求和
# 首先按 NOC 和 Sport 分组，然后对奖牌列求和
team_medals_sum = participants_data.groupby(['NOC', 'Sport'])[['Bronze Medals', 'Gold Medals', 'Silver Medals']].sum().reset_index()

# 2. 计算每个国家每个项目历史上获得的四种奖牌数占奥运会历史上该项目所有奖牌的比例
# 首先计算历史上每个项目的总奖牌数
historical_medals_by_sport = historical_data[historical_data['Medal'] != 'No medal'].groupby(['Sport', 'Medal']).size().unstack(fill_value=0)
historical_medals_by_sport['Total Medals'] = historical_medals_by_sport.sum(axis=1)

# 将历史奖牌数据与当前数据合并
team_medals_sum = team_medals_sum.merge(historical_medals_by_sport, left_on='Sport', right_index=True, how='left')

# 计算比例
team_medals_sum['Gold_Ratio'] = team_medals_sum['Gold Medals'] / team_medals_sum['Gold']
team_medals_sum['Silver_Ratio'] = team_medals_sum['Silver Medals'] / team_medals_sum['Silver']
team_medals_sum['Bronze_Ratio'] = team_medals_sum['Bronze Medals'] / team_medals_sum['Bronze']

# 3. 对每个国家每个项目的参赛队员的 TOPSIS Score 求和
topsis_sum = participants_data.groupby(['NOC', 'Sport'])['TOPSIS Score'].sum().reset_index()
topsis_sum.rename(columns={'TOPSIS Score': 'TOPSIS_Score_Sum'}, inplace=True)

# 合并 TOPSIS Score 总和到结果表中
team_medals_sum = team_medals_sum.merge(topsis_sum, on=['NOC', 'Sport'], how='left')

# 4. 只保留需要的列
final_table = team_medals_sum[['NOC', 'Sport', 'Bronze Medals', 'Gold Medals', 'Silver Medals', 
                               'Gold_Ratio', 'Silver_Ratio', 'Bronze_Ratio', 'TOPSIS_Score_Sum']]

# 5. 保存结果
output_path = "F:/MCM/2025COMAP/Data/team_medals_summary.csv"
final_table.to_csv(output_path, index=False)

print(f"处理完成，结果已保存至：{output_path}")