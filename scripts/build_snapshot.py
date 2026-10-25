#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_snapshot.py —— 从麦当劳 MCP 拉取真实数据，生成本地演示快照。

用法:
    set MCD_MCP_URL=<MCP 端点>
    set MCD_TOKEN=<你的 Token>
    python scripts/build_snapshot.py

输出到 assets/snapshot.json（页面与 Skill 共用，纯离线可跑）。
注意：脚本只从环境变量读取凭证，仓库内不保存任何 Token。
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

URL = os.environ.get("MCD_MCP_URL", "https://mcp.mcd.cn")
TOKEN = os.environ.get("MCD_TOKEN", "")
OUT = Path(__file__).resolve().parent.parent / "assets" / "snapshot.json"

# 需要展开 round 结构的套餐数量（限流 600 次/分，保守取前 N 个）
COMBO_LIMIT = int(os.environ.get("COMBO_LIMIT", "12"))
STORE_CODE = os.environ.get("STORE_CODE", "")


def rpc(method, params, _id=1):
    body = json.dumps({"jsonrpc": "2.0", "id": _id, "method": method, "params": params}).encode()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": "Bearer " + TOKEN,
    }
    if os.environ.get("MCP_CONTEXT"):
        headers["X-WorkBuddy-MCP-Context"] = os.environ["MCP_CONTEXT"]
    req = urllib.request.Request(URL, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
    # Streamable HTTP 可能以 SSE 形式返回
    if raw.lstrip().startswith("{"):
        return json.loads(raw)
    for line in raw.splitlines():
        if line.startswith("data:"):
            try:
                return json.loads(line[5:].strip())
            except Exception:
                pass
    raise RuntimeError("无法解析响应: " + raw[:300])


def call_tool(name, args):
    """调 tools/call，返回文本内容或结构化结果；失败返回 None。"""
    for attempt in range(3):
        try:
            res = rpc("tools/call", {"name": name, "arguments": args}, _id=int(time.time() * 1000) % 100000)
            if "error" in res:
                return None
            content = res.get("result", {}).get("content")
            if content and isinstance(content, list):
                txt = content[0].get("text", "")
                try:
                    return json.loads(txt)
                except Exception:
                    return txt
            return res.get("result")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2 ** attempt)
                continue
            return None
        except Exception:
            return None
    return None


def main():
    if not TOKEN:
        print("缺少 MCD_TOKEN 环境变量", file=sys.stderr)
        return 1

    snap = {"meta": {}, "store": {}, "menu": {}, "nutrition": [], "combos": []}

    t = call_tool("now-time-info", {})
    if isinstance(t, dict):
        snap["meta"]["now"] = t
    print("时间:", (t or {}).get("formatted") if isinstance(t, dict) else "-")

    stores = call_tool("query-nearby-stores", {"beType": 1, "searchType": 1})
    store_list = []
    if isinstance(stores, dict):
        store_list = stores.get("stores") or stores.get("data") or []
    if store_list:
        # 只保留门店名与 code，用于演示；丢弃任何账号/位置隐私字段
        snap["store"] = {
            "storeCode": STORE_CODE or store_list[0].get("storeCode"),
            "storeName": store_list[0].get("storeName") or store_list[0].get("name"),
            "reservation": store_list[0].get("reservationTimeOptions") or store_list[0].get("reservation"),
        }
        # 不导出完整门店列表（属于账号个人数据）；快照只保留实际采样的那一家，
        # 且店名统一泛化为「示例门店」，避免把个人常去门店带进开源仓库。
        snap["store"]["storeName"] = "示例门店"
    code = snap["store"].get("storeCode") or STORE_CODE
    print("门店:", snap["store"].get("storeName"), code)

    if code:
        menu = call_tool("query-meals", {"beType": 1, "orderType": 1, "storeCode": code})
        if isinstance(menu, dict):
            snap["menu"] = menu
        n = 0
        for c in (menu or {}).get("categories", []):
            n += len(c.get("meals", []) or [])
        print("菜单 SKU:", n)

    nut = call_tool("list-nutrition-foods", {})
    if isinstance(nut, list):
        snap["nutrition"] = nut
    elif isinstance(nut, dict):
        snap["nutrition"] = nut.get("foods") or nut.get("data") or []
    print("营养条目:", len(snap["nutrition"]))

    # 展开套餐 round 结构（换配餐对比的数据基础）
    combos = []
    for c in (snap["menu"] or {}).get("categories", []):
        for m in c.get("meals", []) or []:
            if m.get("combo") or m.get("isCombo") or "套" in str(m.get("name", "")):
                combos.append(m)
            if len(combos) >= COMBO_LIMIT:
                break
        if len(combos) >= COMBO_LIMIT:
            break
    for m in combos:
        d = call_tool(
            "query-meal-detail",
            {"beType": 1, "orderType": 1, "storeCode": code, "code": m.get("code")},
        )
        if d:
            snap["combos"].append({"code": m.get("code"), "name": m.get("name"), "price": m.get("currentPrice"), "detail": d})
        time.sleep(0.2)
    print("套餐结构:", len(snap["combos"]))

    snap["meta"]["generatedAt"] = time.strftime("%Y-%m-%d %H:%M:%S")
    snap["meta"]["source"] = "麦当劳 MCP（真实调用）"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(snap, ensure_ascii=False, indent=1), encoding="utf-8")
    print("已写入", OUT, round(OUT.stat().st_size / 1024, 1), "KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
