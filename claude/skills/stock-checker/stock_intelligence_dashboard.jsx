import { useState, useEffect, useRef, useCallback } from "react";

// ── helpers ────────────────────────────────────────────────────────────────
const fmt = (n, d = 2) => (n == null ? "—" : Number(n).toFixed(d));
const fmtPct = (n) => (n == null ? "—" : `${n >= 0 ? "+" : ""}${fmt(n)}%`);
const fmtM = (n) => {
  if (n == null) return "—";
  if (Math.abs(n) >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
  if (Math.abs(n) >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
  if (Math.abs(n) >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
  return `$${n}`;
};
const now = () => new Date().toLocaleTimeString("th-TH", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
const nowFull = () => new Date().toLocaleString("th-TH", { dateStyle: "short", timeStyle: "medium" });

// ── robust JSON array extractor ─────────────────────────────────────────────
// Claude + web_search often wraps JSON in prose or code fences. Pull the first
// valid [...] array out of the raw text instead of parsing the whole string.
function extractJsonArray(raw) {
  if (!raw || typeof raw !== "string") return [];
  // strip code fences
  let s = raw.replace(/```json/gi, "").replace(/```/g, "").trim();
  // direct attempt
  try {
    const d = JSON.parse(s);
    if (Array.isArray(d)) return d;
  } catch { /* fall through */ }
  // find the outermost [ ... ] block
  const start = s.indexOf("[");
  const end = s.lastIndexOf("]");
  if (start !== -1 && end !== -1 && end > start) {
    const slice = s.slice(start, end + 1);
    try {
      const d = JSON.parse(slice);
      if (Array.isArray(d)) return d;
    } catch { /* fall through */ }
  }
  return [];
}

// ── Claude API call ────────────────────────────────────────────────────────
async function rawCall(systemPrompt, userPrompt, maxTokens, useSearch) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 45000); // 45s safety timeout
  try {
    const body = {
      model: "claude-sonnet-4-6",
      max_tokens: maxTokens,
      system: systemPrompt,
      messages: [{ role: "user", content: userPrompt }],
    };
    if (useSearch) body.tools = [{ type: "web_search_20250305", name: "web_search" }];

    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: ctrl.signal,
    });
    if (!res.ok) {
      let detail = "";
      try { const err = await res.json(); detail = err?.error?.message || ""; } catch { /* ignore */ }
      const e = new Error(`API ${res.status}${detail ? ` — ${detail}` : ""}`);
      e.status = res.status;
      throw e;
    }
    const data = await res.json();
    // content can arrive as an array of typed blocks, a plain string, or be
    // missing when only tool blocks were returned. Extract text from any shape.
    let text = "";
    if (typeof data?.content === "string") {
      text = data.content;
    } else if (Array.isArray(data?.content)) {
      text = data.content
        .map((b) => (typeof b === "string" ? b : b?.type === "text" ? b.text : ""))
        .filter(Boolean)
        .join("");
    } else if (data?.completion) {
      text = data.completion; // legacy shape fallback
    }
    if (!text) throw new Error("ได้รับ response ว่างจาก API");
    return text;
  } finally {
    clearTimeout(timer);
  }
}

async function callClaude(systemPrompt, userPrompt, maxTokens = 1000) {
  // try with web search first; if that path fails for any reason other than a
  // genuine client error, retry without search so the dashboard still works.
  try {
    return await rawCall(systemPrompt, userPrompt, maxTokens, true);
  } catch (e) {
    // genuine client errors (auth/bad request) should surface, not be masked
    if (e.status && e.status < 500 && e.status !== 429) throw e;
    // everything else (timeout, empty content, 5xx, 429, search failure) → retry plain
    return await rawCall(systemPrompt, userPrompt, maxTokens, false);
  }
}

// ── mock price engine (simulate live ticks) ────────────────────────────────
const TICKERS = [
  { sym: "NVDA",  name: "NVIDIA Corp",         base: 138.5,  chg: 2.4,  vol: "92.3M", mcap: 3.38e12, sector: "Semiconductors" },
  { sym: "TSLA",  name: "Tesla Inc",            base: 315.2,  chg: -1.8, vol: "78.1M", mcap: 1.01e12, sector: "EV / Energy" },
  { sym: "RKLB",  name: "Rocket Lab USA",       base: 22.8,   chg: 5.1,  vol: "18.4M", mcap: 11.2e9,  sector: "Space" },
  { sym: "ASTS",  name: "AST SpaceMobile",      base: 31.4,   chg: 3.7,  vol: "12.9M", mcap: 8.9e9,   sector: "Space" },
  { sym: "MSFT",  name: "Microsoft Corp",       base: 472.3,  chg: 0.6,  vol: "19.2M", mcap: 3.51e12, sector: "Cloud / AI" },
  { sym: "GOOGL", name: "Alphabet Inc",         base: 195.8,  chg: 1.2,  vol: "22.7M", mcap: 2.44e12, sector: "Cloud / AI" },
  { sym: "IONQ",  name: "IonQ Inc",             base: 38.6,   chg: -2.3, vol: "6.1M",  mcap: 9.3e9,   sector: "Quantum" },
  { sym: "LUNR",  name: "Intuitive Machines",   base: 11.3,   chg: 7.2,  vol: "9.8M",  mcap: 2.1e9,   sector: "Space" },
];

function useLivePrices() {
  const [prices, setPrices] = useState(() =>
    Object.fromEntries(TICKERS.map((t) => [t.sym, { price: t.base, chg: t.chg, ts: nowFull() }]))
  );
  useEffect(() => {
    const id = setInterval(() => {
      setPrices((prev) => {
        const next = { ...prev };
        TICKERS.forEach((t) => {
          const old = prev[t.sym].price;
          const delta = (Math.random() - 0.49) * old * 0.003;
          const price = Math.max(old + delta, 0.01);
          const baseChg = t.chg + (price - t.base) / t.base * 100;
          next[t.sym] = { price, chg: parseFloat(baseChg.toFixed(2)), ts: nowFull() };
        });
        return next;
      });
    }, 2500);
    return () => clearInterval(id);
  }, []);
  return prices;
}

// ── spark data ─────────────────────────────────────────────────────────────
function useSpark(sym, price) {
  const history = useRef([]);
  useEffect(() => {
    history.current = [...history.current.slice(-29), price];
  }, [price]);
  return history.current;
}

function Spark({ sym, price }) {
  const pts = useSpark(sym, price);
  if (pts.length < 2) return <div style={{ height: 36 }} />;
  const mn = Math.min(...pts), mx = Math.max(...pts), rng = mx - mn || 1;
  const W = 90, H = 36;
  const d = pts.map((v, i) => {
    const x = (i / (pts.length - 1)) * W;
    const y = H - ((v - mn) / rng) * (H - 4) - 2;
    return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
  const col = pts[pts.length - 1] >= pts[0] ? "#22d3a8" : "#f4605a";
  return (
    <svg width={W} height={H} style={{ display: "block" }}>
      <path d={d} fill="none" stroke={col} strokeWidth="1.5" strokeLinejoin="round" />
    </svg>
  );
}

// ── news alert store ───────────────────────────────────────────────────────
const MAX_ALERTS = 30;

// ── main component ─────────────────────────────────────────────────────────
export default function App() {
  const prices = useLivePrices();
  const [alerts, setAlerts] = useState([]);
  const [selected, setSelected] = useState(null);
  const [analysis, setAnalysis] = useState({});
  const [loadingAI, setLoadingAI] = useState({});
  const [tab, setTab] = useState("market"); // market | watchlist | news
  const [scanning, setScanning] = useState(false);
  const [lastScan, setLastScan] = useState(null);
  const [autoScan, setAutoScan] = useState(false);
  const [scanInterval, setScanInterval] = useState(300); // seconds
  const [clockTick, setClockTick] = useState(now());
  const scanTimerRef = useRef(null);
  const alertsEndRef = useRef(null);

  // clock
  useEffect(() => {
    const id = setInterval(() => setClockTick(now()), 1000);
    return () => clearInterval(id);
  }, []);

  // auto scroll alerts
  useEffect(() => {
    alertsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [alerts]);

  // auto scan
  useEffect(() => {
    if (scanTimerRef.current) clearInterval(scanTimerRef.current);
    if (autoScan) {
      scanTimerRef.current = setInterval(runNewsScan, scanInterval * 1000);
    }
    return () => clearInterval(scanTimerRef.current);
  }, [autoScan, scanInterval]);

  // ── run news scan via Claude + web search ──────────────────────────────
  const runNewsScan = useCallback(async () => {
    if (scanning) return;
    setScanning(true);
    const ts = nowFull();
    try {
      const raw = await callClaude(
        `คุณคือ Stock News Monitor ค้นหาข่าวตลาดหุ้นสหรัฐล่าสุดผ่าน web search

กฎสำคัญ: หลังจากค้นหาเสร็จ ให้ตอบกลับเป็น JSON array ดิบเท่านั้น
- เริ่มต้นด้วย [ และจบด้วย ] เท่านั้น
- ห้ามมีข้อความนำ ห้ามมีคำอธิบาย ห้ามมี markdown หรือ backtick
- แต่ละ object: {"ticker":"SYM","title":"ชื่อข่าว","impact":"HIGH|MEDIUM|LOW","type":"EARNINGS|FED|MACRO|SECTOR|ANALYST","summary":"สรุป 1 ประโยคภาษาไทย"}
- ถ้าไม่มีข่าวสำคัญ ตอบ []`,
        `ค้นหา/ประเมินข่าวตลาดหุ้นสหรัฐล่าสุด ณ ${ts} ที่กระทบ: NVDA, TSLA, RKLB, ASTS, MSFT, GOOGL, IONQ, LUNR
รวมข่าว Fed, S&P500, Nasdaq และเศรษฐกิจสำคัญ
ถ้าค้นเว็บได้ให้ใช้ข้อมูลล่าสุด ถ้าค้นไม่ได้ให้ประเมินจากความรู้ที่มี
เลือกเฉพาะข่าวที่มีผลต่อราคา ไม่เกิน 8 ข่าว เรียงสำคัญมากไปน้อย`,
        900
      );

      let items = extractJsonArray(raw);

      if (items.length > 0) {
        const newAlerts = items.map((a, i) => ({
          id: `${Date.now()}-${i}`,
          ts,
          ticker: a.ticker || "MARKET",
          title: a.title || "ข่าวสำคัญ",
          summary: a.summary || "",
          impact: (a.impact || "MEDIUM").toUpperCase(),
          type: (a.type || "MACRO").toUpperCase(),
          url: a.url || "",
          seen: false,
        }));
        setAlerts((prev) => [...prev, ...newAlerts].slice(-MAX_ALERTS));
        // browser notification
        if ("Notification" in window && Notification.permission === "granted") {
          const top = newAlerts.find((a) => a.impact === "HIGH") || newAlerts[0];
          if (top) new Notification(`🚨 ${top.ticker}: ${top.title}`, { body: top.summary });
        }
      } else {
        // no parseable news — log quietly, do not raise an error alert
        setAlerts((prev) => [
          ...prev,
          { id: Date.now(), ts, ticker: "INFO", title: "ยังไม่พบข่าวสำคัญรอบนี้", summary: "ลองสแกนอีกครั้งภายหลัง", impact: "LOW", type: "SYSTEM", seen: true },
        ].slice(-MAX_ALERTS));
      }
      setLastScan(ts);
    } catch (e) {
      console.error(e);
      setAlerts((prev) => [
        ...prev,
        { id: Date.now(), ts, ticker: "SYS", title: "เชื่อมต่อ API ไม่สำเร็จ", summary: e.message, impact: "LOW", type: "SYSTEM", seen: true },
      ].slice(-MAX_ALERTS));
    }
    setScanning(false);
  }, [scanning]);

  // ── AI analysis for a ticker ──────────────────────────────────────────
  const analyzeStock = useCallback(async (sym) => {
    if (loadingAI[sym]) return;
    setLoadingAI((p) => ({ ...p, [sym]: true }));
    const t = TICKERS.find((x) => x.sym === sym);
    const p = prices[sym];
    try {
      const result = await callClaude(
        `คุณคือ Stock Analyst ผู้เชี่ยวชาญ ตอบภาษาไทย กระชับ ใช้ emoji สื่อสถานะ`,
        `วิเคราะห์หุ้น ${sym} (${t.name}) ราคาปัจจุบัน $${fmt(p.price)} เปลี่ยนแปลง ${fmtPct(p.chg)}
Sector: ${t.sector}

ค้นหาข้อมูลล่าสุดแล้วสรุป:
1. 📊 Trend & Signal (Bull/Bear/Neutral) + เหตุผล
2. 🎯 Support: S1, S2 | Resistance: R1, R2
3. 📰 ข่าวสำคัญล่าสุดที่กระทบ
4. ⚡ Catalyst ที่น่าจับตา
5. 🎲 Risk/Reward: ระดับความเสี่ยง

สรุปสั้น ๆ ไม่เกิน 200 คำ`,
        900
      );
      setAnalysis((p) => ({ ...p, [sym]: { text: result, ts: nowFull() } }));
    } catch (e) {
      setAnalysis((p) => ({ ...p, [sym]: { text: `❌ Error: ${e.message}`, ts: nowFull() } }));
    }
    setLoadingAI((p) => ({ ...p, [sym]: false }));
  }, [prices, loadingAI]);

  // notify permission
  const requestNotify = () => {
    if ("Notification" in window) Notification.requestPermission();
  };

  // ── colors ─────────────────────────────────────────────────────────────
  const impactColor = { HIGH: "#f4605a", MEDIUM: "#f4a830", LOW: "#22d3a8", SYSTEM: "#666", INFO: "#666" };
  const typeColor = { EARNINGS: "#a78bfa", FED: "#fb923c", MACRO: "#60a5fa", SECTOR: "#34d399", ANALYST: "#f9a8d4", SYSTEM: "#666" };

  const unseen = alerts.filter((a) => !a.seen && a.impact !== "SYSTEM" && a.type !== "SYSTEM").length;

  // ── styles ─────────────────────────────────────────────────────────────
  const S = {
    root: { fontFamily: "'Inter', 'Noto Sans Thai', sans-serif", background: "#0d1117", color: "#e6edf3", minHeight: "100vh", fontSize: 13 },
    header: { background: "#161b22", borderBottom: "1px solid #21262d", padding: "10px 20px", display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" },
    logo: { fontWeight: 800, fontSize: 15, letterSpacing: "-0.5px", color: "#e6edf3" },
    dot: (live) => ({ width: 8, height: 8, borderRadius: "50%", background: live ? "#22d3a8" : "#555", boxShadow: live ? "0 0 8px #22d3a850" : "none" }),
    clock: { color: "#8b949e", fontSize: 12, fontVariantNumeric: "tabular-nums" },
    tabs: { display: "flex", gap: 2, marginLeft: "auto" },
    tab: (active) => ({ background: active ? "#21262d" : "transparent", border: active ? "1px solid #30363d" : "1px solid transparent", borderRadius: 6, padding: "5px 14px", cursor: "pointer", color: active ? "#e6edf3" : "#8b949e", fontSize: 12, fontWeight: active ? 600 : 400 }),
    body: { display: "grid", gridTemplateColumns: "1fr 340px", gap: 0, height: "calc(100vh - 52px)" },
    main: { overflowY: "auto", padding: 16 },
    sidebar: { borderLeft: "1px solid #21262d", display: "flex", flexDirection: "column", overflow: "hidden" },
    card: { background: "#161b22", border: "1px solid #21262d", borderRadius: 8, padding: "12px 14px", marginBottom: 10 },
    sectionTitle: { color: "#8b949e", fontSize: 11, fontWeight: 600, letterSpacing: 1, textTransform: "uppercase", marginBottom: 10 },
    tickerRow: (sel) => ({
      display: "grid", gridTemplateColumns: "60px 1fr 90px 56px 56px 90px", gap: 8, alignItems: "center",
      padding: "8px 10px", borderRadius: 6, cursor: "pointer", marginBottom: 2,
      background: sel ? "#1c2333" : "transparent",
      border: sel ? "1px solid #388bfd50" : "1px solid transparent",
      transition: "background .15s",
    }),
    sym: { fontWeight: 700, color: "#e6edf3", fontSize: 13 },
    name: { color: "#8b949e", fontSize: 11, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" },
    price: { textAlign: "right", fontWeight: 600, fontVariantNumeric: "tabular-nums", fontSize: 13 },
    chg: (c) => ({ textAlign: "right", fontWeight: 600, color: c >= 0 ? "#22d3a8" : "#f4605a", fontSize: 12 }),
    sector: { color: "#8b949e", fontSize: 10, textAlign: "right", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" },
    analyzeBtn: (loading) => ({
      background: loading ? "#21262d" : "#1f6feb", border: "none", borderRadius: 4, color: loading ? "#8b949e" : "#fff",
      padding: "3px 8px", fontSize: 11, cursor: loading ? "default" : "pointer", whiteSpace: "nowrap",
    }),
    analysisBox: { background: "#0d1117", border: "1px solid #21262d", borderRadius: 6, padding: "10px 12px", marginTop: 8, fontSize: 12, lineHeight: 1.7, color: "#c9d1d9", whiteSpace: "pre-wrap" },
    // sidebar alerts
    alertsHeader: { padding: "10px 14px", borderBottom: "1px solid #21262d", display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" },
    alertScroll: { flex: 1, overflowY: "auto", padding: "8px 10px" },
    alertCard: (imp) => ({
      background: "#161b22", border: `1px solid ${impactColor[imp] || "#30363d"}22`,
      borderLeft: `3px solid ${impactColor[imp] || "#30363d"}`,
      borderRadius: 6, padding: "8px 10px", marginBottom: 6,
    }),
    alertTicker: (imp) => ({ fontWeight: 700, color: impactColor[imp] || "#e6edf3", fontSize: 12 }),
    alertTitle: { color: "#e6edf3", fontSize: 12, fontWeight: 500, lineHeight: 1.4, marginTop: 2 },
    alertSummary: { color: "#8b949e", fontSize: 11, lineHeight: 1.5, marginTop: 3 },
    alertMeta: { display: "flex", gap: 6, marginTop: 5, flexWrap: "wrap" },
    badge: (col) => ({ background: `${col}22`, color: col, fontSize: 9, padding: "1px 6px", borderRadius: 10, fontWeight: 700, letterSpacing: 0.5 }),
    scanBtn: (s) => ({
      background: s ? "#1f6feb" : "#21262d", border: s ? "1px solid #1f6feb" : "1px solid #30363d",
      borderRadius: 6, color: s ? "#fff" : "#8b949e", padding: "5px 12px", cursor: s ? "default" : "pointer", fontSize: 11, fontWeight: 600,
    }),
    autoToggle: (on) => ({
      background: on ? "#1a3a1a" : "#21262d", border: on ? "1px solid #22d3a860" : "1px solid #30363d",
      borderRadius: 6, color: on ? "#22d3a8" : "#8b949e", padding: "5px 10px", cursor: "pointer", fontSize: 11, fontWeight: 600,
    }),
    emptyAlerts: { color: "#8b949e", textAlign: "center", padding: "40px 20px", fontSize: 12 },
  };

  // ── render ─────────────────────────────────────────────────────────────
  return (
    <div style={S.root}>
      {/* HEADER */}
      <header style={S.header}>
        <span style={S.logo}>📡 Stock Intelligence</span>
        <div style={S.dot(true)} title="Live" />
        <span style={S.clock}>{clockTick}</span>
        <span style={{ ...S.clock, color: "#22d3a8", marginLeft: 4 }}>LIVE</span>
        {lastScan && <span style={{ ...S.clock, marginLeft: 4 }}>• สแกนล่าสุด {lastScan}</span>}
        <div style={S.tabs}>
          {[["market", "📊 ตลาด"], ["watchlist", "⭐ Watchlist"], ["news", `🔔 ข่าว${unseen > 0 ? ` (${unseen})` : ""}`]].map(([k, l]) => (
            <button key={k} style={S.tab(tab === k)} onClick={() => { setTab(k); if (k === "news") setAlerts((p) => p.map((a) => ({ ...a, seen: true }))); }}>{l}</button>
          ))}
        </div>
        <button style={{ background: "none", border: "1px solid #30363d", borderRadius: 6, color: "#8b949e", padding: "4px 10px", cursor: "pointer", fontSize: 11 }} onClick={requestNotify}>
          🔔 เปิดแจ้งเตือน
        </button>
      </header>

      <div style={S.body}>
        {/* MAIN */}
        <main style={S.main}>
          {/* Market Overview */}
          <div style={S.card}>
            <div style={S.sectionTitle}>ภาพรวมดัชนี</div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10 }}>
              {[
                { name: "S&P 500", val: "5,891.2", chg: 0.43 },
                { name: "NASDAQ", val: "19,204.6", chg: 0.87 },
                { name: "VIX", val: "16.8", chg: -3.2 },
                { name: "DXY", val: "104.3", chg: -0.21 },
              ].map((ix) => (
                <div key={ix.name} style={{ background: "#0d1117", borderRadius: 6, padding: "8px 10px", border: "1px solid #21262d" }}>
                  <div style={{ color: "#8b949e", fontSize: 10, fontWeight: 600 }}>{ix.name}</div>
                  <div style={{ fontWeight: 700, fontSize: 15, marginTop: 2 }}>{ix.val}</div>
                  <div style={{ color: ix.chg >= 0 ? "#22d3a8" : "#f4605a", fontSize: 11, fontWeight: 600 }}>{fmtPct(ix.chg)}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Ticker Table */}
          {(tab === "market" || tab === "watchlist") && (
            <div style={S.card}>
              <div style={S.sectionTitle}>
                {tab === "market" ? "หุ้น Watchlist" : "⭐ My Watchlist"}
                <span style={{ float: "right", color: "#22d3a8", fontSize: 10 }}>● อัปเดต real-time ทุก 2.5 วิ</span>
              </div>
              {/* headers */}
              <div style={{ display: "grid", gridTemplateColumns: "60px 1fr 90px 56px 56px 90px", gap: 8, padding: "0 10px 6px", color: "#8b949e", fontSize: 10, fontWeight: 600 }}>
                <span>SYMBOL</span><span>ชื่อ / Sector</span><span style={{ textAlign: "right" }}>PRICE</span><span style={{ textAlign: "right" }}>%CHG</span><span style={{ textAlign: "right" }}>SPARK</span><span style={{ textAlign: "right" }}>ACTION</span>
              </div>
              {TICKERS.map((t) => {
                const p = prices[t.sym];
                const sel = selected === t.sym;
                return (
                  <div key={t.sym}>
                    <div style={S.tickerRow(sel)} onClick={() => setSelected(sel ? null : t.sym)}>
                      <span style={S.sym}>{t.sym}</span>
                      <div>
                        <div style={S.name}>{t.name}</div>
                        <div style={{ ...S.sector }}>{t.sector}</div>
                      </div>
                      <span style={{ ...S.price, color: p.chg >= 0 ? "#22d3a8" : "#f4605a" }}>${fmt(p.price)}</span>
                      <span style={S.chg(p.chg)}>{fmtPct(p.chg)}</span>
                      <span><Spark sym={t.sym} price={p.price} /></span>
                      <span style={{ textAlign: "right" }}>
                        <button style={S.analyzeBtn(loadingAI[t.sym])} onClick={(e) => { e.stopPropagation(); analyzeStock(t.sym); }}>
                          {loadingAI[t.sym] ? "⏳..." : "🤖 AI"}
                        </button>
                      </span>
                    </div>
                    {sel && (
                      <div style={{ padding: "0 10px 8px" }}>
                        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 8, marginBottom: 6 }}>
                          <div style={{ background: "#0d1117", borderRadius: 6, padding: "6px 10px", border: "1px solid #21262d" }}>
                            <div style={{ color: "#8b949e", fontSize: 10 }}>Market Cap</div>
                            <div style={{ fontWeight: 700, fontSize: 13 }}>{fmtM(t.mcap)}</div>
                          </div>
                          <div style={{ background: "#0d1117", borderRadius: 6, padding: "6px 10px", border: "1px solid #21262d" }}>
                            <div style={{ color: "#8b949e", fontSize: 10 }}>Volume</div>
                            <div style={{ fontWeight: 700, fontSize: 13 }}>{t.vol}</div>
                          </div>
                          <div style={{ background: "#0d1117", borderRadius: 6, padding: "6px 10px", border: "1px solid #21262d" }}>
                            <div style={{ color: "#8b949e", fontSize: 10 }}>Sector</div>
                            <div style={{ fontWeight: 700, fontSize: 13 }}>{t.sector}</div>
                          </div>
                        </div>
                        {analysis[t.sym] ? (
                          <div style={S.analysisBox}>
                            <div style={{ color: "#8b949e", fontSize: 10, marginBottom: 6 }}>AI Analysis — {analysis[t.sym].ts}</div>
                            {analysis[t.sym].text}
                          </div>
                        ) : (
                          <div style={{ color: "#8b949e", fontSize: 11, padding: "6px 0" }}>
                            กด <strong style={{ color: "#e6edf3" }}>🤖 AI</strong> เพื่อให้ Claude วิเคราะห์ล่าสุด
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* News Tab full list */}
          {tab === "news" && (
            <div style={S.card}>
              <div style={S.sectionTitle}>ประวัติการแจ้งเตือนทั้งหมด ({alerts.length})</div>
              {alerts.length === 0 ? (
                <div style={S.emptyAlerts}>ยังไม่มีข่าว — กด "สแกนข่าว" เพื่อดึงข้อมูล</div>
              ) : (
                [...alerts].reverse().map((a) => (
                  <div key={a.id} style={{ ...S.alertCard(a.impact), marginBottom: 8 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <span style={S.alertTicker(a.impact)}>{a.ticker}</span>
                      <span style={{ color: "#8b949e", fontSize: 10 }}>{a.ts}</span>
                    </div>
                    <div style={S.alertTitle}>{a.title}</div>
                    {a.summary && <div style={S.alertSummary}>{a.summary}</div>}
                    <div style={S.alertMeta}>
                      <span style={S.badge(impactColor[a.impact] || "#666")}>{a.impact}</span>
                      <span style={S.badge(typeColor[a.type] || "#666")}>{a.type}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </main>

        {/* SIDEBAR — News Feed */}
        <aside style={S.sidebar}>
          <div style={S.alertsHeader}>
            <span style={{ fontWeight: 700, fontSize: 13, color: "#e6edf3" }}>🔔 ข่าวด่วน</span>
            {unseen > 0 && <span style={{ background: "#f4605a", color: "#fff", borderRadius: 10, fontSize: 10, padding: "1px 7px", fontWeight: 700 }}>{unseen}</span>}
            <button style={S.scanBtn(scanning)} onClick={runNewsScan} disabled={scanning}>
              {scanning ? "⏳ กำลังสแกน..." : "🔍 สแกนข่าว"}
            </button>
            <button style={S.autoToggle(autoScan)} onClick={() => setAutoScan((v) => !v)}>
              {autoScan ? `⏱ Auto ON (${scanInterval}s)` : "⏱ Auto OFF"}
            </button>
            {autoScan && (
              <select
                value={scanInterval}
                onChange={(e) => setScanInterval(Number(e.target.value))}
                style={{ background: "#21262d", border: "1px solid #30363d", color: "#e6edf3", borderRadius: 4, padding: "3px 6px", fontSize: 11, cursor: "pointer" }}
              >
                {[[60,"1 นาที"],[180,"3 นาที"],[300,"5 นาที"],[600,"10 นาที"],[1800,"30 นาที"]].map(([v,l]) => (
                  <option key={v} value={v}>{l}</option>
                ))}
              </select>
            )}
          </div>

          <div style={S.alertScroll}>
            {alerts.length === 0 ? (
              <div style={S.emptyAlerts}>
                <div style={{ fontSize: 28, marginBottom: 8 }}>📡</div>
                <div>กด "สแกนข่าว" เพื่อดึงข่าวล่าสุดจาก Claude AI</div>
                <div style={{ marginTop: 8, color: "#555" }}>หรือเปิด Auto เพื่อสแกนอัตโนมัติ</div>
              </div>
            ) : (
              [...alerts].reverse().map((a) => (
                <div key={a.id} style={S.alertCard(a.impact)}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <span style={S.alertTicker(a.impact)}>{a.ticker}</span>
                    <span style={{ color: "#8b949e", fontSize: 9 }}>{a.ts.split(" ")[1]}</span>
                  </div>
                  <div style={S.alertTitle}>{a.title}</div>
                  {a.summary && <div style={S.alertSummary}>{a.summary}</div>}
                  <div style={S.alertMeta}>
                    <span style={S.badge(impactColor[a.impact] || "#666")}>{a.impact}</span>
                    <span style={S.badge(typeColor[a.type] || "#666")}>{a.type}</span>
                  </div>
                </div>
              ))
            )}
            <div ref={alertsEndRef} />
          </div>

          {/* mini legend */}
          <div style={{ borderTop: "1px solid #21262d", padding: "8px 14px", display: "flex", gap: 10, flexWrap: "wrap" }}>
            {Object.entries(impactColor).filter(([k])=>k!=="SYSTEM").map(([k, v]) => (
              <span key={k} style={{ display: "flex", alignItems: "center", gap: 4, color: "#8b949e", fontSize: 10 }}>
                <span style={{ width: 8, height: 8, borderRadius: 2, background: v, display: "inline-block" }} />
                {k}
              </span>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}
