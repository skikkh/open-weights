#!/usr/bin/env python3
"""data/*.json を検証して site/template.html に埋め込み、docs/index.html を出力する。

使い方: python3 scripts/build.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TEMPLATE = ROOT / "site" / "template.html"
# GitHub Pages（main ブランチの /docs）で配信される
OUT = ROOT / "docs" / "index.html"

COMMERCIAL = {"yes", "conditional", "no"}
# 予告（発表済み・重みは未公開）のエントリは status: "announced"
STATUS = {None, "announced"}
LLM_REQUIRED = ["id", "name", "org", "country", "release", "total_b", "license", "commercial"]
ASR_REQUIRED = ["id", "name", "org", "country", "release", "license", "commercial"]
TTS_REQUIRED = ["id", "name", "org", "country", "release", "license", "commercial", "ja_support"]
# 汎用カテゴリは API 提供で公開日が分からないものがあるので release は任意（ページ上は「公開日 不明」）
GEN_REQUIRED = ["id", "name", "org", "country", "license", "commercial", "tasks"]
# 汎用ページ（data/<id>.json）。ファイルがなければ空として扱う
GEN_PAGES = ["s2s", "music", "image", "video", "3d", "decision"]


def check_frontier(frontier, gen, meta, errors):
    """表示に統合される全ファイルで、同系列・同役割の旧版と重複を防ぐ。"""
    pool = list(frontier)
    for category, items in gen.items():
        pool.extend(dict(m, category=category) for m in items if m.get("access") == "api")
    pool.extend(dict(m, category="llm") for m in meta.get("jp_reference_models", []))
    seen_ids, seen_series = set(), {}
    current_names = {m["name"].casefold(): m["id"] for m in pool}
    for m in pool:
        mid, series = m["id"], m.get("series")
        if mid in seen_ids:
            errors.append(f"有料一覧 {mid}: ファイルをまたいでidが重複しています")
        seen_ids.add(mid)
        if not series or re.search(r"\d+\.\d+", series):
            errors.append(f"有料一覧 {mid}: 版番号を含まない固定のseriesが必要です")
        tier = m.get("availability_tier", "general")
        if tier not in {"general", "limited", "preview", "rollout"}:
            errors.append(f"有料一覧 {mid}: 提供段階が不正です")
        key = (m["category"], series)
        if key in seen_series:
            previous = seen_series[key]
            other = previous[0]
            # 限定後継を待つ間の一般提供版のみ併載できる。
            if len(previous) != 1 or {tier, other.get("availability_tier", "general")} != {"limited", "general"}:
                errors.append(f"有料一覧 {mid}: 同じ系列・役割の現行版が重複 ({other['id']})")
            previous.append(m)
        else:
            seen_series[key] = [m]
        for old in m.get("supersedes", []):
            if old.casefold() in current_names:
                errors.append(f"有料一覧 {mid}: 置換済みの旧版 {old} が現行一覧に残っています")
    return pool


def load(name, default=None):
    path = DATA / name
    if default is not None and not path.exists():
        return default
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def check(kind, items, required, errors):
    seen = set()
    for i, m in enumerate(items):
        label = f"{kind}[{i}] {m.get('id', '?')}"
        for k in required:
            if m.get(k) in (None, ""):
                errors.append(f"{label}: 必須項目 {k} がありません")
        if m.get("id") in seen:
            errors.append(f"{label}: id が重複しています")
        seen.add(m.get("id"))
        if m.get("status") not in STATUS:
            errors.append(f"{label}: status は announced か省略")
        if m.get("status") == "announced" and m.get("supersedes"):
            errors.append(f"{label}: 予告のエントリに supersedes は付けない（重みが出て旧版を消すときに付ける）")
        if m.get("commercial") not in COMMERCIAL:
            errors.append(f"{label}: commercial は yes/conditional/no のどれか")
        for u in [m.get("hf")] + list(m.get("sources") or []):
            if u and not str(u).startswith(("http://", "https://")):
                errors.append(f"{label}: URL が不正 {u}")
        if kind == "tts":
            if m.get("voice_cloning") not in {"zero-shot", "fine-tune", "preset-only", "voice-design", "external-service", "unknown"}:
                errors.append(f"{label}: 声づくりの分類が不正です")
            if not m.get("voice_cloning_note") or not m.get("voice_cloning_sources"):
                errors.append(f"{label}: 声づくりの条件と公式出典が必要です")
        if kind in GEN_PAGES:
            for k in ("params_b", "min_vram_gb", "rec_vram_gb"):
                v = m.get(k)
                if v is not None and not isinstance(v, (int, float)):
                    errors.append(f"{label}: {k} は数値か null")
        if kind == "llm":
            for k in ("total_b", "active_b", "weights_gb", "aa_index", "context_k"):
                v = m.get(k)
                if v is not None and not isinstance(v, (int, float)):
                    errors.append(f"{label}: {k} は数値か null")


def main():
    llm = load("llm.json")
    asr = load("asr.json")
    tts = load("tts.json")
    meta = load("meta.json")
    gen = {k: load(f"{k}.json", []) for k in GEN_PAGES}
    frontier = load("frontier.json", [])
    hw = load("hardware.json", {})
    recipes = load("recipes.json", {})

    errors = []
    check("llm", llm, LLM_REQUIRED, errors)
    check("asr", asr, ASR_REQUIRED, errors)
    check("tts", tts, TTS_REQUIRED, errors)
    for k, items in gen.items():
        check(k, items, GEN_REQUIRED, errors)
    check("frontier", frontier, ["id", "name", "org", "country", "category", "availability_ja", "sources", "verified_at"], errors)
    for m in frontier:
        if m.get("category") not in {"llm", "asr", "tts", "s2s", "music", "image", "video", "3d", "decision"}:
            errors.append(f"frontier {m.get('id')}: カテゴリが不正です")
    paid_pool = check_frontier(frontier, gen, meta, errors)
    if errors:
        print("検証エラー:", *errors, sep="\n  ")
        sys.exit(1)

    payload = json.dumps({"meta": meta, "frontier": frontier, "llm": llm, "asr": asr, "tts": tts, "gen": gen, "hw": hw, "recipes": recipes}, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8")
    if "/*__DATA__*/" not in html:
        print("template.html にデータ差し込み位置 /*__DATA__*/ がありません")
        sys.exit(1)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html.replace("/*__DATA__*/", payload), encoding="utf-8")
    jp = sum(1 for m in llm if m.get("country") == "JP")
    extra = " / ".join(f"{k} {len(v)}" for k, v in gen.items())
    print(f"OK: {OUT.relative_to(ROOT)}  LLM {len(llm)}（国産 {jp}） / ASR {len(asr)} / TTS {len(tts)} / {extra} / 有料 {len(paid_pool)}  {OUT.stat().st_size // 1024}KB")


if __name__ == "__main__":
    main()
