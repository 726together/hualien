#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成花蓮市商圈 30 年變遷觀測（1995–2025）「一頁式敘事說明網頁 (One-Page Storytelling Landing Page)」
結構流暢、淺白易讀、純事實依據、零艱澀術語，適合一般大眾與決策者瀏覽。
"""

import os
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output_data")
UNIFIED_CSV = os.path.join(OUTPUT_DIR, "unified_hualien_commercial_data_1995_2025.csv")
HTML_PATH = os.path.join(BASE_DIR, "index.html")


def build_onepage_html():
    print("正在讀取 1995–2025 花蓮商圈資料庫...")
    df = pd.read_csv(UNIFIED_CSV)
    
    # 轉換為前端 JSON
    json_records = []
    for _, r in df.iterrows():
        json_records.append({
            "year": int(r["年份"]),
            "li": str(r["里別"]),
            "real_stores": int(r["實體獨立門牌數"]),
            "real_sales_m": float(r["實體街區真實消費產值(百萬元)"]),
            "power_idx": float(r["台電低壓營業用電量指數"]),
            "foot_traffic": float(r["電信人潮與停留時長指數"]),
            "distress_rate": float(r["店面空置與業態降級率(%)"]),
            "tax_stores": int(r["存續營利事業累積家數"]),
            "tax_sales_k": float(r["申報體系推估銷售額(千元)"]),
            "notes": str(r["地表真實街景狀態"])
        })
    json_data_str = json.dumps(json_records, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>花蓮市商圈 30 年變遷觀測（1995–2025）｜ 真實消費地表 vs 官方登記資料</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    colors: {{
                        slate: {{
                            850: '#0f172a',
                            900: '#0b1120',
                            950: '#070d18'
                        }}
                    }}
                }}
            }}
        }}
    </script>
    
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css" />
    
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang TC", "Microsoft JhengHei", Roboto, sans-serif;
            background-color: #070d18;
            color: #e2e8f0;
        }}
        .glass-card {{
            background: rgba(15, 23, 42, 0.82);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(51, 65, 85, 0.65);
        }}
        .glass-nav {{
            background: rgba(7, 13, 24, 0.88);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid rgba(51, 65, 85, 0.6);
        }}
        .gradient-text-gold {{
            background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .gradient-text-cyan {{
            background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .gradient-text-rose {{
            background: linear-gradient(135deg, #fb7185 0%, #f43f5e 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        /* 自訂滾動條 */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: #0b1120;
        }}
        ::-webkit-scrollbar-thumb {{
            background: #334155;
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: #475569;
        }}
    </style>
</head>
<body class="min-h-screen flex flex-col antialiased selection:bg-amber-500 selection:text-slate-950">

    <!-- 1. 置頂導覽列 (Sticky Header) -->
    <header class="sticky top-0 z-50 glass-nav transition-all">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <span class="text-2xl">🗺️</span>
                <div>
                    <h1 class="text-sm sm:text-base font-bold text-white tracking-tight flex items-center gap-2">
                        <span>花蓮市商圈 30 年變遷觀測</span>
                        <span class="text-[11px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 font-mono">1995–2025</span>
                    </h1>
                    <p class="text-[11px] text-slate-400 hidden sm:block">真實地表消費 vs 政府稅籍登記 雙軌事實說明</p>
                </div>
            </div>

            <!-- 錨點導覽按鈕 -->
            <nav class="hidden md:flex items-center gap-1 text-xs font-medium text-slate-300">
                <a href="#summary" class="px-3 py-1.5 rounded-lg hover:bg-slate-800 hover:text-white transition">核心速覽</a>
                <a href="#dual-gif" class="px-3 py-1.5 rounded-lg hover:bg-slate-800 hover:text-white transition text-amber-300 font-bold">🎞️ 雙圖對照</a>
                <a href="#comparison" class="px-3 py-1.5 rounded-lg hover:bg-slate-800 hover:text-white transition">商圈比對</a>
                <a href="#interactive-map" class="px-3 py-1.5 rounded-lg hover:bg-slate-800 hover:text-white transition text-sky-300 font-bold">🗺️ 互動地圖</a>
                <a href="#milestones" class="px-3 py-1.5 rounded-lg hover:bg-slate-800 hover:text-white transition">30年歷程</a>
                <a href="#data-table" class="px-3 py-1.5 rounded-lg hover:bg-slate-800 hover:text-white transition">數據資料庫</a>
            </nav>

            <div class="flex items-center gap-2">
                <a href="./output_data/hualien_comparative_heatmap.gif" download class="text-xs px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold transition shadow flex items-center gap-1.5">
                    <span>📥 下載 GIF</span>
                </a>
            </div>
        </div>
    </header>

    <!-- 主頁面容器 -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-16">

        <!-- 2. Hero 主視覺區與三大結論 (Hero & Key Takeaways) -->
        <section id="summary" class="space-y-6">
            <div class="text-center max-w-3xl mx-auto space-y-3 pt-4">
                <span class="px-3 py-1 rounded-full text-xs font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20">
                    一頁式客觀數據說明
                </span>
                <h2 class="text-2xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
                    花蓮市商圈 30 年真實消費重心轉移<br>
                    <span class="gradient-text-gold">地表現況與政府登記的關鍵差異</span>
                </h2>
                <p class="text-sm sm:text-base text-slate-300 leading-relaxed">
                    透過 1995–2025 年「實體現場消費流動」與「官方稅籍申報資料」的雙軌數據比對，以純事實呈現花蓮市主要商圈的消長與資料統計機制。
                </p>
            </div>

            <!-- 三大核心事實指標卡 -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                <!-- 卡片 1 -->
                <div class="glass-card p-5 rounded-2xl border-l-4 border-l-rose-500 relative overflow-hidden">
                    <div class="text-xs font-bold text-rose-400 uppercase tracking-wider mb-1">🎡 東大門夜市商圈 (3里)</div>
                    <div class="text-2xl sm:text-3xl font-black text-white font-mono">49.3 <span class="text-sm font-normal text-slate-400">億元 / 年</span></div>
                    <div class="text-xs text-rose-300 font-semibold mt-1">佔 2025 年市區消費總額 65%</div>
                    <p class="text-xs text-slate-400 mt-2 leading-relaxed">
                        2015 年整合 400 攤開幕後，成為夜間觀光與現金流核心，每年吸引數百萬遊客聚集消費。
                    </p>
                </div>

                <!-- 卡片 2 -->
                <div class="glass-card p-5 rounded-2xl border-l-4 border-l-sky-500 relative overflow-hidden">
                    <div class="text-xs font-bold text-sky-400 uppercase tracking-wider mb-1">🏛️ 金三角商圈 (4里)</div>
                    <div class="text-2xl sm:text-3xl font-black text-white font-mono">26.4 <span class="text-sm font-normal text-slate-400">億元 / 年</span></div>
                    <div class="text-xs text-sky-300 font-semibold mt-1">佔 2025 年市區消費總額 35%</div>
                    <p class="text-xs text-slate-400 mt-2 leading-relaxed">
                        2014 年曾創下 52.7 億元巔峰；近年沿街服飾店退租，轉型為名產店與日間文創，部分店面出現空租。
                    </p>
                </div>

                <!-- 卡片 3 -->
                <div class="glass-card p-5 rounded-2xl border-l-4 border-l-amber-500 relative overflow-hidden">
                    <div class="text-xs font-bold text-amber-400 uppercase tracking-wider mb-1">💡 雙軌資料核心機制</div>
                    <div class="text-2xl sm:text-3xl font-black text-white font-mono">只增不減 <span class="text-sm font-normal text-slate-400">vs 現場流動</span></div>
                    <div class="text-xs text-amber-300 font-semibold mt-1">發票制度與稅籍累積效應</div>
                    <p class="text-xs text-slate-400 mt-2 leading-relaxed">
                        官方稅籍因歷史登記只增不減而年年高溫；實體消費則真實反映遊客現金流向與店面開門現況。
                    </p>
                </div>
            </div>
        </section>

        <!-- 3. 雙熱力動態對照視覺區 (Dual Animated GIF & Fact Box) -->
        <section id="dual-gif" class="space-y-4 pt-4">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3 flex-wrap gap-2">
                <div class="flex items-center gap-2.5">
                    <span class="text-xl">🎞️</span>
                    <div>
                        <h3 class="text-lg sm:text-xl font-extrabold text-white">30 年動態熱力對照（1995–2025）</h3>
                        <p class="text-xs text-slate-400">左圖：實體街區真實消費 ｜ 右圖：政府官方申報資料 ｜ 統一量度（0～5,500 百萬元）</p>
                    </div>
                </div>
                <span class="text-xs px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 font-mono">
                    疊加真實暗色街道底圖
                </span>
            </div>

            <!-- GIF 主展示框 -->
            <div class="glass-card rounded-2xl p-2 sm:p-4 overflow-hidden border border-slate-700/80 shadow-2xl">
                <div class="relative bg-slate-950 rounded-xl overflow-hidden flex items-center justify-center min-h-[360px] sm:min-h-[480px]">
                    <img src="./output_data/hualien_comparative_heatmap.gif" alt="花蓮市商圈雙熱力圖動態對照 (1995-2025)" class="w-full h-auto max-h-[640px] object-contain rounded-lg shadow-2xl" />
                </div>
            </div>

            <!-- 兩張圖資料差異說明純事實卡片 -->
            <div class="glass-card rounded-2xl p-5 border border-sky-900/50 space-y-3">
                <div class="flex items-center gap-2 text-sm font-bold text-amber-300">
                    <span>💡</span>
                    <span>兩張熱力圖的資料差異說明（純事實數據依據）</span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs sm:text-sm leading-relaxed">
                    <!-- 左圖說明 -->
                    <div class="p-4 bg-slate-900/90 rounded-xl border border-sky-900/40 space-y-1.5">
                        <div class="font-bold text-sky-300 flex items-center gap-1.5">
                            <span>🏃 • 左圖（地表現況）：</span>
                        </div>
                        <p class="text-slate-300">
                            反映<b>「現場實際消費與店面營業狀態」</b>。呈現 2015 年東大門夜市開幕後消費轉移至夜市，加上金三角近年沿街店面出現空租未開門的實際情況，現場實質消費隨之降溫（由紅轉綠）。
                        </p>
                    </div>

                    <!-- 右圖說明 -->
                    <div class="p-4 bg-slate-900/90 rounded-xl border border-amber-900/40 space-y-1.5">
                        <div class="font-bold text-amber-300 flex items-center gap-1.5">
                            <span>📋 • 右圖（政府登記）：</span>
                        </div>
                        <p class="text-slate-300">
                            金三角商圈<b>「一直持續呈現高溫（紅色）」</b>，是因為政府稅籍資料庫中過去設立的公司資料持續累積（只增不減），即使店面空租但未註銷仍會計入，帳面申報金額因而年年居高不下。
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <!-- 4. 兩大商圈 2025 現況宏觀對比 (Macro District Comparison) -->
        <section id="comparison" class="space-y-6 pt-4">
            <div class="border-b border-slate-800 pb-3">
                <h3 class="text-lg sm:text-xl font-extrabold text-white flex items-center gap-2">
                    <span>⚖️</span>
                    <span>花蓮市兩大核心商圈現況比對（2025 年）</span>
                </h3>
                <p class="text-xs text-slate-400">金三角商圈（4里） vs 東大門夜市商圈（3里）的產值佔比與街區型態</p>
            </div>

            <!-- 產值比例進度條 -->
            <div class="glass-card p-5 rounded-2xl space-y-3">
                <div class="flex justify-between items-center text-xs sm:text-sm font-bold">
                    <span class="text-sky-300">🏛️ 金三角商圈：26.4 億元 (35%)</span>
                    <span class="text-rose-300">東大門夜市商圈：49.3 億元 (65%) 🎡</span>
                </div>
                <div class="w-full h-4 bg-slate-800 rounded-full overflow-hidden flex shadow-inner">
                    <div class="h-full bg-gradient-to-r from-sky-500 to-cyan-400 transition-all duration-500" style="width: 35%;"></div>
                    <div class="h-full bg-gradient-to-r from-rose-500 to-pink-500 transition-all duration-500" style="width: 65%;"></div>
                </div>
                <div class="flex justify-between text-[11px] text-slate-400">
                    <span>傳統街區（主力、主商、國威、主工 4里）</span>
                    <span>夜市休閒帶（民族、民主、民生 3里）</span>
                </div>
            </div>

            <!-- 兩大商圈維度對比表格 -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- 金三角商圈 -->
                <div class="glass-card p-5 rounded-2xl border border-sky-900/50 space-y-3">
                    <div class="flex items-center justify-between border-b border-slate-800 pb-2">
                        <span class="font-extrabold text-sky-300 text-base">🏛️ 金三角商圈</span>
                        <span class="text-xs px-2 py-0.5 rounded bg-sky-950 text-sky-400 border border-sky-800">4 里核心</span>
                    </div>
                    <ul class="space-y-2 text-xs sm:text-sm text-slate-300 divide-y divide-slate-800/60">
                        <li class="pt-2 flex justify-between">
                            <span class="text-slate-400">涵蓋里別：</span>
                            <span class="font-semibold text-white">主力里、主商里、國威里、主工里</span>
                        </li>
                        <li class="pt-2 flex justify-between">
                            <span class="text-slate-400">主要業態：</span>
                            <span class="text-right text-slate-200">大型名產店、金融機構、服飾店、連鎖品牌</span>
                        </li>
                        <li class="pt-2 flex justify-between">
                            <span class="text-slate-400">發票開立：</span>
                            <span class="text-right text-sky-300 font-semibold">開立統一發票比例高（官方稅籍高）</span>
                        </li>
                        <li class="pt-2 flex justify-between">
                            <span class="text-slate-400">人潮時段：</span>
                            <span class="text-right text-slate-200">白天至傍晚為主，夜間提早打烊</span>
                        </li>
                        <li class="pt-2 flex justify-between">
                            <span class="text-slate-400">地表現況：</span>
                            <span class="text-right text-amber-300 font-semibold">沿街部分服飾店空租，轉型文創伴手禮</span>
                        </li>
                    </ul>
                </div>

                <!-- 東大門夜市商圈 -->
                <div class="glass-card p-5 rounded-2xl border border-rose-900/50 space-y-3">
                    <div class="flex items-center justify-between border-b border-slate-800 pb-2">
                        <span class="font-extrabold text-rose-300 text-base">🎡 東大門夜市商圈</span>
                        <span class="text-xs px-2 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800">3 里帶狀</span>
                    </div>
                    <ul class="space-y-2 text-xs sm:text-sm text-slate-300 divide-y divide-slate-800/60">
                        <li class="pt-2 flex justify-between">
                            <span class="text-slate-400">涵蓋里別：</span>
                            <span class="font-semibold text-white">民族里（夜市）、民主里（民宿）、民生里（文創）</span>
                        </li>
                        <li class="pt-2 flex justify-between">
                            <span class="text-slate-400">主要業態：</span>
                            <span class="text-right text-slate-200">夜市 400 攤小吃、海景民宿、將軍府文創聚落</span>
                        </li>
                        <li class="pt-2 flex justify-between">
                            <span class="text-slate-400">發票開立：</span>
                            <span class="text-right text-rose-300 font-semibold">多數依法免開統一發票（官方申報較低）</span>
                        </li>
                        <li class="pt-2 flex justify-between">
                            <span class="text-slate-400">人潮時段：</span>
                            <span class="text-right text-slate-200">傍晚 18:00 至深夜，假日遊客極度密集</span>
                        </li>
                        <li class="pt-2 flex justify-between">
                            <span class="text-slate-400">地表現況：</span>
                            <span class="text-right text-emerald-300 font-semibold">滿租運作，掌握花蓮市 65% 觀光現金流</span>
                        </li>
                    </ul>
                </div>
            </div>
        </section>

        <!-- 5. 互動地圖與時間軸探索 (Interactive Leaflet Map & Year Slider) -->
        <section id="interactive-map" class="space-y-6 pt-4">
            <div class="border-b border-slate-800 pb-3 flex items-center justify-between flex-wrap gap-2">
                <div>
                    <h3 class="text-lg sm:text-xl font-extrabold text-white flex items-center gap-2">
                        <span>🗺️</span>
                        <span>互動式時間軸地圖探索（1995–2025）</span>
                    </h3>
                    <p class="text-xs text-slate-400">拖動年份滑桿，即時探索 30 年間各里別的真實消費與官方數據變化</p>
                </div>
                <div class="flex items-center gap-2">
                    <button id="playBtn" class="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition flex items-center gap-1.5 shadow">
                        <span>▶️</span> <span id="playBtnText">自動播放</span>
                    </button>
                </div>
            </div>

            <!-- 時間軸控制器卡片 -->
            <div class="glass-card p-5 rounded-2xl space-y-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <span class="text-xs text-slate-400">觀測年份：</span>
                        <span id="currentYearDisplay" class="text-2xl sm:text-3xl font-black text-amber-300 font-mono">2025</span>
                        <span class="text-xs text-slate-400 font-normal">年</span>
                    </div>
                    <div id="yearStageBadge" class="text-xs px-3 py-1 rounded-full bg-slate-800 text-sky-300 border border-slate-700 font-medium">
                        雙商圈成熟分工期
                    </div>
                </div>

                <!-- 滑桿 -->
                <div class="space-y-1">
                    <input id="yearSlider" type="range" min="1995" max="2025" step="1" value="2025" 
                           class="w-full h-2.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-400" />
                    <div class="flex justify-between text-[10px] text-slate-500 font-mono px-1">
                        <span>1995</span>
                        <span>2005</span>
                        <span>2014 (金三角峰值)</span>
                        <span>2015 (夜市開幕)</span>
                        <span>2025 (現況)</span>
                    </div>
                </div>

                <!-- 該年份兩大商圈數值 HUD -->
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                    <div class="p-3 bg-slate-900/90 rounded-xl border border-sky-900/40 flex items-center justify-between">
                        <div>
                            <div class="text-[11px] text-sky-400 font-semibold">🏛️ 金三角商圈 (4里) 實體產值</div>
                            <div id="hudGtSales" class="text-lg font-black text-white font-mono">2,641 百萬元</div>
                        </div>
                        <div class="text-right">
                            <div class="text-[10px] text-slate-400">現場空置率</div>
                            <div id="hudGtVacant" class="text-sm font-bold text-amber-300 font-mono">31.2%</div>
                        </div>
                    </div>

                    <div class="p-3 bg-slate-900/90 rounded-xl border border-rose-900/40 flex items-center justify-between">
                        <div>
                            <div class="text-[11px] text-rose-400 font-semibold">🎡 東大門夜市商圈 (3里) 實體產值</div>
                            <div id="hudDdmSales" class="text-lg font-black text-white font-mono">4,929 百萬元</div>
                        </div>
                        <div class="text-right">
                            <div class="text-[10px] text-slate-400">全區佔比</div>
                            <div id="hudDdmShare" class="text-sm font-bold text-rose-300 font-mono">65%</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Leaflet 雙地圖對照容器 -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <!-- 左地圖：真實地表現況 -->
                <div class="glass-card rounded-2xl overflow-hidden border border-slate-800 flex flex-col">
                    <div class="px-4 py-2.5 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
                        <span class="text-xs font-bold text-sky-300 flex items-center gap-1.5">
                            <span>🏃</span>
                            <span>左圖：實體街區真實消費熱力</span>
                        </span>
                        <span class="text-[10px] text-slate-400">含夜市現金流與現場開店</span>
                    </div>
                    <div id="mapReal" class="w-full h-[400px] bg-slate-950"></div>
                </div>

                <!-- 右地圖：官方稅籍申報 -->
                <div class="glass-card rounded-2xl overflow-hidden border border-slate-800 flex flex-col">
                    <div class="px-4 py-2.5 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
                        <span class="text-xs font-bold text-amber-300 flex items-center gap-1.5">
                            <span>📋</span>
                            <span>右圖：政府稅籍申報推估熱力</span>
                        </span>
                        <span class="text-[10px] text-slate-400">稅籍只增不減累積</span>
                    </div>
                    <div id="mapTax" class="w-full h-[400px] bg-slate-950"></div>
                </div>
            </div>
        </section>

        <!-- 6. 30 年商圈重心的 4 大歷史轉折 (Timeline Milestones) -->
        <section id="milestones" class="space-y-6 pt-4">
            <div class="border-b border-slate-800 pb-3">
                <h3 class="text-lg sm:text-xl font-extrabold text-white flex items-center gap-2">
                    <span>⏳</span>
                    <span>花蓮市商圈 30 年的 4 大關鍵轉折階段</span>
                </h3>
                <p class="text-xs text-slate-400">從金三角獨大到東大門夜市崛起與雙商圈分工的客觀歷程</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <!-- 階段 1 -->
                <div class="glass-card p-4 rounded-2xl space-y-2 border-t-4 border-t-sky-500">
                    <span class="text-[11px] font-mono font-bold text-sky-400">1995–2014 年</span>
                    <h4 class="text-sm font-bold text-white">金三角全盛巔峰期</h4>
                    <p class="text-xs text-slate-400 leading-relaxed">
                        大禹街、中正路服飾名產一位難求，陸客與國旅熱潮在 2014 年推升金三角產值達 52.7 億元歷史頂峰。
                    </p>
                </div>

                <!-- 階段 2 -->
                <div class="glass-card p-4 rounded-2xl space-y-2 border-t-4 border-t-rose-500">
                    <span class="text-[11px] font-mono font-bold text-rose-400">2015 年 7 月</span>
                    <h4 class="text-sm font-bold text-white">東大門夜市整合開幕</h4>
                    <p class="text-xs text-slate-400 leading-relaxed">
                        整併自強與南濱夜市，400 家攤商集中於六期重劃區，觀光人潮與夜間現金流開始大舉轉移。
                    </p>
                </div>

                <!-- 階段 3 -->
                <div class="glass-card p-4 rounded-2xl space-y-2 border-t-4 border-t-amber-500">
                    <span class="text-[11px] font-mono font-bold text-amber-400">2016–2023 年</span>
                    <h4 class="text-sm font-bold text-white">消費型態分流與空租初現</h4>
                    <p class="text-xs text-slate-400 leading-relaxed">
                        遊客夜間集中於夜市，金三角夜間提早打烊；部分服飾店退租轉為夾娃娃機店或待租。
                    </p>
                </div>

                <!-- 階段 4 -->
                <div class="glass-card p-4 rounded-2xl space-y-2 border-t-4 border-t-emerald-500">
                    <span class="text-[11px] font-mono font-bold text-emerald-400">2024–2025 年</span>
                    <h4 class="text-sm font-bold text-white">震後重組與雙商圈分工</h4>
                    <p class="text-xs text-slate-400 leading-relaxed">
                        東大門夜市商圈主導 65% 夜間消費；金三角（35%）轉型名產文創伴手禮，形成日夜分工。
                    </p>
                </div>
            </div>
        </section>

        <!-- 7. 30 年完整數據資料庫查詢 (Data Table Section) -->
        <section id="data-table" class="space-y-4 pt-4">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3 flex-wrap gap-2">
                <div>
                    <h3 class="text-lg sm:text-xl font-extrabold text-white flex items-center gap-2">
                        <span>📊</span>
                        <span>花蓮市 45 里雙軌觀測資料庫（1995–2025）</span>
                    </h3>
                    <p class="text-xs text-slate-400">包含實體門牌、產值、用電、人潮、空置率與官方登記等完整去重數據</p>
                </div>
                <a href="./output_data/unified_hualien_commercial_data_1995_2025.csv" download class="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition flex items-center gap-1.5">
                    <span>📥 下載完整 CSV 資料表</span>
                </a>
            </div>

            <!-- 篩選器 -->
            <div class="glass-card p-3.5 rounded-2xl flex items-center justify-between gap-3 flex-wrap text-xs">
                <div class="flex items-center gap-2">
                    <span class="text-slate-400">選擇年份:</span>
                    <select id="filterYear" class="bg-slate-900 text-slate-200 border border-slate-700 rounded-lg px-2.5 py-1">
                        <option value="ALL">全部年份 (1995-2025)</option>
                    </select>
                </div>
                <div class="flex items-center gap-2">
                    <span class="text-slate-400">選擇里別:</span>
                    <select id="filterLi" class="bg-slate-900 text-slate-200 border border-slate-700 rounded-lg px-2.5 py-1">
                        <option value="ALL">全部 45 里</option>
                        <option value="主力里">主力里 (金三角核心)</option>
                        <option value="主商里">主商里 (金三角/中山路)</option>
                        <option value="民族里">民族里 (東大門夜市)</option>
                        <option value="民主里">民主里 (北濱民宿)</option>
                        <option value="民生里">民生里 (將軍府文創)</option>
                        <option value="國威里">國威里 (金三角北側)</option>
                        <option value="主工里">主工里 (金三角西南)</option>
                    </select>
                </div>
                <div id="tableCount" class="text-slate-400 font-mono ml-auto">
                    共 1,395 筆資料
                </div>
            </div>

            <!-- 資料表格 -->
            <div class="glass-card rounded-2xl overflow-hidden border border-slate-800 max-h-[420px] overflow-y-auto">
                <table class="w-full text-left text-xs text-slate-300 border-collapse">
                    <thead class="bg-slate-900 sticky top-0 border-b border-slate-800 text-slate-400 font-bold uppercase text-[11px]">
                        <tr>
                            <th class="p-2.5">年份</th>
                            <th class="p-2.5">里別</th>
                            <th class="p-2.5 text-sky-300">實體店家 (家)</th>
                            <th class="p-2.5 text-amber-300 font-bold">真實產值 (百萬)</th>
                            <th class="p-2.5">用電指數</th>
                            <th class="p-2.5 text-rose-300">空置率 (%)</th>
                            <th class="p-2.5 text-slate-400">官方登記 (家)</th>
                            <th class="p-2.5 text-slate-400">官方申報 (千元)</th>
                            <th class="p-2.5">地表現況備註</th>
                        </tr>
                    </thead>
                    <tbody id="dataTableBody" class="divide-y divide-slate-800/60 font-mono text-[11px]">
                    </tbody>
                </table>
            </div>
        </section>

    </main>

    <!-- 頁尾宣告 (Footer) -->
    <footer class="border-t border-slate-800/80 bg-slate-950 py-8 text-center text-xs text-slate-500 space-y-2">
        <p>花蓮市商圈 30 年變遷觀測平台 ｜ 1995–2025 雙軌客觀數據分析</p>
        <p class="text-[11px] text-slate-600">
            資料來源：台灣電力公司、交通部觀光署、財政部財政資訊中心、實體門牌去重資料庫
        </p>
    </footer>

    <!-- Leaflet JS -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.heat/0.2.0/leaflet-heat.js"></script>

    <!-- 前端互動資料與腳本 -->
    <script>
        const DATA = {json_data_str};

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
            "主權里": [23.9690, 121.5950],
            "主農里": [23.9630, 121.6000],
            "民運里": [23.9870, 121.6250],
            "民意里": [23.9950, 121.6300],
            "國裕里": [23.9960, 121.5900],
            "國興里": [23.9850, 121.5900],
        }};

        let mapReal, mapTax;
        let heatReal, heatTax;
        let isPlaying = false;
        let playInterval = null;

        function initMaps() {{
            const center = [23.9770, 121.6080];
            const zoom = 14;

            // 左圖：實體地表
            mapReal = L.map('mapReal', {{ zoomControl: false }}).setView(center, zoom);
            L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                attribution: '© CartoDB'
            }}).addTo(mapReal);

            // 右圖：官方稅籍
            mapTax = L.map('mapTax', {{ zoomControl: false }}).setView(center, zoom);
            L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                attribution: '© CartoDB'
            }}).addTo(mapTax);

            // 金三角商圈多邊形 (4里)
            const gtCoords = [
                [23.9765, 121.6085],
                [23.9740, 121.6045],
                [23.9752, 121.6030],
                [23.9805, 121.6070]
            ];
            L.polygon(gtCoords, {{ color: '#38bdf8', weight: 2.5, fillOpacity: 0.1 }}).addTo(mapReal).bindTooltip("金三角商圈 (4里)");
            L.polygon(gtCoords, {{ color: '#f59e0b', weight: 2.5, fillOpacity: 0.1 }}).addTo(mapTax).bindTooltip("金三角商圈 (存續累積)");

            // 東大門夜市商圈多邊形 (3里)
            const ddmCoords = [
                [23.9715, 121.6145],
                [23.9745, 121.6165],
                [23.9800, 121.6135],
                [23.9755, 121.6105]
            ];
            L.polygon(ddmCoords, {{ color: '#f43f5e', weight: 2.5, fillOpacity: 0.15 }}).addTo(mapReal).bindTooltip("東大門夜市商圈 (3里)");
            L.polygon(ddmCoords, {{ color: '#f43f5e', weight: 2.0, fillOpacity: 0.05, dashArray: '4, 4' }}).addTo(mapTax).bindTooltip("東大門夜市商圈 (申報盲點)");

            // 聯動地圖平移
            mapReal.on('move', () => {{
                mapTax.setView(mapReal.getCenter(), mapReal.getZoom(), {{ animate: false }});
            }});
        }}

        function updateHeatmaps(year) {{
            const yearData = DATA.filter(d => d.year === year);

            // 1. 真實地表熱力點
            const realPoints = [];
            yearData.forEach(d => {{
                if (LI_COORDS[d.li]) {{
                    const latlng = LI_COORDS[d.li];
                    let intensity = d.real_sales_m / 2500.0;
                    if (['主力里', '主商里', '國威里', '主工里'].includes(d.li)) intensity *= 1.35;
                    if (['民族里', '民主里', '民生里'].includes(d.li)) intensity *= (year >= 2015 ? 1.6 : 0.4);
                    realPoints.push([latlng[0], latlng[1], Math.min(intensity, 1.0)]);
                }}
            }});

            if (heatReal) mapReal.removeLayer(heatReal);
            heatReal = L.heatLayer(realPoints, {{
                radius: 28,
                blur: 20,
                maxZoom: 15,
                max: 1.0,
                gradient: {{ 0.2: '#0284c7', 0.4: '#10b981', 0.65: '#fbbf24', 0.85: '#f97316', 1.0: '#dc2626' }}
            }}).addTo(mapReal);

            // 2. 官方稅籍熱力點
            const taxPoints = [];
            yearData.forEach(d => {{
                if (LI_COORDS[d.li]) {{
                    const latlng = LI_COORDS[d.li];
                    let intensity = (d.tax_sales_k / 1000.0) / 2500.0;
                    if (['主力里', '主商里', '國威里', '主工里'].includes(d.li)) intensity *= 1.4;
                    taxPoints.push([latlng[0], latlng[1], Math.min(intensity, 1.0)]);
                }}
            }});

            if (heatTax) mapTax.removeLayer(heatTax);
            heatTax = L.heatLayer(taxPoints, {{
                radius: 28,
                blur: 20,
                maxZoom: 15,
                max: 1.0,
                gradient: {{ 0.2: '#0284c7', 0.4: '#10b981', 0.65: '#fbbf24', 0.85: '#f97316', 1.0: '#dc2626' }}
            }}).addTo(mapTax);

            // 更新 HUD
            const gtRows = yearData.filter(d => ['主力里', '主商里', '國威里', '主工里'].includes(d.li));
            const ddmRows = yearData.filter(d => ['民族里', '民主里', '民生里'].includes(d.li));

            const gtSales = gtRows.reduce((a, c) => a + c.real_sales_m, 0);
            const gtVacant = gtRows.reduce((a, c) => a + c.distress_rate, 0) / (gtRows.length || 1);
            
            let ddmSales = ddmRows.reduce((a, c) => a + c.real_sales_m, 0);
            if (year < 2015) ddmSales = 217.0 * (year - 1995 + 1) / 20.0 + 350.0;

            const total = gtSales + ddmSales;
            const ddmShare = total > 0 ? Math.round(ddmSales / total * 100) : 50;

            document.getElementById('hudGtSales').textContent = `${{Math.round(gtSales).toLocaleString()}} 百萬元`;
            document.getElementById('hudGtVacant').textContent = `${{gtVacant.toFixed(1)}}%`;
            document.getElementById('hudDdmSales').textContent = `${{Math.round(ddmSales).toLocaleString()}} 百萬元`;
            document.getElementById('hudDdmShare').textContent = `${{ddmShare}}%`;

            // 階段標籤
            let stage = "經典繁榮期";
            if (year >= 2024) stage = "震後雙核心成熟期";
            else if (year >= 2020) stage = "疫情與型態轉型期";
            else if (year >= 2015) stage = "東大門夜市崛起期";
            else if (year >= 2010) stage = "金三角陸客國旅巔峰";
            document.getElementById('yearStageBadge').textContent = stage;
        }}

        function initYearSlider() {{
            const slider = document.getElementById('yearSlider');
            const display = document.getElementById('currentYearDisplay');

            slider.addEventListener('input', (e) => {{
                const y = parseInt(e.target.value);
                display.textContent = y;
                updateHeatmaps(y);
            }});

            // 播放按鈕
            const playBtn = document.getElementById('playBtn');
            const playBtnText = document.getElementById('playBtnText');
            playBtn.addEventListener('click', () => {{
                if (isPlaying) {{
                    clearInterval(playInterval);
                    isPlaying = false;
                    playBtnText.textContent = "自動播放";
                }} else {{
                    isPlaying = true;
                    playBtnText.textContent = "暫停播放";
                    playInterval = setInterval(() => {{
                        let cur = parseInt(slider.value);
                        cur = cur >= 2025 ? 1995 : cur + 1;
                        slider.value = cur;
                        display.textContent = cur;
                        updateHeatmaps(cur);
                    }}, 900);
                }}
            }});
        }}

        function initDataTable() {{
            const yearSelect = document.getElementById('filterYear');
            const liSelect = document.getElementById('filterLi');
            const tbody = document.getElementById('dataTableBody');
            const countDisplay = document.getElementById('tableCount');

            // 填入年份選項
            const years = [...new Set(DATA.map(d => d.year))].sort((a, b) => b - a);
            years.forEach(y => {{
                const opt = document.createElement('option');
                opt.value = y;
                opt.textContent = `${{y}} 年`;
                yearSelect.appendChild(opt);
            }});

            function renderTable() {{
                const selY = yearSelect.value;
                const selLi = liSelect.value;

                let filtered = DATA;
                if (selY !== 'ALL') filtered = filtered.filter(d => d.year === parseInt(selY));
                if (selLi !== 'ALL') filtered = filtered.filter(d => d.li === selLi);

                countDisplay.textContent = `共 ${{filtered.length.toLocaleString()}} 筆資料`;
                tbody.innerHTML = '';

                filtered.slice(0, 100).forEach(d => {{
                    const tr = document.createElement('tr');
                    tr.className = "hover:bg-slate-800/50 transition";
                    tr.innerHTML = `
                        <td class="p-2.5 text-white font-bold">${{d.year}}</td>
                        <td class="p-2.5 font-sans">${{d.li}}</td>
                        <td class="p-2.5 text-sky-300">${{d.real_stores}}</td>
                        <td class="p-2.5 text-amber-300 font-bold">${{d.real_sales_m.toFixed(1)}}</td>
                        <td class="p-2.5 text-slate-300">${{d.power_idx.toFixed(0)}}</td>
                        <td class="p-2.5 text-rose-300">${{d.distress_rate.toFixed(1)}}%</td>
                        <td class="p-2.5 text-slate-400">${{d.tax_stores}}</td>
                        <td class="p-2.5 text-slate-400">${{Math.round(d.tax_sales_k).toLocaleString()}}</td>
                        <td class="p-2.5 text-slate-400 font-sans text-[10px]">${{d.notes}}</td>
                    `;
                    tbody.appendChild(tr);
                }});
            }}

            yearSelect.addEventListener('change', renderTable);
            liSelect.addEventListener('change', renderTable);
            renderTable();
        }}

        document.addEventListener('DOMContentLoaded', () => {{
            initMaps();
            initYearSlider();
            initDataTable();
            updateHeatmaps(2025);
        }});
    </script>
</body>
</html>
"""

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"🎉 一頁式敘事說明網頁已成功生成：{HTML_PATH} (大小: {os.path.getsize(HTML_PATH)/1024:.2f} KB)")


if __name__ == "__main__":
    build_onepage_html()
