# -*- coding: utf-8 -*-
"""ABC探针：验证GES吃不吃三类关键帧（各测一个变量，其余与正常镜头一致）。
A_时间：worldTime 0.62→0.92（下午→夜方向）[推测映射]
B_视野：fov relative 0.5→0.15（宽→窄方向，恒等映射）[推测映射]
C_盯住：cameraTargetEffect enabled=1，目标=大理(100.16,25.69,2040m)，influence=1
输出：_tmp_valley03/A_时间.esp 等三文件（scratch，不进视频制作/）。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import make_video_assets as M

CAM_C = [(101.51, 27.42), (100.85, 27.28), (100.16, 25.69)]  # 06同款，认得出来
DALI = (100.16, 25.69, 2040.0)  # 大理：经纬+open-meteo实测高程


def base_clip(name, cam, dur):
    n = len(cam)
    return {"base": name, "dur": dur,
            "alts": [M.clip_alts({"alt": 120000}, n)][0],
            "tilts": [30] * n}, cam


def find_block(node, attr_type):
    """找type==attr_type的第一个块（不管有没有关键帧；探针改单值块用）"""
    if isinstance(node, dict):
        if node.get("type") == attr_type:
            return node
        for v in node.values():
            if isinstance(v, (dict, list)):
                found = find_block(v, attr_type)
                if found is not None:
                    return found
    elif isinstance(node, list):
        for item in node:
            found = find_block(item, attr_type)
            if found is not None:
                return found
    return None


def build_probe_a():
    cam = [(103.50, 34.00), (103.60, 32.65), (103.62, 30.99)]
    clip = {"base": "A_时间", "dur": 150, "alts": [150000] * 3, "tilts": [30] * 3}
    esp = M.build_esp(clip, cam)
    # 唯一变量：worldTime打2个关键帧（其余不动）
    wt = find_block(esp, "worldTime")
    wt["keyframes"] = [{"time": 0.0, "value": 0.62}, {"time": 1.0, "value": 0.92}]
    wt["value"] = {"minValueRange": 0.0, "maxValueRange": 1.0, "relative": 0.62}
    return esp


def build_probe_a2():
    """A2：唯一变量=补区间声明（其他与A完全一致）"""
    cam = [(103.50, 34.00), (103.60, 32.65), (103.62, 30.99)]
    clip = {"base": "A2_时间补区间", "dur": 150, "alts": [150000] * 3, "tilts": [30] * 3}
    esp = M.build_esp(clip, cam)
    wt = find_block(esp, "worldTime")
    wt["keyframes"] = [{"time": 0.0, "value": 0.62}, {"time": 1.0, "value": 0.92}]
    wt["value"] = {"minValueRange": 0.0, "maxValueRange": 1.0, "relative": 0.62}
    wt["intimeline"] = True
    return esp


def build_probe_b():
    cam = [(103.50, 34.00), (102.26, 27.88), (100.16, 25.69)]
    clip = {"base": "B_视野", "dur": 150, "alts": [400000] * 3, "tilts": [25] * 3}
    esp = M.build_esp(clip, cam)
    # 唯一变量：fov打2个关键帧（恒等映射，即relative直写）
    fov = find_block(esp, "fov")
    fov["value"] = {"minValueRange": 0.0, "maxValueRange": 1.0, "relative": 0.5}
    fov["keyframes"] = [{"time": 0.0, "value": 0.5}, {"time": 1.0, "value": 0.15}]
    fov["intimeline"] = True
    return esp


def build_probe_b2():
    """B2：唯一变量=时长150→300（10秒，范围0.5→0.15不动）"""
    cam = [(103.50, 34.00), (102.26, 27.88), (100.16, 25.69)]
    clip = {"base": "B2_视野放慢", "dur": 300, "alts": [400000] * 3, "tilts": [25] * 3}
    esp = M.build_esp(clip, cam)
    fov = find_block(esp, "fov")
    fov["value"] = {"minValueRange": 0.0, "maxValueRange": 1.0, "relative": 0.5}
    fov["keyframes"] = [{"time": 0.0, "value": 0.5}, {"time": 1.0, "value": 0.15}]
    fov["intimeline"] = True
    return esp


def build_probe_c():
    clip = {"base": "C_盯住", "dur": 180,
            "alts": [140000, 100000, 160000], "tilts": [30, 30, 20]}
    esp = M.build_esp(clip, CAM_C)
    # 唯一变量：打开注视点锁定，目标=大理，盯死（influence=1）
    tgt = find_block(esp, "cameraTargetEffect")
    for attr in tgt["attributes"]:
        if attr["type"] == "enabled":
            attr["value"] = {"relative": 1}
        elif attr["type"] == "influence":
            attr["value"] = {"relative": 1}
        elif attr["type"] == "poi":
            for p in attr["attributes"]:
                if p["type"] == "longitudePOI":
                    p["value"] = {"minValueRange": -180.0, "maxValueRange": 180.0,
                                  "relative": M.norm(DALI[0], M.LON)}
                elif p["type"] == "latitudePOI":
                    p["value"] = {"minValueRange": -89.9999, "maxValueRange": 89.9999,
                                  "relative": M.norm(DALI[1], M.LAT)}
                elif p["type"] == "altitudePOI":
                    p["value"] = {"minValueRange": -500.0, "maxValueRange": 65117481.0,
                                  "relative": M.norm(DALI[2], M.ALT),
                                  "logarithmic": False}
    return esp


def decode_check(path, need):
    """need: {attr_type: 最少关键帧数}，顺手查值域0~1。"""
    import json
    esp = json.load(open(path, encoding="utf-8"))
    for attr, kmin in need.items():
        blk = M.find_esp_attr(esp, attr)
        assert blk is not None and "keyframes" in blk, f"{attr}无关键帧"
        assert len(blk["keyframes"]) >= kmin, f"{attr}关键帧不足"
        assert all(0.0 <= kf["value"] <= 1.0 for kf in blk["keyframes"]), f"{attr}值越界"
    print(f"OK {os.path.basename(path)}: " +
          ", ".join(f"{a}={len(M.find_esp_attr(esp,a)['keyframes'])}kf" for a in need))


def main():
    import json
    jobs = [("A_时间.esp", build_probe_a,
             {"worldTime": 2, "longitude": 3, "rotationX": 2}),
            ("B_视野.esp", build_probe_b,
             {"fov": 2, "longitude": 3, "rotationX": 2}),
            ("C_盯住.esp", build_probe_c,
             {"longitude": 3, "rotationX": 2}),
            ("A2_时间补区间.esp", build_probe_a2,
             {"worldTime": 2, "longitude": 3, "rotationX": 2}),
            ("B2_视野放慢.esp", build_probe_b2,
             {"fov": 2, "longitude": 3, "rotationX": 2})]
    for fname, fn, need in jobs:
        path = os.path.join(HERE, fname)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(fn(), f, ensure_ascii=False, indent=4)
        decode_check(path, need)
    print("探针3个已生成（scratch，未进视频制作/）")


main()
