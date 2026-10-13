# -*- coding: utf-8 -*-
r"""
fetch_dem.py — OpenTopography 高程下载小工具（备菜脚本）
[INPUT]: 命令行参数：--theme 主题名（例：蒙古大迂回）+ --bbox 南,北,西,东 矩形盒子；
         环境变量 OPENTOPOGRAPHY_API_KEY（钥匙永不写进代码）；可选 --grain-root 覆盖粮库根
[OUTPUT]: 粮库真身 {grain-root}/DEM_Copernicus_GLO30/{theme}/ 下的 .tif 原文件（原名不动）；
          标准输出打印 manifest 账本草稿一行（文件名｜版本｜下载日期｜来源｜标注原文｜覆盖bbox），由 AI 记入正式账本
[POS]: 项目根目录工具脚本，与 make_video_assets.py 并列；备菜工序调用它下厨，LLM 不亲手下载（ADR-010）
[PROTOCOL]: 纯标准库（禁装 numpy 等）；默认只计划不下载（--dry-run），真下必须显式加 --fetch；
         原文件原名不动，加工裁剪另存（粮库规矩）；主题/bbox/输出位置全参数化，蒙古只当默认值
用法：
    python fetch_dem.py --bbox "27.0,34.0,102.0,108.0" --theme "蒙古大迂回" --dry-run
    python fetch_dem.py --bbox "27.0,34.0,102.0,108.0" --theme "蒙古大迂回" --fetch
    python fetch_dem.py --help
"""
import argparse
import datetime
import os
import sys
import urllib.parse
import urllib.request

API_BASE = "https://portal.opentopography.org/API/globaldem"
DEFAULT_DEMTYPE = "COP30"  # Copernicus GLO-30（OpenTopography 侧代号，[推测]以官网文档为准）
DEFAULT_DATASET_DIR = "DEM_Copernicus_GLO30"
DEFAULT_GRAIN_ROOT = r"D:\数字资产\粮库_军事密码"
ATTRIBUTION = "高程: Copernicus DEM GLO-30 (ESA)"
SOURCE = "portal.opentopography.org"


def parse_bbox(s):
    parts = [p.strip() for p in s.split(",")]
    if len(parts) != 4:
        raise ValueError("bbox 须为4个数：南,北,西,东，如 27.0,34.0,102.0,108.0")
    try:
        south, north, west, east = (float(p) for p in parts)
    except ValueError:
        raise ValueError("bbox 4个数须为数字")
    if not (-90 <= south < north <= 90):
        raise ValueError("纬度须满足 -90<=南<北<=90")
    if not (-180 <= west < east <= 180):
        raise ValueError("经度须满足 -180<=西<东<=180")
    return south, north, west, east


def build_url(south, north, west, east, demtype, api_key, outformat="GTiff"):
    params = {
        "demtype": demtype,
        "south": south,
        "north": north,
        "west": west,
        "east": east,
        "outputFormat": outformat,
        "API_Key": api_key,
    }
    return API_BASE + "?" + urllib.parse.urlencode(params)


def mask_key(url):
    # 日志只打掩码版钥匙
    return url.replace(urllib.parse.quote_plus(os.environ.get("OPENTOPOGRAPHY_API_KEY", "")),
                       "***") if os.environ.get("OPENTOPOGRAPHY_API_KEY") else url


def target_path(grain_root, dataset_dir, theme, south, north, west, east, demtype):
    folder = os.path.join(grain_root, dataset_dir, theme)
    name = "%s_%.4fN_%.4fS_%.4fE_%.4fW.tif" % (demtype, north, south, east, west)
    return folder, os.path.join(folder, name)


def manifest_line(filename, bbox_str):
    today = datetime.date.today().isoformat()
    return "%s｜%s｜%s｜%s｜%s｜%s" % (
        filename, DEFAULT_DEMTYPE + " 2023_1", today, SOURCE, ATTRIBUTION, bbox_str)


def main(argv=None):
    ap = argparse.ArgumentParser(description="OpenTopography 高程下载小工具（默认只计划不下载）")
    ap.add_argument("--bbox", required=True, help="矩形盒子：南,北,西,东（度）")
    ap.add_argument("--theme", default="蒙古大迂回", help="主题名（文件夹名），默认蒙古大迂回只作例子")
    ap.add_argument("--grain-root", default=os.environ.get("GRAIN_ROOT", DEFAULT_GRAIN_ROOT),
                    help="粮库根（默认走本机真身，可用环境变量 GRAIN_ROOT 覆盖）")
    ap.add_argument("--dataset-dir", default=DEFAULT_DATASET_DIR)
    ap.add_argument("--demtype", default=DEFAULT_DEMTYPE)
    ap.add_argument("--fetch", action="store_true", help="加了才真下载；不加=只打印计划")
    ap.add_argument("--dry-run", action="store_true", help="只打印计划（默认行为，显式声明用）")
    args = ap.parse_args(argv)

    try:
        south, north, west, east = parse_bbox(args.bbox)
    except ValueError as e:
        print("bbox错：%s" % e, file=sys.stderr)
        return 2

    folder, path = target_path(args.grain_root, args.dataset_dir, args.theme,
                               south, north, west, east, args.demtype)
    bbox_str = "南%s北%s西%s东%s" % (south, north, west, east)

    if not args.fetch:
        print("[计划] 主题：%s" % args.theme)
        print("[计划] 方框：%s" % args.bbox)
        print("[计划] 落点：%s" % path)
        print("[计划] 账本草稿：%s" % manifest_line(os.path.basename(path), bbox_str))
        print("[计划] 未下载（要真下请加 --fetch；钥匙从环境变量 OPENTOPOGRAPHY_API_KEY 读）")
        return 0

    api_key = os.environ.get("OPENTOPOGRAPHY_API_KEY", "")
    if not api_key:
        print("缺钥匙：环境变量 OPENTOPOGRAPHY_API_KEY 为空，先设好再 --fetch（钥匙不写进代码）",
              file=sys.stderr)
        return 3
    if os.path.exists(path):
        print("已存在不重下：%s" % path)
        print(manifest_line(os.path.basename(path), bbox_str))
        return 0

    url = build_url(south, north, west, east, args.demtype, api_key)
    print("正在下载（只此一步联网，存原名不动）...")
    try:
        os.makedirs(folder, exist_ok=True)
        tmp = path + ".part"
        req = urllib.request.Request(url, headers={"User-Agent": "geography-fetch-dem/1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp, open(tmp, "wb") as fw:
            while True:
                chunk = resp.read(1024 * 256)
                if not chunk:
                    break
                fw.write(chunk)
        os.replace(tmp, path)
    except Exception as e:
        print("下载失败：%s（掩码地址：%s）" % (e, mask_key(url)[:160]), file=sys.stderr)
        return 4
    print("落袋：%s" % path)
    print(manifest_line(os.path.basename(path), bbox_str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
