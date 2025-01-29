import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LassoCV
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os
# 设置输入和输出目录
input_dir = "F:/MCM/2025COMAP/Data"
output_dir = "F:/MCM/2025COMAP/Results"
os.makedirs(output_dir, exist_ok=True)

# 1. 加载数据
athletes = pd.read_csv(f'{input_dir}/summerOly_athletes.csv')
host = pd.read_csv(f'{input_dir}/summerOly_hosts.csv')

# 2. 特征工程：创建新变量
# 创建"NewEventParticipation"表示首次参赛项目
athletes['NewEventParticipation'] = athletes.groupby(['NOC', 'Sport'])['Year'].transform('min') == athletes['Year']
athletes['NewEventParticipation'] = athletes['NewEventParticipation'].astype(int)

# 3. 创建合并数据集：将运动员数据和主办国数据结合
athletes['Host'] = athletes['Year'].map(host.set_index('Year')['Host'])  # 将主办国映射到运动员数据

# 4. 选择特征并进行模型训练
# 选择可能影响奖牌数的特征：参赛次数、新项目、主办国影响
athletes['Medal_achieved'] = athletes['Medal'].apply(lambda x: 1 if x != 'No medal' else 0)  # 1为奖牌，0为无奖牌
X = athletes[['NewEventParticipation', 'Host']]
y = athletes['Medal_achieved']

# 对主办国进行数值化处理
X = pd.get_dummies(X, columns=['Host'], drop_first=True)

# 5. 标准化数据
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 6. 拆分数据集为训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# 7. 训练Lasso回归模型
lasso = LassoCV(cv=5, random_state=42)
lasso.fit(X_train, y_train)

# 8. 输出模型系数
print("Lasso Coefficients:", lasso.coef_)
print("Lasso Intercept:", lasso.intercept_)

# 9. 模型预测和效果评估
y_pred = lasso.predict(X_test)

# 10. 输出建议：基于预测的奖牌数变化给出排名
athletes['Predicted_Medal_Change'] = lasso.predict(scaler.transform(pd.get_dummies(athletes[['NewEventParticipation', 'Host']], columns=['Host'], drop_first=True)))
athletes_sorted = athletes.groupby(['NOC', 'Sport']).agg({'Predicted_Medal_Change': 'mean'}).reset_index()
athletes_sorted = athletes_sorted.sort_values(by='Predicted_Medal_Change', ascending=False)

# 11. 输出排名前几个的建议（按照预测的奖牌变化）
top_suggestions = athletes_sorted.head(10)
print("Top 10 Suggestions for Coach Introduction (Sorted by Predicted Medal Change):")
print(top_suggestions)

# 12. 绘制预测结果图
plt.figure(figsize=(10, 6))
sns.barplot(x='Predicted_Medal_Change', y='NOC', data=top_suggestions, palette='Blues_d')
plt.title("Top 10 Countries and Sports Predicted to Gain the Most Medals (Coach Introduction)")
plt.xlabel('Predicted Medal Change')
plt.ylabel('Country Code')
plt.savefig(f"{output_dir}/top_10_suggestions.png")
plt.show()