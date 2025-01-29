import pandas as pd

# 读取预测结果文件
predictions_path = "F:/MCM/2025COMAP/Data/predictions.csv"
predictions = pd.read_csv(predictions_path)

# 按国家分组，计算每个国家的奖牌总数
medal_totals = predictions.groupby("NOC").agg({
    "Predicted_Gold_Medals": "sum",
    "Predicted_Silver_Medals": "sum",
    "Predicted_Bronze_Medals": "sum"
}).reset_index()

# 计算总奖牌数
medal_totals["Total"] = (
    medal_totals["Predicted_Gold_Medals"] +
    medal_totals["Predicted_Silver_Medals"] +
    medal_totals["Predicted_Bronze_Medals"]
)

# 重命名列
medal_totals.rename(columns={
    "Predicted_Gold_Medals": "Gold",
    "Predicted_Silver_Medals": "Silver",
    "Predicted_Bronze_Medals": "Bronze"
}, inplace=True)

# 按总奖牌数（降序）、金牌数（降序）、银牌数（降序）、铜牌数（降序）排序
medal_totals = medal_totals.sort_values(
    by=["Total", "Gold", "Silver", "Bronze"],
    ascending=[False, False, False, False]
).reset_index(drop=True)

# 保存奖牌总榜
medal_rankings_path = "F:/MCM/2025COMAP/Data/medal_rankings.csv"
medal_totals.to_csv(medal_rankings_path, index=False)

print(f"奖牌总榜已保存至：{medal_rankings_path}")
print("奖牌总榜：")
print(medal_totals)