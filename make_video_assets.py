# -*- coding: utf-8 -*-
r"""
make_video_assets.py — 《蒙古大迂回》GES 视频素材生成器 v2（镜头朝向修正版）
[INPUT]: 蒙古大迂回_三路路线.kml（只读，取"东路/中路/西路"三条路线坐标）；下方 CLIPS 表（镜头设计参数）
[OUTPUT]: 视频制作\XX_*.esp 共 11 个相机动画工程文件（只重写 .esp，不触碰 .kml）
[POS]: 项目根目录工具脚本；v1（2026-09-28 初版）的修正版——v1 用了 GES 不认的私有数值编码（按自定义
        min/max 归一化、缺 maxValueRange、水平转向为负值），导致导入 GES 后镜头方向错乱/反向。
[PROTOCOL]: 数值编码规范（改动前必读）——
        GES modelVersion 17 关键帧值 = (实际值 - 区间下限) / (区间上限 - 区间下限)，区间一律用标准区间：
          经度 [-180,180]  纬度 [-89.9999,89.9999]  高度 [-500,65117481]（米）
          水平转向 rotationX [0,360]（罗盘方位角：正北=0°，顺时针，90°=正东）
          俯仰   rotationY [0,180]（0=垂直俯瞰，90=平视）
        依据：GES 原生导出样例（modelVersion 16）、jayin92/GES-utils 实测管线（NeRF 训练逆向验证）、
        Google Maps 相机 bearing/tilt 官方定义。修改本文件后必须重跑 verify 并让用户重测 02。
用法：
    python make_video_assets.py generate      # 重新生成 11 个 .esp 到 视频制作/
    python make_video_assets.py verify [目录]  # 校验解码正确性，默认校验 视频制作/
"""
import json
import math
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "视频制作")
MASTER = os.path.join(BASE, "蒙古大迂回_三路路线.kml")

LON = (-180.0, 180.0)
LAT = (-89.9999, 89.9999)
ALT = (-500.0, 65117481.0)
PAN = (0.0, 360.0)
TILT = (0.0, 180.0)

# ---- 镜头设计表：base=文件名前缀 cam=[(经度,纬度)...] 按飞行顺序 ----
CLIPS = [
    dict(base="01_开场", cam=[(104.30, 36.30), (103.857, 35.376), (103.50, 34.00)],
         alt=200000, tilt=55, dur=240),
    dict(base="02_三路全景", cam=[(103.50, 34.00), (102.00, 30.00), (100.16, 25.69)],
         alt=900000, tilt=50, dur=300),
    dict(base="03_东路", cam="东路", alt=450000, tilt=45, dur=600),
    dict(base="04_中路", cam="中路", alt=450000, tilt=45, dur=600),
    dict(base="05_西路", cam="西路", alt=450000, tilt=45, dur=600),
    dict(base="06_大理会师", cam=[(102.26, 27.88), (101.51, 27.42), (100.85, 27.28), (100.16, 25.69)],
         alt=250000, tilt=40, dur=270),
    dict(base="07_四川战场", cam=[(107.02, 33.07), (105.84, 32.43), (105.57, 32.28), (106.36, 29.96)],
         alt=400000, tilt=45, dur=480),
    dict(base="08_两湖北线", cam=[(117.39, 32.91), (117.22, 31.82), (114.30, 30.55)],
         alt=300000, tilt=45, dur=300),
    dict(base="09_两湖南线", cam=[(102.71, 25.04), (108.36, 22.81), (110.28, 25.27), (110.00, 27.57), (112.93, 28.22)],
         alt=450000, tilt=45, dur=480),
    dict(base="10_安南", cam=[(102.71, 25.04), (103.97, 22.51), (105.85, 21.02)],
         alt=350000, tilt=50, dur=300),
    dict(base="11_终章", cam=[(107.80, 33.30), (106.90, 31.50), (106.36, 29.96)],
         alt=450000, tilt=45, dur=330),
]


def norm(value, rng):
    lo, hi = rng
    return (value - lo) / (hi - lo)


def denorm(value, rng):
    lo, hi = rng
    return lo + value * (hi - lo)


def bearing(c1, c2):
    """罗盘方位角（度）：正北=0°，顺时针；经度差按两点中点纬度做球面缩短"""
    mid_lat = math.radians((c1[1] + c2[1]) / 2.0)
    dx = (c2[0] - c1[0]) * math.cos(mid_lat)
    dy = c2[1] - c1[1]
    return math.degrees(math.atan2(dx, dy)) % 360.0


def unfold(seq):
    """相邻方位角差收敛到 ±180° 内，保证 GES 插值走最短弧；结果可能略越出 [0,360]，方向等价"""
    out = []
    for v in seq:
        if out:
            while v - out[-1] > 180.0:
                v -= 360.0
            while out[-1] - v > 180.0:
                v += 360.0
        out.append(v)
    return out


def keyframes(vals):
    n = len(vals)
    if n == 1:
        return [{"time": 0.0, "value": vals[0]}]
    return [{"time": i / (n - 1), "value": v} for i, v in enumerate(vals)]


def block(label, rng, actuals, extra=None):
    """按标准区间归一化，生成 GES 关键帧块"""
    lo, hi = rng
    vals = [norm(a, rng) for a in actuals]
    value = {"minValueRange": lo, "maxValueRange": hi, "relative": vals[0]}
    if extra:
        value.update(extra)
    return {"type": label, "value": value, "keyframes": keyframes(vals), "intimeline": True}


def parse_master():
    xml = open(MASTER, encoding="utf-8").read()
    places = {}
    for m in re.finditer(r"<Placemark>(.*?)</Placemark>", xml, re.S):
        blk = m.group(1)
        nm = re.search(r"<name>(.*?)</name>", blk, re.S)
        name = nm.group(1).strip() if nm else ""
        cm = re.search(r"<coordinates>(.*?)</coordinates>", blk, re.S)
        coords = []
        if cm:
            coords = [tuple(map(float, ln.strip().split(",")[:2]))
                      for ln in cm.group(1).strip().splitlines() if ln.strip()]
        places[name] = coords
    assert len(places) == 17, f"母版 KML 应含 17 个地标，实际 {len(places)}"
    return places


def pm(places, keyword):
    """按关键字找母版里的路线坐标"""
    for name, coords in places.items():
        if keyword in name:
            return coords
    raise KeyError(f"母版中找不到含「{keyword}」的地标")


def build_esp(clip, cam):
    """把一个片段编译成完整 .esp 数据结构"""
    pans = unfold([bearing(cam[i], cam[i + 1]) for i in range(len(cam) - 1)])
    return {
        "modelVersion": 17,
        "settings": {"name": clip["base"], "frameRate": 30,
                     "dimensions": {"width": 1920, "height": 1080},
                     "duration": clip["dur"], "timeFormat": "frames"},
        "scenes": [{
            "world": {"kmls": []},
            "animationModel": {"roving": False, "logarithmic": False, "groupedPosition": True},
            "duration": clip["dur"],
            "attributes": [
                {"type": "cameraGroup", "inTimeline": True, "attributes": [
                    {"type": "cameraPositionGroup", "inTimeline": True, "attributes": [
                        block("longitude", LON, [c[0] for c in cam]),
                        block("latitude", LAT, [c[1] for c in cam]),
                        block("altitude", ALT, [clip["alt"]] * len(cam), extra={"logarithmic": False}),
                    ]},
                    {"type": "cameraTargetEffect", "attributes": [
                        {"type": "enabled", "value": {}},
                        {"type": "poi", "attributes": [
                            {"type": "longitudePOI", "value": {}},
                            {"type": "latitudePOI", "value": {}},
                            {"type": "altitudePOI", "value": {"logarithmic": False}},
                        ]},
                        {"type": "influence", "value": {}},
                    ]},
                    {"type": "cameraRotationGroup", "inTimeline": True, "attributes": [
                        block("rotationX", PAN, pans),
                        block("rotationY", TILT, [clip["tilt"], clip["tilt"]]),
                        {"type": "rotationZ", "value": {}},
                    ]},
                    {"type": "cameraLensGroup", "attributes": [
                        {"type": "fov", "value": {}},
                        {"type": "exposure", "value": {}},
                        {"type": "aperture", "value": {}},
                        {"type": "minFocusLength", "value": {}},
                    ]},
                ]},
                {"type": "environmentGroup", "attributes": [
                    {"type": "sunGroup", "attributes": [
                        {"type": "sunVisibility", "value": {}},
                        {"type": "worldTime", "value": {"relative": 0.5}}]},
                    {"type": "cloudGroup", "attributes": [
                        {"type": "cloudVisibility", "value": {}},
                        {"type": "cloudopacity", "value": {}},
                        {"type": "cloudheight", "value": {}},
                        {"type": "clouddate", "value": {"relative": 0.9545454545454546}}]},
                    {"type": "starsPlanetsGroup", "attributes": [
                        {"type": "starsEnabled", "value": {}}]},
                    {"type": "seawaterGroup", "attributes": [
                        {"type": "seawater", "value": {}},
                        {"type": "influence", "value": {"relative": 1}}]},
                    {"type": "buildingsEnabled", "value": {}},
                ]},
            ],
            "cameraExport": {"logarithmic": False, "modelVersion": 2},
        }],
        "playbackManager": {"range": {"start": 0, "end": clip["dur"]}},
    }


# ---------------- 生成 ----------------

def resolve_cams():
    places = parse_master()
    out = []
    for clip in CLIPS:
        cam = pm(places, clip["cam"]) if isinstance(clip["cam"], str) else clip["cam"]
        out.append((clip, cam))
    return out


def generate():
    for clip, cam in resolve_cams():
        esp = build_esp(clip, cam)
        path = os.path.join(OUT_DIR, clip["base"] + ".esp")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(esp, f, ensure_ascii=False, indent=4)
        pans = unfold([bearing(cam[i], cam[i + 1]) for i in range(len(cam) - 1)])
        dirs = " ".join(f"{p:.1f}°" for p in pans)
        print(f"OK {clip['base']}: {len(cam)}点 方位[{dirs}] alt={clip['alt']}m tilt={clip['tilt']}° dur={clip['dur']}f")
    print(f"\n已重写 {len(CLIPS)} 个 .esp -> {OUT_DIR}")


# ---------------- 校验 ----------------

def decode_declared(blk, default_range):
    """GES 解码模型A：实际值 = min + 值×(max-min)；块内字段缺失时按标准区间回退（最宽容口径）"""
    lo = blk["value"].get("minValueRange", default_range[0])
    hi = blk["value"].get("maxValueRange", default_range[1])
    return [denorm(kf["value"], (lo, hi)) for kf in blk["keyframes"]]


def decode_fixed(blk, fixed):
    """GES 解码模型B：区间忽略声明、按固定标准区间，值直接线性映射"""
    return [denorm(kf["value"], fixed) for kf in blk["keyframes"]]


def wrap180(v):
    return (v + 180.0) % 360.0 - 180.0


def find_esp_attr(node, attr_type):
    """递归找 esp 属性树里 type == attr_type 且带关键帧的第一个属性块"""
    if isinstance(node, dict):
        if node.get("type") == attr_type and "keyframes" in node:
            return node
        for v in node.values():
            found = find_esp_attr(v, attr_type)
            if found is not None:
                return found
    elif isinstance(node, list):
        for item in node:
            found = find_esp_attr(item, attr_type)
            if found is not None:
                return found
    return None


def verify_dir(path):
    clips = resolve_cams()
    failures = []
    checked = []
    for clip, cam in clips:
        fname = os.path.join(path, clip["base"] + ".esp")
        tag = clip["base"]
        if not os.path.exists(fname):
            failures.append(f"{tag}: 文件不存在 {fname}")
            continue
        esp = json.load(open(fname, encoding="utf-8"))
        lon_b = find_esp_attr(esp, "longitude")
        lat_b = find_esp_attr(esp, "latitude")
        alt_b = find_esp_attr(esp, "altitude")
        rot_b = find_esp_attr(esp, "rotationX")
        tlt_b = find_esp_attr(esp, "rotationY")
        missing = [name for name, blk in (("longitude", lon_b), ("latitude", lat_b), ("altitude", alt_b),
                                          ("rotationX", rot_b), ("rotationY", tlt_b)) if blk is None]
        if missing:
            failures.append(f"{tag}: esp 结构缺关键属性块 {missing}")
            continue
        assert lon_b is not None and lat_b is not None and alt_b is not None and rot_b is not None and tlt_b is not None

        exp_pans = unfold([bearing(cam[i], cam[i + 1]) for i in range(len(cam) - 1)])
        exp_tilt = float(clip["tilt"])

        # 两份解码都验：A=声明区间  B=固定标准区间（v2 编码下两者应一致）
        for model in ("A", "B"):
            if model == "A":
                dl, da, dh = (decode_declared(lon_b, LON), decode_declared(lat_b, LAT), decode_declared(alt_b, ALT))
                dp, dt = decode_declared(rot_b, PAN), decode_declared(tlt_b, TILT)
            else:
                dl, da, dh = (decode_fixed(lon_b, LON), decode_fixed(lat_b, LAT), decode_fixed(alt_b, ALT))
                dp, dt = decode_fixed(rot_b, PAN), decode_fixed(tlt_b, TILT)

            for i, c in enumerate(cam):
                if abs(dl[i] - c[0]) > 1e-6 or abs(da[i] - c[1]) > 1e-6:
                    failures.append(f"{tag}[模型{model}]: 位置KF{i+1} 解码为 ({dl[i]:.5f},{da[i]:.5f})，应为 ({c[0]:.5f},{c[1]:.5f})")
                if abs(dh[i] - clip["alt"]) > 1.0:
                    failures.append(f"{tag}[模型{model}]: 高度KF{i+1} 解码为 {dh[i]:.1f}m，应为 {clip['alt']}m")
            for i, p in enumerate(exp_pans):
                if abs(wrap180(dp[i] - p)) > 1e-6:
                    failures.append(f"{tag}[模型{model}]: 转向KF{i+1} 解码为 {dp[i]:.3f}°，应为 {p:.3f}°")
            for i, t in enumerate(dt):
                if abs(wrap180(t - exp_tilt)) > 1e-6 and abs(t - exp_tilt) > 1e-6:
                    failures.append(f"{tag}[模型{model}]: 俯仰KF{i+1} 解码为 {t:.3f}°，应为 {exp_tilt:.3f}°")

        # 其它结构检查
        times = [kf["time"] for kf in lon_b["keyframes"]]
        if times != sorted(times) or abs(times[0]) > 1e-12 or abs(times[-1] - 1.0) > 1e-12:
            failures.append(f"{tag}: 时间轴异常 {times}")
        if len(lon_b["keyframes"]) != len(cam):
            failures.append(f"{tag}: 位置关键帧数 {len(lon_b['keyframes'])} != {len(cam)}")

        checked.append(f"{tag}: {len(cam)}点 方位[{', '.join(f'{p:.1f}°' for p in exp_pans)}] "
                       f"alt={clip['alt']}m tilt={clip['tilt']}°")

    print(f"== 校验目录: {path} ==")
    for line in checked:
        print("  " + line)
    if failures:
        print(f"\n结果: FAIL（{len(failures)} 处问题，前 12 条）")
        for f_ in failures[:12]:
            print("  x " + f_)
        return 1
    print(f"\n结果: PASS（{len(checked)} 个片段，位置/方位/俯仰/时间轴全部一致）")
    return 0


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "generate":
        generate()
        return 0
    if len(sys.argv) >= 2 and sys.argv[1] == "verify":
        target = sys.argv[2] if len(sys.argv) >= 3 else OUT_DIR
        return verify_dir(target)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
