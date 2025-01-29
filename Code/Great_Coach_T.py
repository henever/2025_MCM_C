import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind
import os
import statsmodels.formula.api as smf
import matplotlib.lines as mlines
# 设置输入和输出目录
input_dir = "F:/MCM/2025COMAP/Data"
output_dir = "F:/MCM/2025COMAP/Results"
os.makedirs(output_dir, exist_ok=True)

# 加载数据
athletes = pd.read_csv(f'{input_dir}/summerOly_athletes.csv')

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

# 定义函数：提取处理组和对照组数据
def prepare_data(athletes, coaches):
    all_data = []

    for _, coach in coaches.iterrows():
        # 提取处理组数据（有“伟大教练”的国家-项目-年份组合）
        treated = athletes[
            (athletes['NOC'] == coach['NOC']) &
            (athletes['Sport'] == coach['Sport']) &
            (athletes['Year'] >= coach['Intervention_Year'] - 4) &  # 干预前后各4年
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
    return combined_data

# 准备数据
combined_data = prepare_data(athletes, coaches)

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
    marker='o',  # 默认的点和线组合
    linewidth=2.5
)

# 图例和美化
plt.title('Medal Count Over Time (Treated vs Control)', fontsize=18, weight='bold')
plt.xlabel('Year', fontsize=14)
plt.ylabel('Total Medal Count', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
# 手动创建图例
control_line = mlines.Line2D([], [], color='#1f77b4', marker='o', linestyle='-', linewidth=2.5, label='Treated Group (Great Coach)')
treated_line = mlines.Line2D([], [], color='#ff7f0e', marker='o', linestyle='-', linewidth=2.5, label='Control Group (No Great Coach)')

# 添加图例
plt.legend(handles=[control_line, treated_line], title='Group', title_fontsize=12, fontsize=12, loc='upper left')

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

# 创建置信区间图
plt.figure(figsize=(10, 6))
plt.errorbar(coefficients, variables, xerr=[coefficients - ci_lower, ci_upper - coefficients], fmt='o', color='b', ecolor='r', capsize=4, label='95% Confidence Interval')
plt.axvline(x=0, color='gray', linestyle='--', linewidth=1)  # 标记零影响线
plt.title('Coefficient Estimates with Confidence Intervals')
plt.xlabel('Coefficient (Effect Size)')
plt.ylabel('Variables')
plt.grid(axis='y', linestyle='--', linewidth=0.5)
plt.legend()
plt.tight_layout()
plt.savefig(f'{output_dir}/confidence_intervals_plot.png')
plt.show()
