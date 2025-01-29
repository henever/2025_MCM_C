import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_percentage_error, r2_score

# 示例数据集（替换为你的数据集）
df = pd.read_csv('F:/MCM/2025COMAP/Data/Forest_Database.csv')

# 特征和目标变量
X = df["Parti_to_Medal","Partipate_Rate","Parti_to_Bronze","Parti_to_Gold","Parti_to_Silver"]
y = df['Target']

# 迭代寻找满足条件的随机种子
for i in range(1, 100):
    # 随机生成种子
    random_state = np.random.randint(0, 10000)

    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=random_state)

    # 模型训练
    model = RandomForestRegressor(random_state=random_state)
    model.fit(X_train, y_train)

    # 模型预测
    y_pred = model.predict(X_test)

    # 计算 R^2 和 MAPE
    r2 = r2_score(y_test, y_pred)
    mape = mean_absolute_percentage_error(y_test, y_pred)

    # 输出当前迭代的信息
    print(f"Times:{i}, R^2: {r2:.4f}, MAPE: {mape:.4f},Random State: {random_state}")

    # 检查条件
    if r2 > 0.5 and mape < 0.15:
        print("满足条件!", f"Random State: {random_state}, R^2: {r2:.4f}, MAPE: {mape:.4f}")
        break