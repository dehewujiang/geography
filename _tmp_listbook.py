# -*- coding: utf-8 -*-
import os, zipfile, re, html
base = os.path.dirname(os.path.abspath(__file__))
epub = [os.path.join(r, f) for r, d, fs in os.walk(base)
        for f in fs if f.lower().endswith(".epub") and ".git" not in r][0]
z = zipfile.ZipFile(epub)
keys = ["钓鱼城", "蒙哥", "合州", "王坚", "张珏", "北返", "鄂州", "潭州",
        "渡口", "关隘", "垭口", "驿站", "嘉陵江", "渠江", "涪江", "合川",
        "钓鱼山", "护国门", "奇胜门", "镇西门"]
chaps = sorted(n for n in z.namelist() if re.match(r"index_split_\d+\.html$", n))
tag = re.compile(r"<[^>]+>")
for c in chaps:
    raw = z.read(c).decode("utf-8", "replace")
    txt = html.unescape(tag.sub("\n", raw))
    lines = [l.strip() for l in txt.split("\n") if l.strip()]
    hits = [l for l in lines if any(k in l for k in keys)]
    if hits:
        print("=" * 20, ascii(c), len(lines), "paras")
        for h in hits[:25]:
            print("  -", h[:140])
print("DONE chapters:", len(chaps))
