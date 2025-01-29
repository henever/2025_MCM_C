import pandas as pd

# 数据路径
data_path = "F:/MCM/2025COMAP/Data"
input_file = f"{data_path}/Deleta_Empty_Birthday_Athlete.csv"  # 请替换为你的文件名
output_file = f"{data_path}/Highlighted_Data.xlsx"  # 保存为 Excel 文件以便显示颜色

# 读取数据
data = pd.read_csv(input_file)

# 定义一个函数，用于标记 Birth_Year 为空的单元格
def highlight_missing_birthyear(val):
    """
    如果 Birth_Year 为空，则标记为黄色背景，并设置文字颜色为黑色。
    """
    if pd.isna(val):  # 如果值为空
        return 'background-color: yellow; color: black'  # 黄色背景，黑色文字
    return ''  # 否则不设置样式

# 对 Birth_Year 列应用颜色标记
styled_data = data.style.applymap(highlight_missing_birthyear, subset=['Birth_Year'])

# 保存为 Excel 文件（支持颜色显示）
styled_data.to_excel(output_file, index=False, engine='openpyxl')
print(f"标记后的数据已保存至：{output_file}")