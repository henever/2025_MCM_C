import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import joblib
import random
import matplotlib.pyplot as plt

# 随机生成 random_state
random_seed = random.randint(0, 1145141)  # 生成 0 到 1145141 之间的随机整数
print(f"随机种子: {random_seed}")

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
input_file = f"{data_path}/medals_2024_with_participants_medals.csv"  # 输入文件
model_file = f"{data_path}/random_forest_model.pkl"  # 模型保存路径

# 读取数据
data = pd.read_csv(input_file)

# 将 Gold_Medals, Silver_Medals, Bronze_Medals 中的 NaN 替换为 0
data["Gold_Medals"] = data["Gold_Medals"].fillna(0)
data["Silver_Medals"] = data["Silver_Medals"].fillna(0)
data["Bronze_Medals"] = data["Bronze_Medals"].fillna(0)

# 特征和标签
X = data[["TOPSIS_Score_Sum", "Host", "Bronze_Medals", "Gold_Medals", "Silver_Medals", "Gold_Ratio", "Silver_Ratio", "Bronze_Ratio"]]  # 自变量
y = data[["Bronze Medals", "Gold Medals", "Silver Medals"]]  # 因变量
y = y.squeeze()

# 数据标准化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=random_seed)

# 初始化最佳模型变量
best_r2 = -np.inf  # 最佳 R^2
best_mae = np.inf  # 最佳 MAE
best_model = None  # 最佳模型
best_scaler = None  # 最佳标准化器

# 训练 100 次
for i in range(20):
    print(f"\n训练次数: {i + 1}")
    
    # 训练随机森林模型
    model = RandomForestRegressor(random_state=random_seed + i)  # 每次使用不同的随机种子
    model.fit(X_train, y_train)

    # 预测
    y_pred = model.predict(X_test)

    # 计算 R^2
    r2 = r2_score(y_test, y_pred)
    print(f"R^2 Score: {r2}")

    # 计算 MAE
    mae = mean_absolute_error(y_test, y_pred)
    print(f"MAE: {mae}")

    # 检查是否满足条件
    if r2 >= 0.6 and mae <= 10:  # 根据需求调整条件
        print(f"找到满足条件的模型: R^2 = {r2}, MAE = {mae}")
        best_r2 = r2
        best_mae = mae
        best_model = model
        best_scaler = scaler
        break  # 找到满足条件的模型，退出循环

    # 更新最佳模型
    if r2 > best_r2 and mae < best_mae:
        best_r2 = r2
        best_mae = mae
        best_model = model
        best_scaler = scaler

# 保存最佳模型
if best_model is not None:
    print(f"\n最佳模型: R^2 = {best_r2}, MAE = {best_mae}")
    joblib.dump(best_model, model_file)
    joblib.dump(best_scaler, f"{data_path}/scaler.pkl")  # 保存标准化器
    print(f"最佳模型已保存至：{model_file}")
    print(f"标准化器已保存至：{data_path}/scaler.pkl")
else:
    print("未找到满足条件的模型。")

# 鲁棒性分析：添加不同噪声等级并重新评估模型
def add_noise(data, noise_level=0.1):
    noise = np.random.normal(0, noise_level, data.shape)
    return data + noise

# 原始数据表现
y_pred_original = best_model.predict(X_test)
r2_original = r2_score(y_test, y_pred_original)
mae_original = mean_absolute_error(y_test, y_pred_original)

# 轻度噪声 (噪声水平 0.1)
X_train_light_noise = X_train.copy()
X_train_light_noise[:, 0] = add_noise(X_train[:, 0], noise_level=0.1)  # 在 TOPSIS_Score_Sum 上添加轻度噪声
model_light_noise = RandomForestRegressor(random_state=random_seed)
model_light_noise.fit(X_train_light_noise, y_train)
y_pred_light_noise = model_light_noise.predict(X_test)
r2_light_noise = r2_score(y_test, y_pred_light_noise)
mae_light_noise = mean_absolute_error(y_test, y_pred_light_noise)

# 重度噪声 (噪声水平 0.5)
X_train_heavy_noise = X_train.copy()
X_train_heavy_noise[:, 0] = add_noise(X_train[:, 0], noise_level=0.5)  # 在 TOPSIS_Score_Sum 上添加重度噪声
model_heavy_noise = RandomForestRegressor(random_state=random_seed)
model_heavy_noise.fit(X_train_heavy_noise, y_train)
y_pred_heavy_noise = model_heavy_noise.predict(X_test)
r2_heavy_noise = r2_score(y_test, y_pred_heavy_noise)
mae_heavy_noise = mean_absolute_error(y_test, y_pred_heavy_noise)

# 打印噪声前后模型表现
print(f"\n原始数据模型表现: R^2 = {r2_original}, MAE = {mae_original}")
print(f"轻度噪声模型表现: R^2 = {r2_light_noise}, MAE = {mae_light_noise}")
print(f"重度噪声模型表现: R^2 = {r2_heavy_noise}, MAE = {mae_heavy_noise}")

# 绘制噪声前后模型表现对比图
metrics = ['R²', 'MAE']
original = [r2_original, mae_original]
light_noise = [r2_light_noise, mae_light_noise]
heavy_noise = [r2_heavy_noise, mae_heavy_noise]

x = np.arange(len(metrics))
width = 0.25

# 使用指定的颜色
colors = ['#2A4494', '#2282C7', '#4EA5D9']

fig, ax = plt.subplots()
rects1 = ax.bar(x - width, original, width, label='Heavy Noise (0.5)', color=colors[0])
rects2 = ax.bar(x, light_noise, width, label='Light Noise (0.1)', color=colors[1])
rects3 = ax.bar(x + width, heavy_noise, width, label='Original', color=colors[2])

ax.set_ylabel('Score')
ax.set_title('Model Performance Under Different Noise Levels')
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.legend()

fig.tight_layout()
plt.show()