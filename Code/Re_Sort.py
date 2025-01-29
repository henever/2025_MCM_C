import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
medal_ranking_file = f"{data_path}/medal_rankings_2028.csv"  # 输入文件
output_file = f"{data_path}/medal_rankings_2028_sorted.csv"  # 输出文件

# 读取数据
medal_ranking = pd.read_csv(medal_ranking_file)

# 计算总奖牌数（如果总奖牌数列不存在）
if "Total" not in medal_ranking.columns:
    medal_ranking["Total"] = medal_ranking["Gold"] + medal_ranking["Silver"] + medal_ranking["Bronze"]

# 按总奖牌数（降序）、金牌数（降序）、银牌数（降序）、铜牌数（降序）排序
medal_ranking_sorted = medal_ranking.sort_values(
    by=["Total", "Gold", "Silver", "Bronze"],
    ascending=[False, False, False, False]
).reset_index(drop=True)

# 保存排序后的结果
medal_ranking_sorted.to_csv(output_file, index=False)

print(f"排序后的奖牌榜已保存至：{output_file}")
print("排序后的奖牌榜：")
print(medal_ranking_sorted)