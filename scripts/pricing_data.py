"""API料金の数値・出典・掲載モデルとの参照関係を検証する。"""
import math
import re


def validate_pricing(data, model_ids):
    errors = []
    if data.get("unit_tokens") != 1_000_000:
        errors.append("API料金の単位は100万トークンに統一してください")
    providers = {p["id"] for p in data.get("providers", [])}
    classes = {p["id"] for p in data.get("classes", [])}
    models = {}
    for m in data.get("models", []):
        if m["id"] in models or m["id"] not in model_ids:
            errors.append(f"API料金モデルの参照・重複: {m['id']}")
        models[m["id"]] = m
        if m.get("class") not in classes or not m.get("developer") or not m.get("family"):
            errors.append(f"API料金モデルの分類が不正: {m['id']}")
    seen = set()
    for q in data.get("quotes", []):
        label = q.get("id", "?")
        if label in seen:
            errors.append(f"API料金id重複: {label}")
        seen.add(label)
        if q.get("model_id") not in models or q.get("provider_id") not in providers:
            errors.append(f"API料金の参照先がありません: {label}")
        if q.get("currency") not in {"USD", "JPY", "CNY"}:
            errors.append(f"API料金の通貨が不正: {label}")
        if q.get("status") not in {"available", "unconfirmed", "subscription", "limited"}:
            errors.append(f"API料金の提供段階が不正: {label}")
        if q.get("plan") not in {"standard", "batch", "off_peak", "flex", "priority"}:
            errors.append(f"API料金の課金方式が不正: {label}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", q.get("verified_at", "")) or not q.get("sources") or not q.get("note_ja"):
            errors.append(f"API料金の確認日・出典・条件が必要: {label}")
        if any(not u.startswith("https://") for u in q.get("sources", [])):
            errors.append(f"API料金の出典URLが不正: {label}")
        all_rates = [q.get("rates", {})]
        all_rates += [t.get("rates", {}) for t in q.get("tiers", [])]
        all_rates += [t.get("rates", {}) for t in q.get("future_rates", [])]
        for r in all_rates:
            for value in r.values():
                if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
                    errors.append(f"API料金は0以上の数値かnull: {label}")
        if q.get("status") == "available" and any(q.get("rates", {}).get(k) is None for k in ["input", "output"]):
            errors.append(f"比較可能なAPI料金には入出力単価が必要: {label}")
        thresholds = [t.get("over_input", -1) for t in q.get("tiers", [])]
        if thresholds != sorted(set(thresholds)) or any(x < 0 for x in thresholds):
            errors.append(f"API料金の長文閾値が不正: {label}")
        dates = [t.get("from", "") for t in q.get("future_rates", [])]
        if dates != sorted(set(dates)) or any(not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) for d in dates):
            errors.append(f"API料金の改定予定日が不正: {label}")
    return errors
