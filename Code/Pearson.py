import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# 读取菜品销售量数据
filepath = 'C:/Users/14210/Desktop/机器学习代码/data/cor.xlsx'
cor = pd.read_excel(filepath) 
# 计算相关系数矩阵，包含了任意两个菜品间的相关系数
print('5种菜品销售量的相关系数矩阵为：\n', cor.corr())

# 绘制相关性热力图
plt.subplots(figsize=(8, 8))  # 设置画面大小 
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号 
sns.heatmap(cor.corr(), annot=True, vmax=1, square=True, cmap="Blues") 
plt.title('相关性热力图')
plt.show()

