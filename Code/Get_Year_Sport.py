import pandas as pd

# 读取数据
file_path = "F:/MCM/2025COMAP/Data/Sport_And_Medal.xlsx"
df = pd.read_excel(file_path)

# 提取项目列
project_columns = [
    "Artistic Swimming", "Diving", "Marathon Swimming", "Swimming", "Water Polo",
    "Archery", "Athletics", "Badminton", "Baseball", "Softball", "3x3", "Basketball",
    "Basque Pelota", "Boxing", "Breaking", "Sprint", "Slalom", "Cricket", "Croquet",
    "BMX Freestyle", "BMX Racing", "Mountain Bike", "Road", "Track", "Dressage",
    "Eventing", "Jumping", "Vaulting", "Driving", "Fencing", "Field hockey",
    "Flag football", "Football", "Golf", "Artistic", "Rhythmic", "Trampoline",
    "Indoor", "Field", "Jeu de Paume", "Judo", "Karate", "Sixes", "Field.1",
    "Modern Pentathlon", "Polo", "Rackets", "Roque", "Coastal", "Rowing", "Sevens",
    "Union", "Sailing", "Shooting", "Skateboarding", "Sport Climbing", "Squash",
    "Surfing", "Table Tennis", "Taekwondo", "Tennis", "Triathlon", "Tug of War",
    "Beach", "Indoor.1", "Water Motorsports", "Weightlifting", "Freestyle", "Greco-Roman"
]

# 按年份和项目统计
yearly_project_counts = df.groupby("Year")[project_columns].sum().reset_index()

# 保存结果
output_path = "F:/MCM/2025COMAP/Data/yearly_sport.csv"
yearly_project_counts.to_csv(output_path, index=False)

print(f"每一年每种项目的数量已保存至：{output_path}")