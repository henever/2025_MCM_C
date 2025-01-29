import pandas as pd
import statsmodels.api as sm

# 文件路径
file_path = "F:/MCM/2025COMAP/Data"
output_path = "F:/MCM/2025COMAP/Results"  # 设置保存路径

# 加载数据
athletes = pd.read_csv(f'{file_path}/summerOly_athletes.csv')
hosts = pd.read_csv(f'{file_path}/summerOly_hosts.csv')
programs = pd.read_csv(f'{file_path}/yearly_sport.csv')

# 将A表格从宽格式转换为长格式（Year, Sport, EventCount）
programs_long = programs.melt(
    id_vars="Year",
    var_name="Sport",
    value_name="EventCount"
)

# 标记新增项目：首次出现的年份标记为1
programs_long["NewEvent"] = programs_long.groupby("Sport")["Year"].transform(
    lambda x: (x == x.min()).astype(int)
)

# 标记东道国
hosts["Host_NOC"] = hosts["Host"]  # 直接使用三字母代码
athletes = pd.merge(athletes, hosts, on="Year", how="left")  # 按年份合并主办国信息
athletes["Host"] = (athletes["NOC"] == athletes["Host_NOC"]).astype(int)  # 标记是否为东道国

# 过滤掉 No medal 的记录
athletes_with_medals = athletes[athletes["Medal"] != "No medal"]

# 按国家-年份汇总总奖牌数
medal_counts = (
    athletes_with_medals.groupby(["NOC", "Year"])["Medal"]
    .count()  # 计算每个国家在每届奥运会上的总奖牌数
    .reset_index(name="Total")
)

# 计算每个国家的历史总奖牌数
historical_medals = medal_counts.groupby("NOC")["Total"].sum().reset_index(name="HistoricalTotal")

# 过滤掉历史上从未获得过奖牌的国家
countries_with_medals = historical_medals[historical_medals["HistoricalTotal"] > 0]["NOC"]
medal_counts = medal_counts[medal_counts["NOC"].isin(countries_with_medals)]

# 合并新增项目标记（按年份）
medal_counts = pd.merge(
    medal_counts,
    programs_long[["Year", "NewEvent"]].drop_duplicates(),
    on="Year",
    how="left"
)

# 确保 Host 列被正确传递
medal_counts = pd.merge(
    medal_counts,
    athletes[["NOC", "Year", "Host"]].drop_duplicates(),
    on=["NOC", "Year"],
    how="left"
)

# 处理缺失值
medal_counts["Host"] = medal_counts["Host"].fillna(0)
medal_counts["NewEvent"] = medal_counts["NewEvent"].fillna(0)

# 添加国家固定效应和年份固定效应
medal_counts["NOC"] = medal_counts["NOC"].astype("category")
medal_counts["Year"] = medal_counts["Year"].astype("category")

# 检查数据
print(medal_counts.head())
print(medal_counts.isnull().sum())

# 构建回归模型
model = sm.OLS.from_formula(
    "Total ~ Host + NewEvent + Host:NewEvent + C(NOC) + C(Year)",
    data=medal_counts
).fit()

# 输出回归结果
print(model.summary())

# 提取 Host 的 β 系数和 P 值
coefficients = model.params
p_values = model.pvalues

host_coefficient = coefficients["Host"]
host_p_value = p_values["Host"]

# 输出 Host 的 β 系数和 P 值
print(f"Host 的 β 系数: {host_coefficient:.4f}")
print(f"Host 的 P 值: {host_p_value:.4f}")

# 判断显著性
if host_p_value < 0.05:
    print("Host 的系数显著，东道国有显著优势。")
else:
    print("Host 的系数不显著，东道国没有显著优势。")

# 提取 Host:NewEvent 的 β 系数和 P 值
host_new_event_coefficient = coefficients["Host:NewEvent"]
host_new_event_p_value = p_values["Host:NewEvent"]

# 输出 Host:NewEvent 的 β 系数和 P 值
print(f"Host:NewEvent 的 β 系数: {host_new_event_coefficient:.4f}")
print(f"Host:NewEvent 的 P 值: {host_new_event_p_value:.4f}")

# 判断显著性
if host_new_event_p_value < 0.05:
    print("Host:NewEvent 的系数显著，东道国在新增项目上有显著优势。")
else:
    print("Host:NewEvent 的系数不显著，东道国在新增项目上没有显著优势。")

# 保存结果到文件
# 保存训练集表格（medal_counts）
medal_counts.to_csv(f'{output_path}/medal_counts.csv', index=False)

# 保存回归结果（summary）到文本文件
with open(f'{output_path}/regression_results.txt', 'w') as f:
    f.write(model.summary().as_text())

# 保存系数和 P 值到 CSV 文件
results_df = pd.DataFrame({
    'Variable': coefficients.index,
    'Coefficient': coefficients.values,
    'P-value': p_values.values
})
results_df.to_csv(f'{output_path}/coefficients_and_pvalues.csv', index=False)

# 保存 Host 的系数和 P 值到单独的文件
host_results = pd.DataFrame({
    'Variable': ['Host'],
    'Coefficient': [host_coefficient],
    'P-value': [host_p_value]
})
host_results.to_csv(f'{output_path}/host_coefficient_and_pvalue.csv', index=False)

print(f"所有结果已保存到 {output_path} 目录中。")