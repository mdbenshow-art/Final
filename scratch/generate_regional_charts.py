import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

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

df_clean = df.dropna(subset=['地區', '種類'])

# Calculate detailed statistics by market
market_stats = df_clean.groupby(['地區', '市場名稱', '種類']).agg(
    平均價=('平均價', 'mean'),
    交易量=('交易量', 'sum'),
    筆數=('平均價', 'count')
).reset_index()

# Save detailed market stats to text
with open(r'c:\Users\admin\Desktop\fainl\scratch\market_regional_details.txt', 'w', encoding='utf-8') as f:
    f.write("=== REGIONAL MARKET DETAILS ===\n\n")
    for r in ['北部', '中部', '南部']:
        f.write(f"--- {r}地區市場交易詳情 ---\n")
        sub_df = market_stats[market_stats['地區'] == r]
        f.write(sub_df.to_string(index=False))
        f.write("\n\n")

# Calculate overall regional statistics
overall_stats = df_clean.groupby(['種類', '地區']).agg(
    平均價_Mean=('平均價', 'mean'),
    交易量_Sum=('交易量', 'sum')
).reset_index()

# Generate visual comparisons
fig, axes = plt.subplots(2, 3, figsize=(18, 10))

# Colors
colors = {'北部': '#4C72B0', '中部': '#55A868', '南部': '#C44E52'}
palette = [colors['北部'], colors['中部'], colors['南部']]

categories = ['水果', '蔬菜', '花卉']

for idx, cat in enumerate(categories):
    cat_df = overall_stats[overall_stats['種類'] == cat]
    
    # Sort regions as North, Central, South
    cat_df = cat_df.set_index('地區').reindex(['北部', '中部', '南部']).reset_index()
    
    # Row 0: Average Price Barplot
    sns.barplot(
        x='地區', 
        y='平均價_Mean', 
        data=cat_df, 
        ax=axes[0, idx], 
        palette=palette,
        hue='地區',
        legend=False
    )
    axes[0, idx].set_title(f'{cat} - 各地區平均交易價格 (元/公斤)', fontsize=14, fontweight='bold')
    axes[0, idx].set_ylabel('平均價 (元/公斤)', fontsize=12)
    axes[0, idx].set_xlabel('')
    
    # Add values on top of bars
    for p in axes[0, idx].patches:
        axes[0, idx].annotate(
            f"{p.get_height():.2f}", 
            (p.get_x() + p.get_width() / 2., p.get_height()), 
            ha='center', va='center', 
            xytext=(0, 8), 
            textcoords='offset points',
            fontsize=11, fontweight='bold'
        )

    # Row 1: Total Volume Barplot (in Metric Tons)
    cat_df['交易量_噸'] = cat_df['交易量_Sum'] / 1000.0
    sns.barplot(
        x='地區', 
        y='交易量_噸', 
        data=cat_df, 
        ax=axes[1, idx], 
        palette=palette,
        hue='地區',
        legend=False
    )
    axes[1, idx].set_title(f'{cat} - 各地區總交易量 (公噸)', fontsize=14, fontweight='bold')
    axes[1, idx].set_ylabel('交易量 (公噸)', fontsize=12)
    axes[1, idx].set_xlabel('')
    
    for p in axes[1, idx].patches:
        axes[1, idx].annotate(
            f"{p.get_height():.1f}", 
            (p.get_x() + p.get_width() / 2., p.get_height()), 
            ha='center', va='center', 
            xytext=(0, 8), 
            textcoords='offset points',
            fontsize=11, fontweight='bold'
        )

plt.suptitle('115年6月12日 台灣農產品各地區價格與交易量對比分析', fontsize=18, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig(r'c:\Users\admin\Desktop\fainl\regional_comparison.png', dpi=150)
plt.close()

print("Charts generated successfully at c:\\Users\\admin\\Desktop\\fainl\\regional_comparison.png")
