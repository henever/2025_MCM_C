import pandas as pd

# 假设 'summerOly_athletes' 是你的原始数据表格
summerOly_athletes = pd.read_csv('F:/MCM/2025COMAP/Data/summerOly_athletes.csv')

# 1. 生成金、银、铜奖牌数和总奖牌数
athlete_medals = summerOly_athletes.groupby(["NOC", "Sport"]).agg(
    Gold_Medals=("Medal", lambda x: (x == "Gold").sum()),       # 金牌数
    Silver_Medals=("Medal", lambda x: (x == "Silver").sum()),   # 银牌数
    Bronze_Medals=("Medal", lambda x: (x == "Bronze").sum()),   # 铜牌数
    No_Medals=("Medal", lambda x: (x == "No medal").sum()),
    Total_Medals=("Medal", lambda x: (x != "No medal").sum())   # 总奖牌数
).reset_index()

# 2. 计算每个国家在每个项目中的总参赛数
country_event_participation = summerOly_athletes.groupby(['NOC', 'Sport']).size().reset_index(name='Country_Event_Participation')

# 3. 计算每个项目的总参赛数（所有国家参赛数）
event_total_participation = summerOly_athletes.groupby('Sport').size().reset_index(name='Event_Total_Participation')

# 4. 将奖牌数、参赛数表格进行合并
merged_data = pd.merge(athlete_medals, country_event_participation, on=['NOC', 'Sport'], how='left')
final_data = pd.merge(merged_data, event_total_participation, on='Sport', how='left')

# 5. 输出结果到 CSV 文件
final_data.to_csv('F:/MCM/2025COMAP/Data/country_event_medals_and_participation.csv', index=False)

# 显示新表格的前几行
print(final_data.head())
