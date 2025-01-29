import pandas as pd
import joblib
import numpy as np

# 1. 加载模型和标准化器
model_path = "F:/MCM/2025COMAP/Data/random_forest_model.pkl"
scaler_path = "F:/MCM/2025COMAP/Data/scaler.pkl"

model = joblib.load(model_path)  # 加载模型
scaler = joblib.load(scaler_path)  # 加载标准化器

# 2. 读取新数据
new_data_path = "F:/MCM/2025COMAP/Data/team_medals_summary.csv"  # 新数据路径
new_data = pd.read_csv(new_data_path)

# 确保新数据的特征与训练时一致
required_features = ["TOPSIS_Score_Sum", "Host", "Bronze_Medals", "Gold_Medals", "Silver_Medals", 
                     "Gold_Ratio", "Silver_Ratio", "Bronze_Ratio"]
X_new = new_data[required_features]

# 3. 对新数据进行标准化
X_new_scaled = scaler.transform(X_new)  # 使用加载的标准化器进行标准化

# 4. 进行预测
predictions = model.predict(X_new_scaled)  # 预测结果是一个二维数组

# 5. 提取目标变量的预测结果，并四舍五入
# 假设模型的输出顺序是 ["Bronze Medals", "Gold Medals", "Silver Medals", "Total Medals"]
new_data["Predicted_Bronze_Medals"] = np.round(predictions[:, 0])  # 第一列是 Bronze Medals，四舍五入
new_data["Predicted_Gold_Medals"] = np.round(predictions[:, 1])    # 第二列是 Gold Medals，四舍五入
new_data["Predicted_Silver_Medals"] = np.round(predictions[:, 2])  # 第三列是 Silver Medals，四舍五入
# new_data["Predicted_Total_Medals"] = np.round(predictions[:, 3])   # 第四列是 Total Medals，四舍五入

# 6. 保存预测结果
output_path = "F:/MCM/2025COMAP/Data/predictions.csv"
new_data.to_csv(output_path, index=False)

print(f"预测完成，结果已保存至：{output_path}")
print("预测结果：")
print(new_data[["NOC", "Sport", "Predicted_Gold_Medals"]])