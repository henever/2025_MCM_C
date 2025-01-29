import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 设置输入和输出目录
input_dir = "F:/MCM/2025COMAP/Data"
output_dir = "F:/MCM/2025COMAP/Results"
os.makedirs(output_dir, exist_ok=True)

# 加载数据
athletes = pd.read_csv(f'{input_dir}/summerOly_athletes.csv')

# 使用你提供的 cases 列表定义优秀教练的案例
cases = [
    {
        "name": "Wang Tongxiang (Diving)",
        "NOC": "AUS",
        "sport": "Diving",
        "intervention_year": 2004
    },
    {
        "name": "Liu Guodong (Table Tennis)",
        "NOC": "SGP",
        "sport": "Table Tennis",
        "intervention_year": 2008
    },
    {
        "name": "Sandro Damilano (Race Walking)",
        "NOC": "CHN",
        "sport": "Athletics",  # 竞走属于田径大项
        "intervention_year": 2012
    },
    {
        "name": "Lang Ping",
        "NOC": "USA",
        "sport": "Indoor.1",  # Volleyball
        "intervention_year": 2008
    }
]

# 将 cases 转换为 DataFrame
coaches = pd.DataFrame(cases)
coaches.rename(columns={"name": "Name", "NOC": "NOC", "sport": "Sport", "intervention_year": "Intervention_Year"}, inplace=True)

# 合并运动员和教练数据
athletes = pd.merge(athletes, coaches, on=['NOC', 'Sport'], how='left')

# 定义函数：准备数据
def prepare_data(athletes, NOC, sport, intervention_year, window=8):
    # 提取处理组数据
    treated = athletes[
        (athletes['NOC'] == NOC) &
        (athletes['Sport'] == sport) &
        (athletes['Medal'] != 'No medal')
    ].groupby('Year')['Medal'].count().reset_index(name='Treated_Medals')
    
    # 提取对照组数据（同一运动，其他国家）
    control = athletes[
        (athletes['NOC'] != NOC) &
        (athletes['Sport'] == sport) &
        (athletes['Medal'] != 'No medal')
    ].groupby('Year')['Medal'].count().reset_index(name='Control_Medals')
    
    # 合并数据并标记干预前后
    df = pd.merge(treated, control, on='Year', how='outer')
    df['Post'] = (df['Year'] >= intervention_year).astype(int)
    df['Treated'] = 1  # 处理组为1
    df['Case'] = f"{NOC}_{sport}"  # 添加案例标识符
    df['Intervention_Year'] = intervention_year  # 添加干预年份
    
    # 填充缺失值（若某年无数据，用前后均值填充）
    df = df.sort_values('Year').infer_objects()  # 修复数据类型
    df = df.interpolate(method='linear', limit_direction='both')
    
    # 删除仍存在缺失值的行
    df = df.dropna(subset=['Treated_Medals', 'Control_Medals'])
    
    # 选择时间窗口（干预前后各window年）
    df = df[
        (df['Year'] >= intervention_year - window) &
        (df['Year'] <= intervention_year + window)
    ]
    return df

# 合并所有案例的数据
all_data = []
for case in cases:
    df = prepare_data(athletes, case['NOC'], case['sport'], case['intervention_year'])
    all_data.append(df)

combined_data = pd.concat(all_data, ignore_index=True)

# 检查数据量和缺失值
print("Number of observations:", len(combined_data))
print("Missing values:\n", combined_data.isnull().sum())

# 填充缺失值
combined_data = combined_data.fillna(0)

# 仅选择数值列
numeric_columns = combined_data.select_dtypes(include=[np.number]).columns
print("Numeric columns:", numeric_columns)

# 计算相关性矩阵
corr_matrix = combined_data[numeric_columns].corr()
print("Correlation matrix:\n", corr_matrix)


# 定义事件研究回归函数
def event_study_regression(df, output_dir):
    # 创建时间交互项（干预前后各两届）
    df['Event_Year'] = df['Year'] - df['Intervention_Year']
    df = df[(df['Event_Year'] >= -2) & (df['Event_Year'] <= 2)]  # 限制事件窗口
    
    # 生成时间虚拟变量（避免特殊字符）
    for k in range(-2, 3):
        var_name = f'Post_{k}' if k >= 0 else f'Post_neg_{-k}'
        df.loc[:, var_name] = (df['Event_Year'] == k).astype(int)
    
    # 运行回归
    formula = 'Treated_Medals ~ '
    formula += ' + '.join([f'Post_neg_{-k}' if k < 0 else f'Post_{k}' for k in range(-2, 3)]) + ' + Control_Medals + C(Case)'
    model = smf.ols(formula, data=df).fit(cov_type='cluster', cov_kwds={'groups': df['Year']})
    
    # 保存结果
    with open(f"{output_dir}/event_study_results.txt", "w") as f:
        f.write(model.summary().as_text())
    
    return model

# 运行事件研究回归
event_study_model = event_study_regression(combined_data, output_dir)

# 定义函数：绘制事件研究动态效应图
def plot_event_study(model, output_dir):
    coefs = model.params.filter(like='Post_')
    ci = model.conf_int().filter(like='Post_')
    
    # 检查 coefs 和 ci 的维度
    print("Coefficients shape:", coefs.shape)
    print("Confidence intervals shape:", ci.shape)
    
    # 确保 ci 的结构正确
    if ci.shape[1] != 2:
        raise ValueError("Confidence intervals must have exactly 2 columns (lower and upper bounds).")
    
    # 修正绘图代码
    plt.figure(figsize=(10, 6))
    plt.errorbar(x=range(-2, 3), y=coefs, yerr=[coefs - ci.iloc[:, 0], ci.iloc[:, 1] - coefs], fmt='o')
    plt.axhline(0, color='red', linestyle='--')
    plt.xticks(range(-2, 3), labels=['t-2', 't-1', 't=0 (Intervention)', 't+1', 't+2'])
    plt.xlabel('Event Time (Olympic Games)')
    plt.ylabel('Effect on Medals')
    plt.title('Dynamic Effects of Coach Intervention (Event Study)')
    plt.savefig(f"{output_dir}/event_study_plot.png")
    plt.close()

# 绘制事件研究图
if event_study_model is not None:
    plot_event_study(event_study_model, output_dir)

# 定义函数：推荐投资方向
def recommend_investment(model, output_dir):
    # 提取回归系数
    coefs = model.params.filter(like='Post_')
    
    # 找到影响最大的项目和案例
    max_impact_case = coefs.idxmax()
    max_impact_value = coefs.max()
    
    # 保存推荐结果
    with open(f"{output_dir}/investment_recommendations.txt", "w") as f:
        f.write(f"Based on the event study analysis, the case with the highest impact is:\n")
        f.write(f"Case: {max_impact_case}\n")
        f.write(f"Estimated Impact: {max_impact_value}\n")
        f.write("\nRecommendation: Invest in a great coach for this case to maximize medal counts.")

# 生成投资推荐
if event_study_model is not None:
    recommend_investment(event_study_model, output_dir)