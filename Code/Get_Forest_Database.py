import pandas as pd

# 读取CSV文件
df = pd.read_csv('F:/MCM/2025COMAP/Data/country_event_medals_and_participation.csv')

# 假设C列的名称为 "C" ，D列的名称为 "D"，我们将结果存储在新列 "E" 中
df['Parti_to_Gold'] = df['Gold_Medals'] / df['Country_Event_Participation']
df['Parti_to_Silver'] = df['Silver_Medals'] / df['Country_Event_Participation']
df['Parti_to_Bronze'] = df['Bronze_Medals'] / df['Country_Event_Participation']
df['Parti_to_Medal'] = df['Total_Medals'] / df['Country_Event_Participation']
df['Partipate_Rate'] = df['Country_Event_Participation'] / df['Event_Total_Participation']
# 输出修改后的DataFrame，查看是否成功
for col in df.columns:
    df[col] = df[col].astype(str).str.lstrip("'")
# 归一化处理



# 将结果保存到新的CSV文件
df.to_csv('F:/MCM/2025COMAP/Data/Forest_Database.csv', index=False)
