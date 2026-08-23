#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將統一資料庫 JSON 安全注入 index.html，確保本機雙擊開啟 (file://) 零 CORS 阻擋、100% 正常顯示地圖
"""

import json
import os
import re
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UNIFIED_CSV = os.path.join(BASE_DIR, "output_data", "unified_hualien_commercial_data_1995_2026.csv")
INDEX_HTML = os.path.join(BASE_DIR, "index.html")

df = pd.read_csv(UNIFIED_CSV)
records = df.to_dict(orient='records')
json_str = json.dumps(records, ensure_ascii=False)

with open(INDEX_HTML, 'r', encoding='utf-8') as f:
    html = f.read()

# 定義要注入的內嵌載入函數
injection_code = f"""
        // 內嵌完整雙軌資料庫 (零 CORS 限制，本機直接雙擊開啟即可運作)
        const EMBEDDED_UNIFIED_DATA = {json_str};

        function loadHistoricalData() {{
            try {{
                historicalData = EMBEDDED_UNIFIED_DATA.map(obj => ({{
                    year: parseInt(obj['年份']),
                    li: obj['里別'],
                    doors: parseInt(obj['實體獨立門牌數']) || 0,
                    real_sales: parseFloat(obj['實體街區真實消費產值(百萬元)']) || 0,
                    power_index: parseFloat(obj['台電低壓營業用電量指數']) || 0,
                    traffic_index: parseFloat(obj['電信人潮與停留時長指數']) || 0,
                    distress_rate: parseFloat(obj['店面空置與業態降級率(%)']) || 0,
                    active_stores: parseFloat(obj['存續營利事業累積家數']) || 0,
                    tax_sales: parseFloat(obj['申報體系推估銷售額(千元)']) || 0,
                    invoice_stores: parseFloat(obj['開立發票店家數']) || 0,
                    capital_sum: parseFloat(obj['登記資本總額(萬元)']) || 0,
                    scene: obj['地表真實街景狀態'] || ''
                }}));
                initTableFilters();
                updateVisuals();
            }} catch (err) {{
                console.error('資料解析失敗:', err);
            }}
        }}
"""

# 使用正則替換 async function loadHistoricalData() { ... }
pattern = r'async function loadHistoricalData\(\)\s*\{[\s\S]*?\}\s*\}\s*\}'
if not re.search(pattern, html):
    pattern = r'async function loadHistoricalData\(\)\s*\{[\s\S]*?\n\s*\}'

new_html = re.sub(pattern, injection_code.strip(), html)

with open(INDEX_HTML, 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f"✅ 資料已安全注入 index.html！新檔案大小：{os.path.getsize(INDEX_HTML)} bytes")
