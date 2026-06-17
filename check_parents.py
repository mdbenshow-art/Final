import pandas as pd
import json

df = pd.read_csv(r'c:\Users\admin\Desktop\fainl\agri_prices_2026-06-12.csv')

# Remove rows with NaN in Crop Name or Type Code
df = df.dropna(subset=['作物名稱', '種類代碼'])

# Extract parent name (split by '-' or ' ')
def get_parent_name(name):
    if '-' in name:
        return name.split('-')[0].strip()
    return name.strip()

df['大類作物名稱'] = df['作物名稱'].apply(get_parent_name)

print("Unique parent crops:", df['大類作物名稱'].nunique())

# Group by Type Code and parent name count
groups = {}
for code, group in df.groupby('種類代碼'):
    parent_crops = group['大類作物名稱'].unique().tolist()
    groups[str(code)] = {
        "unique_parents_count": len(parent_crops),
        "examples": parent_crops[:30]
    }

output_content = f"""Parent Crops Analysis:
Unique parent crops: {df['大類作物名稱'].nunique()}

Groups by Type Code:
{json.dumps(groups, indent=2, ensure_ascii=False)}
"""

with open(r'c:\Users\admin\Desktop\fainl\parent_crop_summary.txt', 'w', encoding='utf-8') as f:
    f.write(output_content)

print("Done!")
