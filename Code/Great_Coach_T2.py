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

# 手动添加“伟大教练”信息
coach_data = [
    {"Name": "Lang Ping", "NOC": "CHN", "Sport": "Volleyball", "Intervention_Year": 2008},
    {"Name": "Lang Ping", "NOC": "USA", "Sport": "Volleyball", "Intervention_Year": 2016},
    {"Name": "Béla Károlyi", "NOC": "ROU", "Sport": "Gymnastics", "Intervention_Year": 1984},
    {"Name": "Béla Károlyi", "NOC": "USA", "Sport": "Gymnastics", "Intervention_Year": 2000},
    {"Name": "Wang Tongxiang", "NOC": "AUS", "Sport": "Diving", "Intervention_Year": 2004},
    {"Name": "Liu Guodong", "NOC": "SGP", "Sport": "Table Tennis", "Intervention_Year": 2008},
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


# 简化模型：移除不显著变量
formula = 'Treated_Medals ~ C(Sport)[T.Gymnastics] + C(Sport)[T.Volleyball] + C(Sport)[T.Table_Tennis]'

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
print("Final Regression Results:")
print(pd.DataFrame({
    'Variable': results['params'].index,
    'Coefficient (beta)': results['params'].values,
    'Std_Error': results['bse'].values,
    'P_Value': results['pvalues'].values,
    'CI_Lower': results['conf_int'].iloc[:, 0].values,
    'CI_Upper': results['conf_int'].iloc[:, 1].values
}))

print("\nFinal Additional Statistics:")
print(f"R-squared: {results['rsquared']}")
print(f"Adjusted R-squared: {results['rsquared_adj']}")
print(f"F-statistic: {results['fvalue']}, F p-value: {results['f_pvalue']}")
print(f"Residual Sum of Squares (SSR): {results['ssr']}")
print(f"Degrees of Freedom (Model): {results['df_model']}")
print(f"Degrees of Freedom (Residual): {results['df_resid']}")
print(f"Number of Observations: {results['nobs']}")
print(f"Number of Variables (k): {results['k']}")