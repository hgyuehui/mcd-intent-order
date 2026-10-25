#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_page.py —— 把 assets/snapshot.json 内联进 index.html，产出可离线双击打开的单文件页面。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
snap = json.loads((ROOT / "assets" / "snapshot.json").read_text(encoding="utf-8"))
html = (ROOT / "index.html").read_text(encoding="utf-8")
blob = json.dumps(snap, ensure_ascii=False, separators=(",", ":"))
if "__SNAPSHOT__" not in html:
    print("[skip] index.html 中无 __SNAPSHOT__ 占位符（可能已内联）")
else:
    html = html.replace("__SNAPSHOT__", blob)
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print(f"[ok] 快照已内联，共 {len(blob)//1024} KB")
