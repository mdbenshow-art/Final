import pandas as pd
import json

# Load dataset
df = pd.read_csv(r'c:\Users\admin\Desktop\fainl\agri_prices_2026-06-12.csv')

# Define regional mapping (8 markets per region)
regions = {
    '北部': ['台北一', '台北二', '台北市場', '板橋區', '三重區', '宜蘭市', '桃農', '花蓮市'],
    '中部': ['台中市', '台中市場', '豐原區', '東勢鎮', '永靖鄉', '彰化市場', '溪湖鎮', '南投市'],
    '南部': ['西螺鎮', '嘉義市', '台南市場', '高雄市', '高雄市場', '鳳山區', '屏東市', '台東市']
}

# Invert mapping for mapping function
market_to_region = {}
for region, markets in regions.items():
    for m in markets:
        market_to_region[m] = region

df['地區'] = df['市場名稱'].map(market_to_region)

# Check if any market is unmapped
unmapped = df[df['地區'].isna()]['市場名稱'].unique()
if len(unmapped) > 0:
    print("Warning: Unmapped markets:", unmapped)

# Map type codes to names
type_names = {
    'N04': '蔬菜',
    'N05': '水果',
    'N06': '花卉'
}
df['種類'] = df['種類代碼'].map(type_names)

# Remove rows without type or region
df_clean = df.dropna(subset=['種類', '地區'])

print("--- Overall Statistics by Region ---")
overall_stats = df_clean.groupby(['種類', '地區']).agg(
    平均價_Mean=('平均價', 'mean'),
    平均價_Median=('平均價', 'median'),
    總交易量=('交易量', 'sum'),
    交易筆數=('平均價', 'count')
).reset_index()

print(overall_stats.to_string(index=False))

# Let's inspect details of specific top crops in each category
# 1. Fruits (N05) - Common crops like 香蕉, 鳳梨-金鑽鳳梨, 芒果-愛文, 西瓜-大西瓜
# 2. Vegetables (N04) - Common crops like 青蔥-粉蔥, 甘藍-初秋, 絲瓜
# 3. Flowers (N06) - Common crops like 大菊-白天星, 火鶴花-紅色, 非洲菊-混合色

common_crops = {
    '水果': ['香蕉', '鳳梨-金鑽鳳梨', '芒果-愛文', '西瓜-大西瓜'],
    '蔬菜': ['青蔥-粉蔥', '甘藍-初秋', '絲瓜', '番茄-牛番茄'],
    '花卉': ['大菊-白天星', '火鶴花-紅色', '非洲菊-混合色', '百合竹']
}

print("\n--- Detailed Common Crops Analysis ---")
crop_stats = []
for category, crops in common_crops.items():
    for crop in crops:
        crop_df = df_clean[(df_clean['種類'] == category) & (df_clean['作物名稱'] == crop)]
        if not crop_df.empty:
            stats = crop_df.groupby('地區').agg(
                平均價_Mean=('平均價', 'mean'),
                平均價_Median=('平均價', 'median'),
                總交易量=('交易量', 'sum')
            ).reset_index()
            stats['作物'] = crop
            stats['種類'] = category
            crop_stats.append(stats)

if crop_stats:
    crop_stats_df = pd.concat(crop_stats)
    print(crop_stats_df.to_string(index=False))
else:
    print("No common crops data found.")

# Save to a text file
with open(r'c:\Users\admin\Desktop\fainl\scratch\regional_analysis.txt', 'w', encoding='utf-8') as f:
    f.write("=== MARKET PRICES REGIONAL ANALYSIS ===\n\n")
    f.write("--- Overall Statistics by Region ---\n")
    f.write(overall_stats.to_string(index=False))
    f.write("\n\n--- Detailed Common Crops Analysis ---\n")
    if crop_stats:
        f.write(crop_stats_df.to_string(index=False))
    f.write("\n")
