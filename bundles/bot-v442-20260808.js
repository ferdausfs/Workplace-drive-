// src/index.js
var PAIR_PAGES = [
  ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD"],
  ["USD/CAD", "AUD/CAD", "GBP/JPY", "EUR/GBP", "NZD/USD"],
  ["USD/CHF", "EUR/JPY", "EUR/AUD", "AUD/JPY"],
  ["BTC/USD", "ETH/USD", "SOL/USD", "BNB/USD"],
  ["XRP/USD", "ADA/USD", "DOGE/USD", "AVAX/USD"]
];
var MAX_WL = 6;
var MAX_HIST = 100;
var MILESTONE = 50;
var MAX_ERRORS = 3;
var NEWS_WINDOW = 15;
var CRYPTO = ["BTC", "ETH", "BNB", "XRP", "SOL", "ADA", "DOGE", "AVAX", "DOT", "LINK"];
var QUOTEX_URL = "https://quotex.com/trade";
var CAL_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json";
var index_default = {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    const secret = () => url.searchParams.get("secret") === env.SETUP_SECRET;
    if (req.method === "POST" && url.pathname === "/webhook") {
      const upd = await req.json().catch(() => null);
      if (upd) ctx.waitUntil(dispatch(upd, env));
      return new Response("OK");
    }
    if (url.pathname === "/setup" && secret()) {
      const hook = `https://${url.hostname}/webhook`;
      const r = await fetch(
        `${TG(env)}/setWebhook`,
        post({ url: hook, allowed_updates: ["message", "callback_query"], drop_pending_updates: true })
      );
      return new Response(JSON.stringify(await r.json(), null, 2), json());
    }
    if (url.pathname === "/runcron" && secret()) {
      const logs = [], force = url.searchParams.get("force") === "true";
      await cron(env, logs, force);
      return new Response(logs.join("\n"), { headers: { "Content-Type": "text/plain" } });
    }
    if (url.pathname === "/debugkv" && secret()) {
      const au = await kget("auto_users", env) || [];
      const users = {};
      for (const id of au) users[id] = await kget(`u:${id}`, env);
      return new Response(JSON.stringify({ auto_users: au, users }, null, 2), json());
    }
    if (url.pathname === "/addauto" && secret()) {
      const id = url.searchParams.get("chat");
      if (!id) return new Response("?chat= required", { status: 400 });
      await addAutoUser(id, env);
      const u = await getUser(id, env);
      u.autoEnabled = true;
      await saveUser(id, u, env);
      return new Response("OK", json());
    }
    if (url.pathname === "/export" && secret()) {
      const id = url.searchParams.get("chat");
      if (!id) return new Response("?chat= required", { status: 400 });
      const h = await getHist(id, env);
      if (!h.length) return new Response("No data", { status: 404 });
      const hdr = "No,Pair,Dir,Grade,Conf,Entry,Exit,Pips,Result,Expiry,Time,ResolvedAt";
      const rows = h.map((x) => [
        x.no || "",
        x.pair || "",
        x.direction || "",
        x.grade || "",
        x.confidence || "",
        x.entryPrice || "",
        x.exitPrice || "",
        x.pips || "",
        x.result || "PENDING",
        x.expiryMinutes || "",
        x.timestamp || "",
        x.resolvedAt || ""
      ].join(","));
      const fname = `ftt-${id}-${(/* @__PURE__ */ new Date()).toISOString().slice(0, 10)}.csv`;
      return new Response([hdr, ...rows].join("\n"), {
        headers: {
          "Content-Type": "text/csv",
          "Content-Disposition": `attachment; filename="${fname}"`
        }
      });
    }
    return new Response("FTT Signal Bot v4.4.2");
  },
  async scheduled(e, env, ctx) {
    ctx.waitUntil(cronLite(env));
  }
};
var TG = (env) => `https://api.telegram.org/bot${env.BOT_TOKEN}`;
var post = (body) => ({ method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
var json = () => ({ headers: { "Content-Type": "application/json" } });
async function tg(method, body, env) {
  if (!env?.BOT_TOKEN) return null;
  try {
    const r = await fetch(`${TG(env)}/${method}`, post(body));
    if (!r.ok) {
      const t = await r.text();
      if (!t.includes("not modified") && !t.includes("too old") && !t.includes("message is not modified"))
        console.error(`tg/${method}:`, t.slice(0, 200));
    }
    return r;
  } catch (e) {
    console.error(`tg/${method}:`, e.message);
    return null;
  }
}
var esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
var SEP = "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501";
var sendMsg = (cid, text, env, extra = {}) => tg("sendMessage", { chat_id: cid, text: String(text || ""), disable_web_page_preview: true, parse_mode: "HTML", ...extra }, env);
var editMsg = (cid, mid, text, env, extra = {}) => tg("editMessageText", { chat_id: cid, message_id: mid, text: String(text || ""), disable_web_page_preview: true, parse_mode: "HTML", ...extra }, env);
var answerCb = (id, env, text = "") => tg("answerCallbackQuery", { callback_query_id: id, text }, env);
var deleteMsg = (cid, mid, env) => tg("deleteMessage", { chat_id: cid, message_id: mid }, env).catch(() => null);
var reply = (cid, mid, text, env, kboard) => {
  const extra = kboard ? { reply_markup: kboard } : {};
  return mid ? editMsg(cid, mid, text, env, extra) : sendMsg(cid, text, env, extra);
};
var kget = async (k, env) => {
  try {
    return await env.BOT_KV.get(k, "json");
  } catch {
    return null;
  }
};
var kput = async (k, v, env, opts = {}) => {
  try {
    await env.BOT_KV.put(k, JSON.stringify(v), opts);
  } catch (e) {
    console.error("kput", k, e.message);
  }
};
var kdel = async (k, env) => {
  try {
    await env.BOT_KV.delete(k);
  } catch {
  }
};
async function getRegimeStats(cid, env) {
  const d = await kget(`rs:${cid}`, env);
  return d || { TRENDING: { w: 0, l: 0 }, RANGING: { w: 0, l: 0 }, BREAKOUT: { w: 0, l: 0 }, VOLATILE: { w: 0, l: 0 } };
}
async function updateRegimeStats(cid, regime, result, env) {
  if (!regime || result !== "WIN" && result !== "LOSS") return;
  const s = await getRegimeStats(cid, env);
  if (!s[regime]) s[regime] = { w: 0, l: 0 };
  result === "WIN" ? s[regime].w++ : s[regime].l++;
  await kput(`rs:${cid}`, s, env);
}
async function getSessionStats(cid, env) {
  const d = await kget(`ss:${cid}`, env);
  return d || {};
}
async function updateSessionStats(cid, sessionKey, result, env) {
  if (!sessionKey || result !== "WIN" && result !== "LOSS") return;
  const s = await getSessionStats(cid, env);
  if (!s[sessionKey]) s[sessionKey] = { w: 0, l: 0 };
  result === "WIN" ? s[sessionKey].w++ : s[sessionKey].l++;
  await kput(`ss:${cid}`, s, env);
}
async function getRisk(cid, env) {
  return await kget(`risk:${cid}`, env) || { streak: 0, type: null };
}
async function updateRisk(cid, result, env) {
  const r = await getRisk(cid, env);
  if (result === "LOSS") {
    r.streak = r.type === "LOSS" ? r.streak + 1 : 1;
    r.type = "LOSS";
  } else if (result === "WIN") {
    r.streak = r.type === "WIN" ? r.streak + 1 : 1;
    r.type = "WIN";
  } else {
    r.streak = 0;
    r.type = null;
  }
  await kput(`risk:${cid}`, r, env, { expirationTtl: 86400 });
  return r;
}
async function getConfTrend(cid, env) {
  return await kget(`ct:${cid}`, env) || [];
}
async function updateConfTrend(cid, confStr, env) {
  const val = parseInt((confStr || "0%").replace("%", ""), 10);
  if (isNaN(val)) return { alert: false };
  const arr = await getConfTrend(cid, env);
  arr.unshift(val);
  const trimmed = arr.slice(0, 5);
  await kput(`ct:${cid}`, trimmed, env, { expirationTtl: 86400 });
  if (trimmed.length >= 3 && trimmed[0] < trimmed[1] && trimmed[1] < trimmed[2])
    return { alert: true, vals: trimmed.slice(0, 3) };
  return { alert: false };
}
async function getEconCalendar(env) {
  try {
    const cached = await kget("econ_cal", env);
    if (cached && cached.ts > Date.now() - 36e5) return cached.events || [];
    const r = await fetch(CAL_URL, { signal: AbortSignal.timeout(6e3) });
    if (!r.ok) return [];
    const events = await r.json();
    await kput("econ_cal", { ts: Date.now(), events }, env, { expirationTtl: 3600 });
    return events;
  } catch {
    return [];
  }
}
async function hasHighImpactNews(env, windowMin = NEWS_WINDOW) {
  try {
    const events = await getEconCalendar(env);
    const now = Date.now();
    const win = windowMin * 60 * 1e3;
    for (const ev of events) {
      if (ev.impact !== "High") continue;
      const evTime = new Date(ev.date).getTime();
      if (isNaN(evTime)) continue;
      const diff = evTime - now;
      if (Math.abs(diff) <= win) {
        const minsAway = Math.round(diff / 6e4);
        return { title: ev.title, currency: ev.country || ev.currency || "?", minsAway };
      }
    }
    return null;
  } catch {
    return null;
  }
}
function getCurrencyExposure(pair, direction) {
  if (!pair || !direction) return {};
  try {
    const p = String(pair).replace("/", "").toUpperCase();
    if (!p || p.length < 6) return {};
    if (CRYPTO.some((c) => p.startsWith(c))) {
      return { _CRYPTO: direction === "BUY" ? "long" : "short" };
    }
    const base = p.slice(0, 3);
    const quote = p.slice(3, 6);
    return direction === "BUY" ? { [base]: "long", [quote]: "short" } : { [base]: "short", [quote]: "long" };
  } catch {
    return {};
  }
}
async function checkCorrelated(cid, newPair, newDir, env) {
  try {
    const h = await getHist(cid, env);
    const pending = h.filter((x) => !x.result && x.direction && x.pair && norm(x.pair) !== norm(newPair));
    const newExp = getCurrencyExposure(newPair, newDir);
    const warnings = [];
    for (const t of pending) {
      const exp = getCurrencyExposure(t.pair, t.direction);
      for (const [currency, side] of Object.entries(newExp)) {
        if (exp[currency] === side) {
          warnings.push(`${disp(t.pair)} ${t.direction} (${currency === "_CRYPTO" ? "crypto" : currency})`);
          break;
        }
      }
    }
    return warnings;
  } catch {
    return [];
  }
}
async function getPendingReminders(env) {
  return await kget("remind_ids", env) || [];
}
async function addReminder(rem, env) {
  await kput(`rem:${rem.tradeId}`, rem, env, { expirationTtl: 3600 });
  const ids = await getPendingReminders(env);
  if (!ids.includes(rem.tradeId)) await kput("remind_ids", [...ids, rem.tradeId], env);
}
async function delReminder(tid, env) {
  await kdel(`rem:${tid}`, env);
  const ids = await getPendingReminders(env);
  await kput("remind_ids", ids.filter((x) => x !== tid), env);
}
var DEF_USER = () => ({
  pair: "EURUSD",
  watchlist: [],
  interval: 5,
  autoEnabled: false,
  noTradeStreak: 0,
  gradeFilter: "ALL",
  minConfidence: 0,
  dailySummary: false,
  summaryHour: 20,
  // [v4.1] new fields
  aiOnlyMode: false,
  // [F02] only send when AI agrees
  blockNews: true,
  // [F03] skip auto signals during news window
  channelId: null,
  // [F10] channel to mirror signals to
  fxMode: "ftt"
  // [FX] 'ftt' | 'fx' | 'both' — signal output mode
});
async function getUser(cid, env) {
  const d = await kget(`u:${cid}`, env);
  return d ? { ...DEF_USER(), ...d } : DEF_USER();
}
var saveUser = (cid, u, env) => kput(`u:${cid}`, u, env);
async function getAutoUsers(env) {
  return await kget("auto_users", env) || [];
}
async function addAutoUser(cid, env) {
  const list = await getAutoUsers(env);
  if (!list.includes(String(cid))) await kput("auto_users", [...list, String(cid)], env);
}
async function removeAutoUser(cid, env) {
  const list = await getAutoUsers(env);
  await kput("auto_users", list.filter((x) => x !== String(cid)), env);
}
async function getSummaryUsers(env) {
  return await kget("summary_users", env) || [];
}
async function addSummaryUser(cid, env) {
  const list = await getSummaryUsers(env);
  if (!list.includes(String(cid))) await kput("summary_users", [...list, String(cid)], env);
}
async function removeSummaryUser(cid, env) {
  const list = await getSummaryUsers(env);
  await kput("summary_users", list.filter((x) => x !== String(cid)), env);
}
var getHist = async (cid, env) => await kget(`h:${cid}`, env) || [];
var getCounter = async (cid, env) => await kget(`cnt:${cid}`, env) || 0;
async function addHist(cid, entry, env) {
  const h = await getHist(cid, env);
  const cnt = await getCounter(cid, env) + 1;
  await kput(`cnt:${cid}`, cnt, env);
  entry.no = cnt;
  h.unshift(entry);
  const cutoff = Date.now() - 30 * 24 * 60 * 60 * 1e3;
  await kput(`h:${cid}`, h.slice(0, MAX_HIST).filter((x) => new Date(x.timestamp).getTime() > cutoff), env);
  return cnt;
}
async function setResult(cid, tid, result, exitPrice, pips, env) {
  const h = await getHist(cid, env);
  const i = h.findIndex((x) => x.id === tid);
  if (i !== -1) {
    h[i] = { ...h[i], result, exitPrice, pips, resolvedAt: (/* @__PURE__ */ new Date()).toISOString() };
    await kput(`h:${cid}`, h, env);
    if (result === "WIN" || result === "LOSS") {
      const trade = h[i];
      if (trade.regime) await updateRegimeStats(cid, trade.regime, result, env);
      if (trade.sessionKey) await updateSessionStats(cid, trade.sessionKey, result, env);
    }
  }
}
var getPendingIds = async (env) => await kget("pending_ids", env) || [];
var savePendingIds = (ids, env) => kput("pending_ids", ids, env);
async function addPending(trade, env) {
  await kput(`pt:${trade.tradeId}`, trade, env, { expirationTtl: 7200 });
  const ids = await getPendingIds(env);
  if (!ids.includes(trade.tradeId)) await kput("pending_ids", [...ids, trade.tradeId], env);
}
var getLock = (cid, pair, env) => kget(`lock:${cid}:${pair}`, env);
var clearLock = (cid, pair, env) => kdel(`lock:${cid}:${pair}`, env);
async function setLock(cid, pair, dir, expiryAt, env) {
  const ttl = Math.max(60, Math.ceil((expiryAt - Date.now()) / 1e3) + 120);
  await kput(`lock:${cid}:${pair}`, { direction: dir, expiryAt }, env, { expirationTtl: ttl });
}
async function logAndSchedule(cid, pair, sig, env) {
  const dir = sig.finalSignal;
  const isFx = sig.mode === "fx";
  const expMins = isFx ? 60 : sig.bestTimeframe?.expiry?.totalMinutes || 5;
  const expAt = Date.now() + expMins * 60 * 1e3;
  const entry = sig.recommendations?.["1min"]?.entry?.price || sig.recommendations?.["5min"]?.entry?.price || null;
  const sl = isFx ? sig.fxLevels?.sl ?? null : null;
  const tp = isFx ? sig.fxLevels?.tp ?? null : null;
  const grade = sig.grade ? `${sig.grade.grade} ${sig.grade.label}` : "";
  const tid = uid();
  const regime = sig.marketRegime || "UNKNOWN";
  const session = sig.session || {};
  const sessionKey = session.overlap && session.overlap !== "NONE" ? session.overlap : session.sessions && session.sessions[0] || "UNKNOWN";
  const no = await addHist(cid, {
    id: tid,
    pair,
    direction: dir,
    confidence: sig.confidence || "0%",
    grade,
    entryPrice: entry,
    expiryMinutes: expMins,
    expiryAt: expAt,
    sl,
    tp,
    fillStatus: sig.fillStatus || "INSTANT",
    timestamp: (/* @__PURE__ */ new Date()).toISOString(),
    result: null,
    regime,
    sessionKey
  }, env);
  await addPending({ chatId: String(cid), tradeId: tid, pair, direction: dir, entryPrice: entry, expiryAt: expAt, signalNo: no, grade, regime, sessionKey, sl, tp, fillStatus: sig.fillStatus || "INSTANT" }, env);
  if (!isFx) {
    const remAt = expAt - 3e4;
    if (remAt > Date.now())
      await addReminder({ tradeId: tid, chatId: String(cid), pair, direction: dir, signalNo: no, remAt }, env);
  }
  await setLock(cid, pair, dir, expAt, env);
  return no;
}
var passGrade = (sig, f) => {
  if (!f || f === "ALL") return true;
  const g = sig.grade?.grade || "";
  if (!g) return false;
  return f === "A" ? ["A+", "A"].includes(g) : f === "AB" ? ["A+", "A", "B"].includes(g) : true;
};
var passConf = (sig, min) => {
  if (!min) return true;
  return parseInt((sig.confidence || "0%").replace("%", ""), 10) >= min;
};
var passAI = (sig, aiOnly) => {
  if (!aiOnly) return true;
  const v = sig?.aiValidation;
  if (!v) return false;
  const status = v.status || v.combined && v.combined.status;
  const agreed = v.agrees !== void 0 ? v.agrees : v.combinedAgreed;
  return status === "OK" && agreed === true;
};
function nextCandleIn(intervalMin) {
  const ms = intervalMin * 60 * 1e3;
  const next = (Math.floor(Date.now() / ms) + 1) * ms;
  const diff = next - Date.now();
  return `${Math.floor(diff / 6e4)}m ${Math.floor(diff % 6e4 / 1e3)}s`;
}
function msToHuman(ms) {
  if (ms <= 0) return "expired";
  const m = Math.floor(ms / 6e4);
  const s = Math.floor(ms % 6e4 / 1e3);
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}
var kb = (rows) => ({ inline_keyboard: rows });
var btn = (text, cb) => ({ text, callback_data: cb });
var signalKb = (no = null) => {
  const rows = [[{ text: "\u{1F4C8} Trade on Quotex", url: QUOTEX_URL }]];
  if (no) rows.push([btn(`\u2705 WIN #${no}`, `res:win:${no}`), btn(`\u274C LOSS #${no}`, `res:loss:${no}`)]);
  rows.push([btn("\u{1F501} New Signal", "cmd:signal"), btn("\u{1F4C8} History", "cmd:history:0"), btn("\u{1F519} Menu", "cmd:main")]);
  return kb(rows);
};
var afterKb = () => kb([
  [btn("\u{1F501} New Signal", "cmd:signal"), btn("\u{1F4C8} History", "cmd:history:0"), btn("\u{1F519} Menu", "cmd:main")]
]);
var mainKb = (u) => kb([
  [btn("\u{1F4CA} Signal Now", "cmd:signal"), btn("\u{1F441} Watchlist", "cmd:watchlist")],
  [btn("\u{1F680} Premium", "cmd:premium"), btn("\u26A1 Quick actions", "cmd:quick")],
  [btn("\u{1F4C8} History", "cmd:history:0"), btn("\u2699\uFE0F Settings", "cmd:settings")]
]);
var quickKb = (u) => kb([
  [btn("\u{1F4CA} Signal Now", "cmd:signal"), btn(u.autoEnabled ? "\u{1F515} Stop Auto" : "\u{1F504} Start Auto", "cmd:toggle_auto")],
  [btn("\u{1F50D} Scan All", "cmd:scanall"), btn("\u{1F4CB} Status", "cmd:status")],
  [btn("\u{1F4C5} Today", "cmd:today"), btn("\u{1F4CA} Weekly", "cmd:weekly"), btn("\u{1F525} Best", "cmd:best")],
  [btn("\u{1F4C9} Risk", "cmd:risk"), btn("\u{1F550} Heatmap", "cmd:heatmap"), btn("\u{1F4D2} Journal", "cmd:journal")],
  [btn("\u{1F3C6} Stats", "cmd:stats"), btn("\u{1F4CB} Summary", "cmd:summary")],
  [btn("\u{1F519} Back", "cmd:main")]
]);
var settingsKb = (u) => {
  const modeLbl = u.fxMode === "fx" ? "FX \u2705" : u.fxMode === "both" ? "BOTH \u{1F504}" : "FTT";
  return kb([
    // ── Signal ──────────────────────────────────────────────────────────────
    [btn(`\u{1F4B9} Mode: ${modeLbl}`, "cmd:fxmode")],
    [btn(`\u{1F3AF} Grade: ${u.gradeFilter || "ALL"}`, "cmd:gradefilter"), btn(`\u{1F4CA} Conf: ${u.minConfidence || 0}%+`, "cmd:conffilter")],
    [btn(`\u23F1 Interval: ${u.interval}min`, "cmd:intervals"), btn(`\u{1F4B1} Pair: ${disp(u.pair)}`, "pairpage:0")],
    // ── Auto ────────────────────────────────────────────────────────────────
    [btn(`\u{1F916} AI Only: ${u.aiOnlyMode ? "ON \u2705" : "OFF"}`, "cmd:aionly"), btn(`\u{1F4F0} News Block: ${u.blockNews !== false ? "ON \u2705" : "OFF"}`, "cmd:blocknews")],
    [btn("\u{1F501} Replay", "cmd:replayhelp")],
    [btn(`\u{1F4C5} Summary: ${u.dailySummary ? "ON" : "OFF"}`, "cmd:togglesummary"), btn(`\u{1F550} ${u.summaryHour ?? 20}:00 UTC`, "cmd:summarytime")],
    // ── Data ────────────────────────────────────────────────────────────────
    [btn(`\u{1F4E1} Channel: ${u.channelId ? "\u2705 Set" : "None"}`, "cmd:channelinfo"), btn("\u2B07 Export", "cmd:exportinfo")],
    [btn("\u{1F519} Back", "cmd:main")]
  ]);
};
var premiumKb = () => kb([
  [btn("\u{1F4E3} Channel Info", "cmd:channelinfo")],
  [btn("\u{1F519} Back", "cmd:main")]
]);
var pairsKb = (page, backTo = "cmd:settings") => {
  page = Math.max(0, Math.min(page, PAIR_PAGES.length - 1));
  const rows = chunk(PAIR_PAGES[page], 2).map((row) => row.map((p) => btn(p, `pair:${p}`)));
  const nav = [];
  if (page > 0) nav.push(btn("\u25C0 Prev", `pairpage:${page - 1}`));
  if (page < PAIR_PAGES.length - 1) nav.push(btn("Next \u25B6", `pairpage:${page + 1}`));
  if (nav.length) rows.push(nav);
  rows.push([btn("\u{1F519} Back", backTo)]);
  return kb(rows);
};
var wlKb = (wl) => {
  const rows = wl.map((p) => [btn(`\u{1F4CA} ${disp(p)}`, `qs:${p}`), btn("\u274C", `wl:rm:${p}`)]);
  rows.push([btn("\u2795 Add Pairs", "wlpage:0")]);
  rows.push([btn("\u{1F519} Back", "cmd:main")]);
  return kb(rows);
};
var wlAddKb = (page, wl) => {
  page = Math.max(0, Math.min(page, PAIR_PAGES.length - 1));
  const rows = chunk(PAIR_PAGES[page], 2).map(
    (row) => row.map((p) => {
      const code = norm(p), inWL = wl.includes(code);
      return btn(inWL ? `\u2705 ${p}` : p, inWL ? `wl:rmpage:${code}:${page}` : `wl:addpage:${code}:${page}`);
    })
  );
  const nav = [];
  if (page > 0) nav.push(btn("\u25C0 Prev", `wlpage:${page - 1}`));
  if (page < PAIR_PAGES.length - 1) nav.push(btn("Next \u25B6", `wlpage:${page + 1}`));
  if (nav.length) rows.push(nav);
  rows.push([btn(`\u2705 Done (${wl.length}/${MAX_WL})`, "cmd:watchlist")]);
  return kb(rows);
};
var intervalKb = () => kb([
  [btn("\u26A1 1min", "interval:1"), btn("\u{1F4CA} 5min", "interval:5"), btn("\u{1F550} 15min", "interval:15")],
  [btn("\u{1F519} Back", "cmd:settings")]
]);
var gradeKb = () => kb([
  [btn("\u{1F310} All", "gf:ALL"), btn("\u2B50 A+B", "gf:AB"), btn("\u{1F3C6} A only", "gf:A")],
  [btn("\u{1F519} Back", "cmd:settings")]
]);
var confKb = () => kb([
  [btn("Any", "cf:0"), btn("60%+", "cf:60"), btn("70%+", "cf:70")],
  [btn("75%+", "cf:75"), btn("80%+", "cf:80"), btn("85%+", "cf:85")],
  [btn("\u{1F519} Back", "cmd:settings")]
]);
var summTimeKb = () => kb([
  [btn("06:00", "sumhour:6"), btn("12:00", "sumhour:12"), btn("18:00", "sumhour:18")],
  [btn("20:00", "sumhour:20"), btn("22:00", "sumhour:22"), btn("00:00", "sumhour:0")],
  [btn("\u{1F519} Back", "cmd:settings")]
]);
var histNavKb = (page, total) => {
  const nav = [];
  if (page > 0) nav.push(btn("\u25C0 Prev", `cmd:history:${page - 1}`));
  if (page < Math.ceil(total / 10) - 1) nav.push(btn("Next \u25B6", `cmd:history:${page + 1}`));
  const rows = [];
  if (nav.length) rows.push(nav);
  rows.push([btn("\u{1F3C6} Stats", "cmd:stats"), btn("\u{1F519} Back", "cmd:main")]);
  return kb(rows);
};
var backQuick = () => [btn("\u{1F519} Back", "cmd:quick"), btn("\u{1F3E0} Menu", "cmd:main")];
var disp = (p) => p ? !p.includes("/") && p.length === 6 ? p.slice(0, 3) + "/" + p.slice(3) : p : "?";
var norm = (p) => String(p ?? "").replace("/", "");
var uid = () => Math.random().toString(36).slice(2, 8).toUpperCase();
var isCr = (p) => CRYPTO.some((b) => String(p || "").startsWith(b));
var chunk = (arr, n) => arr.reduce((r, x, i) => (i % n === 0 ? r.push([x]) : r[r.length - 1].push(x), r), []);
var fmtPrice = (price, pair) => {
  const v = parseFloat(price);
  if (isNaN(v)) return "?";
  return isCr(pair) ? v.toFixed(2) : v.toFixed(5);
};
var modeLabel = (m) => m === "fx" ? "FX" : m === "both" ? "BOTH" : "FTT";
function fmtMainMenu(u, cnt, wr, resolvedN) {
  return `FTT Signal Bot v4.4.2
${SEP}
\u{1F4B1} ${esc(disp(u.pair))} \xB7 ${u.interval}min \xB7 ${modeLabel(u.fxMode)}
\u{1F504} Auto: ${u.autoEnabled ? "ON \u2705" : "OFF"}  \u{1F441} Watchlist: ${u.watchlist.length} pairs
\u{1F3AF} Grade: ${esc(u.gradeFilter || "ALL")}  \u{1F916} AI Only: ${u.aiOnlyMode ? "ON" : "OFF"}
\u{1F4F0} News Block: ${u.blockNews !== false ? "ON" : "OFF"}
${SEP}
\u{1F4CA} Signals: ${cnt}  \u{1F4C8} Win Rate: ${wr}% (${resolvedN} resolved)
${SEP}
\u{1F4A1} <i>Tap a button below</i>`;
}
function fmtQuickMenu(u) {
  return `\u26A1 Quick actions
${SEP}
\u{1F4B1} ${esc(disp(u.pair))} \xB7 ${u.interval}min \xB7 ${modeLabel(u.fxMode)}
\u{1F504} Auto: <b>${u.autoEnabled ? "ON \u2705" : "OFF"}</b>
${SEP}
<b>Primary</b> \u2014 Signal \xB7 Auto \xB7 Scan \xB7 Status
<b>Explore</b> \u2014 Today \xB7 Weekly \xB7 Best \xB7 Risk \xB7 Heatmap \xB7 Journal \xB7 Stats`;
}
function fmtSettings(u) {
  const mode = u.fxMode === "fx" ? "FX \u2705 \u2014 Entry/SL/TP (spot)" : u.fxMode === "both" ? "BOTH \u{1F504} \u2014 SL/TP + expiry" : "FTT \u2014 fixed-time";
  return `\u2699\uFE0F Settings
${SEP}
<b>Signal</b>
\u{1F4B9} Mode: <b>${mode}</b>
<i>Tap Mode to cycle: FTT \u2192 FX \u2192 BOTH</i>
\u{1F3AF} Grade: <b>${esc(u.gradeFilter || "ALL")}</b>  \u{1F4CA} Conf: <b>${u.minConfidence || 0}%+</b>
\u23F1 Interval: <b>${u.interval}min</b>  \u{1F4B1} Pair: <b>${esc(disp(u.pair))}</b>
${SEP}
<b>Auto</b>
\u{1F916} AI Only: <b>${u.aiOnlyMode ? "ON \u2705" : "OFF"}</b>
\u{1F4F0} News Block: <b>${u.blockNews !== false ? "ON \u2705" : "OFF"}</b>
\u{1F4C5} Summary: <b>${u.dailySummary ? `ON (${u.summaryHour ?? 20}:00 UTC)` : "OFF"}</b>
${SEP}
<b>Data</b>
\u{1F4E1} Channel: <b>${u.channelId ? esc(String(u.channelId)) : "None"}</b>
\u2B07 Export: use /export via admin endpoint`;
}
function fmtSignal(data, pair, interval, no, opts = {}) {
  const sig = data.signal;
  const m = normMode(opts.mode);
  const tf = sig?.bestTimeframe?.timeframe || `${interval || 5}min`;
  const modeBadge = m === "both" ? "\u{1F504} <b>BOTH</b>" : m === "fx" || sig?.mode === "fx" ? "\u{1F4B9} <b>FX</b>" : "\u23F1 <b>FTT</b>";
  const header = `\u{1F4CA} <b>${esc(disp(pair))}</b> | ${esc(tf)} | ${modeBadge}`;
  if (data.marketStatus === "CLOSED")
    return `${header}
${SEP}
\u{1F534} <b>Forex Market CLOSED</b>
\u{1F4A1} Try <b>BTC/USD</b> (24/7)`;
  if (!sig)
    return `${header}
${SEP}
\u26AA <b>No signal data</b>
\u{1F4A1} Try again at the next candle close.`;
  const dir = sig.finalSignal || "NO_TRADE";
  const conf = sig.confidence || "0%";
  const grade = sig.grade ? `${sig.grade.grade} ${sig.grade.label}` : "";
  const htf = sig.higherTFTrend || "NEUTRAL";
  const reason = sig.entryReason || "";
  const best = sig.bestTimeframe;
  const expiry = best?.expiry?.humanReadable || null;
  const cd = best?.expiry?.countdown?.label || null;
  const price = sig.recommendations?.["1min"]?.entry?.price || sig.recommendations?.["5min"]?.entry?.price || sig.recommendations?.["15min"]?.entry?.price || null;
  const dE = dir === "BUY" ? "\u{1F7E2}" : dir === "SELL" ? "\u{1F534}" : "\u26AA";
  const hE = htf === "BUY" ? "\u{1F4C8}" : htf === "SELL" ? "\u{1F4C9}" : "\u27A1\uFE0F";
  const regimeE = { TRENDING: "\u{1F535}", RANGING: "\u{1F7E1}", BREAKOUT: "\u{1F7E0}", VOLATILE: "\u{1F534}" };
  let msg = "";
  if (opts.replay) msg += `\u{1F504} <i>REPLAY \u2014 not logged</i>
`;
  if (no) msg += `\u{1F4CC} Signal No. <b>${no}</b>
`;
  msg += header + "\n" + SEP + "\n";
  if (dir === "BUY" || dir === "SELL") {
    const confNum = parseInt(String(conf).replace("%", "")) || 0;
    const confDot = confNum >= 85 ? "\u{1F7E2}" : confNum >= 70 ? "\u{1F7E1}" : "\u{1F534}";
    msg += `${dE} <b>${dir}</b> ${confDot} ${esc(conf)}${grade ? `  [${esc(grade)}]` : ""}
`;
    msg += SEP + "\n";
    if (price) msg += `\u{1F4B0} Entry: <code>${esc(fmtPrice(price, pair))}</code>
`;
    const hasFx = sig.mode === "fx" && sig.fxLevels && sig.fxLevels.sl && sig.fxLevels.tp;
    if (hasFx) {
      msg += `\u{1F6D1} SL: <code>${esc(fmtPrice(sig.fxLevels.sl, pair))}</code>
`;
      msg += `\u{1F3AF} TP: <code>${esc(fmtPrice(sig.fxLevels.tp, pair))}</code>  (1:${esc(sig.fxLevels.rr || "2.5")})
`;
    }
    if (m !== "fx") {
      if (expiry) msg += `\u23F0 Expiry: <b>${esc(expiry)}</b>
`;
      if (cd) msg += `\u{1F550} Candle closes: <code>${esc(cd)}</code>
`;
    }
    const fill = sig.fillStatus || "INSTANT";
    if (fill === "PENDING_ENTRY" || fill === "PENDING") {
      const dist = sig.entryDistancePct != null ? ` (${esc(String(sig.entryDistancePct))}%)` : "";
      msg += `\u23F3 <b>PENDING</b> \u2014 price away from entry${dist}, wait for fill
`;
    } else {
      msg += `\u26A1 <b>INSTANT</b> \u2014 take now
`;
    }
    if (m === "fx" && !hasFx)
      msg += `\u{1F4B9} <i>FX mode \u2014 worker sent no SL/TP levels yet</i>
`;
    msg += SEP + "\n";
    const regime = sig.marketRegime;
    let ctx = `${hE} HTF: <b>${esc(htf)}</b>`;
    if (regime) ctx += ` \xB7 ${regimeE[regime] || "\u26AA"} Regime: <b>${esc(regime)}</b>`;
    msg += ctx + "\n";
    const sv = sig.structureVerdict;
    if (sv && sv.overall && sv.overall !== "N/A") {
      const sE = sv.overall === "ALIGNED" ? "\u2705" : sv.overall === "AGAINST" ? "\u26A0\uFE0F" : sv.overall === "MIXED" ? "\u{1F500}" : "\u27A1\uFE0F";
      let s = `${sE} Structure: <b>${esc(sv.overall)}</b>`;
      if (sv.direction && sv.direction !== "NEUTRAL")
        s += ` (${esc(sv.direction)}${sv.strength ? " " + esc(sv.strength) : ""})`;
      msg += s + "\n";
    }
    if (sig.regimeAdvice) msg += `\u{1F4A1} <i>${esc(sig.regimeAdvice)}</i>
`;
    msg += SEP + "\n";
    if (reason) msg += `\u{1F4DD} <i>${esc(reason)}</i>
`;
    const aiRaw = sig.aiValidation;
    if (aiRaw) {
      const aiStatus = aiRaw.status || aiRaw.combined && aiRaw.combined.status;
      if (aiStatus === "OK") {
        const aiAgrees = aiRaw.agrees !== void 0 ? aiRaw.agrees : aiRaw.combinedAgreed;
        const aiSignal = aiRaw.signal || aiRaw.combined && aiRaw.combined.signal;
        const aiConf = aiRaw.confidence ?? (aiRaw.combined && aiRaw.combined.confidence);
        const aiReason = aiRaw.reason || aiRaw.combined && aiRaw.combined.reason;
        const aiConcerns = aiRaw.concerns || aiRaw.combined && aiRaw.combined.concerns;
        const st = aiAgrees === true ? "\u2705 <b>AGREE</b>" : aiAgrees === false && aiSignal !== "NO_TRADE" ? "\u26A0\uFE0F <b>DISAGREE</b>" : "\u{1F914} <b>UNCERTAIN</b>";
        const aiSig = aiAgrees === true || aiAgrees === false && aiSignal !== "NO_TRADE" ? `<b>${esc(aiSignal)}</b>` : "<b>NO_TRADE</b>";
        msg += `\u{1F916} AI: ${st} \u2014 ${aiSig} (${esc(aiConf)}%)
`;
        if (aiReason) msg += `\u{1F4AC} <i>${esc(aiReason)}</i>
`;
        if (aiConcerns) msg += `\u{1F50D} <i>${esc(aiConcerns)}</i>
`;
      }
    }
    const filters = sig.filtersApplied || [];
    const d2 = filters.filter((f) => f.includes("D2_") || f.includes("BLOCK"));
    if (d2.length) msg += `\u{1F6AB} <b>Blocked:</b> ${d2.map((f) => `<code>${esc(f)}</code>`).join(" ")}
`;
    const aiForSep = aiRaw ? aiRaw.status || aiRaw.combined && aiRaw.combined.status : null;
    if (reason || aiForSep === "OK") msg += SEP + "\n";
    if (opts.newsAlert) {
      const n = Math.abs(opts.newsAlert.minsAway);
      const when = opts.newsAlert.minsAway >= 0 ? `in ${n}min` : `${n}min ago`;
      msg += `\u26A0\uFE0F <b>High-impact news ${when}</b>
\u{1F4F0} ${esc(opts.newsAlert.title)} (${esc(opts.newsAlert.currency)})
`;
    }
    if (opts.correlated && opts.correlated.length) {
      msg += `\u26A0\uFE0F <b>Correlated open:</b> ${esc(opts.correlated.join(", "))}
`;
    }
    msg += opts.replay ? `\u{1F504} <i>Replay only \u2014 result not tracked</i>` : `\u23F3 <i>Result tracked automatically</i>`;
  } else {
    const filters = sig.filtersApplied || [];
    msg += `\u26AA <b>NO TRADE</b>
`;
    msg += filters.length ? `\u{1F515} <b>Filters:</b> ${filters.map((f) => `<code>${esc(f)}</code>`).join(" ")}
` : `\u{1F515} <i>${sig.alignment === "MIXED" ? "Timeframes mixed \u2014 no clear setup" : "Setup not clear yet"}</i>
`;
    msg += `\u{1F4A1} Next check at the next ${esc(tf)} candle close`;
  }
  return msg;
}
function fmtHist(hist, page = 0) {
  const per = 10, slice = hist.slice(page * per, page * per + per);
  if (!hist.length) return `\u{1F4C8} History
${SEP}
No signals yet.

\u{1F4A1} Tap \u{1F4CA} Signal Now to get your first signal.`;
  if (!slice.length) return `\u{1F4C8} History
${SEP}
No more signals on this page.`;
  let msg = `\u{1F4C8} History (${page * per + 1}-${page * per + slice.length} of ${hist.length})
${SEP}
`;
  for (const h of slice) {
    const dE = h.direction === "BUY" ? "\u{1F7E2}" : "\u{1F534}";
    const rE = h.result === "WIN" ? "\u2705" : h.result === "LOSS" ? "\u274C" : h.result === "SKIP" ? "\u23ED" : h.result === "CANCEL" ? "\u{1F5D1}" : "\u23F3";
    const g = h.grade ? ` [${esc(h.grade.split(" ")[0])}]` : "";
    const p = h.pips != null ? ` ${h.pips > 0 ? "+" : ""}${h.pips}` : "";
    const timeStr = !h.result && h.expiryAt ? `\u23F3 ${msToHuman(h.expiryAt - Date.now())} left` : new Date(h.timestamp).toUTCString().slice(5, 17);
    msg += `${rE} #${String(h.no || "?").padStart(3)} ${dE} ${disp(h.pair).padEnd(8)} ${esc(h.confidence || "").padStart(4)}${g}${p.padStart(6)}  ${timeStr}
`;
  }
  return msg;
}
function calcDrawdown(resolved) {
  let balance = 0, peak = 0, maxDd = 0, curLoss = 0, maxLoss = 0;
  for (const h of [...resolved].reverse()) {
    if (h.result === "WIN") {
      balance++;
      curLoss = 0;
    } else {
      balance--;
      curLoss++;
    }
    if (balance > peak) peak = balance;
    const dd = peak - balance;
    if (dd > maxDd) maxDd = dd;
    if (curLoss > maxLoss) maxLoss = curLoss;
  }
  return { maxDd, maxLoss };
}
function fmtStats(hist, regimeStats, sessionStats) {
  const trades = hist.filter((h) => h.direction === "BUY" || h.direction === "SELL");
  const resolved = trades.filter((h) => h.result === "WIN" || h.result === "LOSS");
  const wins = resolved.filter((h) => h.result === "WIN").length;
  const losses = resolved.length - wins;
  const wr = resolved.length > 0 ? Math.round(wins / resolved.length * 100) : 0;
  const pending = trades.filter((h) => !h.result).length;
  let streak = 0, sT = "";
  for (const h of resolved) {
    if (!sT) {
      sT = h.result;
      streak = 1;
    } else if (h.result === sT) streak++;
    else break;
  }
  const { maxDd, maxLoss } = calcDrawdown(resolved);
  let msg = `\u{1F3C6} Win/Loss Stats
${SEP}
`;
  msg += `\u2705 Wins: ${wins}  \u274C Losses: ${losses}
`;
  msg += `\u{1F4CA} Win Rate: ${wr}% (${resolved.length} trades)
`;
  msg += `\u23F3 Pending: ${pending}`;
  if (streak >= 2) msg += `
\u{1F525} Streak: ${streak} ${sT}s`;
  if (maxLoss > 0) msg += `
\u{1F4C9} Max Losing Streak: ${maxLoss}  Max Drawdown: ${maxDd} trades`;
  if (regimeStats) {
    const regimes = Object.entries(regimeStats).filter(([, s]) => s.w + s.l > 0);
    if (regimes.length) {
      msg += `

\u{1F4CA} By Regime:
`;
      const rE = { TRENDING: "\u{1F535}", RANGING: "\u{1F7E1}", BREAKOUT: "\u{1F7E0}", VOLATILE: "\u{1F534}" };
      for (const [r, s] of regimes) {
        const t = s.w + s.l;
        const pct = Math.round(s.w / t * 100);
        msg += `  ${rE[r] || "\u26AA"} ${r}: ${s.w}W/${s.l}L (${pct}%) ${pct >= 55 ? "\u2705" : pct >= 45 ? "\u26A0\uFE0F" : "\u274C"}
`;
      }
    }
  }
  if (sessionStats) {
    const sessions = Object.entries(sessionStats).filter(([, s]) => s.w + s.l > 0);
    if (sessions.length) {
      msg += `
\u23F0 By Session:
`;
      for (const [s, v] of sessions) {
        const t = v.w + v.l;
        const pct = Math.round(v.w / t * 100);
        msg += `  ${s}: ${v.w}W/${v.l}L (${pct}%) ${pct >= 55 ? "\u2705" : pct >= 45 ? "\u26A0\uFE0F" : "\u274C"}
`;
      }
    }
  }
  const pm = {}, gm = {};
  for (const h of resolved) {
    if (!pm[h.pair]) pm[h.pair] = { w: 0, l: 0 };
    h.result === "WIN" ? pm[h.pair].w++ : pm[h.pair].l++;
    const g = (h.grade || "?").split(" ")[0];
    if (!gm[g]) gm[g] = { w: 0, l: 0 };
    h.result === "WIN" ? gm[g].w++ : gm[g].l++;
  }
  if (Object.keys(gm).length) {
    msg += `
Grade:
`;
    for (const [g, s] of Object.entries(gm)) {
      const t = s.w + s.l;
      msg += `  ${esc(g)}: ${s.w}W/${s.l}L (${Math.round(s.w / t * 100)}%)
`;
    }
  }
  if (Object.keys(pm).length) {
    msg += `
Top Pairs:
`;
    Object.entries(pm).sort((a, b) => b[1].w + b[1].l - (a[1].w + a[1].l)).slice(0, 5).forEach(([p, s]) => {
      const t = s.w + s.l;
      msg += `  ${disp(p)}: ${s.w}W/${s.l}L (${Math.round(s.w / t * 100)}%)
`;
    });
  }
  return msg;
}
function fmtJournal(hist, date) {
  const today = date || (/* @__PURE__ */ new Date()).toISOString().slice(0, 10);
  const th = hist.filter((x) => x.timestamp?.startsWith(today));
  if (!th.length) return `\u{1F4D2} Journal \u2014 ${today}
${SEP}
No signals today.`;
  const res = th.filter((x) => x.result === "WIN" || x.result === "LOSS");
  const wins = res.filter((x) => x.result === "WIN").length;
  const wr = res.length > 0 ? Math.round(wins / res.length * 100) : 0;
  let msg = `\u{1F4D2} Trade Journal \u2014 ${today}
${SEP}
`;
  msg += `\u{1F4CA} ${th.length} signals  \u2705 ${wins}W \u274C ${res.length - wins}L  \u{1F4C8} ${wr}%

`;
  for (const x of th.slice(0, 10)) {
    const dE = x.direction === "BUY" ? "\u{1F7E2}" : "\u{1F534}";
    const rE = x.result === "WIN" ? "\u2705" : x.result === "LOSS" ? "\u274C" : x.result === "CANCEL" ? "\u{1F5D1}" : "\u23F3";
    const rg = x.regime ? ` [${esc(x.regime.slice(0, 3))}]` : "";
    const sk = x.sessionKey ? ` ${esc(x.sessionKey.replace("_", "-"))}` : "";
    msg += `${rE} #${x.no} ${dE} ${disp(x.pair)} ${esc(x.confidence || "")}${rg}${sk}
`;
  }
  if (th.length > 10) msg += `...+${th.length - 10} more
`;
  const regToday = {};
  for (const x of res) {
    if (!x.regime) continue;
    if (!regToday[x.regime]) regToday[x.regime] = { w: 0, l: 0 };
    x.result === "WIN" ? regToday[x.regime].w++ : regToday[x.regime].l++;
  }
  if (Object.keys(regToday).length) {
    msg += `
Today's Regimes:
`;
    const rE = { TRENDING: "\u{1F535}", RANGING: "\u{1F7E1}", BREAKOUT: "\u{1F7E0}", VOLATILE: "\u{1F534}" };
    for (const [r, s] of Object.entries(regToday)) {
      const t = s.w + s.l;
      msg += `  ${rE[r] || "\u26AA"} ${r}: ${s.w}W/${s.l}L (${Math.round(s.w / t * 100)}%)
`;
    }
  }
  return msg;
}
function fmtWeekly(hist, weekLabel) {
  const now = /* @__PURE__ */ new Date();
  const day = now.getUTCDay(), diff = day === 0 ? 6 : day - 1;
  const mon = new Date(now);
  mon.setUTCDate(now.getUTCDate() - diff);
  const weekStart = mon.toISOString().slice(0, 10);
  const label = weekLabel || `Week of ${weekStart}`;
  const wh = hist.filter((x) => x.timestamp >= weekStart);
  const res = wh.filter((x) => x.result === "WIN" || x.result === "LOSS");
  const wins = res.filter((x) => x.result === "WIN").length;
  const wr = res.length > 0 ? Math.round(wins / res.length * 100) : 0;
  let msg = `\u{1F4C5} Weekly Report \u2014 ${label}
${SEP}
`;
  msg += `\u{1F4CA} ${wh.length} signals  \u2705 ${wins}W \u274C ${res.length - wins}L
\u{1F4C8} Win Rate: ${wr}%
`;
  const rm = {};
  for (const x of res) {
    if (!x.regime) continue;
    if (!rm[x.regime]) rm[x.regime] = { w: 0, l: 0 };
    x.result === "WIN" ? rm[x.regime].w++ : rm[x.regime].l++;
  }
  if (Object.keys(rm).length) {
    const sorted = Object.entries(rm).map(([r, s]) => {
      const t = s.w + s.l;
      return { r, w: s.w, l: s.l, pct: t > 0 ? Math.round(s.w / t * 100) : 0 };
    }).sort((a, b) => b.pct - a.pct);
    const rIcon = { TRENDING: "\u{1F535}", RANGING: "\u{1F7E1}", BREAKOUT: "\u{1F7E0}", VOLATILE: "\u{1F534}" };
    msg += `
Regimes this week:
`;
    for (const x of sorted) {
      const t = x.w + x.l;
      msg += `  ${rIcon[x.r] || "\u26AA"} ${x.r}: ${x.w}W/${x.l}L (${x.pct}%) ${x.pct >= 55 ? "\u2705" : x.pct >= 45 ? "\u26A0\uFE0F" : "\u274C"}
`;
    }
    if (sorted.length) {
      msg += `
\u{1F4A1} Best: ${sorted[0].r} (${sorted[0].pct}%)
`;
      if (sorted[sorted.length - 1].pct < 45) msg += `\u26A0\uFE0F Avoid: ${sorted[sorted.length - 1].r} (${sorted[sorted.length - 1].pct}%)
`;
    }
  }
  const pm = {};
  for (const x of res) {
    if (!pm[x.pair]) pm[x.pair] = { w: 0, l: 0 };
    x.result === "WIN" ? pm[x.pair].w++ : pm[x.pair].l++;
  }
  const topPairs = Object.entries(pm).map(([p, s]) => {
    const t = s.w + s.l;
    return { p, w: s.w, l: s.l, pct: t > 0 ? Math.round(s.w / t * 100) : 0 };
  }).sort((a, b) => b.pct - a.pct).slice(0, 3);
  if (topPairs.length) {
    msg += `
Top Pairs:
`;
    for (const x of topPairs) msg += `  ${disp(x.p)}: ${x.w}W/${x.l}L (${x.pct}%)
`;
  }
  msg += `
\u{1F504} Keep trading the best regimes next week!`;
  return msg;
}
function fmtRisk(hist) {
  const pending = hist.filter((x) => !x.result && (x.direction === "BUY" || x.direction === "SELL") && x.pair);
  if (!pending.length) return `\u{1F4C9} Open Risk Dashboard
${SEP}
No open trades \u2014 nice and clean. \u2705`;
  const now = Date.now();
  let msg = `\u{1F4C9} Open Risk Dashboard
${SEP}
${pending.length} open trade(s)
`;
  const exposure = {};
  for (const t of pending) {
    const exp = getCurrencyExposure(t.pair, t.direction);
    for (const [cur, side] of Object.entries(exp)) {
      if (!exposure[cur]) exposure[cur] = { long: 0, short: 0 };
      exposure[cur][side]++;
    }
  }
  for (const t of pending) {
    const dE = t.direction === "BUY" ? "\u{1F7E2}" : "\u{1F534}";
    const g = t.grade ? ` [${esc(t.grade.split(" ")[0])}]` : "";
    const rem = t.expiryAt ? msToHuman(t.expiryAt - now) : "?";
    const expired = t.expiryAt && t.expiryAt < now;
    msg += `${dE} #${t.no} ${t.direction} ${disp(t.pair)}${g} ${esc(t.confidence || "")}
`;
    msg += `   Entry: ${t.entryPrice ? fmtPrice(t.entryPrice, t.pair) : "?"}  ${expired ? "\u23F3 Result pending" : `\u23F1 ${rem} left`}
`;
  }
  const multi = Object.entries(exposure).filter(([, v]) => v.long + v.short > 1 && v.long > 0 && v.short === 0);
  if (multi.length) msg += `
Concentrated exposure: ${multi.map(([c, v]) => `${c} x${v.long}`).join(", ")}`;
  return msg;
}
function fmtHeatmap(hist) {
  const resolved = hist.filter((x) => x.result === "WIN" || x.result === "LOSS");
  if (!resolved.length) return `\u{1F550} Hourly Heatmap
${SEP}
No resolved trades yet.`;
  const hmap = {};
  for (const h of resolved) {
    const ts = new Date(h.timestamp).getTime();
    if (isNaN(ts)) continue;
    const hour = new Date(ts).getUTCHours();
    if (!hmap[hour]) hmap[hour] = { w: 0, l: 0 };
    h.result === "WIN" ? hmap[hour].w++ : hmap[hour].l++;
  }
  const entries = Object.entries(hmap).map(([hr, s]) => {
    const t = s.w + s.l;
    return { hr: parseInt(hr), w: s.w, l: s.l, t, pct: Math.round(s.w / t * 100) };
  }).sort((a, b) => a.hr - b.hr);
  let msg = `\u{1F550} Win Rate by Hour (UTC)
${SEP}
`;
  for (const e of entries) {
    const bar = "\u2588".repeat(Math.round(e.pct / 10)) + "\u2591".repeat(10 - Math.round(e.pct / 10));
    const icon = e.pct >= 60 ? "\u2705" : e.pct >= 45 ? "\u26A0\uFE0F" : "\u274C";
    const label = String(e.hr).padStart(2, "0") + ":00";
    msg += `${label}  ${bar}  ${e.pct}%  (${e.w}W/${e.l}L) ${icon}
`;
  }
  const best = [...entries].sort((a, b) => b.pct - a.pct)[0];
  const worst = [...entries].sort((a, b) => a.pct - b.pct)[0];
  if (best) msg += `
\u{1F3C6} Best:  ${String(best.hr).padStart(2, "0")}:00 UTC (${best.pct}%)`;
  if (worst) msg += `
\u26A0\uFE0F Worst: ${String(worst.hr).padStart(2, "0")}:00 UTC (${worst.pct}%)`;
  return msg;
}
function fmtBest(hist) {
  const resolved = hist.filter((x) => x.result === "WIN" || x.result === "LOSS");
  if (!resolved.length) return `\u{1F525} Best Pairs
${SEP}
No resolved trades yet.`;
  const pm = {};
  for (const h of resolved) {
    if (!h.pair) continue;
    if (!pm[h.pair]) pm[h.pair] = { w: 0, l: 0 };
    h.result === "WIN" ? pm[h.pair].w++ : pm[h.pair].l++;
  }
  const ranked = Object.entries(pm).map(([p, s]) => {
    const t = s.w + s.l;
    return { p, w: s.w, l: s.l, t, pct: Math.round(s.w / t * 100) };
  }).filter((x) => x.t >= 3).sort((a, b) => b.pct - a.pct || b.t - a.t);
  if (!ranked.length) return `\u{1F525} Best Pairs
${SEP}
Need at least 3 trades per pair.`;
  const medals = ["\u{1F947}", "\u{1F948}", "\u{1F949}", "4\uFE0F\u20E3", "5\uFE0F\u20E3"];
  let msg = `\u{1F525} Best Pairs Leaderboard
${SEP}
`;
  ranked.slice(0, 7).forEach((x, i) => {
    const bar = "\u2588".repeat(Math.round(x.pct / 10)) + "\u2591".repeat(10 - Math.round(x.pct / 10));
    const icon = x.pct >= 60 ? "\u2705" : x.pct >= 45 ? "\u26A0\uFE0F" : "\u274C";
    msg += `${medals[i] || "  "} ${disp(x.p).padEnd(8)} ${bar} ${x.pct}% (${x.w}W/${x.l}L) ${icon}
`;
  });
  if (ranked.length > 7) msg += `...+${ranked.length - 7} more pairs
`;
  msg += `
\u{1F4A1} Tip: Add top pairs to your Watchlist for auto scanning`;
  return msg;
}
async function dispatch(upd, env) {
  try {
    if (upd.message) await onMessage(upd.message, env);
    else if (upd.callback_query) await onCb(upd.callback_query, env);
  } catch (e) {
    console.error("dispatch:", e.message);
  }
}
async function onMessage(msg, env) {
  const cid = msg.chat.id;
  const text = (msg.text || "").trim();
  const u = await getUser(cid, env);
  const R = (t, kboard) => sendMsg(cid, t, env, kboard ? { reply_markup: kboard } : {});
  if (text.startsWith("/start")) return R(`\u{1F44B} <b>Welcome to FTT Signal Bot</b>

\u{1F4CA} <b>Professional Trading Signals</b>
\u{1F916} AI-validated \xB7 Multi-timeframe \xB7 Real-time

${SEP}
\u{1F4B1} Pair: <b>${esc(disp(u.pair))}</b> \xB7 ${u.interval}min
\u{1F4B9} Mode: <b>${modeLabel(u.fxMode)}</b>
\u{1F504} Auto: <b>${u.autoEnabled ? "ON \u2705" : "OFF"}</b>
\u{1F3AF} Grade: <b>${esc(u.gradeFilter || "ALL")}</b> \xB7 Conf: <b>${u.minConfidence || 0}%+</b>
${SEP}

\u{1F4CA} <b>Signal Now</b> \u2014 instant signal
\u26A1 <b>Quick actions</b> \u2014 Auto \xB7 Scan \xB7 Explore
\u{1F4C8} <b>History</b> \xB7 \u2699\uFE0F <b>Settings</b> \xB7 \u{1F680} <b>Premium</b>

\u{1F4A1} <i>Tap a button below</i>`, mainKb(u));
  if (text.startsWith("/signal")) return doSignal(cid, null, env);
  if (text.startsWith("/scan")) return doScanAll(cid, null, env);
  if (text.startsWith("/auto")) return doToggle(cid, null, env);
  if (text.startsWith("/status")) return doStatus(cid, null, env);
  if (text.startsWith("/history")) return doHist(cid, null, 0, env);
  if (text.startsWith("/stats")) return doStats(cid, null, env);
  if (text.startsWith("/watchlist")) return doWatchlist(cid, null, env);
  if (text.startsWith("/today")) return doToday(cid, null, env);
  if (text.startsWith("/summary")) return doSummary(cid, null, env);
  if (text.startsWith("/cancelall")) return doCancelAll(cid, null, env);
  if (text.startsWith("/journal")) return doJournal(cid, null, env);
  if (text.startsWith("/weekly")) return doWeekly(cid, null, env);
  if (text.startsWith("/analyze")) return doAnalyze(cid, null, text.slice(8).trim() || null, env);
  if (text.startsWith("/risk")) return doRisk(cid, null, env);
  if (text.startsWith("/heatmap")) return doHeatmap(cid, null, env);
  if (text.startsWith("/best")) return doBest(cid, null, env);
  if (text.startsWith("/replay")) return doReplay(cid, null, text.slice(7).trim() || null, env);
  if (text.startsWith("/setchannel ")) {
    const chanId = text.slice(12).trim();
    if (!chanId) return R("\u274C Usage: /setchannel @channelname  or  /setchannel -100123456789", mainKb(u));
    u.channelId = chanId;
    await saveUser(cid, u, env);
    return R(`\u2705 Channel set to ${chanId}

Make sure the bot is an admin of that channel.`, mainKb(u));
  }
  if (text.startsWith("/clearchannel")) {
    u.channelId = null;
    await saveUser(cid, u, env);
    return R("\u2705 Channel removed.", mainKb(u));
  }
  if (text.startsWith("/win ") || text.startsWith("/loss ")) {
    const parts = text.split(" ");
    const result = text.startsWith("/win") ? "WIN" : "LOSS";
    const no = parseInt(parts[1], 10);
    if (isNaN(no)) return R(`\u274C Usage: /win 5  or  /loss 5`, mainKb(u));
    return doManualResult(cid, null, no, result, env);
  }
  if (text.startsWith("/pair ")) {
    const raw = text.slice(6).trim().toUpperCase().replace(/[\s/]/g, "");
    u.pair = raw;
    await saveUser(cid, u, env);
    return R(`\u2705 Pair set to ${disp(raw)}`, mainKb(u));
  }
  if (text.startsWith("/interval ")) {
    const m = parseInt(text.slice(10).trim(), 10);
    if ([1, 5, 15].includes(m)) {
      u.interval = m;
      await saveUser(cid, u, env);
      return R(`\u2705 Interval: ${m}min`, mainKb(u));
    }
    return R("\u274C Use: 1, 5, or 15", mainKb(u));
  }
  if (text.startsWith("/help"))
    return R(`<b>FTT Signal Bot \u2014 Commands</b>

\u{1F4CA} <b>Core:</b>
/signal \u2014 get signal
/scan \u2014 scan all pairs
/auto \u2014 toggle auto scan

\u{1F4C8} <b>Analytics:</b>
/history \u2014 trade history
/stats \u2014 win rate stats
/today \u2014 today's performance
/summary \u2014 daily summary
/best \u2014 best pairs leaderboard
/risk \u2014 risk dashboard
/heatmap \u2014 win rate by hour

\u2699\uFE0F <b>Settings:</b>
/pair EURUSD \u2014 set pair
/interval 5 \u2014 set interval
/watchlist \u2014 manage watchlist
/replay EURUSD \u2014 analyze without logging
/setchannel \u2014 mirror to channel
/cancelall \u2014 cancel pending
/win <no> /loss <no> \u2014 manual override

\u{1F4A1} <i>Just type a pair name to scan instantly</i>`, mainKb(u));
  const rawPair = text.toUpperCase().replace(/[\s\/\-_.]/g, "");
  if (rawPair.length >= 6) {
    const allPairs = PAIR_PAGES.flat().map((p) => norm(p));
    const matched = allPairs.find((p) => p === rawPair);
    const fuzzy = matched || allPairs.find((p) => rawPair.startsWith(p.slice(0, 3)) && rawPair.endsWith(p.slice(3)));
    if (fuzzy) return doQuickSignal(cid, null, fuzzy, env);
  }
  return R("Use the buttons below \u{1F447}", mainKb(u));
}
async function onCb(cb, env) {
  const cid = cb.message.chat.id;
  const mid = cb.message.message_id;
  const data = cb.data;
  await answerCb(cb.id, env, "");
  const u = await getUser(cid, env);
  try {
    await _handleCb(cid, mid, data, u, env);
  } catch (e) {
    console.error("onCb [" + data + "]:", e.message);
    try {
      await editMsg(cid, mid, `\u26A0\uFE0F Error: ${esc(e.message.slice(0, 100))}

Tap menu to continue.`, env, { reply_markup: mainKb(u) });
    } catch {
      await sendMsg(cid, `\u26A0\uFE0F Something went wrong. Use /start to reset.`, env, { reply_markup: mainKb(u) });
    }
  }
}
async function _handleCb(cid, mid, data, u, env) {
  const R = (text, kboard) => reply(cid, mid, text, env, kboard);
  if (data === "cmd:main") {
    const h = await getHist(cid, env);
    const res = h.filter((x) => x.result === "WIN" || x.result === "LOSS");
    const wr = res.length > 0 ? Math.round(res.filter((x) => x.result === "WIN").length / res.length * 100) : 0;
    const cnt = await getCounter(cid, env);
    return R(fmtMainMenu(u, cnt, wr, res.length), mainKb(u));
  }
  if (data === "cmd:signal") return doSignal(cid, mid, env);
  if (data === "cmd:toggle_auto") return doToggle(cid, mid, env);
  if (data === "cmd:scanall") return doScanAll(cid, mid, env);
  if (data === "cmd:status") return doStatus(cid, mid, env);
  if (data === "cmd:stats") return doStats(cid, mid, env);
  if (data === "cmd:watchlist") return doWatchlist(cid, mid, env);
  if (data === "cmd:today") return doToday(cid, mid, env);
  if (data === "cmd:summary") return doSummary(cid, mid, env);
  if (data === "cmd:settings") return doSettings(cid, mid, env);
  if (data === "cmd:settings2") return doSettings(cid, mid, env);
  if (data === "cmd:quick") return doQuick(cid, mid, env);
  if (data === "cmd:journal") return doJournal(cid, mid, env);
  if (data === "cmd:weekly") return doWeekly(cid, mid, env);
  if (data === "cmd:risk") return doRisk(cid, mid, env);
  if (data === "cmd:heatmap") return doHeatmap(cid, mid, env);
  if (data === "cmd:best") return doBest(cid, mid, env);
  if (data === "cmd:premium") return doPremium(cid, mid, env);
  if (data === "cmd:exportinfo") return doExportInfo(cid, mid, env);
  if (data === "cmd:replayhelp") return R(`\u{1F504} Signal Replay
${SEP}
Type <code>/replay EURUSD</code> to get a live signal without logging it.

Great for analysis before committing to a trade.`, settingsKb(u));
  if (data.startsWith("cmd:history:")) return doHist(cid, mid, parseInt(data.split(":")[2]) || 0, env);
  if (data === "cmd:intervals") return R("\u23F1 Select Interval:", intervalKb());
  if (data === "cmd:gradefilter") return R("\u{1F3AF} Grade Filter:", gradeKb());
  if (data === "cmd:conffilter") return R("\u{1F4CA} Min Confidence:", confKb());
  if (data === "cmd:summarytime") return R("\u{1F550} Daily Summary Time (UTC):", summTimeKb());
  if (data === "cmd:togglesummary") {
    u.dailySummary = !u.dailySummary;
    await saveUser(cid, u, env);
    if (u.dailySummary) await addSummaryUser(cid, env);
    else await removeSummaryUser(cid, env);
    return R(fmtSettings(u), settingsKb(u));
  }
  if (data === "cmd:aionly") {
    u.aiOnlyMode = !u.aiOnlyMode;
    await saveUser(cid, u, env);
    return R(fmtSettings(u), settingsKb(u));
  }
  if (data === "cmd:blocknews") {
    u.blockNews = !(u.blockNews !== false);
    await saveUser(cid, u, env);
    return R(fmtSettings(u), settingsKb(u));
  }
  if (data === "cmd:fxmode") {
    const cycle = { ftt: "fx", fx: "both", both: "ftt" };
    u.fxMode = cycle[normMode(u.fxMode)] || "ftt";
    await saveUser(cid, u, env);
    return R(fmtSettings(u), settingsKb(u));
  }
  if (data === "cmd:channelinfo") {
    const chanInfo = u.channelId ? `\u{1F4E1} Channel Mode
${SEP}
Channel: <code>${esc(u.channelId)}</code>

Signals are auto-posted there.

To change: /setchannel &lt;id&gt;
To remove: /clearchannel` : `\u{1F4E1} Channel Mode
${SEP}
No channel set.

To enable:
1. Add bot as admin to your channel
2. Send /setchannel @yourchannel
   or /setchannel -100123456789`;
    return R(chanInfo, settingsKb(u));
  }
  if (data.startsWith("interval:")) {
    u.interval = parseInt(data.split(":")[1], 10);
    await saveUser(cid, u, env);
    return R(fmtSettings(u), settingsKb(u));
  }
  if (data.startsWith("sumhour:")) {
    u.summaryHour = parseInt(data.split(":")[1], 10);
    await saveUser(cid, u, env);
    return R(fmtSettings(u), settingsKb(u));
  }
  if (data.startsWith("gf:")) {
    u.gradeFilter = data.slice(3);
    await saveUser(cid, u, env);
    return R(fmtSettings(u), settingsKb(u));
  }
  if (data.startsWith("cf:")) {
    u.minConfidence = parseInt(data.split(":")[1], 10);
    await saveUser(cid, u, env);
    return R(fmtSettings(u), settingsKb(u));
  }
  if (data.startsWith("pairpage:")) return R("\u{1F4B1} Select default pair:", pairsKb(parseInt(data.split(":")[1], 10)));
  if (data.startsWith("pair:")) {
    u.pair = norm(data.slice(5));
    await saveUser(cid, u, env);
    return R(fmtSettings(u), settingsKb(u));
  }
  if (data.startsWith("wlpage:")) return R(`\u{1F441} Add to Watchlist (${u.watchlist.length}/${MAX_WL}):`, wlAddKb(parseInt(data.split(":")[1], 10), u.watchlist));
  if (data.startsWith("wl:rm:")) {
    u.watchlist = u.watchlist.filter((p) => p !== data.slice(6));
    await saveUser(cid, u, env);
    return doWatchlist(cid, mid, env);
  }
  if (data.startsWith("wl:addpage:")) {
    const parts = data.split(":"), pair = parts[2], page = parseInt(parts[3] || "0", 10);
    if (!u.watchlist.includes(pair) && u.watchlist.length < MAX_WL) {
      u.watchlist = [...u.watchlist, pair];
      await saveUser(cid, u, env);
    }
    return R(`\u{1F441} Add to Watchlist (${u.watchlist.length}/${MAX_WL}):`, wlAddKb(page, u.watchlist));
  }
  if (data.startsWith("wl:rmpage:")) {
    const parts = data.split(":"), pair = parts[2], page = parseInt(parts[3] || "0", 10);
    u.watchlist = u.watchlist.filter((p) => p !== pair);
    await saveUser(cid, u, env);
    return R(`\u{1F441} Add to Watchlist (${u.watchlist.length}/${MAX_WL}):`, wlAddKb(page, u.watchlist));
  }
  if (data === "cmd:cancelall") return doCancelAll(cid, mid, env);
  if (data.startsWith("qs:")) return doQuickSignal(cid, mid, data.slice(3), env);
  if (data.startsWith("res:win:")) return doManualResult(cid, mid, parseInt(data.split(":")[2], 10), "WIN", env);
  if (data.startsWith("res:loss:")) return doManualResult(cid, mid, parseInt(data.split(":")[2], 10), "LOSS", env);
}
async function restoreMainMsg(cid, mid, u, env) {
  if (!mid) return;
  const h = await getHist(cid, env);
  const res = h.filter((x) => x.result === "WIN" || x.result === "LOSS");
  const wr = res.length > 0 ? Math.round(res.filter((x) => x.result === "WIN").length / res.length * 100) : 0;
  const cnt = await getCounter(cid, env);
  await editMsg(cid, mid, fmtMainMenu(u, cnt, wr, res.length), env, { reply_markup: mainKb(u) });
}
async function doSignal(cid, mid, env) {
  const u = await getUser(cid, env);
  let loadingMid = mid;
  if (mid) {
    await editMsg(cid, mid, `\u23F3 Fetching ${disp(u.pair)}...`, env, {});
  } else {
    const r = await sendMsg(cid, `\u23F3 Fetching ${disp(u.pair)}...`, env, {});
    try {
      const j = await r?.json();
      loadingMid = j?.result?.message_id || null;
    } catch {
    }
  }
  try {
    const [data, newsAlert] = await Promise.all([
      fetchSig(u.pair, env, { mode: normMode(u.fxMode) }),
      hasHighImpactNews(env).catch(() => null)
    ]);
    const sig = data.signal;
    const dir = sig?.finalSignal;
    let no = null, corrWarnings = [];
    if (dir === "BUY" || dir === "SELL") {
      corrWarnings = await checkCorrelated(cid, u.pair, dir, env);
      no = await logAndSchedule(cid, u.pair, sig, env);
    }
    const useKb = dir === "BUY" || dir === "SELL" ? signalKb(no) : afterKb();
    await sendMsg(cid, fmtSignal(data, u.pair, u.interval, no, { newsAlert, correlated: corrWarnings, mode: normMode(u.fxMode) }), env, { reply_markup: useKb });
    if (mid) {
      await restoreMainMsg(cid, mid, u, env);
    } else if (loadingMid) {
      await deleteMsg(cid, loadingMid, env);
    }
    if ((dir === "BUY" || dir === "SELL") && sig?.confidence) {
      const ct = await updateConfTrend(cid, sig.confidence, env);
      if (ct.alert)
        await sendMsg(cid, `\u{1F4C9} Confidence Dropping \u2014 last 3: ${ct.vals[2]}% \u2192 ${ct.vals[1]}% \u2192 ${ct.vals[0]}%

Consider waiting for a stronger setup.`, env, { reply_markup: kb([[btn("\u{1F3C6} Stats", "cmd:stats"), btn("\u{1F519} Menu", "cmd:main")]]) });
    }
  } catch (e) {
    const err = `\u274C Signal fetch failed

${SEP}
\u26A0\uFE0F ${esc(e.message.slice(0, 150))}
${SEP}

\u{1F4A1} Try again in a few seconds.`;
    if (mid) await editMsg(cid, mid, err, env, { reply_markup: mainKb(u) });
    else {
      if (loadingMid) await deleteMsg(cid, loadingMid, env);
      await sendMsg(cid, err, env, { reply_markup: mainKb(u) });
    }
  }
}
async function doQuickSignal(cid, mid, pair, env) {
  const u = await getUser(cid, env);
  let loadingMid = mid;
  if (mid) {
    await editMsg(cid, mid, `\u23F3 Fetching ${disp(pair)}...`, env, {});
  } else {
    const r = await sendMsg(cid, `\u23F3 Fetching ${disp(pair)}...`, env, {});
    try {
      const j = await r?.json();
      loadingMid = j?.result?.message_id || null;
    } catch {
    }
  }
  try {
    const [data, newsAlert] = await Promise.all([
      fetchSig(pair, env, { mode: normMode(u.fxMode) }),
      hasHighImpactNews(env).catch(() => null)
    ]);
    const sig = data.signal;
    const dir = sig?.finalSignal;
    let no = null, corrWarnings = [];
    if (dir === "BUY" || dir === "SELL") {
      corrWarnings = await checkCorrelated(cid, pair, dir, env);
      no = await logAndSchedule(cid, pair, sig, env);
    }
    const useKb = dir === "BUY" || dir === "SELL" ? signalKb(no) : afterKb();
    await sendMsg(cid, fmtSignal(data, pair, u.interval, no, { newsAlert, correlated: corrWarnings, mode: normMode(u.fxMode) }), env, { reply_markup: useKb });
    if (mid) {
      await restoreMainMsg(cid, mid, u, env);
    } else if (loadingMid) {
      await deleteMsg(cid, loadingMid, env);
    }
    if ((dir === "BUY" || dir === "SELL") && sig?.confidence) {
      const ct = await updateConfTrend(cid, sig.confidence, env);
      if (ct.alert)
        await sendMsg(cid, `\u{1F4C9} Confidence Dropping \u2014 last 3: ${ct.vals[2]}% \u2192 ${ct.vals[1]}% \u2192 ${ct.vals[0]}%

Consider waiting for a stronger setup.`, env, { reply_markup: kb([[btn("\u{1F3C6} Stats", "cmd:stats"), btn("\u{1F519} Menu", "cmd:main")]]) });
    }
  } catch (e) {
    const err = `\u274C Failed: ${esc(e.message.slice(0, 150))}`;
    if (mid) await editMsg(cid, mid, err, env, { reply_markup: mainKb(u) });
    else {
      if (loadingMid) await deleteMsg(cid, loadingMid, env);
      await sendMsg(cid, err, env, { reply_markup: mainKb(u) });
    }
  }
}
async function doScanAll(cid, mid, env) {
  const u = await getUser(cid, env);
  const list = [u.pair, ...u.watchlist].filter((p, i, a) => a.indexOf(p) === i);
  let loadingMid = mid;
  if (mid) {
    await editMsg(cid, mid, `\u{1F50D} Scanning ${list.length} pairs...`, env, {});
  } else {
    const r = await sendMsg(cid, `\u{1F50D} Scanning ${list.length} pairs...`, env, {});
    try {
      const j = await r?.json();
      loadingMid = j?.result?.message_id || null;
    } catch {
    }
  }
  let found = 0;
  for (const pair of list) {
    try {
      const data = await fetchSig(pair, env, { mode: normMode(u.fxMode) });
      const sig = data.signal;
      const dir = sig?.finalSignal;
      if ((dir === "BUY" || dir === "SELL") && passGrade(sig, u.gradeFilter) && passConf(sig, u.minConfidence) && passAI(sig, u.aiOnlyMode)) {
        const corrWarnings = await checkCorrelated(cid, pair, dir, env);
        const no = await logAndSchedule(cid, pair, sig, env);
        await sendMsg(cid, fmtSignal(data, pair, u.interval, no, { correlated: corrWarnings, mode: normMode(u.fxMode) }), env, { reply_markup: signalKb(no) });
        found++;
      }
    } catch (e) {
      console.error(`scan ${pair}:`, e.message);
    }
  }
  const summary = found > 0 ? `\u2705 ${found} signal(s) found across ${list.length} pairs` : `\u26AA No signals across ${list.length} pairs`;
  if (mid) {
    await restoreMainMsg(cid, mid, u, env);
    await sendMsg(cid, summary, env, { reply_markup: afterKb() });
  } else {
    if (loadingMid) await deleteMsg(cid, loadingMid, env);
    await sendMsg(cid, summary, env, { reply_markup: mainKb(u) });
  }
}
async function doToggle(cid, mid, env) {
  const u = await getUser(cid, env);
  u.autoEnabled = !u.autoEnabled;
  u.noTradeStreak = 0;
  await saveUser(cid, u, env);
  if (u.autoEnabled) {
    await addAutoUser(cid, env);
  } else {
    await removeAutoUser(cid, env);
    await kdel(`lc:${cid}`, env);
    await kput(`errcnt:${cid}`, 0, env);
  }
  const wl = u.watchlist.map(disp).join(", ");
  const t = u.autoEnabled ? `\u{1F504} Auto Scan ON
${SEP}
${esc(disp(u.pair))}${wl ? "\nWatchlist: " + esc(wl) : ""}
Interval: ${u.interval}min  Grade: ${esc(u.gradeFilter || "ALL")}
AI Only: ${u.aiOnlyMode ? "ON" : "OFF"}  News Block: ${u.blockNews !== false ? "ON" : "OFF"}
\u23F0 Next scan: ${nextCandleIn(u.interval)}` : `\u{1F515} Auto Scan OFF
${SEP}
Auto scanning stopped.`;
  return reply(cid, mid, t, env, quickKb(u));
}
async function doQuick(cid, mid, env) {
  const u = await getUser(cid, env);
  return reply(cid, mid, fmtQuickMenu(u), env, quickKb(u));
}
async function doSettings(cid, mid, env) {
  const u = await getUser(cid, env);
  return reply(cid, mid, fmtSettings(u), env, settingsKb(u));
}
async function doPremium(cid, mid, env) {
  const t = `\u{1F680} Premium
${SEP}
<b>Coming soon \u2014 future features</b>

\u{1F680} Signal priority (faster delivery)
\u{1F4C8} More pairs & custom watchlists
\u{1F3AF} Advanced grade filters
\u{1F4CA} Extended history & CSV export
\u{1F514} Multi-channel alerts
\u{1F916} Higher AI confidence gates
${SEP}
\u{1F4A1} <i>This is informational only \u2014 no payment, no unlock yet.</i>
All current features are free for every user.`;
  return reply(cid, mid, t, env, premiumKb());
}
async function doExportInfo(cid, mid, env) {
  const t = `\u2B07 Export History
${SEP}
CSV export is available via the admin endpoint:

<code>/export?secret=\u2026&amp;chat=${cid}</code>

Columns: No, Pair, Dir, Grade, Conf, Entry, Exit, Pips, Result, Expiry, Time, ResolvedAt

\u{1F4A1} Ask your bot admin if you need a dump.`;
  return reply(cid, mid, t, env, settingsKb(await getUser(cid, env)));
}
async function doStatus(cid, mid, env) {
  const u = await getUser(cid, env);
  const cnt = await getCounter(cid, env);
  const h = await getHist(cid, env);
  const pen = h.filter((x) => !x.result && x.direction).length;
  const nextScan = u.autoEnabled ? `
\u23F0 Next scan: ${nextCandleIn(u.interval)}` : "";
  const t = `\u{1F4CB} Status
${SEP}
Pair: ${esc(disp(u.pair))}
Watchlist: ${u.watchlist.map(disp).join(", ") || "None"}
Interval: ${u.interval}min
Auto: ${u.autoEnabled ? "ON" : "OFF"}${nextScan}
Grade: ${esc(u.gradeFilter || "ALL")}
Min Conf: ${u.minConfidence || 0}%
AI Only: ${u.aiOnlyMode ? "ON" : "OFF"}
News Block: ${u.blockNews !== false ? "ON" : "OFF"}
Summary: ${u.dailySummary ? "ON" : "OFF"}
Channel: ${u.channelId ? esc(String(u.channelId)) : "None"}
Total Signals: ${cnt}  Pending: ${pen}`;
  return reply(cid, mid, t, env, kb([[btn("\u2699\uFE0F Settings", "cmd:settings"), btn("\u{1F4C9} Risk", "cmd:risk")], backQuick()]));
}
async function doHist(cid, mid, page, env) {
  const h = await getHist(cid, env);
  return reply(cid, mid, fmtHist(h, page), env, histNavKb(page, h.length));
}
async function doStats(cid, mid, env) {
  const h = await getHist(cid, env);
  const rs = await getRegimeStats(cid, env);
  const ss = await getSessionStats(cid, env);
  return reply(cid, mid, fmtStats(h, rs, ss), env, kb([[btn("\u{1F4C8} History", "cmd:history:0"), btn("\u{1F4D2} Journal", "cmd:journal"), btn("\u{1F525} Best", "cmd:best")], backQuick()]));
}
async function doJournal(cid, mid, env) {
  const h = await getHist(cid, env);
  return reply(cid, mid, fmtJournal(h), env, kb([[btn("\u{1F4C8} History", "cmd:history:0"), btn("\u{1F3C6} Stats", "cmd:stats")], backQuick()]));
}
async function doWeekly(cid, mid, env) {
  const h = await getHist(cid, env);
  return reply(cid, mid, fmtWeekly(h), env, kb([[btn("\u{1F3C6} Stats", "cmd:stats"), btn("\u{1F4D2} Journal", "cmd:journal")], backQuick()]));
}
async function doRisk(cid, mid, env) {
  const h = await getHist(cid, env);
  return reply(cid, mid, fmtRisk(h), env, kb([[btn("\u{1F5D1} Cancel All", "cmd:cancelall"), btn("\u{1F4C8} History", "cmd:history:0")], backQuick()]));
}
async function doHeatmap(cid, mid, env) {
  const h = await getHist(cid, env);
  return reply(cid, mid, fmtHeatmap(h), env, kb([[btn("\u{1F3C6} Stats", "cmd:stats"), btn("\u{1F525} Best Pairs", "cmd:best")], backQuick()]));
}
async function doBest(cid, mid, env) {
  const h = await getHist(cid, env);
  return reply(cid, mid, fmtBest(h), env, kb([[btn("\u{1F550} Heatmap", "cmd:heatmap"), btn("\u{1F3C6} Stats", "cmd:stats")], backQuick()]));
}
async function doReplay(cid, mid, pairRaw, env) {
  const u = await getUser(cid, env);
  const pair = pairRaw ? pairRaw.toUpperCase().replace(/[\s\/\-_.]/g, "") : norm(u.pair);
  if (mid) await editMsg(cid, mid, `\u{1F504} Replaying ${disp(pair)} (not logged)...`, env, {});
  else await sendMsg(cid, `\u{1F504} Replaying ${disp(pair)} (not logged)...`, env, {});
  try {
    const data = await fetchSig(pair, env, { mode: normMode(u.fxMode) });
    const sig = data?.signal;
    if (!sig) return sendMsg(cid, `\u274C No data for ${disp(pair)}`, env, { reply_markup: mainKb(u) });
    const msg = fmtSignal(data, pair, u.interval, null, { replay: true, mode: normMode(u.fxMode) });
    await sendMsg(cid, msg, env, { reply_markup: kb([
      [btn("\u{1F4CA} Get Signal (log it)", `qs:${norm(pair)}`), btn("\u{1F519} Menu", "cmd:main")]
    ]) });
    await restoreMainMsg(cid, mid, u, env);
  } catch (e) {
    await sendMsg(cid, `\u274C Replay failed: ${esc(e.message)}`, env, { reply_markup: mainKb(u) });
  }
}
async function doAnalyze(cid, mid, pairRaw, env) {
  const u = await getUser(cid, env);
  const pair = pairRaw ? pairRaw.toUpperCase().replace(/[\s\/\-_.]/g, "") : norm(u.pair);
  await reply(cid, mid, `\u{1F50D} Analyzing ${disp(pair)}...`, env);
  try {
    const data = await fetchSig(pair, env, { mode: normMode(u.fxMode) });
    const sig = data?.signal;
    if (!sig) return sendMsg(cid, `\u274C No data for ${disp(pair)}`, env, { reply_markup: mainKb(u) });
    const dir = sig.finalSignal || "NO_TRADE";
    const conf = sig.confidence || "0%";
    const dE = dir === "BUY" ? "\u{1F7E2}" : dir === "SELL" ? "\u{1F534}" : "\u26AA";
    const rg = sig.marketRegime || "UNKNOWN";
    const rIcon = { TRENDING: "\u{1F535}", RANGING: "\u{1F7E1}", BREAKOUT: "\u{1F7E0}", VOLATILE: "\u{1F534}" };
    let msg = `\u{1F50D} Analysis: ${esc(disp(pair))}
${SEP}
`;
    msg += `${dE} <b>${esc(dir)}</b>  ${esc(conf)}  ${sig.grade?.grade ? `[${esc(sig.grade.grade)} ${esc(sig.grade.label || "")}]` : ""}
`;
    msg += `${rIcon[rg] || "\u26AA"} Regime: <b>${esc(rg)}</b>
`;
    msg += `\u{1F4C8} HTF: <b>${esc(sig.higherTFTrend || "NEUTRAL")}</b>
`;
    msg += `\u{1F517} Alignment: <b>${esc(sig.alignment || "MIXED")}</b>
${SEP}
`;
    for (const tf of ["1min", "5min", "15min"]) {
      const r = sig.recommendations?.[tf];
      if (!r) continue;
      const td = r.direction === "BUY" ? "\u{1F7E2}" : r.direction === "SELL" ? "\u{1F534}" : "\u26AA";
      msg += `${td} ${tf}: <b>${esc(r.direction)}</b> ${r.score?.diff?.toFixed(1) || 0} diff (${esc(r.confluence || "")})
`;
    }
    if (sig.entryReason) msg += `
\u{1F4DD} <i>${esc(sig.entryReason)}</i>
`;
    if (sig.regimeAdvice) msg += `\u{1F4A1} <i>${esc(sig.regimeAdvice)}</i>
`;
    const aiA = sig.aiValidation;
    if (aiA) {
      const aiAStatus = aiA.status || aiA.combined && aiA.combined.status;
      if (aiAStatus === "OK") {
        const aiASig = aiA.signal || aiA.combined && aiA.combined.signal;
        const aiAConf = aiA.confidence ?? (aiA.combined && aiA.combined.confidence);
        const aiAConc = aiA.concerns || aiA.combined && aiA.combined.concerns;
        msg += `
\u{1F916} AI: <b>${esc(aiASig)}</b> ${esc(aiAConf)}%`;
        if (aiAConc) msg += ` \u26A0\uFE0F ${esc(aiAConc)}`;
        msg += "\n";
      }
    }
    await sendMsg(cid, msg, env, { reply_markup: kb([[btn("\u{1F4CA} Get Signal", `qs:${norm(pair)}`), btn("\u{1F504} Replay", `cmd:replayhelp`), btn("\u{1F519} Menu", "cmd:main")]]) });
  } catch (e) {
    await sendMsg(cid, `\u274C Analysis failed: ${esc(e.message)}`, env, { reply_markup: mainKb(u) });
  }
}
async function doWatchlist(cid, mid, env) {
  const u = await getUser(cid, env);
  const t = `\u{1F441} Watchlist (${u.watchlist.length}/${MAX_WL})

${u.watchlist.length ? u.watchlist.map(disp).join(", ") : "Empty"}

\u{1F4CA} = Quick signal  \u274C = Remove`;
  return reply(cid, mid, t, env, wlKb(u.watchlist));
}
async function doToday(cid, mid, env) {
  const h = await getHist(cid, env);
  const today = (/* @__PURE__ */ new Date()).toISOString().slice(0, 10);
  const th = h.filter((x) => x.timestamp?.startsWith(today));
  if (!th.length) return reply(cid, mid, `\u{1F4C5} Today (${today})
${SEP}
No signals yet.`, env, kb([backQuick()]));
  const res = th.filter((x) => x.result === "WIN" || x.result === "LOSS");
  const wins = res.filter((x) => x.result === "WIN").length;
  const wr = res.length > 0 ? Math.round(wins / res.length * 100) : 0;
  let t = `\u{1F4C5} Today \u2014 ${today}
${SEP}
\u{1F4CA} ${th.length} signals  \u2705 ${wins}W \u274C ${res.length - wins}L
\u{1F4C8} Win Rate: ${wr}%

`;
  for (const x of th.slice(0, 8)) {
    const dE = x.direction === "BUY" ? "\u{1F7E2}" : "\u{1F534}";
    const rE = x.result === "WIN" ? "\u2705" : x.result === "LOSS" ? "\u274C" : x.result === "CANCEL" ? "\u{1F5D1}" : "\u23F3";
    t += `${rE} #${x.no} ${dE} ${disp(x.pair)}${x.grade ? " [" + esc(x.grade.split(" ")[0]) + "]" : ""} ${esc(x.confidence || "")}
`;
  }
  return reply(cid, mid, t, env, kb([[btn("\u{1F4C8} History", "cmd:history:0"), btn("\u{1F4C9} Risk", "cmd:risk")], backQuick()]));
}
async function doSummary(cid, mid, env) {
  const h = await getHist(cid, env);
  const today = (/* @__PURE__ */ new Date()).toISOString().slice(0, 10);
  const th = h.filter((x) => x.timestamp?.startsWith(today));
  if (!th.length) return reply(cid, mid, `No signals today yet.`, env, kb([backQuick()]));
  const res = th.filter((x) => x.result === "WIN" || x.result === "LOSS");
  const wins = res.filter((x) => x.result === "WIN").length;
  const wr = res.length > 0 ? Math.round(wins / res.length * 100) : 0;
  const allR = h.filter((x) => x.result === "WIN" || x.result === "LOSS");
  const allWR = allR.length > 0 ? Math.round(allR.filter((x) => x.result === "WIN").length / allR.length * 100) : 0;
  const trend = wr > allWR ? "\u{1F4C8} Above avg" : wr < allWR ? "\u{1F4C9} Below avg" : "\u27A1\uFE0F On avg";
  const gm = {};
  for (const x of res) {
    const g = (x.grade || "?").split(" ")[0];
    if (!gm[g]) gm[g] = { w: 0, l: 0 };
    x.result === "WIN" ? gm[g].w++ : gm[g].l++;
  }
  let t = `\u{1F4C5} Daily Summary \u2014 ${today}
${SEP}
\u{1F4CA} ${th.length} signals  Resolved: ${res.length}
\u2705 ${wins}W  \u274C ${res.length - wins}L
\u{1F4C8} Win Rate: ${wr}%
`;
  if (Object.keys(gm).length) {
    t += `
Grades:
`;
    for (const [g, s] of Object.entries(gm)) {
      const tt = s.w + s.l;
      t += `  ${esc(g)}: ${s.w}W/${s.l}L (${Math.round(s.w / tt * 100)}%)
`;
    }
  }
  t += `
${trend} (all-time: ${allWR}%)`;
  return reply(cid, mid, t, env, kb([[btn("\u{1F4C8} History", "cmd:history:0"), btn("\u{1F3C6} Stats", "cmd:stats")], backQuick()]));
}
async function doCancelAll(cid, mid, env) {
  const u = await getUser(cid, env);
  const h = await getHist(cid, env);
  const pend = h.filter((x) => !x.result && x.direction);
  if (!pend.length) return reply(cid, mid, `\u2139\uFE0F No pending trades to cancel.`, env, mainKb(u));
  const allIds = await getPendingIds(env);
  const myTids = pend.map((x) => x.id);
  for (const trade of pend) {
    await setResult(cid, trade.id, "CANCEL", null, null, env);
    await clearLock(cid, trade.pair, env);
    await kdel(`pt:${trade.id}`, env);
    await delReminder(trade.id, env);
  }
  await savePendingIds(allIds.filter((id) => !myTids.includes(id)), env);
  return reply(cid, mid, `\u{1F5D1} Cancelled ${pend.length} pending trade(s).`, env, mainKb(u));
}
async function doManualResult(cid, mid, no, result, env) {
  const u = await getUser(cid, env);
  const h = await getHist(cid, env);
  const trade = h.find((x) => x.no === no);
  if (!trade)
    return reply(cid, mid, `\u274C Signal #${no} not found.`, env, mainKb(u));
  if (trade.result === "WIN" || trade.result === "LOSS")
    return reply(cid, mid, `\u2139\uFE0F Signal #${no} already resolved as ${trade.result}.`, env, mainKb(u));
  await setResult(cid, trade.id, result, null, null, env);
  await clearLock(cid, trade.pair, env);
  await kdel(`pt:${trade.id}`, env);
  await delReminder(trade.id, env);
  const ids = await getPendingIds(env);
  await savePendingIds(ids.filter((id) => id !== trade.id), env);
  const dE = trade.direction === "BUY" ? "\u{1F7E2}" : "\u{1F534}";
  const rE = result === "WIN" ? "\u2705 WIN" : "\u274C LOSS";
  return reply(
    cid,
    mid,
    `${rE} \u2014 manually set
${SEP}
${dE} #${no} ${trade.direction} ${disp(trade.pair)}${trade.grade ? ` [${esc(trade.grade)}]` : ""}`,
    env,
    afterKb()
  );
}
var workerModeParam = (m) => m === "fx" || m === "both" || m === true ? "&mode=fx" : "";
var normMode = (m) => {
  if (m === "fx" || m === "both") return m;
  return "ftt";
};
async function fetchSig(pair, env, opts = {}) {
  const WORKER_URL = "https://fttotcv6.umuhammadiswa.workers.dev";
  const mode = workerModeParam(opts.mode);
  const url = `${WORKER_URL}/api/signal?pair=${pair}${mode}`;
  const withTimeout = async (p, label) => {
    let timer;
    const timeoutP = new Promise((_, rej) => {
      timer = setTimeout(() => rej(new Error(label)), 2e4);
    });
    try {
      return await Promise.race([p, timeoutP]);
    } finally {
      clearTimeout(timer);
      p.catch(() => {
      });
    }
  };
  const res = env.SIGNAL_WORKER ? await withTimeout(env.SIGNAL_WORKER.fetch(new Request(url, { headers: { Accept: "application/json" } })), "Service binding timeout 20s") : await fetch(url, { headers: { Accept: "application/json" }, signal: AbortSignal.timeout(2e4) });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${(await res.text().catch(() => "")).slice(0, 150)}`);
  return withTimeout(res.json(), "Signal worker response timeout 20s");
}
async function fetchPrice(pair, env) {
  try {
    const d = await fetchSig(pair, env);
    return d?.signal?.recommendations?.["1min"]?.entry?.price || d?.signal?.recommendations?.["5min"]?.entry?.price || d?.signal?.recommendations?.["15min"]?.entry?.price || null;
  } catch {
    return null;
  }
}
async function cronLite(env) {
  const logs = [];
  const log = (m) => {
    console.log(m);
    logs.push(String(m));
  };
  log(`CronLite ${(/* @__PURE__ */ new Date()).toISOString()}`);
  if (!env?.BOT_TOKEN) {
    log("ERROR: BOT_TOKEN missing");
    return;
  }
  if (!env?.BOT_KV) {
    log("ERROR: BOT_KV missing");
    return;
  }
  await autoScan(env, log).catch((e) => log("ScanErr: " + e.message));
  await resultCheck(env, log).catch((e) => log("ResultErr: " + e.message));
  await expiryReminder(env, log).catch((e) => log("ReminderErr: " + e.message));
  await dailySummary(env, log).catch((e) => log("SummaryErr: " + e.message));
  await weeklyReport(env, log).catch((e) => log("WeeklyErr: " + e.message));
  log("Done");
}
async function cron(env, logs = [], force = false) {
  const log = (m) => {
    console.log(m);
    logs.push(String(m));
  };
  log(`Cron ${(/* @__PURE__ */ new Date()).toISOString()}`);
  if (!env?.BOT_TOKEN) {
    log("ERROR: BOT_TOKEN missing");
    return;
  }
  if (!env?.BOT_KV) {
    log("ERROR: BOT_KV missing");
    return;
  }
  await autoScan(env, log).catch((e) => log("ScanErr: " + e.message));
  await resultCheck(env, log).catch((e) => log("ResultErr: " + e.message));
  await expiryReminder(env, log).catch((e) => log("ReminderErr: " + e.message));
  await dailySummary(env, log).catch((e) => log("SummaryErr: " + e.message));
  await weeklyReport(env, log).catch((e) => log("WeeklyErr: " + e.message));
  log("Done");
}
async function autoScan(env, log) {
  const users = await getAutoUsers(env);
  log(`Scan: ${users.length} users`);
  const now = Date.now();
  let newsAlert = null;
  try {
    newsAlert = await hasHighImpactNews(env);
  } catch {
  }
  if (newsAlert) log(`News alert: ${newsAlert.title} (${newsAlert.currency}) in ${newsAlert.minsAway}min`);
  for (const cid of users) {
    try {
      const u = await getUser(cid, env);
      if (!u.autoEnabled) continue;
      const intervalMin = u.interval || 5;
      const intervalMs = intervalMin * 60 * 1e3;
      const currentCandle = Math.floor(now / intervalMs) * intervalMs;
      const lastCandle = await kget(`lc:${cid}`, env) || 0;
      if (currentCandle <= lastCandle) {
        log(`Skip ${cid} \u2014 same candle`);
        continue;
      }
      await kput(`lc:${cid}`, currentCandle, env, { expirationTtl: intervalMin * 60 * 2 });
      if (u.blockNews !== false && newsAlert) {
        log(`News skip for ${cid}: ${newsAlert.title}`);
        if (Math.abs(newsAlert.minsAway) <= intervalMin) {
          const sign = newsAlert.minsAway >= 0 ? "in" : "ago";
          await sendMsg(cid, `\u{1F6AB} Auto scan paused
${SEP}
\u26A0\uFE0F ${esc(newsAlert.title)} (${esc(newsAlert.currency)}) ${sign} ${Math.abs(newsAlert.minsAway)}min
${SEP}

Signals resume after the news window.`, env);
        }
        continue;
      }
      const list = [u.pair, ...u.watchlist].filter((p, i, a) => a.indexOf(p) === i);
      let anySignalSent = false, pairErrors = 0;
      for (const pair of list) {
        try {
          const scKey = `sc:${cid}:${norm(pair)}`;
          const lastPairCandle = await kget(scKey, env) || 0;
          if (lastPairCandle >= currentCandle) {
            log(`Dedup ${pair}`);
            continue;
          }
          const data = await fetchSig(pair, env, { mode: normMode(u.fxMode) });
          const sig = data.signal;
          const dir = sig?.finalSignal;
          if (dir === "BUY" || dir === "SELL") {
            const passesMain = passGrade(sig, u.gradeFilter) && passConf(sig, u.minConfidence) && passAI(sig, u.aiOnlyMode);
            if (!passesMain) {
              log(`Filtered ${pair}`);
              continue;
            }
            const lock = await getLock(cid, pair, env);
            if (lock?.direction === dir && lock?.expiryAt > now) {
              log(`Locked ${pair}`);
              continue;
            }
            const no = await logAndSchedule(cid, pair, sig, env);
            await kput(scKey, currentCandle, env, { expirationTtl: intervalMin * 60 + 60 });
            log(`Logged #${no} ${pair} ${dir}`);
            anySignalSent = true;
            if (sig.confidence) {
              const ct = await updateConfTrend(cid, sig.confidence, env);
              if (ct.alert)
                await sendMsg(cid, `\u{1F4C9} Confidence Dropping \u2014 last 3: ${ct.vals[2]}% \u2192 ${ct.vals[1]}% \u2192 ${ct.vals[0]}%

Consider waiting for a stronger setup.`, env, { reply_markup: kb([[btn("\u{1F3C6} Stats", "cmd:stats"), btn("\u{1F519} Menu", "cmd:main")]]) });
            }
          }
        } catch (e) {
          log(`Pair ${pair}: ${e.message}`);
          pairErrors++;
        }
      }
      if (list.length > 0 && pairErrors === list.length) {
        const errKey = `errcnt:${cid}`;
        const errs = (await kget(errKey, env) || 0) + 1;
        await kput(errKey, errs, env, { expirationTtl: 3600 });
        log(`Worker errors for ${cid}: ${errs}/${MAX_ERRORS}`);
        if (errs >= MAX_ERRORS) {
          u.autoEnabled = false;
          await saveUser(cid, u, env);
          await removeAutoUser(cid, env);
          await kdel(`lc:${cid}`, env);
          await kput(errKey, 0, env);
          await sendMsg(cid, `\u26A0\uFE0F Auto Scan paused

Signal worker unreachable \u2014 ${MAX_ERRORS} consecutive failures.
Fix the worker then tap \u{1F504} Start Auto to resume.`, env, { reply_markup: mainKb(u) });
          log(`Auto paused for ${cid}`);
        }
      } else if (pairErrors === 0 && list.length > 0) {
        await kput(`errcnt:${cid}`, 0, env);
      }
      if (!anySignalSent) {
        u.noTradeStreak = (u.noTradeStreak || 0) + 1;
        if (u.noTradeStreak >= 12) {
          await sendMsg(
            cid,
            `\u26AA No setup for ${u.noTradeStreak} scans across ${list.length} pair(s).`,
            env,
            { reply_markup: kb([[btn("\u{1F515} Stop Auto", "cmd:toggle_auto"), btn("\u{1F519} Menu", "cmd:main")]]) }
          );
          u.noTradeStreak = 0;
        }
      } else {
        u.noTradeStreak = 0;
      }
      await saveUser(cid, u, env);
    } catch (e) {
      log(`User ${cid}: ${e.message}`);
    }
  }
}
async function resultCheck(env, log) {
  const ids = await getPendingIds(env);
  if (!ids.length) return;
  log(`Results: ${ids.length} pending`);
  const now = Date.now(), keep = [];
  const isPendingFill = (t) => ["PENDING_ENTRY", "PENDING"].includes(t.fillStatus);
  const touchedEntry = (t, current) => {
    const entry = parseFloat(t.entryPrice);
    if (isNaN(entry) || isNaN(current)) return false;
    return t.direction === "BUY" ? current <= entry : current >= entry;
  };
  const noteEntryTouch = async (t, tid, current) => {
    if (!isPendingFill(t) || t.entryHit === true || !touchedEntry(t, current)) return false;
    t.entryHit = true;
    await kput(`pt:${tid}`, t, env, { expirationTtl: 7200 });
    return true;
  };
  const finish = async (t, tid, current, result, hitNote, lateMin) => {
    const entry = parseFloat(t.entryPrice);
    const diff = current - entry;
    const pips = isCr(t.pair) ? Math.round(Math.abs(diff) * 100) / 100 : Math.round(Math.abs(diff) * 1e4 * 10) / 10;
    const moveS = isCr(t.pair) ? `${diff > 0 ? "+" : ""}$${pips}` : `${diff > 0 ? "+" : ""}${pips} pips`;
    const pct = !isNaN(entry) && entry !== 0 ? diff / entry * 100 : 0;
    await setResult(t.chatId, tid, result, current, pips, env);
    await clearLock(t.chatId, t.pair, env);
    await kdel(`pt:${tid}`, env);
    await delReminder(tid, env);
    const dE = t.direction === "BUY" ? "\u{1F7E2}" : "\u{1F534}";
    const rE = result === "WIN" ? "\u2705 <b>WIN</b>" : "\u274C <b>LOSS</b>";
    const gS = t.grade ? ` [${esc(t.grade)}]` : "";
    const notes = [`#${t.signalNo || tid}`];
    if (hitNote) notes.push(hitNote);
    if (lateMin > 1) notes.push(`+${lateMin}min`);
    const entryHit = t.entryHit === true || !isPendingFill(t);
    const hitLine = entryHit ? `\u26A1 Entry hit \u2713 \u2014 price reached entry` : `\u26A0\uFE0F Entry miss \u2014 price never reached entry (result may be misleading)`;
    await sendMsg(
      t.chatId,
      `\u{1F4CC} Signal ${notes.join(" \xB7 ")}
${rE} \u2014 ${dE} ${esc(disp(t.pair))}${gS}
${SEP}
\u{1F4B0} Entry: <code>${esc(fmtPrice(entry, t.pair))}</code> \u2192 Exit: <code>${esc(fmtPrice(current, t.pair))}</code>
\u{1F3AF} Result: <b>${result}</b> ${moveS} (${diff > 0 ? "+" : ""}${pct.toFixed(2)}%)
${SEP}
${hitLine}`,
      env,
      { reply_markup: afterKb() }
    );
    const risk = await updateRisk(t.chatId, result, env);
    if (risk.type === "LOSS" && risk.streak >= 3) {
      await sendMsg(
        t.chatId,
        `\u26A0\uFE0F Risk Alert \u2014 ${risk.streak} Consecutive Losses

Consider taking a break or reducing trade size.`,
        env,
        { reply_markup: kb([[btn("\u{1F3C6} Check Stats", "cmd:stats"), btn("\u{1F515} Stop Auto", "cmd:toggle_auto")], [btn("\u{1F519} Continue", "cmd:main")]]) }
      );
    }
    await checkMilestone(t.chatId, env);
  };
  const skipTrade = async (t, tid, reason) => {
    await setResult(t.chatId, tid, "SKIP", null, null, env);
    await clearLock(t.chatId, t.pair, env);
    await kdel(`pt:${tid}`, env);
    await delReminder(tid, env);
    await sendMsg(t.chatId, `\u23ED Tracking #${t.signalNo || tid} \u2014 ${reason}`, env, { reply_markup: afterKb() });
  };
  for (const tid of ids) {
    try {
      const t = await kget(`pt:${tid}`, env);
      if (!t) continue;
      const isFx = !!(t.sl && t.tp);
      if (t.expiryAt > now) {
        if (isFx) {
          const cur2 = await fetchPrice(t.pair, env);
          if (!cur2) {
            keep.push(tid);
            continue;
          }
          const current2 = parseFloat(cur2);
          await noteEntryTouch(t, tid, current2);
          const sl = parseFloat(t.sl), tp = parseFloat(t.tp);
          if (isNaN(current2) || isNaN(sl) || isNaN(tp)) {
            keep.push(tid);
            continue;
          }
          const hitTp = t.direction === "BUY" ? current2 >= tp : current2 <= tp;
          const hitSl = t.direction === "BUY" ? current2 <= sl : current2 >= sl;
          if (hitTp) await finish(t, tid, current2, "WIN", "\u{1F3AF} TP hit", 0);
          else if (hitSl) await finish(t, tid, current2, "LOSS", "\u{1F6D1} SL hit", 0);
          else keep.push(tid);
        } else if (isPendingFill(t)) {
          const cur2 = await fetchPrice(t.pair, env);
          if (cur2) await noteEntryTouch(t, tid, parseFloat(cur2));
          keep.push(tid);
        } else {
          keep.push(tid);
        }
        continue;
      }
      const cur = await fetchPrice(t.pair, env);
      if (!cur || !t.entryPrice) {
        await skipTrade(t, tid, "price unavailable");
        continue;
      }
      const entry = parseFloat(t.entryPrice);
      const current = parseFloat(cur);
      if (isNaN(entry) || isNaN(current)) {
        await skipTrade(t, tid, "invalid price data");
        continue;
      }
      await noteEntryTouch(t, tid, current);
      const diff = current - entry;
      const result = t.direction === "BUY" ? diff > 0 ? "WIN" : "LOSS" : diff < 0 ? "WIN" : "LOSS";
      const late = Math.round((now - t.expiryAt) / 6e4);
      await finish(t, tid, current, result, isFx ? "\u23F0 60min horizon" : null, late);
    } catch (e) {
      log(`Result ${tid}: ${e.message}`);
      keep.push(tid);
    }
  }
  await savePendingIds(keep, env);
}
async function dailySummary(env, log) {
  const hour = (/* @__PURE__ */ new Date()).getUTCHours();
  const users = await getSummaryUsers(env);
  log(`Summary: ${users.length} users, hour=${hour}`);
  for (const cid of users) {
    try {
      const u = await getUser(cid, env);
      if (!u.dailySummary || hour !== (u.summaryHour ?? 20)) continue;
      const last = await kget(`ds:${cid}`, env) || 0;
      if (Date.now() - last < 55 * 60 * 1e3) continue;
      const h = await getHist(cid, env);
      const today = (/* @__PURE__ */ new Date()).toISOString().slice(0, 10);
      const th = h.filter((x) => x.timestamp?.startsWith(today));
      if (!th.length) continue;
      const res = th.filter((x) => x.result === "WIN" || x.result === "LOSS");
      const wins = res.filter((x) => x.result === "WIN").length;
      const wr = res.length > 0 ? Math.round(wins / res.length * 100) : 0;
      const gm = {};
      for (const x of res) {
        const g = (x.grade || "?").split(" ")[0];
        if (!gm[g]) gm[g] = { w: 0, l: 0 };
        x.result === "WIN" ? gm[g].w++ : gm[g].l++;
      }
      let sumT = `\u{1F4C5} Daily Summary \u2014 ${today}
${SEP}
\u{1F4CA} ${th.length} signals  \u2705 ${wins}W \u274C ${res.length - wins}L
\u{1F4C8} Win Rate: ${wr}%
\u23F3 Pending: ${th.filter((x) => !x.result).length}`;
      if (Object.keys(gm).length) {
        sumT += `
${SEP}
Grades:
`;
        for (const [g, s] of Object.entries(gm)) {
          const tt = s.w + s.l;
          sumT += `  ${esc(g)}: ${s.w}W/${s.l}L (${Math.round(s.w / tt * 100)}%)
`;
        }
      }
      await sendMsg(cid, sumT, env, { reply_markup: kb([[btn("\u{1F4C8} History", "cmd:history:0"), btn("\u{1F3C6} Stats", "cmd:stats")]]) });
      await kput(`ds:${cid}`, Date.now(), env);
      log(`Summary sent to ${cid}`);
    } catch (e) {
      log(`Summary ${cid}: ${e.message}`);
    }
  }
}
async function expiryReminder(env, log) {
  const ids = await getPendingReminders(env);
  if (!ids.length) return;
  const now = Date.now(), remaining = [];
  for (const tid of ids) {
    try {
      const r = await kget(`rem:${tid}`, env);
      if (!r) continue;
      if (r.remAt > now) {
        remaining.push(tid);
        continue;
      }
      const dE = r.direction === "BUY" ? "\u{1F7E2}" : "\u{1F534}";
      await sendMsg(r.chatId, `\u23F0 Signal #${r.signalNo} expires in ~30s
${SEP}
${dE} <b>${esc(r.direction)}</b> ${esc(disp(r.pair))}`, env);
      await kdel(`rem:${tid}`, env);
      log(`Reminder sent #${r.signalNo}`);
    } catch (e) {
      log(`Reminder ${tid}: ${e.message}`);
      remaining.push(tid);
    }
  }
  await kput("remind_ids", remaining, env);
}
async function weeklyReport(env, log) {
  const now = /* @__PURE__ */ new Date();
  const day = now.getUTCDay(), hour = now.getUTCHours();
  if (day !== 1 || hour !== 8) return;
  const users = await getAutoUsers(env);
  log(`Weekly: ${users.length} users`);
  for (const cid of users) {
    try {
      const lastKey = `wr:${cid}`;
      const last = await kget(lastKey, env) || 0;
      if (Date.now() - last < 6 * 24 * 60 * 60 * 1e3) continue;
      const h = await getHist(cid, env);
      await sendMsg(cid, fmtWeekly(h), env, { reply_markup: kb([[btn("\u{1F3C6} Stats", "cmd:stats"), btn("\u{1F4D2} Journal", "cmd:journal")], [btn("\u{1F525} Best Pairs", "cmd:best"), btn("\u{1F519} Menu", "cmd:main")]]) });
      await kput(lastKey, Date.now(), env);
      log(`Weekly sent to ${cid}`);
    } catch (e) {
      log(`Weekly ${cid}: ${e.message}`);
    }
  }
}
async function checkMilestone(cid, env) {
  try {
    const mk = `ms:${cid}`;
    const ms = await kget(mk, env) || { lastCount: 0 };
    const h = await getHist(cid, env);
    const res = h.filter((x) => x.result === "WIN" || x.result === "LOSS");
    const since = Math.max(0, res.length - ms.lastCount);
    if (since < MILESTONE) return;
    const batch = res.slice(0, since);
    const wins = batch.filter((x) => x.result === "WIN").length;
    const wr = Math.round(wins / batch.length * 100);
    const gm = {}, pm = {};
    for (const x of batch) {
      const g = (x.grade || "?").split(" ")[0];
      if (!gm[g]) gm[g] = { w: 0, l: 0 };
      x.result === "WIN" ? gm[g].w++ : gm[g].l++;
      if (!pm[x.pair]) pm[x.pair] = { w: 0, l: 0 };
      x.result === "WIN" ? pm[x.pair].w++ : pm[x.pair].l++;
    }
    let t = `\u{1F3C1} ${MILESTONE}-Signal Report (#${batch[batch.length - 1]?.no || "?"} to #${batch[0]?.no || "?"})
${SEP}
\u2705 ${wins}W  \u274C ${batch.length - wins}L
\u{1F4CA} Win Rate: ${wr}%

Grades:
`;
    for (const [g, s] of Object.entries(gm)) {
      const tt = s.w + s.l;
      t += `  ${esc(g)}: ${s.w}W/${s.l}L (${Math.round(s.w / tt * 100)}%)
`;
    }
    t += `
Top Pairs:
`;
    Object.entries(pm).sort((a, b) => b[1].w + b[1].l - (a[1].w + a[1].l)).slice(0, 4).forEach(([p, s]) => {
      const tt = s.w + s.l;
      t += `  ${disp(p)}: ${s.w}W/${s.l}L (${Math.round(s.w / tt * 100)}%)
`;
    });
    t += `
\u{1F504} Next ${MILESTONE} signals tracking starts now.`;
    await sendMsg(cid, t, env, { reply_markup: kb([[btn("\u{1F4C8} History", "cmd:history:0"), btn("\u{1F3C6} Stats", "cmd:stats"), btn("\u{1F525} Best Pairs", "cmd:best")]]) });
    await kput(mk, { lastCount: res.length }, env);
  } catch (e) {
    console.error("milestone:", e.message);
  }
}
export {
  index_default as default
};
