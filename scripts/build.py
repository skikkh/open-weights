#!/usr/bin/env python3
"""data/*.json を検証して site/template.html に埋め込み、docs/index.html を出力する。

使い方: python3 scripts/build.py
"""
import json
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
    hw = load("hardware.json", {})
    recipes = load("recipes.json", {})

    errors = []
    check("llm", llm, LLM_REQUIRED, errors)
    check("asr", asr, ASR_REQUIRED, errors)
    check("tts", tts, TTS_REQUIRED, errors)
    for k, items in gen.items():
        check(k, items, GEN_REQUIRED, errors)
    if errors:
        print("検証エラー:", *errors, sep="\n  ")
        sys.exit(1)

    payload = json.dumps({"meta": meta, "llm": llm, "asr": asr, "tts": tts, "gen": gen, "hw": hw, "recipes": recipes}, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8")
    if "/*__DATA__*/" not in html:
        print("template.html にデータ差し込み位置 /*__DATA__*/ がありません")
        sys.exit(1)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html.replace("/*__DATA__*/", payload), encoding="utf-8")
    jp = sum(1 for m in llm if m.get("country") == "JP")
    extra = " / ".join(f"{k} {len(v)}" for k, v in gen.items())
    print(f"OK: {OUT.relative_to(ROOT)}  LLM {len(llm)}（国産 {jp}） / ASR {len(asr)} / TTS {len(tts)} / {extra}  {OUT.stat().st_size // 1024}KB")


if __name__ == "__main__":
    main()
