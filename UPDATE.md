# 定期更新の手順（3日ごと）

このリポジトリは「AIモデル図鑑」（https://skikkh.github.io/open-weights/ ）のデータとビルド一式です。
定期更新エージェントはこの手順どおりに作業してください。

## 0. 前提

- 今日の日付を `date +%F` で確認する。モデルの学習知識は古いので、**必ず Web 検索と一次情報（Hugging Face のモデルページ、公式ブログ、GitHub、公式ドキュメント）で裏を取る**。
- 推測で数値を埋めない。わからない値は `null`。報道だけが根拠の情報は `confidence` を `medium` か `low` にする。
- 既存エントリの書き方（日本語の文体、項目の粒度）に合わせる。
- `docs/index.html` は生成物なので手で編集しない。

## 1. ファイル構成

| ファイル | 中身 |
|---|---|
| `data/llm.json` | LLM（海外＋国産）。国産は `country: "JP"` |
| `data/asr.json` | 日本語音声認識 |
| `data/tts.json` | 日本語音声合成 |
| `data/frontier.json` | フロンティア・有料のLLM・音声等。全カテゴリの定期更新対象 |
| `data/frontier-review.json` | AA各一覧との照合台帳。掲載・旧版・日本語対象外・保留を記録 |
| `data/s2s.json` `music.json` `image.json` `video.json` `3d.json` `decision.json` | 汎用カテゴリ（同じスキーマ） |
| `data/meta.json` | 更新日、次回予定、収録ルール、更新履歴、出典、重み非公開モデルの参考メモ |
| `data/recipes.json` | 大型LLMを Artificial Analysis「Laptops & Workstations」の5機種に載せるレシピ（大型LLMページの「載せるなら」表） |
| `data/hardware.json` | Artificial Analysis「Laptops & Workstations」の実測（`aa_local`）、ローカル機の一覧と価格（`devices`）、量子化ローカルの総括（`summary_ja`） |
| `site/template.html` | ページの雛形（`/*__DATA__*/` にデータが入る） |
| `scripts/build.py` | 検証して `docs/index.html` を生成 |

## 2. 収録ルール（全カテゴリ共通）

1. **公開モデル中心とフロンティア・有料の両側、全カテゴリを毎回更新する**。公開側は重み配布あり、有料側はAPI・会員サービス・契約提供を対象とする。国産LLMではAPIも通常一覧に統合する。音楽・画像・動画・3Dも重み公開の有無に限定しない。
2. **同じ系列・役割は最新の提供版だけ**。後継が提供されたら旧行を消し、新行の `supersedes` に旧版名を残す。単なるAPI別名・推論effort・提供業者違いで件数を増やさない。限定後継の一般提供までは一般提供の現行版を保持する。
3. 同じ世代でも Flash／Pro、サイズ違い、T2V版／I2V版など用途が分かれるものは別エントリ。
4. 公開LLMは40B超を大型、40B以下をローカルに分類。100B以上と40〜100Bの規模も明示する。有料モデルのパラメータ数は非公表なら推測しない。
5. ASR・TTS・Speech to Speech は日本語で使えるものを中心にする。
6. **予告も載せる**: 公式に発表され、重み（API提供カテゴリはサービス）の公開日や公開予定が示されているが、まだ出ていないモデルは「予告」として載せる。`status: "announced"`、`announced`（発表日）を付け、`release` には公開予定日（分からなければ予定月）を入れる。予告のエントリには `supersedes` と `pick` を付けず、旧版は重みが出るまで消さない。根拠は公式発表（ブログ・公式X・ドキュメント）で取り、報道だけなら confidence を medium か low にする。半年以上動きのない予告は消す。
7. 件数合わせで旧版を残したり役割の違う現行版を省いたりしない。ASR・TTSの日本語非対応・未確認候補も照合台帳に理由を残す。日本語のWebページがあるだけでは日本語音声対応の根拠にならない。

## 3. 更新作業

1. `data/meta.json` の `updated_at`（前回更新日）以降のニュースを、カテゴリごとに検索する。
   - **有料側も必須**: `data/frontier.json`、各汎用データの `access: "api"`、`meta.jp_reference_models` をすべて対象とする。
   - 下のAA各一覧の埋め込みデータ／表を取得し、前回の `frontier-review.json` と比較する。AAは候補発見・測定値の出典であり、最新版・提供開始・対応言語は公式の現行モデル表と変更履歴で確認する。AAの評価追加日をデビュー日として転記しない。
   - **Web検索だけに頼らず、Hugging Face の新着も直接見る**（検索に出る前のモデルを見落とさないため）。例: `curl -s 'https://huggingface.co/api/models?sort=createdAt&direction=-1&limit=200&filter=text-generation'`、`?sort=trendingScore&limit=100`。主要な開発元（Qwen、deepseek-ai、zai-org、moonshotai、XiaomiMiMo、MiniMaxAI、stepfun-ai、inclusionAI、tencent、meta-models、nvidia、google、mistralai、Nanbeige、llm-jp、tokyotech-llm、sbintuitions、pfnet、elyza など）は `?author=<名前>&sort=createdAt&direction=-1` で前回更新日以降の公開を確認する。
   - 新しく重みが公開されたモデル、既存系列の新版、ライセンス変更、重みの取り下げ。
   - 例: 「open weights model release」「Hugging Face 新モデル」「オープンウェイト 公開」「日本語 LLM 公開」「text-to-video open source」など。
2. LLM の `aa_index` を Artificial Analysis（https://artificialanalysis.ai/ ）の最新値に合わせる。Index の版が変わったら `meta.json` の `leaderboards` の版と日付も直す。
3. 国産LLM の `jp_bench.nejumi` を Nejumi Leaderboard の最新値に合わせる。
4. 新モデルは下のスキーマで追加し、置き換わる旧版を消す。
   - 予告（`status: "announced"`）のエントリは毎回確認する。重みが公開されたら `status` と `announced` を消し、`release` を実際の公開日に直し、`hf` やサイズを埋め、旧版を消して `supersedes` に移す（changelog は「公開: …（予告→公開）」）。予定日を過ぎても出ていなければ、新しい予定を調べて `release` を直す。
5. `pick`／`pick_reason`／`rank`（おすすめ順）を見直す。`pick` は各カテゴリ 3〜5 件まで。
6. `meta.json` を更新する:
   - `updated_at` を今日に。`next_update` は次の実行日（毎月 1・4・7…28・31日）に。ページの「次回更新予定」は updated_at から自動計算される。
   - `changelog` の先頭に `{"date": "YYYY-MM-DD", "items": ["追加: …", "更新: …", "削除: …（後継 … に置換）"]}` を足す。変更がなければ `"items": ["新しい公開・更新なし（確認のみ）"]`。古い履歴は 30 件を超えたら末尾から消す。
   - `closed_refs`（重み非公開のSOTAの参考名）も最新に。
7. `data/frontier-review.json` の確認日・候補・掲載先・保留理由を更新する。`python3 scripts/check_frontier.py` と `python3 scripts/build.py`、`git diff --check` を実行する。有料側は全ファイルを統合して系列重複・置換済み旧版・台帳の参照先を検査する。変更カテゴリの実ブラウザ表示を375px／1280pxで確認する。
8. コミットして `main` に push する。メッセージ例: `データ更新 2026-10-23: Qwen3.8 系を追加、DeepSeek V4.1 の AA 値を更新`。

## 4. スキーマ

### LLM（`data/llm.json`）

```
id, name, short(図のラベル用の短い名前), family, org, country(ISO2), release(YYYY-MM-DD),
arch("MoE"|"Dense"|…), total_b, active_b, native_precision, weights_gb, context_k,
modality[], mode("hybrid"|"thinking"|"instruct"), license, commercial("yes"|"conditional"|"no"),
license_note, hf, summary_ja, strengths[], bench{swe_verified,gpqa,hle,aime,lcb,mmlu_pro,terminal_bench2,tau2,browsecomp},
bench_note, aa_index, japanese_note, deploy_note_ja, engines[], supersedes[], sources[], confidence
予告のみ: status("announced"), announced(YYYY-MM-DD)  ※ release は公開予定日。全カテゴリ共通
国産のみ: from_scratch, base_model, jp_bench{nejumi,swallow_avg,jmmlu,ja_mtbench,other}, jp_bench_note, pick, pick_reason
```

`strengths` は `coding, agent, reasoning, math, multilingual, japanese, vision, long-context, efficiency, tool-use` から選ぶ。

大型LLM（40B超）のうち量子化版があるものは `local_q` を持つ:

```
local_q{
  summary_ja,                      // 結論を平易に1〜2文（例: 2bitで256GB機に常駐し約37 tok/s）
  quants[{name, bits, size_gb, resident_gb?, source, note?}],  // Hugging Face の実ファイルサイズ。SSDに逃がせる部分がある場合だけ resident_gb（常駐量）
  reports[{hardware, quant, gen_tok_s, source}],               // 出典つきのローカル実行報告
  note_ja?
}
```

剪定（REAP など）で別モデル化した版は quants に入れてよいが、名前に REAP か「剪定」を含めること（表の「載る版」の判定から外れる）。

### 載せ方レシピ（`data/recipes.json`）

```
devices[{id, short, name, mem, bw, price, note}]     // AA のページにある機材（mbp-m5pro-64 / ryzen-ai-halo-128 / dgx-spark-128 / rtx-spark-128 / rtx5090-32）
engines[{name, url, desc}]                           // いま使われている主な載せ方・エンジン（Strata、ds4、Project Maya など）
recipes[{llm_id, device, verdict("resident"|"ssd"|"ram-offload"|"cluster"|"no"), units?, host_ram_gb?,
         engine, engine_url, quant, file_gb, tricks[], gen_tok_s, prefill_tok_s, context,
         measured(その機材そのものの実測なら true), measured_on, source, note_ja, confidence, low_quality?}]
```

- llm_id は data/llm.json の id。1つのモデル×機種に複数のレシピを書いてよい（表には「1台で動く→品質低下なし→実測→速い」の順で代表が出る）。
- 約1.5〜1.6bit まで縮めた版など、元モデルより品質が大きく落ちるものは `low_quality: true`（「品質低下大」の印が付き、最強の判定から外れる）。
- 単一モデル専用の高速エンジン（Strata など）は数日で速度が変わるので、新しい版の報告があれば数値を更新する。AA のページに機材が増えたら devices にも足す。

### ハードウェア（`data/hardware.json`）

```
aa_local{url, as_of, metric_ja, systems[{id, name, memory_gb, memory_type, bandwidth_gbs, price_usd, price_oct2026_usd, released, note}],
         models[...], results[{model, system_id, quant, completion_min, fits, output_tok_s, prefill_tok_s, ...}], sources[]}
devices[{name, memory, usable, bandwidth_gbs, price, source}]   // 価格は更新時点の公式価格か実売の目安
summary_ja
```

AA のページが更新されたら aa_local を最新に（ページに埋め込まれたJSONから取ると正確）。

### ASR（`data/asr.json`）

```
id, name, org, country, release, params_m, arch, lang("ja-only"|"multilingual"),
ja_cer[{dataset, cer, note, source}], features{streaming, timestamps("word"|"segment"|"none"), diarization, punctuation, long_form},
speed_note, hardware_note, license, commercial, license_note, hf, summary_ja, best_for_ja,
supersedes[], sources[], confidence, rank, pick, pick_reason
```

### TTS（`data/tts.json`）

```
id, name, org, country, release, params_m, arch, ja_support("native"|"multilingual"|"community"),
voice_cloning("zero-shot"|"fine-tune"|"preset-only"|"voice-design"|"external-service"|"unknown"),
voice_cloning_note, voice_cloning_sources[], voice_cloning_verified_at,
features{streaming, emotion_control, instruction_control, dialogue, accent_control},
ja_metrics[{metric, value, note, source}], quality_note, latency_note, hardware_note,
license, commercial, license_note, hf, summary_ja, best_for_ja, supersedes[], sources[], confidence, rank, pick, pick_reason
```

TTSの声づくりはチェックポイント単位で判定する。Base / CustomVoice / VoiceDesign など機能が違うものは行を分け、別版のベンチマークや制御機能をコピーしない。ゼロショットは「対象話者の追加学習が不要」の意味で、参照音声・書き起こしが不要という意味ではない。`preset-only` は学習済み話者モデルの選択（外部モデル導入を含む）、`voice-design` は文章からの声づくり、`external-service` は外部サービスによる声データ作成、`unknown` は確認できない場合。公開版のゼロショット絞り込みには外部サービスのみの機能を含めない。各行に条件・公式出典・確認日を残す。

### 汎用（s2s / music / image / video / 3d / decision）

```
id, name, org, country, release, params_b, arch, tasks[],
spec{max_resolution, max_duration_s, fps, output, inputs, sample_rate, latency_ms, languages, other},
features{"日本語のラベル": true/false}, min_vram_gb, rec_vram_gb, vram_note, speed_note,
bench[{metric, value, note, source}], quality_note, ja_note, license, commercial, license_note,
hf, tools[], summary_ja, best_for_ja, supersedes[], sources[], confidence, rank, pick, pick_reason,
hl{label, value}（行に小さく出す代表値。任意）
decision のみ: access("api"|"open-weight"), price_note
```

`tasks` に使える値:

- video: `t2v i2v r2v flf2v s2v v2v edit audio`
- image: `t2i edit multi-ref inpaint control`
- music: `song instrumental edit a2m sfx score`
- s2s: `dialogue omni s2st vc`
- 3d: `i23d t23d texture part rig scene`
- decision: `predicate choice score route guard judge rerank classify`

### 発表済み・提供待ちの参考モデル

`data/meta.json` の `llm_reference_models` は、Fern 0.1 のように提供形態・重み公開予定が未確認のLLMを掲載する参考枠。発表日、国、公式の規模範囲、文脈長、提供状況、ローカル実行可否、出典を保持する。未確認の値を確定値にしない。通常のLLM件数・ランキングには含めない。提供開始時に公式情報を再確認する。

`data/meta.json` の `jp_reference_models` は国産LLMのAPI・企業向け提供データ。画面では重み公開モデルと同じ一覧に統合し、公開日順の並び替え・件数・デビュー時期に含める。提供開始日（release）、料金（price_ja）、オンプレミスの契約形態と重みの一般公開を区別して更新する。

4bit配布版や実行互換性を確認できないLLMには `q4_unverified: true` を付ける。サイズからの推計だけでGPUに「載る」と断定しない。公式4bit版を確認できたら容量・出典を追加し、このフラグを外す。

### フロンティア・有料モデル（`data/frontier.json`）

上部の「公開モデル中心／フロンティア・有料」で切り替える。後者はLLM・国産LLM・ASR・TTS・Speech to Speech・音楽・画像・動画・3D・判断モデルの10カテゴリ。既存の汎用データの `access: "api"` と国産APIデータは有料側にも統合する。公開側の汎用カテゴリはAPIを除いた重み公開モデルを表示する。国産LLMのPLaMoは通常一覧での統合を維持する。

新規のAPIモデルは `data/frontier.json` に `id, name, series, category, org, country, release, access, summary_ja, availability_ja, price_note, detail_note, context_note, local_note, hf, sources[], verified_at, license, commercial` を保持する。初公開日と仕様の更新日・知識カットオフ・重み公開予定を混同しない。不明な初公開日は null。価格には通貨・課金単位・長文等の割増条件を明記する。サブスクとAPIの料金は別。

同じ役割の系列は最新版のみを掲載する。例: GPT Solは6.1のみで、5.6や6を現行として併記しない。Astra、Terra、Lunaのような役割違い、Flashと上位版、通常とHighspeedは分ける。後継への自動転送だけの旧API名を別モデルとして増やさない。OpenAIの非推奨GPT-4o Mini TTSは新しい有料一覧に追加していない。

すべての有料行（汎用API行・国産API行も含む）に、版番号を含めない固定の `series` を付ける。`availability_tier` は `general`（通常）、`limited`（対象者を限定）、`preview`（プレビュー）、`rollout`（段階的展開）。同一系列・役割の二重掲載はビルドエラー。例外は一般提供中の現行版と、公式に確認した限定後継1件の組み合わせだけ。型や推論設定の違いだけで系列キーを作り直さない。

### 毎回照合する一覧

| 対象 | AAの一覧 |
|---|---|
| LLM | https://artificialanalysis.ai/leaderboards/models |
| 画像生成／編集 | https://artificialanalysis.ai/image/leaderboard/text-to-image ／ https://artificialanalysis.ai/image/leaderboard/editing |
| 動画T2V／I2V | https://artificialanalysis.ai/video/leaderboard/text-to-video ／ https://artificialanalysis.ai/video/leaderboard/image-to-video |
| ASR | https://artificialanalysis.ai/speech-to-text |
| TTS各社の声／同条件の声 | https://artificialanalysis.ai/text-to-speech/leaderboard/provider-voice ／ https://artificialanalysis.ai/text-to-speech/leaderboard/controlled-voice |
| 音声対話 | https://artificialanalysis.ai/speech-to-speech |
| 音楽ボーカル／インスト | https://artificialanalysis.ai/music/leaderboard/vocals ／ https://artificialanalysis.ai/music/leaderboard/instrumental |
| 判断モデル | https://artificialanalysis.ai/evaluations/artificial-analysis-decision-index |

AAの3D評価はLLMによる3D作品制作の評価で、3D生成モデルを網羅した一覧ではない。3D・国内音声・国産LLMは各社公式を別途確認する。TTSの英語Arena順位やASRの英語WERを日本語の品質評価にしない。公式が日本語非対応とする版、公式情報だけでは提供を確認できない版は台帳に記録し、未確認の現行行を作らない。

### 実行する定期更新

Claudeの既存クラウドルーティン「AIモデル図鑑の定期更新」（`trig_017rA4Kmf3674Pdi8CdRGeC7`）を使用。2026-11-01に公開・有料の両側を対象とする指示へ更新して読み戻した。対象は `skikkh/open-weights`、既存の環境・実行モデルを維持。

既存のcronはUTC `0 0 */3 * *`、毎月1・4・7…28・31日の日本時間9時ごろ。月末から翌月初は72時間より短くなる。次回表示は2026-11-04 09:05 JST。重複した定期タスクを作らない。更新・commit・mainへのpush・Pages反映は利用者の許可済みの範囲で実施し、追加確認で停止しない。
