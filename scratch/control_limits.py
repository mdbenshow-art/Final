import pandas as pd
import numpy as np

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

df_clean = df.dropna(subset=['地區', '種類', '平均價'])

print("--- Level 1: Category & Region 3-Sigma Control Limits ---")
results = []
outliers_list = []

for (cat, reg), group in df_clean.groupby(['種類', '地區']):
    mean_val = group['平均價'].mean()
    std_val = group['平均價'].std()
    
    # Handle std = NaN or 0
    if pd.isna(std_val):
        std_val = 0.0
        
    ucl = mean_val + 3 * std_val
    lcl = max(0.0, mean_val - 3 * std_val)
    
    # Find outliers
    outliers = group[(group['平均價'] > ucl) | (group['平均價'] < lcl)]
    
    results.append({
        '種類': cat,
        '地區': reg,
        '樣本數': len(group),
        '平均價': mean_val,
        '標準差': std_val,
        '管制下限_LCL': lcl,
        '管制上限_UCL': ucl,
        '異常筆數': len(outliers)
    })
    
    for idx, row in outliers.iterrows():
        outliers_list.append({
            '種類': cat,
            '地區': reg,
            '作物名稱': row['作物名稱'],
            '市場名稱': row['市場名稱'],
            '平均價': row['平均價'],
            '加減三標準差範圍': f"[{lcl:.2f}, {ucl:.2f}]",
            '偏離值': row['平均價'] - ucl if row['平均價'] > ucl else row['平均價'] - lcl
        })

results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

print("\n--- Level 2: Crop-Specific 3-Sigma Control Limits (Across All Markets) ---")
# To find true market price anomalies, we look at crops with at least 10 market records
crop_counts = df_clean['作物名稱'].value_counts()
target_crops = crop_counts[crop_counts >= 10].index.tolist()

crop_control_limits = []
crop_outliers = []

for crop in target_crops:
    crop_df = df_clean[df_clean['作物名稱'] == crop]
    mean_val = crop_df['平均價'].mean()
    std_val = crop_df['平均價'].std()
    
    if pd.isna(std_val) or std_val == 0:
        continue
        
    ucl = mean_val + 3 * std_val
    lcl = max(0.0, mean_val - 3 * std_val)
    
    outliers = crop_df[(crop_df['平均價'] > ucl) | (crop_df['平均價'] < lcl)]
    
    if len(outliers) > 0:
        crop_control_limits.append({
            '作物名稱': crop,
            '種類': crop_df['種類'].iloc[0],
            '市場數量': len(crop_df),
            '均價': mean_val,
            '標準差': std_val,
            'LCL': lcl,
            'UCL': ucl,
            '異常數': len(outliers)
        })
        for idx, row in outliers.iterrows():
            crop_outliers.append({
                '作物名稱': crop,
                '市場名稱': row['市場名稱'],
                '地區': row['地區'],
                '實際單價': row['平均價'],
                '正常範圍(LCL-UCL)': f"[{lcl:.2f} - {ucl:.2f}]",
                '類型': '超高價(高於UCL)' if row['平均價'] > ucl else '超低價(低於LCL)'
            })

crop_control_limits_df = pd.DataFrame(crop_control_limits)
crop_outliers_df = pd.DataFrame(crop_outliers)

print("\nCrops with market anomalies:")
if not crop_control_limits_df.empty:
    print(crop_control_limits_df.to_string(index=False))
else:
    print("No crops found with market anomalies.")

print("\nDetailed market price anomalies:")
if not crop_outliers_df.empty:
    print(crop_outliers_df.to_string(index=False))
else:
    print("No detailed anomalies found.")

# Write outputs to a text file
with open(r'c:\Users\admin\Desktop\fainl\scratch\control_limits_analysis.txt', 'w', encoding='utf-8') as f:
    f.write("=== 3-SIGMA CONTROL LIMITS ANALYSIS ===\n\n")
    f.write("--- 1. 大類別與地區之管制界限 ---\n")
    f.write(results_df.to_string(index=False))
    f.write("\n\n--- 2. 大類別與地區之異常交易明細 ---\n")
    if outliers_list:
        f.write(pd.DataFrame(outliers_list).to_string(index=False))
    else:
        f.write("無異常交易\n")
    f.write("\n\n--- 3. 作物別之管制界限與異常市場分析 ---\n")
    if not crop_control_limits_df.empty:
        f.write("作物管制範圍：\n")
        f.write(crop_control_limits_df.to_string(index=False))
        f.write("\n\n異常市場明細：\n")
        f.write(crop_outliers_df.to_string(index=False))
    else:
        f.write("無作物別異常市場\n")
