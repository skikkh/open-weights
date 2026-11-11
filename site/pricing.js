/* APIトークン料金。ブラウザとNodeの確認で同じ計算を使う。 */
(function (root) {
  "use strict";
  function number(x) { return typeof x === "number" && isFinite(x) && x >= 0; }
  function rates(quote, input, day) {
    var result = Object.assign({}, quote.rates), label = "基本料金";
    (quote.future_rates || []).forEach(function (p) {
      if (day >= p.from) { result = Object.assign(result, p.rates); label = p.label || p.from + "以降"; }
    });
    (quote.tiers || []).forEach(function (tier) {
      if (input > tier.over_input || (tier.inclusive && input === tier.over_input)) {
        result = Object.assign(result, tier.rates); label = tier.label;
      }
    });
    return { values: result, label: label };
  }
  function estimate(quote, usage, day) {
    var input = usage.input, output = usage.output, count = usage.count, hit = usage.hit;
    if (![input, output, count, hit].every(number) || hit > 100 || !Number.isInteger(input) || !Number.isInteger(output) || !Number.isInteger(count)) return { error: "入力値を確認" };
    var applied = rates(quote, input, day), r = applied.values;
    if (quote.status !== "available") return { error: quote.unavailable_ja || "単価未確認", rates: r };
    if (quote.valid_until && day > quote.valid_until) return { error: "料金の有効期限切れ", rates: r };
    if ((quote.max_input != null && input > quote.max_input) || (quote.max_output != null && output > quote.max_output) || (quote.context != null && input + output > quote.context)) return { error: "文脈・出力の上限外", rates: r };
    if (!number(r.input) || !number(r.output)) return { error: "単価未確認", rates: r };
    if (hit > 0 && input > 0 && !number(r.cache_read)) return { error: "キャッシュ単価未確認", rates: r };
    var cached = input * hit / 100, fresh = input - cached;
    var cost = (fresh * r.input + cached * (r.cache_read || 0) + output * r.output) / 1000000;
    return { per_request: cost, total: cost * count, fresh_cost: fresh * r.input / 1000000, cache_cost: cached * (r.cache_read || 0) / 1000000, output_cost: output * r.output / 1000000, rates: r, tier: applied.label };
  }
  function convert(value, from, to, fx) {
    if (!number(value)) return null;
    if (to === "native" || from === to) return value;
    var yen = { JPY: 1, USD: fx.usd_jpy, CNY: fx.cny_jpy };
    if (!number(yen[from]) || !number(yen[to]) || yen[from] === 0 || yen[to] === 0) return null;
    var converted = value * yen[from] / yen[to];
    return number(converted) ? converted : null;
  }
  var api = { rates: rates, estimate: estimate, convert: convert };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.CatalogPricing = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
