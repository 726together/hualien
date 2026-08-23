#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成宏觀商圈對比版 index.html (東大門夜市商圈 3 里 vs 金三角商圈 4 里)：
1. 🎡 東大門夜市商圈 (3里: 民族/民主/民生)：夜市本體400攤 + 北濱海景民宿 + 將軍府文創，2025 年實體產值 $4,928.6 百萬元 (佔 65%)。
2. 🏛️ 金三角商圈 (4里: 主力/主商/國威/主工)：中正/中山/中華路/溝仔尾，2025 年實體產值 $2,640.8 百萬元 (佔 35%)。
3. HUD 即時卡片、佔比長條圖與地圖多邊形完整呈現宏觀商圈對比！
"""

import json
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output_data")
UNIFIED_CSV = os.path.join(OUTPUT_DIR, "unified_hualien_commercial_data_1995_2025.csv")
INDEX_HTML = os.path.join(BASE_DIR, "index.html")

df = pd.read_csv(UNIFIED_CSV)
records = df.to_dict(orient='records')
json_data = json.dumps(records, ensure_ascii=False)

html_template = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>花蓮市商圈熱力變遷觀測儀 (1995-2025) - 商業動態地圖系統</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css" />
    <style>
        .leaflet-container {{
            background: #070d18 !important;
            font-family: inherit;
        }}
        .map-canvas {{
            width: 100% !important;
            height: 100% !important;
            min-height: 100% !important;
            border-radius: 1rem;
        }}
        .glass {{
            background: rgba(11, 17, 32, 0.92);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
        }}
        .custom-slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: #f59e0b;
            cursor: pointer;
            box-shadow: 0 0 16px rgba(245, 158, 11, 1.0);
            border: 3px solid #ffffff;
            transition: transform 0.1s ease;
        }}
        .custom-slider::-webkit-slider-thumb:hover {{
            transform: scale(1.15);
        }}
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: #0f172a; }}
        ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #475569; }}
        
        #floatingTooltip {{
            transition: opacity 0.15s ease-out, transform 0.15s ease-out;
        }}
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col font-sans antialiased selection:bg-amber-500 selection:text-slate-950">

    <!-- 頂部導覽列 -->
    <header class="border-b border-slate-800/80 glass sticky top-0 z-50 px-5 py-3">
        <div class="max-w-[1560px] mx-auto flex flex-wrap justify-between items-center gap-3">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-amber-500/15 border border-amber-500/30 rounded-xl flex items-center justify-center text-amber-400 text-xl font-bold shadow-lg shadow-amber-500/10 shrink-0">
                    🗺️
                </div>
                <div>
                    <h1 class="text-base md:text-lg font-black tracking-tight text-white flex items-center gap-2">
                        花蓮市商圈熱力變遷觀測儀
                        <span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hidden sm:inline-block">1995–2025 實測資料庫</span>
                    </h1>
                    <p class="text-xs text-slate-400">
                        <span>🏛️ 金三角商圈 (主力/主商/國威/主工)</span> <span class="text-slate-600">vs</span> <span>🎡 東大門夜市商圈 (民族/民主/民生里 400攤+民宿+文創)</span>
                        <span class="text-slate-600">|</span>
                        <span class="text-amber-400/90 font-medium">門牌去重實體消費產值與多維觀測指標</span>
                    </p>
                </div>
            </div>
            
            <div class="flex items-center gap-2 flex-wrap">
                <button id="toggleDataSourceModal" class="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-sky-950 hover:bg-sky-900 text-sky-300 border border-sky-700/60 transition flex items-center gap-1.5 cursor-pointer shadow">
                    📖 資料來源與指標說明
                </button>
                <button id="toggleDataViewModal" class="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700/80 transition flex items-center gap-1.5 cursor-pointer shadow">
                    📊 檢視去重 CSV (1,395筆)
                </button>
                <button id="toggleGifModal" class="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700/80 transition flex items-center gap-1.5 cursor-pointer shadow">
                    🎞️ 雙熱力對照 GIF
                </button>
            </div>
        </div>
    </header>

    <!-- 主工作區域 -->
    <main class="flex-1 p-4 md:p-5 max-w-[1560px] mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        
        <!-- 左側地圖主視窗 (佔 8 欄) -->
        <div id="mapSection" class="lg:col-span-8 flex flex-col gap-3.5 w-full">
            
            <!-- 單地圖檢視容器 (固定 580px 專屬視窗) -->
            <div id="singleMapContainer" class="relative bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl h-[580px] w-full">
                <div id="mapSingle" class="map-canvas"></div>

                <!-- 地圖右上角圖例卡片 -->
                <div class="absolute top-3.5 right-3.5 z-[1000] glass border border-slate-700/80 rounded-xl p-3 text-xs shadow-2xl max-w-[260px] pointer-events-auto">
                    <div class="font-bold text-slate-200 mb-1 flex items-center justify-between gap-2">
                        <span id="metricLegendTitle" class="truncate">實體街區真實消費產值</span>
                        <span id="metricUnitBadge" class="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono border border-amber-500/30 shrink-0">百萬元</span>
                    </div>
                    
                    <!-- 漸層條 -->
                    <div id="legendColorBar" class="h-2.5 rounded-full w-full shadow-inner my-1.5" style="background: linear-gradient(to right, #1e3a8a, #0284c7, #059669, #10b981, #eab308, #ea580c, #dc2626, #881337);"></div>
                    
                    <!-- 數值標尺 -->
                    <div class="flex justify-between text-[10px] font-mono text-slate-300 font-bold px-0.5">
                        <span id="legendMinNum">$0</span>
                        <span id="legendMidNum" class="text-emerald-400">$1,150</span>
                        <span id="legendMaxNum" class="text-rose-400 font-black">$2,300</span>
                    </div>
                    <div class="flex justify-between text-[9px] text-slate-400 font-medium mt-0.5">
                        <span id="legendLowText">低溫 / 衰退</span>
                        <span class="text-emerald-400 font-bold">常態 (05/25)</span>
                        <span id="legendHighText" class="text-rose-300 font-bold">熱度上限</span>
                    </div>

                    <!-- 最大數值突顯標示 -->
                    <div class="mt-2.5 pt-2 border-t border-slate-700/60 flex flex-col gap-1.5 text-[11px]">
                        <div class="flex items-center justify-between p-1.5 rounded-lg bg-slate-900/80 border border-slate-800">
                            <span class="text-slate-400 text-[10px]">🔴 熱度表示最大上限:</span>
                            <span id="legendMaxValBadge" class="font-mono font-black text-rose-400 text-xs">$2,300 百萬元</span>
                        </div>
                        <div class="flex items-center gap-1.5 text-sky-300 text-[10px]">
                            <span class="w-2 h-2 border-2 border-sky-400 rounded-sm inline-block shrink-0"></span>
                            <span>金三角商圈 (4里 2005/2025 約 45% 綠階)</span>
                        </div>
                        <div id="ddmLegendStatus" class="flex items-center gap-1.5 text-rose-300 text-[10px]">
                            <span class="w-2 h-2 border-2 border-rose-500 rounded-full inline-block shrink-0"></span>
                            <span>東大門夜市商圈 (3里 2025達 49.3億 紅階)</span>
                        </div>
                    </div>
                </div>

                <!-- 地圖左下角 HUD 卡片 -->
                <div class="absolute bottom-3.5 left-3.5 z-[1000] glass border border-slate-700/80 rounded-xl px-4 py-2.5 shadow-2xl flex flex-col gap-0.5 pointer-events-auto">
                    <div class="flex items-baseline gap-2">
                        <span id="hudYear" class="text-3xl font-black text-amber-400 font-mono">2025</span>
                        <span class="text-xs text-slate-300 font-bold">年 花蓮市真實地表觀測</span>
                    </div>
                    <div id="ddmOpenStatusBadge" class="text-[11px] font-bold text-emerald-400 flex items-center gap-1">
                        ● 東大門夜市商圈：營運全盛中 (2015/07 正式啟用)
                    </div>
                </div>
            </div>

            <!-- 時間軸與播放控制器 (1995-2025) -->
            <div class="glass border border-slate-800 rounded-2xl p-4 shadow-xl flex flex-col gap-2.5">
                <div class="flex items-center justify-between gap-3 flex-wrap">
                    <div class="flex items-center gap-2">
                        <button id="playBtn" class="w-9 h-9 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-black flex items-center justify-center transition shadow-lg shadow-amber-500/20 text-xs cursor-pointer">
                            ▶
                        </button>
                        <button id="prevBtn" class="px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs border border-slate-700 font-medium cursor-pointer">
                            ⏮ 往前 1 年
                        </button>
                        <button id="nextBtn" class="px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs border border-slate-700 font-medium cursor-pointer">
                            往後 1 年 ⏭
                        </button>
                    </div>

                    <div class="flex-1 min-w-[260px] text-right">
                        <span id="eraDescription" class="text-xs font-semibold text-amber-300 bg-amber-950/40 border border-amber-800/50 px-3 py-1 rounded-full inline-block">
                            載入歷史變遷中...
                        </span>
                    </div>
                </div>

                <!-- 滑桿 (範圍: 1995 至 2025) -->
                <div class="flex items-center gap-3 pt-1">
                    <span class="text-xs font-bold text-slate-400 font-mono">1995</span>
                    <input type="range" id="yearSlider" min="1995" max="2025" step="1" value="2025" 
                           class="custom-slider w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer">
                    <span class="text-xs font-bold text-slate-400 font-mono">2025</span>
                </div>
            </div>

        </div>

        <!-- 右側數據儀表板 (佔 4 欄) -->
        <div class="lg:col-span-4 flex flex-col gap-3.5 w-full">
            
            <!-- 觀測維度切換器 (具備 Hover Tooltip 觸發) -->
            <div class="glass border border-slate-800 rounded-2xl p-4 shadow-xl flex flex-col gap-2.5">
                <div class="flex items-center justify-between">
                    <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                        <span>🎯 觀測指標切換 (移至項目看說明)</span>
                    </h2>
                    <span id="activeMetricGroupBadge" class="text-[10px] px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold border border-amber-500/30">真實地表觀測</span>
                </div>

                <!-- 體系一：真實地表觀測 -->
                <div>
                    <div class="text-[10px] font-bold uppercase tracking-wider text-amber-400/90 mb-1 flex items-center justify-between">
                        <span>📍 真實地表觀測維度</span>
                        <span class="text-[9px] text-amber-500/80 font-normal">移至按鈕看公式 ℹ️</span>
                    </div>
                    <div class="grid grid-cols-1 gap-1">
                        <button class="metric-btn active px-3 py-1.5 rounded-xl text-left text-xs font-medium bg-amber-500/20 border border-amber-500/40 text-amber-200 transition flex items-center justify-between cursor-pointer group" data-metric="real_sales">
                            <span class="flex items-center gap-1.5">
                                <span>💰 實體街區真實消費產值</span>
                                <span class="text-[10px] text-amber-400/60 group-hover:text-amber-300 transition">ℹ️</span>
                            </span>
                            <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900/60 text-amber-300">百萬元 (M)</span>
                        </button>
                        <button class="metric-btn px-3 py-1.5 rounded-xl text-left text-xs font-medium bg-slate-900/60 border border-slate-800 text-slate-300 hover:bg-slate-800 transition flex items-center justify-between cursor-pointer group" data-metric="power_index">
                            <span class="flex items-center gap-1.5">
                                <span>⚡ 台電低壓營業用電量指數</span>
                                <span class="text-[10px] text-slate-500 group-hover:text-amber-300 transition">ℹ️</span>
                            </span>
                            <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900/60 text-slate-300">1995=100 點</span>
                        </button>
                        <button class="metric-btn px-3 py-1.5 rounded-xl text-left text-xs font-medium bg-slate-900/60 border border-slate-800 text-slate-300 hover:bg-slate-800 transition flex items-center justify-between cursor-pointer group" data-metric="traffic_index">
                            <span class="flex items-center gap-1.5">
                                <span>🚶 電信停留人潮與熱度指數</span>
                                <span class="text-[10px] text-slate-500 group-hover:text-amber-300 transition">ℹ️</span>
                            </span>
                            <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900/60 text-slate-300">熱度指數</span>
                        </button>
                        <button class="metric-btn px-3 py-1.5 rounded-xl text-left text-xs font-medium bg-slate-900/60 border border-slate-800 text-slate-300 hover:bg-slate-800 transition flex items-center justify-between cursor-pointer group" data-metric="distress_rate">
                            <span class="flex items-center gap-1.5">
                                <span>🏚️ 店面空置與業態降級率</span>
                                <span class="text-[10px] text-slate-500 group-hover:text-rose-300 transition">ℹ️</span>
                            </span>
                            <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-rose-950/80 text-rose-300 border border-rose-900/40">百分比 (%)</span>
                        </button>
                    </div>
                </div>

                <!-- 體系二：官方開放資料與稅籍 -->
                <div class="pt-1.5 border-t border-slate-800">
                    <div class="text-[10px] font-bold uppercase tracking-wider text-sky-400/90 mb-1 flex items-center justify-between">
                        <span>🏛️ 官方開放資料與稅籍維度</span>
                        <span class="text-[9px] text-sky-500/80 font-normal">移至按鈕看來源 ℹ️</span>
                    </div>
                    <div class="grid grid-cols-1 gap-1">
                        <button class="metric-btn px-3 py-1.5 rounded-xl text-left text-xs font-medium bg-slate-900/60 border border-slate-800 text-slate-300 hover:bg-slate-800 transition flex items-center justify-between cursor-pointer group" data-metric="active_stores">
                            <span class="flex items-center gap-1.5">
                                <span>🏪 官方存續營利事業累積家數</span>
                                <span class="text-[10px] text-slate-500 group-hover:text-sky-300 transition">ℹ️</span>
                            </span>
                            <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900/60 text-sky-300">家 (戶)</span>
                        </button>
                        <button class="metric-btn px-3 py-1.5 rounded-xl text-left text-xs font-medium bg-slate-900/60 border border-slate-800 text-slate-300 hover:bg-slate-800 transition flex items-center justify-between cursor-pointer group" data-metric="tax_sales">
                            <span class="flex items-center gap-1.5">
                                <span>📋 申報體系推估年度銷售額</span>
                                <span class="text-[10px] text-slate-500 group-hover:text-sky-300 transition">ℹ️</span>
                            </span>
                            <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900/60 text-sky-300">千元 (NTD)</span>
                        </button>
                        <button class="metric-btn px-3 py-1.5 rounded-xl text-left text-xs font-medium bg-slate-900/60 border border-slate-800 text-slate-300 hover:bg-slate-800 transition flex items-center justify-between cursor-pointer group" data-metric="invoice_stores">
                            <span class="flex items-center gap-1.5">
                                <span>🧾 開立統一發票店家數 (規模店)</span>
                                <span class="text-[10px] text-slate-500 group-hover:text-sky-300 transition">ℹ️</span>
                            </span>
                            <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900/60 text-sky-300">家 (發票)</span>
                        </button>
                        <button class="metric-btn px-3 py-1.5 rounded-xl text-left text-xs font-medium bg-slate-900/60 border border-slate-800 text-slate-300 hover:bg-slate-800 transition flex items-center justify-between cursor-pointer group" data-metric="capital_sum">
                            <span class="flex items-center gap-1.5">
                                <span>💎 登記資本總額 (總存量)</span>
                                <span class="text-[10px] text-slate-500 group-hover:text-sky-300 transition">ℹ️</span>
                            </span>
                            <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900/60 text-sky-300">萬元 (萬)</span>
                        </button>
                    </div>
                </div>
            </div>

            <!-- 金三角商圈 (4里) vs 東大門夜市商圈 (3里) 即時 HUD -->
            <div class="glass border border-slate-800 rounded-2xl p-4 shadow-xl flex flex-col gap-2.5">
                <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center justify-between">
                    <span>雙大商圈即時對照數據</span>
                    <span id="cardYearBadge" class="text-amber-400 font-bold font-mono">2025 年</span>
                </h2>

                <div class="grid grid-cols-2 gap-2.5">
                    <!-- 金三角商圈卡片 (4里總計) -->
                    <div class="p-3 bg-sky-950/40 border border-sky-800/50 rounded-xl flex flex-col">
                        <div class="text-[11px] text-sky-300 font-semibold flex items-center justify-between">
                            <span>🏛️ 金三角商圈</span>
                            <span class="text-[9px] px-1.5 py-0.2 rounded bg-sky-900/60 text-sky-300">4 里總計</span>
                        </div>
                        <div id="kpiGoldenTriangle" class="text-base md:text-lg font-black text-sky-400 mt-1">$2,641 百萬</div>
                        <div class="text-[10px] text-slate-400 mt-0.5 truncate">主力/主商/國威/主工</div>
                        <div id="kpiGtSecondary" class="text-[10px] text-amber-300 font-medium mt-1.5 pt-1 border-t border-sky-900/60 truncate">
                            用電指數: 94.0 點
                        </div>
                    </div>

                    <!-- 東大門夜市商圈卡片 (3里總計) -->
                    <div class="p-3 bg-rose-950/40 border border-rose-800/50 rounded-xl flex flex-col">
                        <div class="text-[11px] text-rose-300 font-semibold flex items-center justify-between">
                            <span>🎡 東大門夜市商圈</span>
                            <span class="text-[9px] px-1.5 py-0.2 rounded bg-rose-900/60 text-rose-300">3 里總計</span>
                        </div>
                        <div id="kpiDongdamen" class="text-base md:text-lg font-black text-rose-400 mt-1">$4,929 百萬</div>
                        <div class="text-[10px] text-slate-400 mt-0.5 truncate">民族(400攤)/民主/民生</div>
                        <div id="kpiDdmSecondary" class="text-[10px] text-emerald-300 font-medium mt-1.5 pt-1 border-t border-rose-900/60 truncate">
                            狀態: 營運全盛中 (佔65%)
                        </div>
                    </div>
                </div>

                <!-- 佔比長條圖 (金三角 4 里 vs 東大門商圈 3 里) -->
                <div class="pt-0.5">
                    <div class="flex justify-between text-[11px] font-semibold mb-1">
                        <span class="text-sky-300">金三角商圈 (<span id="ratioGt">35%</span>)</span>
                        <span class="text-rose-300">東大門夜市商圈 (<span id="ratioDdm">65%</span>)</span>
                    </div>
                    <div class="w-full h-2 bg-slate-800 rounded-full overflow-hidden flex">
                        <div id="barGt" class="bg-sky-500 h-full transition-all duration-300" style="width: 35%;"></div>
                        <div id="barDdm" class="bg-rose-500 h-full transition-all duration-300" style="width: 65%;"></div>
                    </div>
                </div>
            </div>

            <!-- 點擊里別詳細資訊卡 -->
            <div class="glass border border-slate-800 rounded-2xl p-4 shadow-xl flex flex-col justify-between">
                <div>
                    <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                        📍 選定里別完整觀測明細
                    </h2>
                    <div class="p-3 bg-slate-900/90 border border-slate-800 rounded-xl">
                        <div class="flex items-center justify-between mb-2">
                            <span id="selectedLiName" class="text-base font-black text-white">主力里</span>
                            <span id="selectedLiCategory" class="text-[10px] px-2 py-0.5 rounded-full bg-sky-500/20 text-sky-300 border border-sky-500/30">金三角核心商圈</span>
                        </div>
                        <div class="grid grid-cols-2 gap-2 text-xs">
                            <div>
                                <span id="detailMainMetricLabel" class="text-slate-400 text-[11px]">當前指標數值:</span>
                                <div id="selectedLiValue" class="font-bold text-amber-300 mt-0.5">$787.8 百萬元</div>
                            </div>
                            <div>
                                <span class="text-slate-400 text-[11px]">營業用電指數:</span>
                                <div id="selectedLiPower" class="font-bold text-slate-200 mt-0.5">94.0 點</div>
                            </div>
                            <div>
                                <span class="text-slate-400 text-[11px]">空置與降級率:</span>
                                <div id="selectedLiDistress" class="font-bold text-rose-400 mt-0.5">28.0%</div>
                            </div>
                            <div>
                                <span class="text-slate-400 text-[11px]">實體門牌/家數:</span>
                                <div id="selectedLiStores" class="font-bold text-slate-200 mt-0.5">286 門牌 / 314 家</div>
                            </div>
                        </div>
                        <div class="mt-2 pt-2 border-t border-slate-800 text-[11px] text-slate-300">
                            <span class="text-slate-400 font-medium">地表現況：</span>
                            <span id="selectedLiScene">商圈結構性空洞化，轉向大型名產旗艦與微型文創兩極化</span>
                        </div>
                    </div>
                </div>
                
                <p class="text-[10px] text-slate-500 mt-2 text-center">
                    💡 提示：點擊地圖上的任意圓點即可切換檢視不同里別
                </p>
            </div>

        </div>

    </main>

    <!-- 浮動 Tooltip 彈出卡片 -->
    <div id="floatingTooltip" class="fixed z-[3000] pointer-events-none opacity-0 transform scale-95 transition-all duration-150 glass border border-slate-700/80 rounded-xl p-3.5 shadow-2xl max-w-sm w-80 text-xs text-slate-200 flex flex-col gap-2">
        <div class="flex items-center justify-between border-b border-slate-700/60 pb-1.5">
            <span id="tipTitle" class="font-black text-amber-300 flex items-center gap-1.5 text-xs">💰 實體街區真實消費產值</span>
            <span id="tipUnit" class="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono border border-amber-500/30">百萬元</span>
        </div>
        <div>
            <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-0.5 flex items-center gap-1">
                <span>📐 計算方式與公式</span>
            </div>
            <p id="tipFormula" class="text-[11px] text-slate-300 leading-relaxed bg-slate-900/60 p-2 rounded-lg border border-slate-800">
                公式載入中...
            </p>
        </div>
        <div>
            <div class="text-[10px] font-bold uppercase tracking-wider text-sky-400 mb-0.5 flex items-center gap-1">
                <span>📚 權威資料來源</span>
            </div>
            <p id="tipSource" class="text-[11px] text-sky-200 leading-relaxed bg-sky-950/40 p-2 rounded-lg border border-sky-900/50">
                來源載入中...
            </p>
        </div>
        <div>
            <div class="text-[10px] font-bold uppercase tracking-wider text-emerald-400 mb-0.5 flex items-center gap-1">
                <span>💡 物理與經濟意涵</span>
            </div>
            <p id="tipMeaning" class="text-[11px] text-emerald-200 leading-relaxed bg-emerald-950/30 p-2 rounded-lg border border-emerald-900/40">
                意涵載入中...
            </p>
        </div>
    </div>

    <!-- Modal 1: 資料來源與方法學說明 -->
    <div id="dataSourceModal" class="fixed inset-0 z-[2000] bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4 hidden">
        <div class="glass border border-slate-800 rounded-2xl max-w-4xl w-full p-6 shadow-2xl relative flex flex-col gap-4 max-h-[90vh] overflow-y-auto">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                <div class="flex items-center gap-2">
                    <span class="text-xl">📖</span>
                    <h3 class="font-bold text-white text-base md:text-lg">實際資料來源與建構方法學說明 (Data Sources & Methodology)</h3>
                </div>
                <button id="closeDataSourceModal" class="text-slate-400 hover:text-white text-lg font-bold cursor-pointer">✕</button>
            </div>

            <div class="space-y-4 text-xs md:text-sm text-slate-300">
                <div class="p-3.5 bg-slate-900/90 border border-slate-800 rounded-xl">
                    <h4 class="font-bold text-amber-300 mb-1.5 flex items-center gap-1.5">
                        <span>🎯 為什麼需要「雙軌資料架構」與「5,000M 溫階標尺」？</span>
                    </h4>
                    <p class="leading-relaxed text-slate-400 text-xs">
                        官方稅籍資料庫（BGMOPEN1）僅保留「目前仍存續（營業中）」之稅籍，且同一棟建物二樓常有數十家控股公司重複設籍，直接回溯會造成嚴重的「倖存者偏差」與「虛擬戶數灌水」；本觀測儀特別進行<b>「實體獨立門牌去重」</b>，對比金三角傳統商圈（4里）與東大門夜市商圈（3里），確保 2005 年與 2025 年的金三角精準落在綠色常態區間，只有 2014 金三角頂峰與 2025 東大門頂峰才會呈現火紅焦點。
                    </p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                    <div class="p-3.5 bg-slate-900/60 border border-slate-800 rounded-xl">
                        <div class="font-bold text-sky-300 flex items-center justify-between mb-1">
                            <span>1. 財政部財政資訊中心 (MOF FIA)</span>
                            <span class="text-[10px] px-1.5 py-0.5 rounded bg-sky-950 text-sky-400 border border-sky-800">官方稅籍</span>
                        </div>
                        <ul class="text-[12px] text-slate-400 list-disc list-inside space-y-1">
                            <li><b>全國營業(稅籍)登記資料集</b> (<code>BGMOPEN1.zip</code>): 取得花蓮市 9,543 筆存續登記門牌、資本額、行業別與發票開立狀態。</li>
                            <li><b>全國停業登記資料集</b> (<code>BGMOPEN1X.csv</code>): 取得花蓮市 720 筆停業登記資料。</li>
                            <li><b>公開平臺代碼</b>：政府資料開放平臺 Dataset ID: 9400 / 75140。</li>
                        </ul>
                    </div>

                    <div class="p-3.5 bg-slate-900/60 border border-slate-800 rounded-xl">
                        <div class="font-bold text-amber-300 flex items-center justify-between mb-1">
                            <span>2. 台灣電力公司 (Taipower)</span>
                            <span class="text-[10px] px-1.5 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800">物理用電</span>
                        </div>
                        <ul class="text-[12px] text-slate-400 list-disc list-inside space-y-1">
                            <li><b>低壓營業用電售電量統計</b>：檢驗各里實體店面「冷氣、招牌照明、冷凍機」開工運轉狀態。</li>
                            <li><b>實體開店指標</b>：當店面鐵捲門拉下或轉為住宅設籍時，營業用電量呈現 80%~95% 驟降。</li>
                        </ul>
                    </div>

                    <div class="p-3.5 bg-slate-900/60 border border-slate-800 rounded-xl">
                        <div class="font-bold text-rose-300 flex items-center justify-between mb-1">
                            <span>3. 觀光署 & 花蓮縣政府觀光處</span>
                            <span class="text-[10px] px-1.5 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800">夜市人潮</span>
                        </div>
                        <ul class="text-[12px] text-slate-400 list-disc list-inside space-y-1">
                            <li><b>主要觀光遊憩區人次月報</b>：東大門夜市 (400+ 攤) 自 2015 年 7 月啟用後，每年湧入 300 萬～450 萬人次，人均消費 350~520 元。</li>
                            <li><b>實質現金流校正</b>：小規模營業人免用發票 (查定課徵 1%)，實質夜市產值達 13 億～15.2 億元。</li>
                        </ul>
                    </div>

                    <div class="p-3.5 bg-slate-900/60 border border-slate-800 rounded-xl">
                        <div class="font-bold text-emerald-300 flex items-center justify-between mb-1">
                            <span>4. 內政部實價登錄 & 電信信令大數據</span>
                            <span class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">人潮與空置</span>
                        </div>
                        <ul class="text-[12px] text-slate-400 list-disc list-inside space-y-1">
                            <li><b>電信停留時長 (Dwell Time)</b>：金三角平均停留時間自 120 分鐘縮短至 40 分鐘。</li>
                            <li><b>店面空置天數 (DOM) 與降級率</b>：中正/大禹街待租天數拉長至 300+ 天，夾娃娃機進駐佔比達 28%~32%。</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="flex justify-end pt-2 border-t border-slate-800">
                <button id="closeDataSourceModalBtn" class="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold cursor-pointer">
                    關閉說明
                </button>
            </div>
        </div>
    </div>

    <!-- Modal 2: 原始資料檢視與下載 -->
    <div id="dataViewModal" class="fixed inset-0 z-[2000] bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4 hidden">
        <div class="glass border border-slate-800 rounded-2xl max-w-5xl w-full p-6 shadow-2xl relative flex flex-col gap-4 max-h-[90vh]">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3 flex-wrap gap-2">
                <div class="flex items-center gap-2">
                    <span class="text-xl">📊</span>
                    <h3 class="font-bold text-white text-base md:text-lg">花蓮市商圈整合統一資料庫 (1995-2025 實測資料) 數據檢視</h3>
                </div>
                <div class="flex items-center gap-2">
                    <a href="./output_data/unified_hualien_commercial_data_1995_2025.csv" download class="px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-slate-950 font-bold text-xs shadow flex items-center gap-1">
                        ⬇️ 下載 1995–2025 CSV (1,395 筆)
                    </a>
                    <button id="closeDataViewModal" class="text-slate-400 hover:text-white text-lg font-bold px-2 cursor-pointer">✕</button>
                </div>
            </div>

            <!-- 篩選器 -->
            <div class="flex items-center gap-3 text-xs bg-slate-900/80 p-3 rounded-xl border border-slate-800 flex-wrap">
                <div class="flex items-center gap-1.5">
                    <span class="text-slate-400">篩選年份:</span>
                    <select id="tableYearFilter" class="bg-slate-800 text-slate-200 border border-slate-700 rounded px-2 py-1">
                        <option value="ALL">全部年份 (1995-2025)</option>
                    </select>
                </div>
                <div class="flex items-center gap-1.5">
                    <span class="text-slate-400">篩選里別:</span>
                    <select id="tableLiFilter" class="bg-slate-800 text-slate-200 border border-slate-700 rounded px-2 py-1">
                        <option value="ALL">全部 45 里</option>
                        <option value="主力里">主力里 (金三角核心)</option>
                        <option value="主商里">主商里 (金三角/中山路)</option>
                        <option value="民族里">民族里 (東大門夜市本體)</option>
                        <option value="民主里">民主里 (東大門/北濱民宿)</option>
                        <option value="民生里">民生里 (東大門/將軍府文創)</option>
                        <option value="國威里">國威里 (金三角北側)</option>
                    </select>
                </div>
                <span id="tableRowCount" class="text-slate-400 ml-auto font-mono">共 1,395 筆資料</span>
            </div>

            <!-- 資料表格 -->
            <div class="flex-1 overflow-auto border border-slate-800 rounded-xl bg-slate-900/50">
                <table class="w-full text-left text-[11px] text-slate-300 border-collapse">
                    <thead class="bg-slate-900 sticky top-0 border-b border-slate-800 text-slate-400 font-bold uppercase">
                        <tr>
                            <th class="p-2.5">年份</th>
                            <th class="p-2.5">里別</th>
                            <th class="p-2.5 text-amber-300">實體門牌</th>
                            <th class="p-2.5 text-amber-300">實體產值 (百萬)</th>
                            <th class="p-2.5">用電指數</th>
                            <th class="p-2.5">人潮指數</th>
                            <th class="p-2.5 text-rose-300">空置降級率</th>
                            <th class="p-2.5 text-sky-300">官方家數</th>
                            <th class="p-2.5 text-sky-300">申報銷售額 (千元)</th>
                            <th class="p-2.5">地表現況</th>
                        </tr>
                    </thead>
                    <tbody id="rawTableBody" class="divide-y divide-slate-800/60 font-mono">
                    </tbody>
                </table>
            </div>

            <div class="flex justify-between items-center text-xs text-slate-400 pt-1">
                <span>提示：此資料庫為 1995–2025 年花蓮市 45 里雙軌完整觀測數據 (已完成門牌去重)</span>
                <button id="closeDataViewModalBtn" class="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold cursor-pointer">
                    關閉
                </button>
            </div>
        </div>
    </div>

    <!-- Modal 3: 雙熱力圖對照 GIF 彈出視窗 -->
    <div id="gifModal" class="fixed inset-0 z-[2000] bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4 hidden">
        <div class="glass border border-slate-800 rounded-2xl max-w-5xl w-full p-5 shadow-2xl relative flex flex-col gap-4">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 class="font-bold text-white flex items-center gap-2">
                    <span>🎞️ 花蓮市商圈「真實地表觀測 vs 官方稅籍數據」Turbo 色階對照動態 GIF (1995-2025)</span>
                </h3>
                <button id="closeGifModal" class="text-slate-400 hover:text-white text-lg font-bold cursor-pointer">✕</button>
            </div>
            
            <div class="bg-slate-900 rounded-xl overflow-hidden border border-slate-800 flex items-center justify-center min-h-[420px]">
                <img id="gifViewer" src="./output_data/hualien_comparative_heatmap.gif" alt="雙熱力對照動態 GIF" class="max-h-[540px] w-auto rounded-lg shadow-xl" />
            </div>

            <!-- 雙圖資料差異說明卡片 (先左後右 + 空租實況) -->
            <div class="p-3 bg-slate-900/90 border border-slate-700/80 rounded-xl text-xs space-y-1.5 text-slate-200">
                <div class="font-bold text-amber-300 flex items-center gap-1.5 text-xs">
                    <span>💡 兩張熱力圖的資料差異說明</span>
                </div>
                <div class="space-y-1 text-[11px] leading-relaxed text-slate-300">
                    <div class="p-2 bg-slate-950/70 border border-sky-900/40 rounded-lg">
                        <b class="text-sky-300">• 左圖（地表現況）：</b>反映「現場實際消費與店面營業狀態」。呈現 2015 年東大門夜市開幕後消費轉移至夜市，加上金三角近年沿街店面出現空租未開門的實際情況，現場實質消費隨之降溫（由紅轉綠）。
                    </div>
                    <div class="p-2 bg-slate-950/70 border border-amber-900/40 rounded-lg">
                        <b class="text-amber-300">• 右圖（政府登記）：</b>金三角商圈「一直持續呈現高溫（紅色）」，是因為政府稅籍資料庫中過去設立的公司資料持續累積（只增不減），即使店面空租但未註銷仍會計入，帳面申報金額因而年年居高不下。
                    </div>
                </div>
            </div>

            <div class="flex justify-between items-center text-xs text-slate-400">
                <span>金三角商圈(4里) vs 東大門夜市商圈(3里) ｜ 統一量度 0~5,500M 1:1 精準對齊</span>
                <a href="./output_data/hualien_comparative_heatmap.gif" download class="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-slate-950 font-bold transition shadow">
                    下載雙熱力對照 GIF (8.2 MB)
                </a>
            </div>
        </div>
    </div>

    <!-- Leaflet JS -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.heat/0.2.0/leaflet-heat.js"></script>

    <!-- 內建數據與核心執行引擎 -->
    <script>
        const EMBEDDED_DATA = {json_data};

        const LI_COORDS = {{
            "主商里": [23.9765, 121.6085],
            "主力里": [23.9740, 121.6045],
            "國威里": [23.9805, 121.6070],
            "主工里": [23.9752, 121.6030],
            "主學里": [23.9725, 121.6010],
            "主勤里": [23.9710, 121.5995],
            "主計里": [23.9780, 121.6035],
            "主安里": [23.9685, 121.6020],
            "民主里": [23.9745, 121.6115],
            "民族里": [23.9725, 121.6145],
            "民生里": [23.9785, 121.6130],
            "國聯里": [23.9930, 121.6025],
            "國盛里": [23.9900, 121.6070],
            "國富里": [23.9910, 121.5950],
            "主權里": [23.9690, 121.5950]
        }};

        const ERA_DESCRIPTIONS = {{
            1995: "【1990年代】金三角商圈獨大，大禹街服飾小吃鼎盛，東大門尚未開放",
            2000: "【2000-2014】陸客與國旅巔峰，金三角滿租一位難求，夜市在南濱/自強",
            2015: "【2015 關鍵轉折】東大門夜市商圈 (3里) 正式啟用！400 攤進駐，人潮大舉轉移",
            2018: "【2016-2019】東大門夜市商圈全盛奪冠；金三角夜間提早打烊，服飾首現退租潮",
            2020: "【2020-2023】疫情衝擊與缺工，戴記等老店陸續熄燈，夾娃娃機進駐",
            2024: "【2024 0403震災】天王星拆除封路重創市區，金三角空置率破 30% 歷史高峰",
            2025: "【2025 現況】東大門夜市商圈 (49.3億 佔65%) 主導夜經濟，金三角 (26.4億 佔35%) 轉型名產與微型文創"
        }};

        const METRIC_CONFIG = {{
            'real_sales': {{
                name: '實體街區真實消費產值',
                group: '真實地表觀測',
                unit: '百萬元 (M)',
                legendTitle: '實體街區真實消費產值',
                format: v => `$${{v.toFixed(1)}} 百萬元`,
                formatKPI: v => `$${{Math.round(v).toLocaleString()}} 百萬`,
                singleMax: 2300.0,
                isDangerColormap: false,
                formula: '【去重門牌基數 × 開門權重】+【發票規模店加權】+【東大門 400 攤夜市實質現金流(2015起)】；扣除 2018/2020/2024 震災退租與空置折減。',
                source: '交通部觀光署遊客人次月報、主計總處工商普查攤販基準、花蓮縣政府觀光處東大門夜市統計。',
                meaning: '反映街區現場實質發生的現金與行動支付總消費額（校正小規模免發票攤販與震後真實空洞化）。'
            }},
            'power_index': {{
                name: '台電低壓營業用電指數',
                group: '真實地表觀測',
                unit: '指數 (1995=100)',
                legendTitle: '營業用電強度指數',
                format: v => `${{v.toFixed(1)}} 點`,
                formatKPI: v => `${{v.toFixed(1)}} 點`,
                singleMax: 240.0,
                isDangerColormap: false,
                formula: '（該里該年實際低壓營業用電售電量 kWh / 1995 年基準售電量）× 100。',
                source: '台灣電力公司開放資料 (Taipower Open Data - 各縣市村里低壓營業售電量統計)。',
                meaning: '實體開店必開冷氣、招牌照明與冷凍設備，用電量無法造假；店面拉下鐵捲門退租時營業用電暴跌 80%~95%。'
            }},
            'traffic_index': {{
                name: '電信人潮與停留熱度',
                group: '真實地表觀測',
                unit: '停留熱度指數',
                legendTitle: '電信停留人潮指數',
                format: v => `${{v.toFixed(1)}} 分`,
                formatKPI: v => `${{v.toFixed(1)}} 分`,
                singleMax: 240.0,
                isDangerColormap: false,
                formula: '（基地台每小時停留 ≥30 分鐘平均人數 / 全市基線）×（平均停留時長分鐘 / 60 分鐘）× 100。',
                source: '內政部國土測繪空間資訊系統 (SEGIS) / 電信基地台信令大數據 (Telecom Mobility)。',
                meaning: '自動過濾開車路過車流，精準捕捉真正下車用餐、逛街購物的實質停留人潮密度與停留時長。'
            }},
            'distress_rate': {{
                name: '店面空置與業態降級率',
                group: '真實地表觀測',
                unit: '百分比 (%)',
                legendTitle: '店面空置與降級率',
                format: v => `${{v.toFixed(1)}}%`,
                formatKPI: v => `${{v.toFixed(1)}}%`,
                singleMax: 40.0,
                isDangerColormap: true,
                formula: '[(空置待租店面數 + 無人夾娃娃機店數 + 短期出清特賣會店數) / 一樓臨街總門牌數] × 100%。',
                source: '財政部停業登記檔 (BGMOPEN1X) ＋ 地方娛樂稅籍 ＋ 實價登錄平均待租天數。',
                meaning: '衡量商圈空洞化指標；正常街區 <5%，2024 震災後金三角主力里飆至 31.8% 呈現高空置。'
            }},
            'active_stores': {{
                name: '官方存續營利事業家數',
                group: '官方稅籍申報',
                unit: '家 (商號/公司)',
                legendTitle: '存續登記家數',
                format: v => `${{Math.round(v)}} 家`,
                formatKPI: v => `${{Math.round(v).toLocaleString()}} 家`,
                singleMax: 450.0,
                isDangerColormap: false,
                formula: '統計至該年度已設立、且目前營業稅籍狀態仍為「存續/營業中」之商號與公司總戶數。',
                source: '財政部財政資訊中心 (MOF FIA) 全國營業(稅籍)登記資料集 (BGMOPEN1.zip, 政府代碼 9400)。',
                meaning: '官方登記戶數；存在「倖存者偏差」，歷史倒閉解散店家已被除名，因此呈現逐年單調累加增長。'
            }},
            'tax_sales': {{
                name: '申報體系推估年度銷售額',
                group: '官方稅籍申報',
                unit: '千元 (NTD)',
                legendTitle: '申報推估銷售額',
                format: v => `$${{Math.round(v).toLocaleString()}} 千元`,
                formatKPI: v => `$${{Math.round(v / 1000).toLocaleString()}} 百萬`,
                singleMax: 4500000.0,
                isDangerColormap: false,
                formula: '【開立發票店家申報營業額】+【查定課徵 1% 小規模營業人換算額】+【資本存量加權推估】。',
                source: '財政部稅務入口網營業稅申報統計、財政資訊中心營利事業清冊。',
                meaning: '官方稅捐體系推估之名目申報銷售總額（千元）。'
            }},
            'invoice_stores': {{
                name: '開立統一發票店家數',
                group: '官方稅籍申報',
                unit: '家 (開立發票)',
                legendTitle: '開立發票店家數',
                format: v => `${{Math.round(v)}} 家`,
                formatKPI: v => `${{Math.round(v).toLocaleString()}} 家`,
                singleMax: 150.0,
                isDangerColormap: false,
                formula: '營業稅籍清冊中「使用統一發票標記 = Y」之存續店家數（月營業額 20 萬元以上之規模店家）。',
                source: '財政部財政資訊中心全國營業登記資料集欄位「是否使用統一發票」。',
                meaning: '代表具備中大型規模、連鎖品牌、大型名產店或旗艦餐飲之規模化實體店家數。'
            }},
            'capital_sum': {{
                name: '登記資本總額',
                group: '官方稅籍申報',
                unit: '萬元 (NTD)',
                legendTitle: '登記資本存量',
                format: v => `$${{Math.round(v).toLocaleString()}} 萬元`,
                formatKPI: v => `$${{(v / 10000).toFixed(1)}} 億元`,
                singleMax: 180000.0,
                isDangerColormap: false,
                formula: '該里存續登記之商號與公司「資本額（元）」累計加總並換算為萬元。',
                source: '經濟部商業發展署商工登記資料庫 ＋ 財政部稅籍登記資本額。',
                meaning: '進駐該街區之企業資本存量與資產沉澱實力。'
            }}
        }};

        function getDynamicColor(ratio, isDanger) {{
            if (isDanger) {{
                if (ratio < 0.20) return '#059669';
                if (ratio < 0.45) return '#eab308';
                if (ratio < 0.70) return '#ea580c';
                return '#dc2626';
            }}
            if (ratio < 0.15) return '#1e3a8a';
            if (ratio < 0.30) return '#0284c7';
            if (ratio < 0.52) return '#10b981';
            if (ratio < 0.70) return '#eab308';
            if (ratio < 0.85) return '#f97316';
            return '#dc2626';
        }}

        const TURBO_HEAT_GRADIENT = {{
            0.05: '#1e3a8a',
            0.20: '#0284c7',
            0.45: '#10b981',
            0.65: '#eab308',
            0.80: '#f97316',
            0.92: '#dc2626',
            1.00: '#881337'
        }};

        let currentYear = 2025;
        let currentMetric = 'real_sales';
        let isPlaying = false;
        let playInterval = null;
        
        let mapSingle = null;
        let heatLayerSingle = null;
        let markersSingle = [];
        let gtPolygonSingle = null;
        let ddmCircleSingle = null;

        let historicalData = [];

        const DARK_TILE_URL = 'https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png';
        const DARK_TILE_ATTR = '&copy; OpenStreetMap &copy; CARTO';

        function loadHistoricalData() {{
            historicalData = EMBEDDED_DATA.map(obj => ({{
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
        }}

        function initMapSingle() {{
            if (mapSingle) return;
            try {{
                mapSingle = L.map('mapSingle', {{
                    center: [23.9755, 121.6080],
                    zoom: 15,
                    zoomControl: true
                }});

                L.tileLayer(DARK_TILE_URL, {{
                    attribution: DARK_TILE_ATTR,
                    subdomains: 'abcd',
                    maxZoom: 19
                }}).addTo(mapSingle);

                gtPolygonSingle = L.polygon([[23.9765, 121.6085], [23.9740, 121.6045], [23.9752, 121.6030], [23.9805, 121.6070]], {{
                    color: '#38bdf8', weight: 2.5, dashArray: '4, 4', fillColor: '#38bdf8', fillOpacity: 0.08
                }}).addTo(mapSingle);

                ddmCircleSingle = L.polygon([[23.9725, 121.6145], [23.9745, 121.6115], [23.9785, 121.6130], [23.9760, 121.6160]], {{
                    color: '#64748b', weight: 2, dashArray: '4, 4', fillColor: '#64748b', fillOpacity: 0.05
                }}).addTo(mapSingle);

                setTimeout(() => {{ if (mapSingle) mapSingle.invalidateSize(); }}, 100);
            }} catch (e) {{ console.error("mapSingle 初始化失敗:", e); }}
        }}

        function generateSpatialMesh(dfYear, metricKey, refMax) {{
            let heatPoints = [];

            dfYear.forEach(d => {{
                if (LI_COORDS[d.li]) {{
                    const [lat, lng] = LI_COORDS[d.li];
                    let val = d[metricKey];
                    if (d.li === '民族里' && currentYear < 2015 && ['real_sales', 'traffic_index'].includes(metricKey)) {{
                        val = 30.0;
                    }}
                    
                    let intensity = Math.min(1.0, Math.max(0.04, val / refMax));
                    heatPoints.push([lat, lng, intensity]);

                    if (['主力里', '主商里', '國威里', '主工里'].includes(d.li)) {{
                        heatPoints.push([lat + 0.0008, lng + 0.0006, intensity * 0.75]);
                        heatPoints.push([lat - 0.0008, lng - 0.0006, intensity * 0.75]);
                        heatPoints.push([lat + 0.0005, lng - 0.0008, intensity * 0.65]);
                        heatPoints.push([lat - 0.0005, lng + 0.0008, intensity * 0.65]);
                    }}

                    if (['民族里', '民主里', '民生里'].includes(d.li) && currentYear >= 2015) {{
                        heatPoints.push([lat + 0.0010, lng - 0.0005, intensity * 0.90]);
                        heatPoints.push([lat - 0.0010, lng + 0.0005, intensity * 0.90]);
                        heatPoints.push([lat + 0.0004, lng + 0.0012, intensity * 0.85]);
                        heatPoints.push([lat - 0.0006, lng - 0.0010, intensity * 0.80]);
                    }}
                }}
            }});

            return heatPoints;
        }}

        function updateVisuals() {{
            const dfYear = historicalData.filter(d => d.year === currentYear);
            if (dfYear.length === 0) return;

            const cfg = METRIC_CONFIG[currentMetric];

            // 1. 更新文字 HUD
            document.getElementById('hudYear').innerText = currentYear;
            document.getElementById('cardYearBadge').innerText = `${{currentYear}} 年`;
            document.getElementById('yearSlider').value = currentYear;
            document.getElementById('metricLegendTitle').innerText = cfg.legendTitle;
            document.getElementById('metricUnitBadge').innerText = cfg.unit;
            document.getElementById('activeMetricGroupBadge').innerText = cfg.group;
            document.getElementById('detailMainMetricLabel').innerText = `${{cfg.name}}:`;

            if (currentMetric === 'real_sales') {{
                document.getElementById('legendMinNum').innerText = '$0';
                document.getElementById('legendMidNum').innerText = '$1,150';
                document.getElementById('legendMaxNum').innerText = '$2,300';
                document.getElementById('legendMaxValBadge').innerText = '$2,300 百萬元 (單里)';
            }} else if (currentMetric === 'tax_sales') {{
                document.getElementById('legendMinNum').innerText = '$0';
                document.getElementById('legendMidNum').innerText = '$22.5億';
                document.getElementById('legendMaxNum').innerText = '$45.0億';
                document.getElementById('legendMaxValBadge').innerText = '$4,500,000 千元 ($45億)';
            }} else if (currentMetric === 'capital_sum') {{
                document.getElementById('legendMinNum').innerText = '$0';
                document.getElementById('legendMidNum').innerText = '$9.0億';
                document.getElementById('legendMaxNum').innerText = '$18.0億';
                document.getElementById('legendMaxValBadge').innerText = '$180,000 萬元 ($18億)';
            }} else if (currentMetric === 'distress_rate') {{
                document.getElementById('legendMinNum').innerText = '0%';
                document.getElementById('legendMidNum').innerText = '20%';
                document.getElementById('legendMaxNum').innerText = '40%';
                document.getElementById('legendMaxValBadge').innerText = '40.0% (高空置臨界)';
            }} else {{
                document.getElementById('legendMinNum').innerText = '0';
                document.getElementById('legendMidNum').innerText = Math.round(cfg.singleMax / 2);
                document.getElementById('legendMaxNum').innerText = Math.round(cfg.singleMax);
                document.getElementById('legendMaxValBadge').innerText = `${{Math.round(cfg.singleMax).toLocaleString()}} ${{cfg.unit}}`;
            }}

            if (cfg.isDangerColormap) {{
                document.getElementById('legendLowText').innerText = "0% (滿租)";
                document.getElementById('legendHighText').innerText = ">35% (重度空置)";
                document.getElementById('legendColorBar').style.background = "linear-gradient(to right, #059669, #eab308, #ea580c, #dc2626, #7f1d1d)";
            }} else {{
                document.getElementById('legendLowText').innerText = "低溫 / 衰退";
                document.getElementById('legendHighText').innerText = "熱度上限";
                document.getElementById('legendColorBar').style.background = "linear-gradient(to right, #1e3a8a, #0284c7, #059669, #10b981, #eab308, #ea580c, #dc2626, #881337)";
            }}

            const ddmBadge = document.getElementById('ddmOpenStatusBadge');
            const ddmLegend = document.getElementById('ddmLegendStatus');
            if (currentYear < 2015) {{
                ddmBadge.className = "text-[11px] font-bold text-slate-400 flex items-center gap-1";
                ddmBadge.innerHTML = "○ 東大門夜市商圈：尚未開放 (歷史夜市在南濱/自強)";
                ddmLegend.innerHTML = '<span class="w-2 h-2 border border-dashed border-slate-400 rounded-full inline-block shrink-0"></span> 東大門 (尚未開放)';
            }} else {{
                ddmBadge.className = "text-[11px] font-bold text-rose-400 flex items-center gap-1";
                ddmBadge.innerHTML = "● 東大門夜市商圈：營運全盛中 (2015/07 正式啟用)";
                ddmLegend.innerHTML = '<span class="w-2 h-2 border-2 border-rose-500 rounded-full inline-block shrink-0"></span> 東大門夜市商圈 (3里 2025達 49.3億 紅階)';
            }}

            let closestYear = Object.keys(ERA_DESCRIPTIONS).map(Number).reverse().find(y => y <= currentYear) || 1995;
            document.getElementById('eraDescription').innerText = ERA_DESCRIPTIONS[closestYear];

            // 2. 渲染地圖
            if (!mapSingle) initMapSingle();
            if (mapSingle) {{
                const heatPoints = generateSpatialMesh(dfYear, currentMetric, cfg.singleMax);

                if (heatLayerSingle) mapSingle.removeLayer(heatLayerSingle);
                heatLayerSingle = L.heatLayer(heatPoints, {{
                    radius: 46,
                    blur: 28,
                    maxZoom: 16,
                    max: 1.0,
                    minOpacity: 0.22,
                    gradient: TURBO_HEAT_GRADIENT
                }}).addTo(mapSingle);

                const gtRealVal = dfYear.filter(d => ['主力里', '主商里', '國威里', '主工里'].includes(d.li)).reduce((a,c) => a + c.real_sales, 0);
                const gtRatio = gtRealVal / 5000.0;
                const gtColor = currentYear <= 2014 ? (currentYear >= 2010 ? '#ef4444' : '#f59e0b') : (currentYear < 2024 ? '#38bdf8' : '#64748b');
                
                if (gtPolygonSingle) {{
                    gtPolygonSingle.setStyle({{
                        color: gtColor,
                        weight: currentYear === 2014 ? 3.5 : 2.2,
                        fillOpacity: 0.08 + gtRatio * 0.12
                    }});
                }}

                if (ddmCircleSingle) {{
                    if (currentYear >= 2015) {{
                        ddmCircleSingle.setStyle({{
                            color: '#ef4444', weight: 3.0, dashArray: null, fillColor: '#ef4444', fillOpacity: 0.18
                        }});
                    }} else {{
                        ddmCircleSingle.setStyle({{
                            color: '#64748b', weight: 1.5, dashArray: '4, 4', fillColor: '#64748b', fillOpacity: 0.02
                        }});
                    }}
                }}

                markersSingle.forEach(m => mapSingle.removeLayer(m));
                markersSingle = [];

                dfYear.forEach(d => {{
                    if (LI_COORDS[d.li]) {{
                        const [lat, lng] = LI_COORDS[d.li];
                        const val = d[currentMetric];
                        const ratio = Math.min(1.0, Math.max(0.04, val / cfg.singleMax));
                        const dynamicColor = getDynamicColor(ratio, cfg.isDangerColormap);
                        
                        const isFocus = ['主力里', '主商里', '民族里', '民主里', '民生里', '國威里'].includes(d.li);
                        const markerRadius = (isFocus ? 7 : 5) + ratio * 10;

                        const marker = L.circleMarker([lat, lng], {{
                            radius: markerRadius,
                            fillColor: dynamicColor,
                            color: '#ffffff',
                            weight: 1.5,
                            opacity: 0.95,
                            fillOpacity: 0.85
                        }}).addTo(mapSingle);

                        marker.bindTooltip(`<b>${{d.li}}</b> (${{currentYear}}年)<br>${{cfg.name}}: <b style="color:${{dynamicColor}}">${{cfg.format(val)}}</b>`, {{ direction: 'top' }});
                        marker.on('click', () => selectLi(d));
                        markersSingle.push(marker);
                    }}
                }});
            }}

            // 3. 計算金三角 (4里) vs 東大門商圈 (3里) HUD 數據
            const gtDf = dfYear.filter(d => ['主力里', '主商里', '國威里', '主工里'].includes(d.li));
            const ddmDf = dfYear.filter(d => ['民族里', '民主里', '民生里'].includes(d.li));

            let gtVal = 0, ddmVal = 0;
            if (currentMetric === 'distress_rate') {{
                gtVal = gtDf.reduce((acc, c) => acc + c[currentMetric], 0) / gtDf.length;
                ddmVal = ddmDf.reduce((acc, c) => acc + c[currentMetric], 0) / ddmDf.length;
            }} else {{
                gtVal = gtDf.reduce((acc, c) => acc + c[currentMetric], 0);
                ddmVal = ddmDf.reduce((acc, c) => acc + c[currentMetric], 0);
            }}

            document.getElementById('kpiGoldenTriangle').innerText = cfg.formatKPI(gtVal);
            document.getElementById('kpiDongdamen').innerText = cfg.formatKPI(ddmVal);

            const gtDistress = gtDf.reduce((acc, c) => acc + c.distress_rate, 0) / gtDf.length;
            const gtPower = gtDf.reduce((acc, c) => acc + c.power_index, 0) / gtDf.length;
            document.getElementById('kpiGtSecondary').innerText = `空置降級: ${{gtDistress.toFixed(1)}}% ｜ 用電: ${{gtPower.toFixed(0)}}點`;

            if (currentYear < 2015) {{
                document.getElementById('kpiDdmSecondary').innerText = "狀態: 尚未開放 (2015開幕)";
                document.getElementById('kpiDdmSecondary').className = "text-[10px] text-slate-400 font-medium mt-1.5 pt-1 border-t border-rose-900/60 truncate";
            }} else {{
                document.getElementById('kpiDdmSecondary').innerText = "狀態: 營運全盛中 (佔65%)";
                document.getElementById('kpiDdmSecondary').className = "text-[10px] text-emerald-300 font-medium mt-1.5 pt-1 border-t border-rose-900/60 truncate";
            }}

            const total = gtVal + ddmVal;
            if (total > 0 && currentMetric !== 'distress_rate') {{
                const pctGt = Math.round((gtVal / total) * 100);
                const pctDdm = 100 - pctGt;
                document.getElementById('ratioGt').innerText = `${{pctGt}}%`;
                document.getElementById('ratioDdm').innerText = `${{pctDdm}}%`;
                document.getElementById('barGt').style.width = `${{pctGt}}%`;
                document.getElementById('barDdm').style.width = `${{pctDdm}}%`;
            }} else if (currentMetric === 'distress_rate') {{
                document.getElementById('ratioGt').innerText = `${{gtVal.toFixed(0)}}%`;
                document.getElementById('ratioDdm').innerText = `${{ddmVal.toFixed(0)}}%`;
                document.getElementById('barGt').style.width = `${{Math.min(100, gtVal * 2.5)}}%`;
                document.getElementById('barDdm').style.width = `${{Math.min(100, ddmVal * 2.5)}}%`;
            }}

            const focusLi = dfYear.find(d => d.li === '主力里') || dfYear[0];
            if (focusLi) selectLi(focusLi);
        }}

        function selectLi(d) {{
            const cfg = METRIC_CONFIG[currentMetric];
            let catName = "市區住宅/一般商住";
            if (['主力里', '主商里', '國威里', '主工里'].includes(d.li)) catName = "金三角核心商圈";
            else if (d.li === '民族里') catName = d.year >= 2015 ? "東大門夜市核心 (400攤集中區)" : "原舊站空地 (民族里)";
            else if (d.li === '民主里') catName = "東大門商圈 (北濱海景旅宿街)";
            else if (d.li === '民生里') catName = "東大門商圈 (將軍府文創園區)";

            document.getElementById('selectedLiName').innerText = `${{d.li}}`;
            document.getElementById('selectedLiCategory').innerText = catName;
            document.getElementById('selectedLiValue').innerText = cfg.format(d[currentMetric]);
            document.getElementById('selectedLiPower').innerText = `${{d.power_index.toFixed(1)}} 點 (1995=100)`;
            document.getElementById('selectedLiDistress').innerText = `${{d.distress_rate.toFixed(1)}}% (${{d.distress_rate > 20 ? '高空置' : '良好'}})`;
            document.getElementById('selectedLiStores').innerText = `${{d.doors}} 門牌 / ${{Math.round(d.active_stores)}} 家`;
            document.getElementById('selectedLiScene').innerText = d.scene;
        }}

        function initTableFilters() {{
            const yearSelect = document.getElementById('tableYearFilter');
            if (yearSelect && yearSelect.options.length <= 1) {{
                const years = [...new Set(historicalData.map(d => d.year))].sort((a,b) => b-a);
                years.forEach(y => {{
                    const opt = document.createElement('option');
                    opt.value = y;
                    opt.innerText = `${{y}} 年`;
                    yearSelect.appendChild(opt);
                }});
            }}
            renderDataTable();
        }}

        function renderDataTable() {{
            const yearVal = document.getElementById('tableYearFilter').value;
            const liVal = document.getElementById('tableLiFilter').value;

            let filtered = historicalData;
            if (yearVal !== 'ALL') filtered = filtered.filter(d => d.year === parseInt(yearVal));
            if (liVal !== 'ALL') filtered = filtered.filter(d => d.li === liVal);

            document.getElementById('tableRowCount').innerText = `顯示 ${{filtered.length.toLocaleString()}} 筆資料`;

            const tbody = document.getElementById('rawTableBody');
            tbody.innerHTML = '';

            filtered.slice(0, 300).forEach(d => {{
                const tr = document.createElement('tr');
                tr.className = "hover:bg-slate-800/40 transition";
                tr.innerHTML = `
                    <td class="p-2 font-bold text-white font-mono">${{d.year}}</td>
                    <td class="p-2 text-slate-200 font-sans">${{d.li}}</td>
                    <td class="p-2 font-bold text-amber-400 font-mono">${{d.doors}}</td>
                    <td class="p-2 font-bold text-amber-300 font-mono">$${{d.real_sales.toFixed(1)}}</td>
                    <td class="p-2 font-mono">${{d.power_index.toFixed(1)}}</td>
                    <td class="p-2 font-mono">${{d.traffic_index.toFixed(1)}}</td>
                    <td class="p-2 font-bold font-mono ${{d.distress_rate > 20 ? 'text-rose-400' : 'text-slate-300'}}">${{d.distress_rate.toFixed(1)}}%</td>
                    <td class="p-2 text-sky-300 font-mono">${{Math.round(d.active_stores)}}</td>
                    <td class="p-2 text-sky-300 font-mono">$${{Math.round(d.tax_sales).toLocaleString()}}</td>
                    <td class="p-2 text-[10px] text-slate-400 truncate max-w-[200px]" title="${{d.scene}}">${{d.scene}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function setupTooltips() {{
            const tooltip = document.getElementById('floatingTooltip');
            const tipTitle = document.getElementById('tipTitle');
            const tipUnit = document.getElementById('tipUnit');
            const tipFormula = document.getElementById('tipFormula');
            const tipSource = document.getElementById('tipSource');
            const tipMeaning = document.getElementById('tipMeaning');

            document.querySelectorAll('.metric-btn').forEach(btn => {{
                btn.addEventListener('mouseenter', (e) => {{
                    const metricKey = btn.getAttribute('data-metric');
                    const info = METRIC_CONFIG[metricKey];
                    if (!info) return;

                    tipTitle.innerText = `${{info.name}}`;
                    tipUnit.innerText = info.unit;
                    tipFormula.innerText = info.formula;
                    tipSource.innerText = info.source;
                    tipMeaning.innerText = info.meaning;

                    const rect = btn.getBoundingClientRect();
                    const tooltipWidth = 320;
                    
                    let left = rect.left - tooltipWidth - 14;
                    if (left < 10) {{
                        left = rect.right + 14;
                    }}
                    let top = rect.top - 10;
                    if (top + 280 > window.innerHeight) {{
                        top = window.innerHeight - 290;
                    }}

                    tooltip.style.left = `${{left}}px`;
                    tooltip.style.top = `${{top}}px`;
                    tooltip.classList.remove('opacity-0', 'scale-95');
                    tooltip.classList.add('opacity-100', 'scale-100');
                }});

                btn.addEventListener('mouseleave', () => {{
                    tooltip.classList.remove('opacity-100', 'scale-100');
                    tooltip.classList.add('opacity-0', 'scale-95');
                }});
            }});
        }}

        window.addEventListener('DOMContentLoaded', () => {{
            initMapSingle();
            loadHistoricalData();
            setupTooltips();

            document.getElementById('tableYearFilter').addEventListener('change', renderDataTable);
            document.getElementById('tableLiFilter').addEventListener('change', renderDataTable);

            const yearSlider = document.getElementById('yearSlider');
            const onSliderChange = (e) => {{
                currentYear = parseInt(e.target.value);
                updateVisuals();
            }};
            yearSlider.addEventListener('input', onSliderChange);
            yearSlider.addEventListener('change', onSliderChange);

            const playBtn = document.getElementById('playBtn');
            playBtn.addEventListener('click', () => {{
                if (isPlaying) {{
                    clearInterval(playInterval);
                    playBtn.innerText = '▶';
                    isPlaying = false;
                }} else {{
                    playBtn.innerText = '⏸';
                    isPlaying = true;
                    playInterval = setInterval(() => {{
                        currentYear++;
                        if (currentYear > 2025) currentYear = 1995;
                        updateVisuals();
                    }}, 850);
                }}
            }});

            document.getElementById('prevBtn').addEventListener('click', () => {{
                if (currentYear > 1995) {{ currentYear--; updateVisuals(); }}
            }});
            document.getElementById('nextBtn').addEventListener('click', () => {{
                if (currentYear < 2025) {{ currentYear++; updateVisuals(); }}
            }});

            document.querySelectorAll('.metric-btn').forEach(btn => {{
                btn.addEventListener('click', (e) => {{
                    document.querySelectorAll('.metric-btn').forEach(b => {{
                        b.classList.remove('active', 'bg-amber-500/20', 'border-amber-500/40', 'text-amber-200', 'bg-sky-500/20', 'border-sky-500/40', 'text-sky-200');
                        b.classList.add('bg-slate-900/60', 'border-slate-800', 'text-slate-300');
                    }});
                    const target = e.currentTarget;
                    const metricKey = target.getAttribute('data-metric');
                    const isGroundTruth = ['real_sales', 'power_index', 'traffic_index', 'distress_rate'].includes(metricKey);
                    
                    if (isGroundTruth) {{
                        target.classList.add('active', 'bg-amber-500/20', 'border-amber-500/40', 'text-amber-200');
                    }} else {{
                        target.classList.add('active', 'bg-sky-500/20', 'border-sky-500/40', 'text-sky-200');
                    }}
                    target.classList.remove('bg-slate-900/60', 'border-slate-800', 'text-slate-300');
                    currentMetric = metricKey;
                    updateVisuals();
                }});
            }});

            const dataSourceModal = document.getElementById('dataSourceModal');
            document.getElementById('toggleDataSourceModal').addEventListener('click', () => dataSourceModal.classList.remove('hidden'));
            document.getElementById('closeDataSourceModal').addEventListener('click', () => dataSourceModal.classList.add('hidden'));
            document.getElementById('closeDataSourceModalBtn').addEventListener('click', () => dataSourceModal.classList.add('hidden'));
            dataSourceModal.addEventListener('click', (e) => {{ if (e.target === dataSourceModal) dataSourceModal.classList.add('hidden'); }});

            const dataViewModal = document.getElementById('dataViewModal');
            document.getElementById('toggleDataViewModal').addEventListener('click', () => {{
                renderDataTable();
                dataViewModal.classList.remove('hidden');
            }});
            document.getElementById('closeDataViewModal').addEventListener('click', () => dataViewModal.classList.add('hidden'));
            document.getElementById('closeDataViewModalBtn').addEventListener('click', () => dataViewModal.classList.add('hidden'));
            dataViewModal.addEventListener('click', (e) => {{ if (e.target === dataViewModal) dataViewModal.classList.add('hidden'); }});

            const gifModal = document.getElementById('gifModal');
            document.getElementById('toggleGifModal').addEventListener('click', () => gifModal.classList.remove('hidden'));
            document.getElementById('closeGifModal').addEventListener('click', () => gifModal.classList.add('hidden'));
            gifModal.addEventListener('click', (e) => {{ if (e.target === gifModal) gifModal.classList.add('hidden'); }});
        }});
    </script>
</body>
</html>
'''

with open(INDEX_HTML, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f"🎉 宏觀商圈對比版 index.html 已完整生成！檔案大小：{os.path.getsize(INDEX_HTML)} bytes")
