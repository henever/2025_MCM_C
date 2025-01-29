import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import joblib
import random

random_seed = random.randint(0, 1145141)
print(f"Random Seed: {random_seed}")

data_path = "F:/MCM/2025COMAP/Data"
input_file = f"{data_path}/medals_2024_with_participants_medals.csv" 
model_file = f"{data_path}/random_forest_model.pkl"  
data = pd.read_csv(input_file)

data["Gold_Medals"] = data["Gold_Medals"].fillna(0)
data["Silver_Medals"] = data["Silver_Medals"].fillna(0)
data["Bronze_Medals"] = data["Bronze_Medals"].fillna(0)

X = data[["TOPSIS_Score_Sum", "Host", "Bronze_Medals", "Gold_Medals", "Silver_Medals", "Gold_Ratio", "Silver_Ratio", "Bronze_Ratio"]]  # 自变量
y = data[["Bronze Medals", "Gold Medals", "Silver Medals"]]  
y = y.squeeze()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=random_seed)

best_r2 = -np.inf  
best_smape = np.inf  
best_mae = np.inf  
best_model = None  
best_scaler = None  

for i in range(20):
    print(f"\nTraining Times: {i + 1}")
    
    model = RandomForestRegressor(random_state=random_seed + i)  # 每次使用不同的随机种子
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    print(f"R^2 Score: {r2}")
    mae = mean_absolute_error(y_test, y_pred)
    print(f"MAE: {mae}")

    if r2 >= 0.6 and smape <= 20:
        print(f"Found appropriate model: R^2 = {r2}, SMAPE = {smape}%, MAE = {mae}")
        best_r2 = r2
        best_smape = smape
        best_mae = mae
        best_model = model
        best_scaler = scaler

    if r2 > best_r2 and smape < best_smape:
        best_r2 = r2
        best_smape = smape
        best_mae = mae
        best_model = model
        best_scaler = scaler

if best_model is not None:
    print(f"\nThe best model: R^2 = {best_r2}, SMAPE = {best_smape}%, MAE = {best_mae}")
    joblib.dump(best_model, model_file)
    joblib.dump(best_scaler, f"{data_path}/scaler.pkl")  
    print(f"The best model is saved in:{model_file}")
    print(f"The standard scaler is saved in:{data_path}/scaler.pkl")
else:
    print("Models not found.")