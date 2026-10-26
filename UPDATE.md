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
| `data/s2s.json` `music.json` `image.json` `video.json` `3d.json` `decision.json` | 汎用カテゴリ（同じスキーマ） |
| `data/meta.json` | 更新日、次回予定、収録ルール、更新履歴、出典、重み非公開モデルの参考メモ |
| `data/hardware.json` | Artificial Analysis「Laptops & Workstations」の実測（`aa_local`）、ローカル機の一覧と価格（`devices`）、量子化ローカルの総括（`summary_ja`） |
| `site/template.html` | ページの雛形（`/*__DATA__*/` にデータが入る） |
| `scripts/build.py` | 検証して `docs/index.html` を生成 |

## 2. 収録ルール（全カテゴリ共通）

1. 重みがダウンロードできるもの（オープンウェイト）だけ。例外は Decision Model ページで、API 提供のもの（OpenAI Decisions API、TypeSafe Jev など）も `access: "api"` で載せる。
2. **各系列の最新世代だけ**。後継が出たら旧版のエントリを消し、新エントリの `supersedes` に旧版名を足す。
3. 同じ世代でも Flash／Pro、サイズ違い、T2V版／I2V版など用途が分かれるものは別エントリ。
4. LLM は総パラメータ 100B 以上の大型〜超巨大が中心。主要系列の注目中型（単体GPUに載るもの）は少数だけ。
5. ASR・TTS・Speech to Speech は日本語で使えるものを中心にする。
6. **予告も載せる**: 公式に発表され、重み（API提供カテゴリはサービス）の公開日や公開予定が示されているが、まだ出ていないモデルは「予告」として載せる。`status: "announced"`、`announced`（発表日）を付け、`release` には公開予定日（分からなければ予定月）を入れる。予告のエントリには `supersedes` と `pick` を付けず、旧版は重みが出るまで消さない。根拠は公式発表（ブログ・公式X・ドキュメント）で取り、報道だけなら confidence を medium か low にする。半年以上動きのない予告は消す。
7. 件数の目安: LLM 海外 25〜35／国産 8〜14、ASR 10〜16、TTS 12〜18、その他各 10〜18。

## 3. 更新作業

1. `data/meta.json` の `updated_at`（前回更新日）以降のニュースを、カテゴリごとに検索する。
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
7. `python3 scripts/build.py` を実行し、`OK:` が出ることを確認する。検証エラーが出たらデータを直す。
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
voice_cloning("zero-shot"|"fine-tune"|"preset-only"),
features{streaming, emotion_control, instruction_control, dialogue, accent_control},
ja_metrics[{metric, value, note, source}], quality_note, latency_note, hardware_note,
license, commercial, license_note, hf, summary_ja, best_for_ja, supersedes[], sources[], confidence, rank, pick, pick_reason
```

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
