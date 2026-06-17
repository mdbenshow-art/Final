import pandas as pd

# Load data
df = pd.read_csv(r'c:\Users\admin\Desktop\fainl\agri_prices_2026-06-12.csv')

# Define regions
regions = {
    '北部': ['台北一', '台北二', '台北市場', '板橋區', '三重區', '宜蘭市', '桃農', '花蓮市'],
    '中部': ['台中市', '台中市場', '豐原區', '東勢鎮', '永靖鄉', '彰化市場', '溪湖鎮', '南投市'],
    '南部': ['西螺鎮', '嘉義市', '台南市場', '高雄市', '高雄市場', '鳳山區', '屏東市', '台東市']
}

# Map regions
market_to_region = {}
for r, ms in regions.items():
    for m in ms:
        market_to_region[m] = r

df['地區'] = df['市場名稱'].map(market_to_region)
type_names = {'N04': '蔬菜', 'N05': '水果', 'N06': '花卉'}
df['種類'] = df['種類代碼'].map(type_names)

df_clean = df.dropna(subset=['地區', '種類', '作物名稱'])

# For each category and region, find Top 3 crops by volume
categories = ['水果', '蔬菜', '花卉']
regions_list = ['北部', '中部', '南部']

output = []

for cat in categories:
    output.append(f"==================== {cat} ====================\n")
    for r in regions_list:
        output.append(f"--- {r}地區 Top 5 交易量作物 ---")
        sub_df = df_clean[(df_clean['種類'] == cat) & (df_clean['地區'] == r)]
        
        # Group by crop
        crop_stats = sub_df.groupby('作物名稱').agg(
            總交易量=('交易量', 'sum'),
            平均價_加權=('平均價', lambda x: (x * sub_df.loc[x.index, '交易量']).sum() / sub_df.loc[x.index, '交易量'].sum() if sub_df.loc[x.index, '交易量'].sum() > 0 else x.mean()),
            平均價_算術=('平均價', 'mean')
        ).reset_index()
        
        top_crops = crop_stats.sort_values(by='總交易量', ascending=False).head(5)
        
        for i, row in enumerate(top_crops.itertuples(), 1):
            output.append(f" {i}. {row.作物名稱:<15} | 交易量: {row.總交易量:10.1f} kg | 加權平均價: {row.平均價_加權:6.2f} 元/公斤")
        output.append("")

with open(r'c:\Users\admin\Desktop\fainl\scratch\crop_regional_top5.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("Top 5 crops analysis generated successfully.")
