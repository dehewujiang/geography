# -*- coding: utf-8 -*-
"""
[INPUT]: 根目录母版KML + 粮库 GeoNames CN.zip（路径读根目录 粮库.md 路牌）
[OUTPUT]: 坐标核验表（stdout）——每个地标/节点：旧坐标 vs GeoNames 前3候选 + 差距km
[POS]: 工具箱——把母版里"LLM估算"的坐标与权威地名库对账，产出核验表供人审；只读不写任何数据
[PROTOCOL]: 变更时更新此头部，然后检查同级 说明.txt
"""
import os, re, math, zipfile
import xml.etree.ElementTree as ET

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KML_PATH = os.path.join(BASE, "蒙古大迂回_三路路线.kml")
NS = {"k": "http://www.opengis.net/kml/2.2"}

# 节点名→查询名（母版描述里的叫法有修饰，这里映射到 GeoNames 能查的名字）
ALIASES = {
    "陕西汉中": "汉中",
    "云南": "昆明",          # 南北两线起点坐标实测=昆明
    "大理北门": "大理",
    "都江堰西缘": "都江堰",
    "汉源渡大渡河": "汉源",
    "南宁老苍关": "南宁",     # 老苍关另案细查
    "合川钓鱼城": "钓鱼城",
    "合州": "合川",
    "荆山怀远": "怀远",
}
# 7 个点名地标：完整名→查询名
POINT_NAMES = {
    "安南-河内1258年请降称臣": "河内",
    "起点-临洮集结1253年8月": "临洮",
    "分兵点-达拉沟": "达拉沟",
    "中转-大理1253年12月": "大理",
    "湖南-长沙1259年围城": "长沙",
    "湖北-武昌1259年被围": "武昌",
    "结局-钓鱼城1259年8月蒙哥去世": "钓鱼城",
}


def km(lon1, lat1, lon2, lat2):
    dx = (lon2 - lon1) * 111.32 * math.cos(math.radians((lat1 + lat2) / 2))
    dy = (lat2 - lat1) * 110.57
    return math.hypot(dx, dy)


def graveyard_root():
    text = open(os.path.join(BASE, "粮库.md"), encoding="utf-8").read()
    m = re.search(r"([A-Za-z]:\\[^\s`）)]+)", text)
    path = m.group(1).rstrip("\\")
    return path


def chain_names(desc):
    """从描述里抠 'A→B→C' 链（首元素去前缀从句、末元素去尾部从句、去括号注）"""
    if not desc:
        return None
    m = re.search(r"[^：。]*→[^。]*", desc)
    if not m:
        return None
    parts = [p.strip() for p in m.group(0).split("→")]
    parts[0] = parts[0].rsplit("，", 1)[-1]
    for i in range(1, len(parts)):
        parts[i] = parts[i].split("，", 1)[0]
    return [re.sub(r"[（(].*?[)）]", "", p).strip() for p in parts]


def parse_kml():
    """→ [(placemark名, 类型, [节点])]；节点=(raw名或None, lon, lat)"""
    root = ET.parse(KML_PATH).getroot()
    out = []
    for pm in root.findall(".//k:Placemark", NS):
        pname = (pm.findtext("k:name", "", NS) or "").strip()
        desc = pm.findtext("k:description", "", NS) or ""
        coords = []
        line = pm.find("k:LineString", NS)
        point = pm.find("k:Point", NS)
        ctext = None
        if line is not None:
            ctext = line.findtext("k:coordinates", "", NS)
        elif point is not None:
            ctext = point.findtext("k:coordinates", "", NS)
        for tok in (ctext or "").split():
            p = tok.split(",")
            coords.append((float(p[0]), float(p[1])))
        if not coords:
            continue
        if point is not None:
            name = POINT_NAMES.get(pname, pname)
            out.append((pname, "Point", [(name, *coords[0])]))
        else:
            names = chain_names(desc)
            if names is None:
                out.append((pname, "Line无链", [(None, lon, lat) for lon, lat in coords]))
            else:
                flag = "" if len(names) == len(coords) else "名数≠点数"
                nodes = []
                for i, (lon, lat) in enumerate(coords):
                    nm = names[i] if i < len(names) else None
                    nodes.append((nm, lon, lat))
                out.append((pname + (f" [{flag}]" if flag else ""), "Line", nodes))
    return out


def geonames_scan(targets):
    gpath = os.path.join(graveyard_root(), "GeoNames_中国", "CN.zip")
    pat = re.compile("|".join(map(re.escape, sorted(targets, key=len, reverse=True))))
    hits = {t: [] for t in targets}
    seen = set()
    with zipfile.ZipFile(gpath) as z, z.open("CN.txt") as f:
        for line in f:
            s = line.decode("utf-8", "replace")
            if not pat.search(s):
                continue
            x = s.rstrip("\n").split("\t")
            if len(x) < 15:
                continue
            for t in targets:
                if t == x[1] or t == x[2] or (x[3] and t in x[3]):
                    k = (t, x[1], x[4], x[5])
                    if k in seen:
                        continue
                    seen.add(k)
                    try:
                        lon, lat = float(x[5]), float(x[4])
                    except ValueError:
                        continue
                    hits[t].append({
                        "name": x[1], "ascii": x[2], "lon": lon, "lat": lat,
                        "cls": x[6], "code": x[7], "pop": int(x[14] or 0), "adm": x[10],
                    })
    return hits


def rank(cands, lon, lat):
    def key(c):
        cls = 0 if c["cls"] == "P" else (1 if c["cls"] == "A" else 2)
        return (round(km(lon, lat, c["lon"], c["lat"])), cls, -c["pop"])
    return sorted(cands, key=key)


def fmt(c):
    return f"{c['name']} {c['lon']:.4f},{c['lat']:.4f} [{c['cls']}{c['code']}] 人口{c['pop']} adm{c['adm']}"


def main():
    marks = parse_kml()
    anchor = {}
    targets = set()
    for _, _, nodes in marks:
        for nm, lon, lat in nodes:
            if nm:
                q = ALIASES.get(nm, nm)
                targets.add(q)
                anchor.setdefault(q, (lon, lat))
    print(f"查询目标 {len(targets)} 个\n")
    hits = geonames_scan(targets)

    print("=" * 80)
    print("一、逐节点对照（首选=离旧点最近的同名候选）")
    print("=" * 80)
    for pname, kind, nodes in marks:
        print(f"\n## {pname}（{kind}）")
        for nm, lon, lat in nodes:
            if nm is None:
                print(f"  ? 未命名节点  旧: {lon:.4f},{lat:.4f}")
                continue
            q = ALIASES.get(nm, nm)
            cands = rank(hits.get(q, []), lon, lat)
            if not cands:
                print(f"  ✗ {nm:<10} 旧: {lon:.4f},{lat:.4f}   查无此名")
                continue
            best = cands[0]
            d = km(lon, lat, best["lon"], best["lat"])
            print(f"  · {nm:<10} 旧: {lon:.4f},{lat:.4f} → {fmt(best)} 距{d:.1f}km")

    print("\n" + "=" * 80)
    print("二、每名全候选（按离旧点距离排，前6；供人审挑县城驻地/歧义）")
    print("=" * 80)
    for t in sorted(hits):
        c = rank(hits[t], *anchor[t])
        print(f"\n【{t}】{len(c)} 条")
        for x in c[:6]:
            d = km(anchor[t][0], anchor[t][1], x["lon"], x["lat"])
            print(f"   {d:7.1f}km  {fmt(x)}")
    print("\nDONE")


if __name__ == "__main__":
    main()
