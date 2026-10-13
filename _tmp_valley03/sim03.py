# -*- coding: utf-8 -*-
"""03东路贴沟试点：沿地形找低线（标准库-only，采样一次，结果烘进主脚本离线复现）."""
import heapq
import json
import math
import os
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ANCHORS = [  # 母版东路9点，只当骨架，不改母版
    (103.50, 34.00), (103.70, 32.88), (103.60, 32.65), (103.62, 30.99),
    (103.04, 29.98), (102.26, 27.88), (101.71, 26.58), (101.23, 25.50),
    (100.16, 25.69),
]
STEP = 0.05      # 约5.5km网格（试点精度；窄谷可能漏，见输出stats）
MARGIN = 0.20    # 腿包络外扩
CHUNK = 50       # API每批点数（429限流后调小）
SLEEP = 2.5      # 批间隔秒（429限流后拉长）
BACKOFF = (60, 120, 180)  # 429退避秒
SRC = "open-meteo elevation API, 2026-10-12"


ELEV_CACHE = os.path.join(HERE, "elev_cache.json")  # 高程成果缓存：每批落盘，断点续跑


def load_elev_cache():
    if os.path.exists(ELEV_CACHE):
        return json.load(open(ELEV_CACHE, encoding="utf-8"))
    return {}


def save_elev_cache(cache):
    json.dump(cache, open(ELEV_CACHE, "w", encoding="utf-8"))


def fetch_elev(pts):
    """pts=[(lat,lon)...] -> [elev...]，分批GET；高程按点缓存，每批落盘."""
    out = []
    ec = load_elev_cache()
    for i in range(0, len(pts), CHUNK):
        seg = pts[i:i + CHUNK]
        lat = ",".join(f"{p[0]:.4f}" for p in seg)
        lon = ",".join(f"{p[1]:.4f}" for p in seg)
        url = (f"https://api.open-meteo.com/v1/elevation?latitude={lat}&longitude={lon}")
        for attempt in (1, 2, 3, 4):
            try:
                with urllib.request.urlopen(url, timeout=30) as r:
                    got = json.load(r)["elevation"]
                for p, e in zip(seg, got):
                    out.append(ec.setdefault(f"{p[0]:.4f},{p[1]:.4f}", e))
                save_elev_cache(ec)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 4:
                    time.sleep(BACKOFF[attempt - 1])  # 限流退避
                    continue
                raise
            except Exception:
                if attempt == 4:
                    raise
                time.sleep(2 * attempt)
        time.sleep(SLEEP)
    return out


def km(a, b):
    mid = math.radians((a[1] + b[1]) / 2.0)
    return math.hypot((a[0] - b[0]) * math.cos(mid) * 111.32, (a[1] - b[1]) * 110.57)


def leg_path(p, q):
    lon0, lon1 = min(p[0], q[0]) - MARGIN, max(p[0], q[0]) + MARGIN
    lat0, lat1 = min(p[1], q[1]) - MARGIN, max(p[1], q[1]) + MARGIN
    nx = int(round((lon1 - lon0) / STEP)) + 1
    ny = int(round((lat1 - lat0) / STEP)) + 1
    cells = [(lat0 + j * STEP, lon0 + i * STEP) for j in range(ny) for i in range(nx)]
    elev = fetch_elev(cells)
    E = {idx: (e if e is not None else 4000.0) for idx, e in enumerate(elev)}

    def nearest(pt):
        i = min(nx - 1, max(0, int(round((pt[0] - lon0) / STEP))))
        j = min(ny - 1, max(0, int(round((pt[1] - lat0) / STEP))))
        return j * nx + i

    S, T = nearest(p), nearest(q)
    DIRS = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
            (-1, -1, 1.4142), (-1, 1, 1.4142), (1, -1, 1.4142), (1, 1, 1.4142)]
    INF = float("inf")
    dist = {S: 0.0}
    prev = {}
    pq = [(0.0, S)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == T:
            break
        if d > dist.get(u, INF):
            continue
        ux, uy = u % nx, u // nx
        for dx, dy, f in DIRS:
            vx, vy = ux + dx, uy + dy
            if not (0 <= vx < nx and 0 <= vy < ny):
                continue
            v = vy * nx + vx
            step_km = STEP * 111.0 * f
            climb = max(0.0, E[v] - E[u])
            # 代价=距离×(1+爬升惩罚+高海拔惩罚)：宁绕远，不爬高、不驻高
            w = step_km * (1.0 + climb / 150.0 + max(0.0, E[v] - 1500.0) / 1500.0)
            nd = d + w
            if nd < dist.get(v, INF):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if T not in prev and T != S:
        raise RuntimeError("leg无通路")
    cells_out, u = [], T
    while u != S:
        cells_out.append(u)
        u = prev[u]
    cells_out.append(S)
    cells_out.reverse()
    return [(lon0 + (c % nx) * STEP, lat0 + (c // nx) * STEP) for c in cells_out]


def resample(path, every_km=8.0):
    cum = [0.0]
    for i in range(1, len(path)):
        cum.append(cum[-1] + km(path[i - 1], path[i]))
    total = cum[-1]
    n = max(2, int(round(total / every_km)))
    out, k = [path[0]], 1
    for s in range(1, n):
        target = total * s / n
        while k < len(cum) - 1 and cum[k] < target:
            k += 1
        t = 0.0 if cum[k] == cum[k - 1] else (target - cum[k - 1]) / (cum[k] - cum[k - 1])
        a, b = path[k - 1], path[k]
        out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    out.append(path[-1])
    return out, total


def straight_elev(p, q):
    n = 40
    pts = [(p[1] + (q[1] - p[1]) * i / n, p[0] + (q[0] - p[0]) * i / n) for i in range(n + 1)]
    return fetch_elev(pts)


def main():
    cache_path = os.path.join(HERE, "legs_cache.json")
    cache = {}
    if os.path.exists(cache_path):
        cache = json.load(open(cache_path, encoding="utf-8"))
    full, legs_km, elevs_straight = [], [], []
    for i in range(len(ANCHORS) - 1):
        key = str(i)
        if key in cache:
            path = [tuple(p) for p in cache[key]["path"]]
            st = cache[key]["straight"]
            _, total = resample(path)
            print(f"leg{i}: 缓存命中 total约{total:.0f}km", flush=True)
        else:
            p, q = ANCHORS[i], ANCHORS[i + 1]
            path = leg_path(p, q)
            st = straight_elev(p, q)
            cache[key] = {"path": [list(p) for p in path], "straight": st}
            json.dump(cache, open(cache_path, "w", encoding="utf-8"))
            _, total = resample(path)
            print(f"leg{i}: {len(path)}格 total约{total:.0f}km", flush=True)
        legs_km.append(round(total, 1))
        full.extend(path if i == 0 else path[1:])
        elevs_straight.extend(st)
        print(f"leg{i}: {len(path)}格 total约{total:.0f}km", flush=True)
    pts, total = resample(full)
    pe = fetch_elev([(la, lo) for lo, la in pts])
    stats = {
        "legs_km": legs_km,
        "total_km": round(total, 1),
        "n_points": len(pts),
        "path_max_m": round(max(pe)),
        "straight_max_m": round(max(e for e in elevs_straight if e is not None)),
        "step_deg": STEP,
        "src": SRC,
    }
    with open(os.path.join(HERE, "sim03.json"), "w", encoding="utf-8") as f:
        json.dump({"points": [[round(lo, 4), round(la, 4)] for lo, la in pts],
                   "stats": stats}, f, ensure_ascii=False, indent=1)
    print(json.dumps(stats, ensure_ascii=False, indent=1))


main()
