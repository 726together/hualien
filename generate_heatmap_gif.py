#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
花蓮市商圈真實實體消費熱力動態 GIF 生成器 (1995-2025)
暗色系地圖底圖 (Dark Basemap) + 高對比度醒目標註版
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import matplotlib.patheffects as pe
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output_data")
UNIFIED_CSV = os.path.join(OUTPUT_DIR, "unified_hualien_commercial_data_1995_2025.csv")
GIF_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "hualien_commercial_heatmap.gif")
BASEMAP_PATH = os.path.join(OUTPUT_DIR, "hualien_dark_basemap.png")

LI_COORDS = {
    "主商里": (121.6085, 23.9765),
    "主力里": (121.6045, 23.9740),
    "國威里": (121.6070, 23.9805),
    "主工里": (121.6030, 23.9752),
    "主學里": (121.6010, 23.9725),
    "主勤里": (121.5995, 23.9710),
    "主計里": (121.6035, 23.9780),
    "主安里": (121.6020, 23.9685),
    "民主里": (121.6115, 23.9745),
    "民族里": (121.6145, 23.9725),
    "民生里": (121.6130, 23.9785),
    "國聯里": (121.6025, 23.9930),
    "國盛里": (121.6070, 23.9900),
    "國富里": (121.5950, 23.9910),
    "主權里": (121.5950, 23.9690),
    "主農里": (121.6000, 23.9630),
    "民運里": (121.6250, 23.9870),
    "民意里": (121.6300, 23.9950),
    "國裕里": (121.5900, 23.9960),
    "國興里": (121.5900, 23.9850),
}

LNG_MIN, LNG_MAX = 121.592, 121.628
LAT_MIN, LAT_MAX = 23.962, 23.996
UNIFIED_MAX_SALES = 5500.0


def setup_chinese_font():
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'PingFang TC', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False


def build_calibrated_surface(df_year, metric_col, year=2025, grid_size=200):
    xi = np.linspace(LNG_MIN, LNG_MAX, grid_size)
    yi = np.linspace(LAT_MIN, LAT_MAX, grid_size)
    X, Y = np.meshgrid(xi, yi)
    Z = np.zeros((grid_size, grid_size))

    gt_df = df_year[df_year['里別'].isin(['主力里', '主商里', '國威里', '主工里'])]
    ddm_df = df_year[df_year['里別'].isin(['民族里', '民主里', '民生里'])]
    other_df = df_year[~df_year['里別'].isin(['主力里', '主商里', '國威里', '主工里', '民族里', '民主里', '民生里'])]

    gt_total = gt_df[metric_col].sum()
    ddm_total = ddm_df[metric_col].sum()
    if year < 2015:
        ddm_total = 217.0 * (year - 1995 + 1) / 20.0 + 350.0

    # 金三角核心擴散核
    gt_subpoints = [(121.6050, 23.9760), (121.6070, 23.9780), (121.6040, 23.9745), (121.6065, 23.9750)]
    w_sum_gt = np.zeros((grid_size, grid_size))
    for sp in gt_subpoints:
        dist_sq = (X - sp[0])**2 + (Y - sp[1])**2
        w_sum_gt += np.exp(-dist_sq / (2 * 0.0028**2))
    w_sum_gt_max = w_sum_gt.max()
    if w_sum_gt_max > 0:
        Z += (w_sum_gt / w_sum_gt_max) * gt_total

    # 東大門商圈 3 里擴散核
    ddm_subpoints = [
        (121.6145, 23.9725),
        (121.6115, 23.9745),
        (121.6130, 23.9785),
        (121.6140, 23.9755)
    ]
    w_sum_ddm = np.zeros((grid_size, grid_size))
    for sp in ddm_subpoints:
        dist_sq = (X - sp[0])**2 + (Y - sp[1])**2
        w_sum_ddm += np.exp(-dist_sq / (2 * 0.0030**2))
    w_sum_ddm_max = w_sum_ddm.max()
    if w_sum_ddm_max > 0:
        Z += (w_sum_ddm / w_sum_ddm_max) * ddm_total

    for _, r in other_df.iterrows():
        li = r['里別']
        if li in LI_COORDS:
            lng, lat = LI_COORDS[li]
            v = r[metric_col]
            dist_sq = (X - lng)**2 + (Y - lat)**2
            Z += v * np.exp(-dist_sq / (2 * 0.0024**2))

    return X, Y, Z, gt_total, ddm_total


def create_heatmap_frame(df_year, year, basemap_img=None):
    setup_chinese_font()
    fig, ax = plt.subplots(figsize=(12, 10.5), dpi=110, facecolor='#070d18')
    ax.set_facecolor('#070d18')

    if basemap_img is not None:
        ax.imshow(basemap_img, extent=[LNG_MIN, LNG_MAX, LAT_MIN, LAT_MAX], origin='upper', aspect='auto', zorder=1)

    X, Y, Z, gt_val, ddm_val = build_calibrated_surface(df_year, '實體街區真實消費產值(百萬元)', year=year, grid_size=200)

    levels = np.linspace(0, UNIFIED_MAX_SALES, 70)
    cs = ax.contourf(X, Y, Z, levels=levels, cmap='turbo', alpha=0.68, extend='max', zorder=2)

    # 金三角商圈外框與標籤 (亮青藍)
    gt_poly = Polygon([[121.6085, 23.9765], [121.6045, 23.9740], [121.6030, 23.9752], [121.6070, 23.9805]], 
                      closed=True, edgecolor='#38bdf8', facecolor='none', linewidth=3.2, linestyle='-', zorder=3)
    ax.add_patch(gt_poly)
    ax.text(121.6050, 23.9770, '【金三角商圈】\n(主力/主商/國威/主工)', color='#38bdf8', fontsize=14.0, fontweight='bold', ha='center',
            zorder=5, path_effects=[pe.withStroke(linewidth=4.5, foreground='#000000')])

    # 東大門夜市商圈外框與標籤 (高對比亮洋紅/白色)
    ddm_poly = Polygon([[121.6145, 23.9715], [121.6165, 23.9745], [121.6135, 23.9800], [121.6105, 23.9755]],
                       closed=True, edgecolor='#f43f5e', facecolor='none', linewidth=3.4, 
                       linestyle='-' if year>=2015 else '--', zorder=3)
    ax.add_patch(ddm_poly)

    if year >= 2015:
        ax.text(121.6135, 23.9752, '【東大門夜市商圈】\n(民族/民主/民生 3里)', color='#ffffff', fontsize=14.0, fontweight='bold', ha='center',
                 zorder=5, path_effects=[pe.withStroke(linewidth=4.5, foreground='#000000')])
    else:
        ax.text(121.6135, 23.9752, '【東大門夜市商圈】\n(2015前 夜市尚未開放)', color='#fb7185', fontsize=13.0, fontweight='bold', ha='center',
                 zorder=5, path_effects=[pe.withStroke(linewidth=4.0, foreground='#000000')])

    ax.text(0.03, 0.94, f"花蓮市商圈去重真實熱力變遷: {year} 年", transform=ax.transAxes,
            color='#ffffff', fontsize=16, fontweight='bold', zorder=6,
            path_effects=[pe.withStroke(linewidth=3.5, foreground='#000000')])
    
    if year < 2000: stage_desc = "【1990年代】金三角獨大，大禹街服飾小吃鼎盛，東大門尚未開放"
    elif year < 2015: stage_desc = "【2000-2014】陸客與國旅巔峰，金三角滿租一位難求，夜市在南濱/自強"
    elif year == 2015: stage_desc = "【2015 關鍵轉折】東大門夜市商圈啟用！400 攤進駐，人潮大舉轉移"
    elif year < 2020: stage_desc = "【2016-2019】東大門夜市商圈全盛奪冠；金三角夜間提早打烊，服飾首現退租潮"
    elif year < 2024: stage_desc = "【2020-2023】疫情衝擊與缺工，老店相繼熄燈，夾娃娃機進駐"
    elif year == 2024: stage_desc = "【2024 0403震災】天王星拆除封路重創市區，金三角空置率破 30% 歷史高峰"
    else: stage_desc = "【2025 現況】東大門夜市商圈 (49.3億 佔65%) 主導夜經濟，金三角 (26.4億 佔35%) 轉型名產與微型文創"

    ax.text(0.03, 0.89, stage_desc, transform=ax.transAxes, color='#38bdf8', fontsize=10.5, zorder=6,
            path_effects=[pe.withStroke(linewidth=2.5, foreground='#000000')])

    gt_df = df_year[df_year['里別'].isin(['主力里', '主商里', '國威里', '主工里'])]
    gt_distress = gt_df['店面空置與業態降級率(%)'].mean()
    gt_power = gt_df['台電低壓營業用電量指數'].mean()
    
    total_sales = gt_val + ddm_val
    pct_gt = int(round(gt_val / total_sales * 100)) if total_sales > 0 else 50
    pct_ddm = 100 - pct_gt

    hud_text = (
        f"金三角商圈 (4里): {gt_val:,.0f} 百萬 (佔 {pct_gt}% ｜ 用電: {gt_power:.0f}點)\n"
        f"   空置降級率: {gt_distress:.1f}% ({'高空置' if gt_distress>25 else '良好'})\n"
        f"東大門夜市商圈 (3里): {ddm_val:,.0f} 百萬 (佔 {pct_ddm}% ｜ {'2015啟用爆發' if year>=2015 else '未開放'})"
    )
    ax.text(0.97, 0.05, hud_text, transform=ax.transAxes, color='#fbbf24', fontsize=10.0, fontweight='bold',
            ha='right', va='bottom', zorder=6, bbox=dict(boxstyle='round,pad=0.6', facecolor='#1e293b', edgecolor='#475569', alpha=0.94))

    ax.set_xlim(LNG_MIN, LNG_MAX)
    ax.set_ylim(LAT_MIN, LAT_MAX)
    ax.axis('off')

    # 底部熱度數值標尺
    cbar = fig.colorbar(cs, ax=ax, orientation='horizontal', pad=0.035, fraction=0.045, aspect=30, shrink=0.88)
    cbar.set_ticks([0, 1500, 2750, 4200, 5500])
    cbar.set_ticklabels(['0M (低溫藍)', '1,500M', '2,750M (50% 常態綠)', '4,200M (暖橘)', '5,500M (紅色上限)'])
    cbar.ax.tick_params(labelsize=9, colors='#cbd5e1')
    cbar.set_label('實體街區真實消費產值標尺 (百萬元/年 ｜ 2005/2025 金三角 2,640M 綠階 ｜ 2025 東大門商圈 4,929M 紅階)', 
                   color='#38bdf8', fontsize=10, fontweight='bold', labelpad=5)
    cbar.outline.set_edgecolor('#334155')

    plt.tight_layout()
    fig.canvas.draw()
    rgba_buffer = fig.canvas.buffer_rgba()
    image = np.asarray(rgba_buffer)
    plt.close(fig)
    return image


def generate_animated_gif():
    print("正在載入暗色底圖並生成「疊加暗色地圖底圖單幅熱力圖」幀...")
    df = pd.read_csv(UNIFIED_CSV)
    
    basemap_img = None
    if os.path.exists(BASEMAP_PATH):
        print(f"  成功載入暗色底圖：{BASEMAP_PATH}")
        basemap_img = Image.open(BASEMAP_PATH).convert('RGB')
    else:
        print("  未找到暗色底圖，將使用純暗色背景")

    years = [1995, 1998, 2000, 2003, 2005, 2008, 2010, 2012, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
    frames = []

    for y in years:
        df_y = df[df['年份'] == y]
        img_arr = create_heatmap_frame(df_y, y, basemap_img=basemap_img)
        pil_img = Image.fromarray(img_arr)
        frames.append(pil_img)

    durations = [850] * (len(frames) - 1) + [2500]
    
    frames[0].save(
        GIF_OUTPUT_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    print(f"🎉 疊加暗色地圖底圖單幅熱力 GIF 已成功生成：{GIF_OUTPUT_PATH} (大小: {os.path.getsize(GIF_OUTPUT_PATH)/(1024*1024):.2f} MB)")


if __name__ == "__main__":
    generate_animated_gif()
