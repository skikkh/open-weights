# AIモデル図鑑

国内外の最新AIモデルのまとめサイトです。対象は大型LLM・ローカルLLM・国産LLM・音声認識・音声合成・Speech to Speech・音楽・画像・動画・3D・Decision Model。自前のGPUやPCに載せられるオープンウェイトを中心に、比較用のAPIサービスも載せています。

公開先: https://skikkh.github.io/open-weights/

有料APIのトークン料金は [API料金比較](https://skikkh.github.io/open-weights/#frontier-pricing) で、開発会社・同じモデルの提供元・同等クラス別に比較できます。入力・出力量、キャッシュ命中率、月間回数を指定して試算。原通貨を保持し、長文割増と公式の料金改定予定を反映します。

- データ: `data/*.json`
- ページの雛形: `site/template.html`
- ビルド: `python3 scripts/build.py`（検証して `docs/index.html` を生成。GitHub Pages は `main` の `/docs` を配信）
- 定期更新の手順: [UPDATE.md](UPDATE.md)（3日ごとに自動実行）
- 最新の更新記録: [11月5日の即時更新](audits/2026-11-05-即時更新.md)（Kimi公開確認・8行の補完・確認範囲と保留理由）
- API料金比較の条件・出典・検証: [11月12日の追加記録](audits/2026-11-12-API料金比較.md)
