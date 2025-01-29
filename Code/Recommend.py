import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind
import os
import statsmodels.formula.api as smf

# 设置输入和输出目录
input_dir = "F:/MCM/2025COMAP/Data"
output_dir = "F:/MCM/2025COMAP/Results"
os.makedirs(output_dir, exist_ok=True)

# 加载数据
athletes = pd.read_csv(f'{input_dir}/summerOly_athletes.csv')
host_data = pd.read_csv(f'{input_dir}/summerOly_hosts.csv')
# 标记首次参赛的项目
athletes['NewEventParticipation'] = athletes.groupby(['NOC', 'Sport'])['Year'].transform('min') == athletes['Year']
athletes['NewEventParticipation'] = athletes['NewEventParticipation'].astype(int)

# 合并 athletes 数据和 host_data 数据
athletes = pd.merge(athletes, host_data, on='Year', how='left')

# 创建 Host 变量（1 表示主办国，0 表示非主办国）
athletes['Host'] = (athletes['NOC'] == athletes['Host']).astype(int)
# Step 1: 计算首次参赛的项目
athletes['NewEventParticipation'] = (
    athletes.groupby(['NOC', 'Sport'])['Year'].transform('min') == athletes['Year']
).astype(int)
# 检查结果
print(athletes[['Year', 'NOC', 'Host', 'Sport']].head())

# 手动添加“伟大教练”信息
coach_data = [
    {"Name": "Lang Ping", "NOC": "CHN", "Sport": "Volleyball", "Intervention_Year": 2016},
    {"Name": "Lang Ping", "NOC": "USA", "Sport": "Volleyball", "Intervention_Year": 2008},
    {"Name": "Béla Károlyi", "NOC": "ROU", "Sport": "Gymnastics", "Intervention_Year": 1984},
    {"Name": "Béla Károlyi", "NOC": "USA", "Sport": "Gymnastics", "Intervention_Year": 2000},
    {"Name": "Wang Tongxiang", "NOC": "AUS", "Sport": "Diving", "Intervention_Year": 2004},
    {"Name": "Sandro Damilano", "NOC": "CHN", "Sport": "Athletics", "Intervention_Year": 2012}
]
coaches = pd.DataFrame(coach_data)
# 保留教练干预信息
coaches_cleaned = coaches[['NOC', 'Sport', 'Intervention_Year']]

# 去重，确保每个运动员每年的参赛记录唯一
unique_athletes = athletes[['Name', 'NOC', 'Year']].drop_duplicates()

# 按国家和年份统计独立运动员数量
athlete_counts = unique_athletes.groupby(['NOC', 'Year']).size().reset_index(name='Athletes')

# 检查结果
print(athlete_counts.head())

# 定义函数：提取处理组和对照组数据
def prepare_data(athletes, coaches):
    all_data = []

    for _, coach in coaches.iterrows():
        # 提取处理组数据（干预前后各 4 年的教练影响）
        treated = athletes[
            (athletes['NOC'] == coach['NOC']) &
            (athletes['Sport'] == coach['Sport']) &
            (athletes['Year'] >= coach['Intervention_Year'] - 4) &
            (athletes['Year'] <= coach['Intervention_Year'] + 4)
        ].copy()
        treated['Treated'] = 1  # 标记为处理组
        treated['Intervention_Year'] = coach['Intervention_Year']  # 添加干预年份

        # 提取对照组数据（同一项目，其他国家，相同年份范围）
        control = athletes[
            (athletes['NOC'] != coach['NOC']) &
            (athletes['Sport'] == coach['Sport']) &
            (athletes['Year'] >= coach['Intervention_Year'] - 4) &
            (athletes['Year'] <= coach['Intervention_Year'] + 4)
        ].copy()
        control['Treated'] = 0  # 标记为对照组
        control['Intervention_Year'] = coach['Intervention_Year']  # 添加干预年份

        # 合并处理组和对照组
        all_data.append(treated)
        all_data.append(control)

    # 合并所有数据
    combined_data = pd.concat(all_data, ignore_index=True)

    # 确保 NewEventParticipation 被正确同步
    combined_data['NewEventParticipation'] = (
        combined_data.groupby(['NOC', 'Sport'])['Year'].transform('min') == combined_data['Year']
    ).astype(int)

    return combined_data


# 准备数据
combined_data = prepare_data(athletes, coaches)

# 合并运动员数量到主数据中
combined_data = pd.merge(combined_data, athlete_counts, on=['NOC', 'Year'], how='left')

# 检查合并后是否成功
print(combined_data[['NOC', 'Year', 'Athletes']].head())

# 填补缺失值为 0
combined_data['Athletes'] = combined_data['Athletes'].fillna(0).astype(int)
# 合并教练信息到 combined_data
combined_data = combined_data.merge(
    coaches_cleaned,
    on=['NOC', 'Sport'],
    how='left'
)

# 标记是否有教练干预
combined_data['Coach_Introduced'] = (
    (combined_data['Intervention_Year'] == combined_data['Year'])
).astype(int)

# 删除冗余列
combined_data.drop(columns=['Intervention_Year'], inplace=True)

# 检查更新后的 combined_data
print(combined_data.head())

# 检查结果
print(combined_data['Athletes'].describe())

# 检查数据完整性
print("Missing values in combined_data:")
print(combined_data.isnull().sum())

# 检查奖牌数据
print("Medal counts:")
print(combined_data['Medal'].value_counts())

# 计算处理组和对照组的平均奖牌数
treated_medals = combined_data[
    (combined_data['Treated'] == 1) &
    (combined_data['Medal'] != 'No medal')
].groupby(['NOC', 'Sport', 'Intervention_Year'])['Medal'].count().reset_index(name='Treated_Medals')

control_medals = combined_data[
    (combined_data['Treated'] == 0) &
    (combined_data['Medal'] != 'No medal')
].groupby(['NOC', 'Sport', 'Intervention_Year'])['Medal'].count().reset_index(name='Control_Medals')

# 检查分组结果
print("Treated medals after grouping:")
print(treated_medals)

print("Control medals after grouping:")
print(control_medals)

# 合并数据
medal_counts = pd.merge(treated_medals, control_medals, on=['Sport', 'Intervention_Year'], how='outer').fillna(0)

# 计算平均奖牌数
avg_treated_medals = medal_counts['Treated_Medals'].mean()
avg_control_medals = medal_counts['Control_Medals'].mean()

print(f"Average medals (Treated Group): {avg_treated_medals}")
print(f"Average medals (Control Group): {avg_control_medals}")

# 提取处理组和对照组的奖牌数
treated_medals_list = medal_counts['Treated_Medals'].dropna().tolist()
control_medals_list = medal_counts['Control_Medals'].dropna().tolist()

# 进行 t 检验
t_stat, p_value = ttest_ind(treated_medals_list, control_medals_list)
print(f"T-statistic: {t_stat}, P-value: {p_value}")

# 判断显著性
if p_value < 0.05:
    print("The difference is statistically significant.")
else:
    print("The difference is not statistically significant.")

# 检查绘图数据
plot_data = combined_data[combined_data['Medal'] != 'No medal']
print("Plot data:")
print(plot_data.head())

# 将 Medal 列转换为分类数据
plot_data['Medal'] = plot_data['Medal'].astype('category')

# 绘制奖牌数分布图
plt.figure(figsize=(10, 6))
sns.boxplot(
    x='Treated', 
    y='Medal', 
    data=plot_data, 
    palette={0: 'blue', 1: 'red', 'Bronze': 'red', 'Silver': 'red', 'Gold': 'red'}  # 为 Treated 列分配颜色
)
plt.xticks([0, 1], ['Control Group', 'Treated Group'])
plt.xlabel('Group')
plt.ylabel('Medal Count')
plt.title('Medal Count Distribution: Treated vs Control Group')
plt.savefig(f"{output_dir}/medal_count_distribution.png")
plt.close()

# 绘制奖牌类型分布图
plt.figure(figsize=(10, 6))
sns.countplot(
    x='Medal', 
    hue='Treated',  # 按 Treated 分组
    data=plot_data, 
    palette={0: 'blue', 1: 'red', 'Bronze': 'red', 'Silver': 'red', 'Gold': 'red'}  # 为 Treated 列分配颜色
)
plt.xlabel('Medal Type')
plt.ylabel('Count')
plt.title('Medal Type Distribution: Treated vs Control Group')
plt.savefig(f"{output_dir}/medal_type_distribution.png")
plt.close()



# 简化模型：移除 Control_Medals
formula = 'Treated_Medals ~ Control_Medals + C(Sport)'

# 运行回归模型
model = smf.ols(formula, data=medal_counts.dropna()).fit()

# 提取回归结果
results = {
    "params": model.params,
    "bse": model.bse,
    "pvalues": model.pvalues,
    "conf_int": model.conf_int(),
    "rsquared": model.rsquared,
    "rsquared_adj": model.rsquared_adj,
    "fvalue": model.fvalue,
    "f_pvalue": model.f_pvalue,
    "ssr": model.ssr,
    "df_model": model.df_model,
    "df_resid": model.df_resid,
    "nobs": model.nobs,
    "k": len(model.params)
}

# 输出结果
print("Improved Regression Results:")
print(pd.DataFrame({
    'Variable': results['params'].index,
    'Coefficient (beta)': results['params'].values,
    'Std_Error': results['bse'].values,
    'P_Value': results['pvalues'].values,
    'CI_Lower': results['conf_int'].iloc[:, 0].values,
    'CI_Upper': results['conf_int'].iloc[:, 1].values
}))

print("\nImproved Additional Statistics:")
print(f"R-squared: {results['rsquared']}")
print(f"Adjusted R-squared: {results['rsquared_adj']}")
print(f"F-statistic: {results['fvalue']}, F p-value: {results['f_pvalue']}")
print(f"Residual Sum of Squares (SSR): {results['ssr']}")
print(f"Degrees of Freedom (Model): {results['df_model']}")
print(f"Degrees of Freedom (Residual): {results['df_resid']}")
print(f"Number of Observations: {results['nobs']}")
print(f"Number of Variables (k): {results['k']}")

import matplotlib.colors as mcolors

# 修复绘图代码
plt.figure(figsize=(14, 7))

# 按照 Year 和 Treated 分组，计算奖牌数量
Medal_Count = (
    combined_data[combined_data['Medal'] != 'No medal']  # 过滤掉没有奖牌的数据
    .groupby(['Year', 'Treated'])
    .size()  # 计算每组的数量
    .reset_index(name='Medal_Count')  # 重置索引并命名列
)
# 按照 Year 和 Treated 分组，统计每年的奖牌数
plot_data = (
    combined_data[combined_data['Medal'] != 'No medal']  # 筛选掉没有奖牌的数据
    .groupby(['Year', 'Treated'])  # 按年份和是否有干预分组
    .size()  # 统计每组的数量
    .reset_index(name='Medal_Count')  # 重置索引并给统计列命名
)

# 查看数据结构
print(plot_data.head())
# 背景渐变色
gradient = np.linspace(0, 1, 256).reshape(1, -1)
gradient = np.vstack((gradient, gradient))
plt.imshow(
    gradient,
    extent=(plot_data['Year'].min(), plot_data['Year'].max(), 0, plot_data['Medal_Count'].max()),
    aspect='auto',
    cmap=mcolors.LinearSegmentedColormap.from_list('Gradient', ['#e6f7ff', '#cce7ff', '#99cfff'])
)



# 时间序列图
sns.lineplot(
    x='Year', 
    y='Medal_Count', 
    hue='Treated', 
    data=plot_data,
    palette={0: '#1f77b4', 1: '#ff7f0e'},  # 蓝色和橙色
    marker='o',
    linewidth=2.5
)

# 图例和美化
plt.title('Medal Count Over Time (Treated vs Control)', fontsize=18, weight='bold')
plt.xlabel('Year', fontsize=14)
plt.ylabel('Total Medal Count', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(
    title='Group', 
    labels=['Control Group (No Great Coach)', 'Treated Group (Great Coach)'], 
    title_fontsize=12, 
    fontsize=12,
    loc='upper left'
)

# 保存图像
plt.tight_layout()
plt.savefig(f"{output_dir}/medal_count_trend_beautified.png", dpi=300)
plt.close()




# 项目奖牌分布
plt.figure(figsize=(12, 6))
sns.boxplot(
    x='Sport', 
    y='Medal', 
    hue='Treated', 
    data=combined_data[combined_data['Medal'] != 'No medal']
)
plt.title('Medal Distribution by Sport (Treated vs Control)', fontsize=16)
plt.xlabel('Sport', fontsize=12)
plt.ylabel('Medal Count', fontsize=12)
plt.xticks(rotation=45)
plt.legend(title='Group')
plt.savefig(f"{output_dir}/medal_distribution_by_sport.png")
plt.close()

# 计算均值（确保 medal_counts 数据正确）
avg_medals = medal_counts[['Treated_Medals', 'Control_Medals']].mean()

# 绘制柱状图
plt.figure(figsize=(8, 5))

# 创建渐变背景
gradient = np.linspace(0, 1, 256).reshape(1, -1)
gradient = np.vstack((gradient, gradient))
plt.imshow(
    gradient,
    extent=(-0.5, 1.5, 0, avg_medals.max() + 2),  # 调整背景范围
    aspect='auto',
    cmap=mcolors.LinearSegmentedColormap.from_list('Gradient', ['#e6f7ff', '#cce7ff', '#99cfff']),
    alpha=0.3  # 调整透明度
)

# 绘制柱状图
avg_medals.plot(
    kind='bar',
    color=['#1f77b4', '#99d4ff'],  # 蓝色调
    alpha=0.8,
    edgecolor='black'
)

# 美化图表
plt.title('Average Medals: Treated vs Control Group', fontsize=16, weight='bold')
plt.xlabel('Group', fontsize=12)
plt.ylabel('Average Medal Count', fontsize=12)
plt.xticks([0, 1], ['Treated Group', 'Control Group'], fontsize=10)
plt.yticks(fontsize=10)
plt.grid(axis='y', linestyle='--', alpha=0.6)

# 保存图像
plt.tight_layout()
plt.savefig(f"{output_dir}/average_medal_comparison_with_gradient.png", dpi=300)
plt.close()


# 热力图：干预前后国家奖牌变化
# 筛选有伟大教练影响的国家
great_coach_nocs = coaches['NOC'].unique()

# 筛选数据：仅包括有伟大教练影响的国家
filtered_heatmap_data = combined_data[
    combined_data['NOC'].isin(great_coach_nocs)
].pivot_table(
    index='NOC', 
    columns='Year', 
    values='Medal', 
    aggfunc='count'
).fillna(0)

# 绘制热力图
plt.figure(figsize=(12, 8))
sns.heatmap(
    filtered_heatmap_data, 
    annot=True, 
    fmt=".0f", 
    cmap="YlGnBu", 
    linewidths=0.5, 
    cbar_kws={'label': 'Medal Count'}
)
plt.title('Heatmap of Medal Count for Countries Influenced by Great Coaches (Before and After Intervention)', fontsize=14)
plt.xlabel('Year')
plt.ylabel('Country (NOC)')
plt.tight_layout()
plt.savefig(f"{output_dir}/great_coach_heatmap.png")
plt.close()



# 提取变量和置信区间
variables = results['params'].index
coefficients = results['params'].values
ci_lower = results['conf_int'].iloc[:, 0].values
ci_upper = results['conf_int'].iloc[:, 1].values

# 筛选适合引入教练的国家和项目
def recommend_countries_for_coaches_no_gdp_population(athletes):
    # 计算每个国家和项目的历史奖牌总数
    medal_totals = athletes[athletes['Medal'] != 'No medal'].groupby(['NOC', 'Sport'])['Medal'].count()
    medal_totals = medal_totals.reset_index().rename(columns={'Medal': 'Total_Medals'})
    
    # 计算每个国家和项目的历史参赛人数
    athlete_counts = athletes.groupby(['NOC', 'Sport'])['Name'].count().reset_index().rename(columns={'Name': 'Athlete_Count'})
    
    # 合并奖牌总数和参赛人数
    data = pd.merge(medal_totals, athlete_counts, on=['NOC', 'Sport'], how='outer').fillna(0)
    
    # 计算奖牌率（奖牌数 / 参赛人数），避免参赛人数多但奖牌少的国家被忽略
    data['Medal_Rate'] = data['Total_Medals'] / (data['Athlete_Count'] + 1e-5)  # 防止除以零
    
    # 筛选条件：奖牌率低于中位数，但参赛人数高于中位数
    median_medal_rate = data['Medal_Rate'].median()
    median_athlete_count = data['Athlete_Count'].median()
    
    recommendations = data[
        (data['Medal_Rate'] < median_medal_rate) & 
        (data['Athlete_Count'] > median_athlete_count)
    ]
    
    return recommendations

# 推荐引入教练的国家和项目

# 聚合数据
aggregated_data = combined_data.groupby(['Year', 'NOC', 'Sport']).agg(
    Athletes=('Athletes', 'sum'),                # 汇总运动员人数
    Total_Medals=('Medal', lambda x: (x != 'No medal').sum()),  # 奖牌总数
    NewEventParticipation=('NewEventParticipation', 'max'),  # 首次参赛标记
    Coach_Introduced=('Coach_Introduced', 'max')  # 教练干预标记
).reset_index()

# 合并 Host 信息
aggregated_data = aggregated_data.merge(host_data, on='Year', how='left')
aggregated_data['Host'] = (aggregated_data['NOC'] == aggregated_data['Host']).astype(int)

# 检查生成数据
print(aggregated_data.head())

aggregated_data['Coach_Introduced'] = aggregated_data['Intervention_Year'].notna().astype(int)
aggregated_data.drop(columns=['Intervention_Year'], inplace=True)

recommendations = recommend_countries_for_coaches_no_gdp_population(athletes)
print("Recommended countries and sports for introducing coaches:")
print(recommendations)

# 模拟引入教练并预测奖牌数提升
def simulate_coach_effect_no_gdp_population(combined_data, recommendations):
    # 为推荐的国家和项目添加“引入教练”变量
    combined_data['Coach_Introduced'] = 0
    for _, row in recommendations.iterrows():
        combined_data.loc[
            (combined_data['NOC'] == row['NOC']) & 
            (combined_data['Sport'] == row['Sport']),
            'Coach_Introduced'
        ] = 1
    
    # 更新回归模型公式
    formula = 'Medal ~ Athletes + Host + NewEventParticipation + Coach_Introduced'
    model = smf.ols(formula, data=combined_data).fit()
    
    # 预测引入教练前后的奖牌数
    combined_data['Predicted_Medals_Before'] = model.predict(
        combined_data.assign(Coach_Introduced=0)  # 无教练
    )
    combined_data['Predicted_Medals_After'] = model.predict(
        combined_data.assign(Coach_Introduced=1)  # 引入教练
    )
    
    # 计算奖牌提升量
    combined_data['Medal_Increase'] = combined_data['Predicted_Medals_After'] - combined_data['Predicted_Medals_Before']
    
    # 聚合预测结果
    aggregated = combined_data.groupby(['NOC', 'Sport'])[['Medal_Increase']].sum().reset_index()
    aggregated = aggregated.merge(recommendations, on=['NOC', 'Sport'], how='inner')  # 仅保留推荐的国家和项目
    return aggregated

# 模拟引入教练的效果

coach_effect_predictions = simulate_coach_effect_no_gdp_population(aggregated_data, recommendations)

# 输出预测结果
print("Predicted medal increases after introducing coaches:")
print(coach_effect_predictions)

# 保存预测结果为CSV
coach_effect_predictions.to_csv(f"{output_dir}/coach_effect_predictions_no_gdp_population.csv", index=False)

# 可视化预测结果
plt.figure(figsize=(10, 6))
sns.barplot(
    x='Medal_Increase', 
    y='Sport', 
    hue='NOC', 
    data=coach_effect_predictions, 
    palette='viridis'
)
plt.title('Predicted Medal Increases After Introducing Coaches')
plt.xlabel('Predicted Medal Increase')
plt.ylabel('Sport')
plt.legend(title='NOC', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(f"{output_dir}/predicted_medal_increases_no_gdp_population.png")
plt.close()
