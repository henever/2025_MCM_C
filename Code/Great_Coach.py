import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 设置输入和输出目录
input_dir = "F:/MCM/2025COMAP/Data"
output_dir = "F:/MCM/2025COMAP/Results"
os.makedirs(output_dir, exist_ok=True)  # 创建输出目录（如果不存在）

# 加载数据
athletes = pd.read_csv(f'{input_dir}/summerOly_athletes.csv')

# 案例定义
cases = [
    {
        "name": "Wang Tongxiang (Diving)",
        "country": "AUS",
        "sport": "Diving",
        "intervention_year": 2004
    },
    {
        "name": "Liu Guodong (Table Tennis)",
        "country": "SGP",
        "sport": "Table Tennis",
        "intervention_year": 2008
    },
    {
        "name": "Sandro Damilano (Race Walking)",
        "country": "CHN",
        "sport": "Athletics",  # 竞走属于田径大项
        "intervention_year": 2012
    }
]

# 定义通用函数：提取国家-运动-年份奖牌数
def prepare_data(athletes, country, sport, intervention_year, window=16):
    # 提取处理组数据
    treated = athletes[
        (athletes['NOC'] == country) &
        (athletes['Sport'] == sport) &
        (athletes['Medal'] != 'No medal')  # 只保留获奖记录
    ].groupby('Year')['Medal'].count().reset_index(name='Treated_Medals')
    
    # 提取对照组数据（同一运动，其他国家）
    control = athletes[
        (athletes['NOC'] != country) &
        (athletes['Sport'] == sport) &
        (athletes['Medal'] != 'No medal')
    ].groupby('Year')['Medal'].count().reset_index(name='Control_Medals')
    
    # 合并数据并标记干预前后
    df = pd.merge(treated, control, on='Year', how='outer')
    df['Post'] = (df['Year'] >= intervention_year).astype(int)
    df['Treated'] = 1  # 处理组为1
    
    # 填充缺失值（若某年无数据，用前后均值填充）
    df = df.sort_values('Year').interpolate(method='linear', limit_direction='both')
    
    # 删除仍存在缺失值的行
    df = df.dropna(subset=['Treated_Medals', 'Control_Medals'])
    
    # 选择时间窗口（干预前后各window年）
    df = df[
        (df['Year'] >= intervention_year - window) &
        (df['Year'] <= intervention_year + window)
    ]
    return df

# 定义DID回归函数
def did_regression(df, case_name, output_dir):
    if len(df) < 2:  # 检查数据是否足够
        print(f"--- {case_name} ---")
        print("Not enough data for regression.")
        return None
    
    df['TreatedxPost'] = df['Treated'] * df['Post']
    # 确保数据中没有缺失值
    df = df.dropna(subset=['Treated_Medals', 'Control_Medals', 'Treated', 'Post', 'TreatedxPost'])
    
    if len(df) < 2:  # 再次检查数据是否足够
        print(f"--- {case_name} ---")
        print("Not enough data for regression after dropping missing values.")
        return None
    
    # 运行回归
    model = smf.ols(
        'Treated_Medals ~ Treated + Post + TreatedxPost + Control_Medals',
        data=df
    ).fit()
    
    # 保存回归结果到文件
    with open(f"{output_dir}/{case_name}_regression_results.txt", "w") as f:
        f.write(model.summary().as_text())
    
    return model

# 对每个案例运行回归并保存结果
results = {}
for case in cases:
    df = prepare_data(athletes, case['country'], case['sport'], case['intervention_year'])
    model = did_regression(df, case['name'], output_dir)
    if model is not None:
        results[case['name']] = model
        print(f"--- {case['name']} ---")
        print(model.summary())

# 绘制处理组与对照组趋势对比
def plot_trends(df, case, output_dir):
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='Year', y='Treated_Medals', label='Treated (Coach Changed)')
    sns.lineplot(data=df, x='Year', y='Control_Medals', label='Control (Same Sport, Other Countries)')
    plt.axvline(x=case['intervention_year'], color='red', linestyle='--', label='Intervention Year')
    plt.title(f"Medal Trends: {case['name']}")
    plt.ylabel('Medals')
    plt.legend()
    plt.savefig(f"{output_dir}/{case['name']}_trends.png")  # 保存图像
    plt.close()

# 示例：王同祥案例趋势图
for i in range(len(cases)):
    case = cases[i]
    df_loop = prepare_data(athletes, case['country'], case['sport'], case['intervention_year'])
    if not df_loop.empty:
        plot_trends(df_loop, case, output_dir)
    else:
        print(f"No data available for {case[i].name} case after preprocessing.")

# 根据DID系数排序推荐
recommendations = []
for case_name, model in results.items():
    coef = model.params['TreatedxPost']
    p_value = model.pvalues['TreatedxPost']
    if coef > 0 and p_value < 0.05:
        # 解析案例信息
        sport = case_name.split('(')[-1].replace(')', '').strip()
        country = next(c['country'] for c in cases if c['name'] == case_name)
        # 推荐逻辑：选择同一运动内当前奖牌数低的国家
        current_medals = athletes[
            (athletes['Year'] == 2020) &  # 假设最新数据为2020年
            (athletes['Sport'] == sport) &
            (athletes['Medal'] != 'No medal')
        ].groupby('NOC')['Medal'].count().reset_index(name='Medals')
        # 排除已处理国家，选择奖牌最少的国家
        candidates = current_medals[
            (current_medals['NOC'] != country) &
            (current_medals['Medals'] < current_medals['Medals'].median())
        ]
        if not candidates.empty:
            target = candidates.nsmallest(1, 'Medals')['NOC'].values[0]
            recommendations.append({
                "Sport": sport,
                "Current Low-Performance Country": target,
                "Expected Medal Increase per Olympics": round(coef, 1)
            })

# 输出推荐结果到文件
if recommendations:
    recommendations_df = pd.DataFrame(recommendations)
    recommendations_df.to_csv(f"{output_dir}/recommendations.csv", index=False)
    print("Recommended Investments in Coaches:")
    print(recommendations_df)
else:
    print("No significant cases found for recommendations.")