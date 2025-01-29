import pandas as pd
import statsmodels.formula.api as smf

# 示例路径（改成你的路径）
input_dir = "F:/MCM/2025COMAP/Data"
output_dir = "F:/MCM/2025COMAP/Results"

# 加载数据
athletes = pd.read_csv(f"{input_dir}/summerOly_athletes.csv")
coaches = pd.DataFrame([
    {"Name": "Lang Ping", "NOC": "CHN", "Sport": "Volleyball", "Intervention_Year": 2008},
    {"Name": "Lang Ping", "NOC": "USA", "Sport": "Volleyball", "Intervention_Year": 2016},
    {"Name": "Béla Károlyi", "NOC": "ROU", "Sport": "Gymnastics", "Intervention_Year": 1984},
    {"Name": "Béla Károlyi", "NOC": "USA", "Sport": "Gymnastics", "Intervention_Year": 2000},
    {"Name": "Wang Tongxiang", "NOC": "AUS", "Sport": "Diving", "Intervention_Year": 2004},
    {"Name": "Liu Guodong", "NOC": "SGP", "Sport": "Table Tennis", "Intervention_Year": 2008},
    {"Name": "Sandro Damilano", "NOC": "CHN", "Sport": "Athletics", "Intervention_Year": 2012},
])
host_data = pd.read_csv(f"{input_dir}/summerOly_hosts.csv")  # 假设 host_data 包含 'Year' 和 'Host'

# 处理 athletes 数据，标记首次参赛的项目
athletes['NewEventParticipation'] = (
    athletes.groupby(['NOC', 'Sport'])['Year'].transform('min') == athletes['Year']
).astype(int)

# 合并教练信息到 athletes 数据
combined_data = athletes.merge(
    coaches[['NOC', 'Sport', 'Intervention_Year']],
    on=['NOC', 'Sport'],
    how='left'
)

# 标记是否是教练干预年份
combined_data['Coach_Introduced'] = (
    combined_data['Year'] == combined_data['Intervention_Year']
).astype(int)

# 删除冗余列
combined_data.drop(columns=['Intervention_Year'], inplace=True)

# 合并 Host 信息
combined_data = combined_data.merge(host_data, on='Year', how='left')
combined_data['Host'] = (combined_data['NOC'] == combined_data['Host']).astype(int)

# 检查合并后的 combined_data
print(combined_data.head())

# 汇总数据，生成 aggregated_data
aggregated_data = combined_data.groupby(['Year', 'NOC', 'Sport']).agg(
    Athletes=('Name', 'count'),                # 运动员人数
    Total_Medals=('Medal', lambda x: (x != 'No medal').sum()),  # 奖牌总数
    NewEventParticipation=('NewEventParticipation', 'max'),  # 首次参赛标记
    Coach_Introduced=('Coach_Introduced', 'max'),  # 教练干预标记
    Host=('Host', 'max')  # 是否主办国
).reset_index()

# 确认 aggregated_data 的内容
print(aggregated_data.head())

# 回归模型：预测奖牌数
formula = 'Total_Medals ~ Athletes + Host + NewEventParticipation + Coach_Introduced + Athletes*Coach_Introduced '
model = smf.ols(formula, data=aggregated_data).fit()

# 输出模型摘要
print(model.summary())

# 使用模型预测奖牌数（基于现有数据）
aggregated_data['Predicted_Medals'] = model.predict(aggregated_data)

# 计算如果引入教练后的奖牌数增加量（即Coach_Introduced为1时的预测奖牌数）
aggregated_data['Predicted_Medals_With_Coach'] = model.predict(
    aggregated_data.assign(Coach_Introduced=1)  # 模拟引入教练后的情形
)

# 计算增加的奖牌数
aggregated_data['Medal_Increase_With_Coach'] = aggregated_data['Predicted_Medals_With_Coach'] - aggregated_data['Predicted_Medals']

# 筛选出引入教练能显著增加奖牌数的项目
significant_increase = aggregated_data[aggregated_data['Medal_Increase_With_Coach'] > 0]

# 输出需要引入教练的项目和国家，并预测奖牌数增加
print("Countries and Sports where coaches should be introduced (with predicted medal increase):")
print(significant_increase[['NOC', 'Sport', 'Medal_Increase_With_Coach']])

# 保存预测结果到文件
significant_increase[['NOC', 'Sport', 'Medal_Increase_With_Coach']].to_csv(f"{output_dir}/coach_recommendations.csv", index=False)