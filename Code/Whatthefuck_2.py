import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind
import os

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

# 绘制奖牌类型的分布图
plt.figure(figsize=(10, 6))
sns.countplot(
    x='Medal', 
    hue='Treated',  # 按 Treated 分组
    data=plot_data, 
    palette={0: 'blue', 1: 'red'}  # 为 Treated 列分配颜色
)
plt.xlabel('Medal Type')
plt.ylabel('Count')
plt.title('Medal Type Distribution: Treated vs Control Group')
plt.savefig(f"{output_dir}/medal_type_distribution.png")
plt.close()

# 运行事件研究回归模型
formula = 'Treated_Medals ~ Post_neg_2 + Post_neg_1 + Post_0 + Post_1 + Post_2 + Control_Medals + C(Case)'
model = smf.ols(formula, data=combined_data).fit(cov_type='cluster', cov_kwds={'groups': combined_data['Year']})

# 提取论文所需统计量
model_summary = {
    "Nobs": model.nobs,                  # 观测值数量
    "DF_Model": model.df_model,          # 模型自由度
    "DF_Resid": model.df_resid,          # 残差自由度
    "F_Statistic": model.fvalue,         # F统计量
    "F_PValue": model.f_pvalue,          # F检验p值
    "SSR": model.ssr,                    # 残差平方和
    "RSquared": model.rsquared,          # R²
    "RSquared_Adj": model.rsquared_adj,  # 调整后R²
}

# 回归系数详情
coeff_details = []
for param in model.params.index:
    if 'Post' in param:  # 仅提取时间虚拟变量系数
        coeff = {
            "Variable": param,
            "Coefficient": model.params[param],
            "Std_Error": model.bse[param],
            "CI_Lower": model.conf_int().loc[param, 0],
            "CI_Upper": model.conf_int().loc[param, 1],
            "T_Stat": model.tvalues[param],
            "P_Value": model.pvalues[param]
        }
        coeff_details.append(coeff)

# 转换为DataFrame便于输出
coeff_df = pd.DataFrame(coeff_details)

# 输出结果到文件
with open(f"{output_dir}/regression_results.txt", "w") as f:
    # 写入模型总体信息
    f.write("=== Model Summary ===\n")
    for key, value in model_summary.items():
        f.write(f"{key}: {value:.4f}\n")
    
    # 写入系数详情
    f.write("\n=== Coefficient Details ===\n")
    f.write(coeff_df.to_string(index=False))

# 保存系数表为CSV（用于论文表格）
coeff_df.to_csv(f"{output_dir}/coefficient_table.csv", index=False)