import pandas as pd
import json

df = pd.read_csv(r'c:\Users\admin\Desktop\fainl\agri_prices_2026-06-12.csv')

summary = {
    "total_rows": len(df),
    "unique_types": df['種類代碼'].unique().tolist(),
    "unique_crops_count": df['作物名稱'].nunique(),
    "unique_markets_count": df['市場名稱'].nunique(),
}

groups = {}
for code, group in df.groupby('種類代碼'):
    crops = group['作物名稱'].dropna().unique().tolist()
    groups[str(code)] = {
        "count": len(crops),
        "examples": crops[:20]
    }

output_content = f"""Summary:
{json.dumps(summary, indent=2, ensure_ascii=False)}

Groups by Type Code:
{json.dumps(groups, indent=2, ensure_ascii=False)}
"""

with open(r'c:\Users\admin\Desktop\fainl\crop_summary_utf8.txt', 'w', encoding='utf-8') as f:
    f.write(output_content)

print("Done writing summary!")
