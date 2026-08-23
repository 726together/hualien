#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下載並拼接花蓮市區暗色系地圖底圖 (CartoDB Dark Matter)
供動態 GIF 熱力圖作為地理背景使用
"""

import math
import os
import urllib.request
from PIL import Image, ImageEnhance, ImageFilter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output_data")
BASEMAP_PATH = os.path.join(OUTPUT_DIR, "hualien_dark_basemap.png")

# 地理邊界 (與 GIF 坐標系 100% 吻合)
LNG_MIN, LNG_MAX = 121.592, 121.628
LAT_MIN, LAT_MAX = 23.962, 23.996
ZOOM = 15


def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile


def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg


def download_and_stitch_dark_basemap():
    print(f"正在計算花蓮市區暗色瓦片地圖 (Zoom {ZOOM})...")
    x_min, y_min = deg2num(LAT_MAX, LNG_MIN, ZOOM)
    x_max, y_max = deg2num(LAT_MIN, LNG_MAX, ZOOM)

    tiles_x = x_max - x_min + 1
    tiles_y = y_max - y_min + 1
    print(f"  瓦片範圍: X: {x_min} ~ {x_max} ({tiles_x}片), Y: {y_min} ~ {y_max} ({tiles_y}片)")

    stitched_width = tiles_x * 256
    stitched_height = tiles_y * 256
    stitched_img = Image.new('RGB', (stitched_width, stitched_height), (7, 13, 24))

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    tile_cache_dir = os.path.join(OUTPUT_DIR, "tile_cache")
    os.makedirs(tile_cache_dir, exist_ok=True)

    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            tile_path = os.path.join(tile_cache_dir, f"dark_{ZOOM}_{x}_{y}.png")
            if not os.path.exists(tile_path):
                # CartoDB Dark Matter tile server
                url = f"https://a.basemaps.cartocdn.com/dark_all/{ZOOM}/{x}/{y}.png"
                try:
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=8) as resp:
                        with open(tile_path, 'wb') as f:
                            f.write(resp.read())
                except Exception as e:
                    print(f"    無法下載瓦片 {url} ({e})，使用備用黑色瓦片")
                    black_tile = Image.new('RGB', (256, 256), (11, 17, 32))
                    black_tile.save(tile_path)

            tile_img = Image.open(tile_path).convert('RGB')
            pos_x = (x - x_min) * 256
            pos_y = (y - y_min) * 256
            stitched_img.paste(tile_img, (pos_x, pos_y))

    # 計算精確裁剪範圍以對齊 [LNG_MIN, LNG_MAX, LAT_MIN, LAT_MAX]
    top_lat, left_lon = num2deg(x_min, y_min, ZOOM)
    bottom_lat, right_lon = num2deg(x_max + 1, y_max + 1, ZOOM)

    crop_left = int((LNG_MIN - left_lon) / (right_lon - left_lon) * stitched_width)
    crop_right = int((LNG_MAX - left_lon) / (right_lon - left_lon) * stitched_width)
    crop_top = int((top_lat - LAT_MAX) / (top_lat - bottom_lat) * stitched_height)
    crop_bottom = int((top_lat - LAT_MIN) / (top_lat - bottom_lat) * stitched_height)

    crop_left = max(0, crop_left)
    crop_top = max(0, crop_top)
    crop_right = min(stitched_width, crop_right)
    crop_bottom = min(stitched_height, crop_bottom)

    cropped_basemap = stitched_img.crop((crop_left, crop_top, crop_right, crop_bottom))
    
    # 微調對比度與亮度使道路輪廓清晰但不過於刺眼
    enhancer = ImageEnhance.Contrast(cropped_basemap)
    cropped_basemap = enhancer.enhance(1.25)
    enhancer_bright = ImageEnhance.Brightness(cropped_basemap)
    cropped_basemap = enhancer_bright.enhance(1.1)

    cropped_basemap.save(BASEMAP_PATH, "PNG")
    print(f"🎉 花蓮市暗色底圖已成功生成並儲存至：{BASEMAP_PATH} (尺寸: {cropped_basemap.size})")


if __name__ == "__main__":
    download_and_stitch_dark_basemap()
