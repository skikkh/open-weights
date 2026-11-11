#!/usr/bin/env node
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const root = path.resolve(__dirname, "..");
const P = require(path.join(root, "site/pricing.js"));
const data = JSON.parse(fs.readFileSync(path.join(root, "data/pricing.json"), "utf8"));
const quote = (model, provider, plan = "standard") => data.quotes.find(q => q.model_id === model && q.provider_id === provider && q.plan === plan);
const usage = (input, output = 1000, hit = 0, count = 1) => ({ input, output, hit, count });
const estimate = (q, u, day = "2026-11-12") => P.estimate(q, u, day);
const near = (actual, expected) => assert.ok(Math.abs(actual - expected) < 1e-10, `${actual} != ${expected}`);
let checks = 0;
function test(name, fn) { fn(); checks++; }
test("入力・出力・月間件数", () => near(estimate(quote("gpt-6.1-sol", "openai"), usage(10000, 2000, 0, 1000)).total, 40));
test("27.2万を超えた全量に長文単価", () => {
 const q = quote("gpt-6.1-sol", "openai");
 assert.equal(estimate(q, usage(272000)).rates.input, 2);
 assert.equal(estimate(q, usage(272001)).rates.input, 4);
 near(estimate(q, usage(272001, 1000, 100)).per_request, .0694002);
});
test("Haikuの入力閾値はキャッシュ分も含む", () => {
 const q = quote("claude-haiku-5-5", "anthropic");
 assert.equal(estimate(q, usage(100000)).rates.output, .5);
 assert.equal(estimate(q, usage(100001, 1000, 100)).rates.output, 2.5);
});
test("Grokの公式表は20万以上", () => {
 const q = quote("grok-4-7", "xai");
 assert.equal(estimate(q, usage(199999)).rates.input, 2);
 assert.equal(estimate(q, usage(200000)).rates.input, 4);
});
test("Emberは20万超のみ割増", () => {
 const q = quote("muse-ember", "meta");
 assert.equal(estimate(q, usage(200000)).rates.input, .1);
 assert.equal(estimate(q, usage(200001)).rates.input, .3);
});
test("未確認キャッシュ単価を無料にしない", () => {
 const q = quote("plamo-3-1-prime", "pfn");
 near(estimate(q, usage(1000)).per_request, .31);
 assert.equal(estimate(q, usage(1000, 1000, 50)).error, "キャッシュ単価未確認");
});
test("無料と0リクエストを正しく扱う", () => {
 const q = { status: "available", rates: { input: 0, output: 0, cache_read: 0 } };
 assert.equal(estimate(q, usage(1000, 1000, 100)).total, 0);
 assert.equal(estimate(quote("gpt-6.1-sol", "openai"), usage(1000, 1000, 0, 0)).total, 0);
});
test("導入価格の終了日", () => {
 const q = quote("gemini-4-carbon", "google");
 assert.equal(estimate(q, usage(1000), "2026-11-30").rates.input, 2);
 assert.equal(estimate(q, usage(1000), "2026-12-01").rates.input, 4);
 assert.equal(estimate(quote("tencent-hy4-api", "tencent"), usage(1000), "2027-01-01").rates.input, 6);
});
test("長文・出力上限を越える見積を出さない", () => {
 const q = { status: "available", rates: { input: 1, output: 1 }, context: 100, max_output: 20 };
 assert.equal(estimate(q, usage(90, 11)).error, "文脈・出力の上限外");
 assert.equal(estimate(q, usage(1, 21)).error, "文脈・出力の上限外");
});
test("負数・NaN・小数・100%超を拒否", () => {
 const q = quote("gpt-6.1-sol", "openai");
 for (const u of [usage(-1), usage(NaN), usage(.5), usage(1, 1, 101), usage(1, 1, 0, 1.5)]) assert.ok(estimate(q, u).error);
});
test("限定提供・会費を0円の従量料金にしない", () => {
 assert.ok(estimate(quote("muse-wonder-full", "meta"), usage(1000)).error);
 assert.ok(estimate(quote("gpt-6-cyber", "openai"), usage(1000)).error);
});
test("換算レートなし・ゼロで異通貨を比較しない", () => {
 assert.equal(P.convert(60, "JPY", "USD", {}), null);
 assert.equal(P.convert(60, "JPY", "USD", { usd_jpy: 0 }), null);
 assert.equal(P.convert(2, "USD", "JPY", { usd_jpy: 1e308 }), null);
 near(P.convert(60, "JPY", "USD", { usd_jpy: 150 }), .4);
 near(P.convert(2, "USD", "JPY", { usd_jpy: 150 }), 300);
});
test("OpenRouterの1トークン単価を100万に変換", () => {
 const q = data.quotes.find(q => q.model_id === "kimi-k3-1-pro-api" && q.provider_id === "or-relace");
 near(q.rates.input, .2375); near(q.rates.output, 8.4085);
});
test("同じモデルを複数の提供元で比較", () => {
 const q = data.quotes.filter(q => q.model_id === "kimi-k3-1-pro-api");
 assert.ok(new Set(q.map(q => q.provider_id)).size >= 4);
 assert.ok(q.every(q => q.sources.length && q.verified_at));
});
console.log(`OK: API料金 ${data.models.length}モデル・${data.quotes.length}経路、境界・通貨・割引等${checks}項目`);
