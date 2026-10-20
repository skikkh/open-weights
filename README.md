# オープンウェイト図鑑

自前のGPUやPCに載せられる最新オープンウェイトモデル（大型LLM・ローカルLLM・国産LLM・音声認識・音声合成・Speech to Speech・音楽・画像・動画・3D・Decision Model）のまとめサイトです。

公開先: https://skikkh.github.io/open-weights/

- データ: `data/*.json`
- ページの雛形: `site/template.html`
- ビルド: `python3 scripts/build.py`（検証して `docs/index.html` を生成。GitHub Pages は `main` の `/docs` を配信）
- 定期更新の手順: [UPDATE.md](UPDATE.md)（3日ごとに自動実行）
