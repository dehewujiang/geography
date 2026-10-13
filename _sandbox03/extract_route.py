# -*- coding: utf-8 -*-
"""沙盘试点数据准备：从母版KML抽取东路路线+全部地标，输出 route.json.

[INPUT]: 母版《蒙古大迂回_三路路线.kml》（只读，项目唯一坐标来源）
[OUTPUT]: 同目录 route.json（route=东路坐标串；landmarks=全部带名地标）
[POS]: _sandbox03 的数据入口，index.html 只吃这个 json，不直接读母版
[PROTOCOL]: 母版地标数=17；此处只读不校验17（校验归 make_video_assets.py）
"""
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "蒙古大迂回_三路路线.kml")


def parse_placemarks(xml):
    out = []
    for block in re.findall(r"<Placemark>.*?</Placemark>", xml, re.S):
        nm = re.search(r"<name>(.*?)</name>", block, re.S)
        name = nm.group(1).strip() if nm else ""
        coords = re.search(r"<coordinates>(.*?)</coordinates>", block, re.S)
        if not coords:
            continue
        pts = []
        for tup in coords.group(1).split():
            first = tup.split(",")[:2]
            pts.append([float(first[0]), float(first[1])])
        kind = "route" if "<LineString" in block else "place"
        out.append({"name": name, "kind": kind, "coords": pts})
    return out


def east_route(placemarks):
    """东路=母版9点骨架；匹配名含'东路'，剔除临时/对照标记."""
    cands = [p for p in placemarks if p["kind"] == "route" and "东路" in p["name"]]
    if not cands:
        raise SystemExit("母版里找不到含'东路'的路线，请人工核对地名清单：%s"
                         % [p["name"] for p in placemarks if p["kind"] == "route"])
    cands.sort(key=lambda p: len(p["name"]))  # 最短名=正主，长名多为别名
    return cands[0]


def match_landmarks(placemarks, route):
    """给路线9点配地名：找同名地点（坐标差<0.5°），配不上的用序号."""
    places = [p for p in placemarks if p["kind"] == "place"]
    named = []
    for i, (lon, lat) in enumerate(route):
        best, bd = None, 0.5
        for p in places:
            for lo, la in p["coords"]:
                d = math.hypot(lo - lon, la - lat)
                if d < bd:
                    best, bd = p, d
        named.append(best["name"] if best else f"点{i + 1}")
    return named


def main():
    with open(SRC, encoding="utf-8") as f:
        placemarks = parse_placemarks(f.read())
    assert len(placemarks) == 17, f"母版地标数应为17，实际{len(placemarks)}"
    route_pm = east_route(placemarks)
    named = match_landmarks(placemarks, route_pm["coords"])
    data = {
        "route_name": route_pm["name"],
        "route": route_pm["coords"],
        "station_names": named,
        "landmarks": [
            {"name": p["name"], "kind": p["kind"], "coords": p["coords"][:1]}
            for p in placemarks
        ],
    }
    out = os.path.join(HERE, "route.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"路线[{route_pm['name']}] {len(route_pm['coords'])}点")
    print("站名：", " → ".join(named))
    print(f"写出 {out}")


main()
