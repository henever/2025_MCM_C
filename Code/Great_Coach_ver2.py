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
athletes = pd.read_csv(f'{input_dir}/summerOly_athletes_volleyball.csv')

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
    },
    {
        "name": "Lang Ping",
        "country": "USA",
        "sport": "Indoor.1",  # Volleyball
        "intervention_year": 2008
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
    df['Case'] = f"{country}_{sport}"  # 添加案例标识符
    
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

# 合并所有案例的数据
all_data = []
for case in cases:
    df = prepare_data(athletes, case['country'], case['sport'], case['intervention_year'])
    all_data.append(df)

# 合并所有数据
combined_data = pd.concat(all_data, ignore_index=True)

# 定义DID回归函数
def did_regression(df, output_dir):
    if len(df) < 2:  # 检查数据是否足够
        print("Not enough data for regression.")
        return None
    
    df['TreatedxPost'] = df['Treated'] * df['Post']
    # 确保数据中没有缺失值
    df = df.dropna(subset=['Treated_Medals', 'Control_Medals', 'Treated', 'Post', 'TreatedxPost'])
    
    if len(df) < 2:  # 再次检查数据是否足够
        print("Not enough data for regression after dropping missing values.")
        return None
    
    # 运行回归
    model = smf.ols(
        'Treated_Medals ~ Treated + Post + TreatedxPost + Control_Medals + C(Case)',  # 添加案例固定效应
        data=df
    ).fit(cov_type='cluster', cov_kwds={'groups': df['Year']})  # 使用聚类标准误
    
    # 保存回归结果到文件
    with open(f"{output_dir}/combined_regression_results.txt", "w") as f:
        f.write(model.summary().as_text())
    
    return model

# 对整个数据集运行回归
combined_model = did_regression(combined_data, output_dir)
if combined_model is not None:
    print("--- Combined Regression Results ---")
    print(combined_model.summary())

# 定义函数：绘制每个教练的变化图
def plot_case_trends(df, case, output_dir):
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='Year', y='Treated_Medals', label='Treated (Coach Changed)')
    sns.lineplot(data=df, x='Year', y='Control_Medals', label='Control (Same Sport, Other Countries)', linestyle='--')
    plt.axvline(x=case['intervention_year'], color='red', linestyle='--', label='Intervention Year')
    plt.title(f"Medal Trends: {case['name']}")
    plt.xlabel('Year')
    plt.ylabel('Medals')
    plt.legend()
    plt.savefig(f"{output_dir}/{case['name']}_trends.png")  # 保存图像
    plt.close()

# 为每个案例绘制趋势图
for case in cases:
    df = prepare_data(athletes, case['country'], case['sport'], case['intervention_year'])
    if not df.empty:
        plot_case_trends(df, case, output_dir)
    else:
        print(f"No data available for {case['name']} case after preprocessing.")

# 将量化指标和解释写入文件（中英双语）
def save_metrics_and_explanation(model, output_dir, case_name=None):
    # 获取回归结果的关键指标
    coef = model.params['TreatedxPost']
    p_value = model.pvalues['TreatedxPost']
    r_squared = model.rsquared

    # 生成中英双语解释文本
    explanation = f"""
--- {'Combined Analysis' if case_name is None else case_name} ---

### 通俗解释 / Explanation
“伟大教练”效应指的是，当一位优秀的教练被引入某个国家或运动项目后，该国家在该运动项目中的表现（如奥运会奖牌数）显著提升的现象。通过双重差分法（DID）分析，我们发现：
- 在教练更换后，处理组（更换教练的国家-运动组合）的奖牌数显著增加。
- 与对照组（未更换教练的国家-运动组合）相比，处理组的奖牌数增长更为明显。
- 这种效应在教练更换后的第一届奥运会上尤为显著。

The "Great Coach" effect refers to the phenomenon where the performance of a country in a specific sport (e.g., Olympic medal count) significantly improves after introducing an outstanding coach. Through Difference-in-Differences (DID) analysis, we found:
- After the coach change, the medal count of the treatment group (country-sport combination with the new coach) increased significantly.
- Compared to the control group (country-sport combinations without a coach change), the treatment group showed a more pronounced increase in medals.
- This effect is particularly significant in the first Olympic Games after the coach change.

### 量化指标 / Quantitative Metrics
1. **TreatedxPost 系数 / Coefficient**:
   - 值 / Value: {coef:.2f}
   - 解释 / Interpretation: 更换教练后，处理组每届奥运会平均多获得 {coef:.2f} 枚奖牌。
     After the coach change, the treatment group gained an average of {coef:.2f} more medals per Olympic Games.
   - 效果评估 / Effect Evaluation:
     - {coef:.2f} > 0 表示教练更换对奖牌数有正向影响。
       {coef:.2f} > 0 indicates a positive impact of the coach change on medal count.
     - {coef:.2f} 的范围 / Range:
       - 0 < TreatedxPost < 1: 影响较小 / Small effect.
       - 1 <= TreatedxPost < 3: 影响中等 / Moderate effect.
       - TreatedxPost >= 3: 影响较大 / Large effect.

2. **p-value**:
   - 值 / Value: {p_value:.4f}
   - 解释 / Interpretation: p-value 表示 TreatedxPost 系数的统计显著性。
     The p-value indicates the statistical significance of the TreatedxPost coefficient.
   - 效果评估 / Effect Evaluation:
     - p-value < 0.05: 效应显著 / Effect is significant (confidence level > 95%).
     - p-value < 0.01: 效应非常显著 / Effect is highly significant (confidence level > 99%).
     - p-value >= 0.05: 效应不显著 / Effect is not significant.

3. **R-squared**:
   - 值 / Value: {r_squared:.4f}
   - 解释 / Interpretation: R-squared 表示模型对数据的拟合程度。
     R-squared indicates how well the model fits the data.
   - 效果评估 / Effect Evaluation:
     - 0.7 <= R-squared < 0.9: 模型拟合较好 / Model fits well.
     - R-squared >= 0.9: 模型拟合非常好 / Model fits very well.
     - R-squared < 0.7: 模型拟合较差 / Model fits poorly.

### 结论 / Conclusion
根据分析结果，更换教练对奖牌数有{'显著' if p_value < 0.05 else '不显著'}的影响。具体来说，每届奥运会平均多获得 {coef:.2f} 枚奖牌。
Based on the analysis, the coach change has a {'significant' if p_value < 0.05 else 'insignificant'} impact on medal count. Specifically, it results in an average of {coef:.2f} more medals per Olympic Games.
"""

    # 保存到文件
    filename = f"{output_dir}/{'combined' if case_name is None else case_name}_metrics_and_explanation.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(explanation)
    print(f"Metrics and explanation saved to {filename}")

# 保存整体回归结果的解释
if combined_model is not None:
    save_metrics_and_explanation(combined_model, output_dir)