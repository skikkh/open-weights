#!/usr/bin/env python3
"""有料一覧・照合台帳と、旧版を混ぜる反例を確認する。外部APIは呼ばない。"""
from build import GEN_PAGES, check_frontier, load


def main():
    frontier = load("frontier.json")
    gen = {k: load(f"{k}.json", []) for k in GEN_PAGES}
    meta = load("meta.json")
    errors = []
    pool = check_frontier(frontier, gen, meta, errors)
    review = load("frontier-review.json")
    all_ids = {m["id"] for m in pool}
    for kind in ["llm", "asr", "tts"] + GEN_PAGES:
        all_ids.update(m["id"] for m in load(f"{kind}.json"))
    allowed = {"掲載", "旧版", "要確認", "日本語対象外", "統合サービス", "比較対象", "公開側の候補", "選定範囲外"}
    assert review["as_of"] == meta["updated_at"], "照合日と更新日が異なります"
    assert len(review["boards"]) >= 12, "AAの各カテゴリの確認記録が必要です"
    for m in review["candidates"]:
        assert m["disposition"] in allowed, m["name"]
        assert m["reason"] and m["sources"], m["name"]
        assert set(m["model_ids"]) <= all_ids, m["name"]
        assert m["disposition"] != "掲載" or m["model_ids"], m["name"]
    assert not errors, "\n".join(errors)
    # ファイルをまたいだ旧版や異なる提供段階を混ぜても、誤って通らないこと。
    base = dict(id="current", name="現行版", category="image", series="提供元 画像 旗艦", access="api", availability_tier="general")
    def rejects(items, extra=None):
        found = []
        check_frontier(items, extra or {}, {}, found)
        return bool(found)
    assert not rejects([base])
    old = dict(base, id="old", name="旧版")
    assert rejects([base], {"image": [old]}), "別ファイルの同系列旧版が通過"
    assert rejects([dict(base, supersedes=["旧版"]), dict(old, series="誤った別系列")]), "置換済み旧版が通過"
    limited = dict(base, id="limited", name="限定後継", availability_tier="limited")
    assert not rejects([base, limited]), "一般提供版と限定後継の併載を誤拒否"
    assert rejects([base, limited, dict(limited, id="second")]), "限定後継が二重に通過"
    assert rejects([base, dict(base, id="preview", availability_tier="preview")]), "同役割のプレビューを無条件で併載"
    assert rejects([dict(base, series="旗艦 1.0")]), "版番号を含む可変系列キーが通過"
    sol = [m["name"] for m in pool if m["series"] == "OpenAI GPT Sol"]
    assert sol == ["GPT-6.1 Sol"], sol
    print(f"OK: 有料{len(pool)}件・AA候補{len(review['candidates'])}件、系列重複・旧版・限定後継の反例6件")


if __name__ == "__main__":
    main()
