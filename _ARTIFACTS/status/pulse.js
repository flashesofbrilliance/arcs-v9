/* Live pulse. Every number comes from app.arcs.care/api/pulse, which reads the PRIVATE
   repo server-side (token never reaches the browser) and returns counts only. A section
   the server could not read arrives as null and is listed in p.degraded: the static floor
   in the HTML stays and a small "degraded" tag shows. Never a false zero. */
(function () {
  var PULSE = "https://app.arcs.care/api/pulse";
  function $(id) { return document.getElementById(id); }
  function set(id, txt) { var e = $(id); if (e) e.textContent = txt; }
  function tag(id, on) { var e = $(id); if (e) e.classList.toggle("on", !!on); }
  function rel(iso) {
    var s = Math.max(0, (Date.now() - Date.parse(iso)) / 1000);
    if (s < 60) return "just now";
    if (s < 3600) return Math.floor(s / 60) + "m ago";
    if (s < 86400) return Math.floor(s / 3600) + "h ago";
    return Math.floor(s / 86400) + "d ago";
  }
  function applyDebt(d) {
    var ship = d.byStatus.done, ip = d.byStatus["in-progress"], bl = d.byStatus.decision, nx = d.byStatus.open;
    var total = ship + ip + bl + nx;
    [["ship", ship], ["prog", ip], ["block", bl], ["next", nx]].forEach(function (x) {
      set("su-lead-" + x[0], x[1]); set("su-lab-" + x[0], x[1]); set("su-z-" + x[0], x[1]);
      var e = $("su-bar-" + x[0]); if (e) e.style.width = (total ? (x[1] / total * 100).toFixed(1) : 0) + "%";
    });
    set("su-lead-total", total);
    set("su-stamp", "Live from the issue tracker by status label · shipped is cumulative · as of " + new Date().toLocaleTimeString());
  }
  // Card items: curated public labels grouped by live status (PUBLIC_ITEMS in src/lib/pulse.ts). Never an issue title.
  var CARD = { decision: "block", open: "next", "in-progress": "prog", done: "ship" };
  function applyItems(items) {
    Object.keys(CARD).forEach(function (k) {
      var ul = $("su-items-" + CARD[k]), arr = items[k]; if (!ul || !Array.isArray(arr)) return;
      ul.textContent = "";
      (arr.length ? arr : ["Nothing in this state."]).forEach(function (x) {
        var li = document.createElement("li"); li.className = "su-zli" + (arr.length ? "" : " su-none"); li.textContent = x; ul.appendChild(li);
      });
    });
  }
  var SEV = { P1: ["high", "HIGH"], P2: ["med", "MED"], P3: ["low", "LOW"] };
  var ST = { open: ["open", "OPEN"], "in-progress": ["gated", "IN PROGRESS"], decision: ["open", "AWAITING DECISION"], done: ["mit", "RESOLVED"] };
  function applyRisks(r) {
    document.querySelectorAll("tr[data-risk]").forEach(function (tr) {
      var v = r[tr.getAttribute("data-risk")]; if (!v) return;
      var a = SEV[v.sev], b = ST[v.status];
      var sev = tr.querySelector('[data-r="sev"]'), st = tr.querySelector('[data-r="status"]');
      if (a && sev) { sev.className = "chip " + a[0]; sev.textContent = a[1]; }
      if (b && st) { st.className = "chip " + b[0]; st.textContent = b[1]; }
    });
  }
  function drawTempo(rows) {
    var el = $("tempo-live"); if (!el || !rows || !rows.length) return;
    var max = Math.max.apply(null, rows.map(function (r) { return r[1]; })) || 1;
    el.textContent = "";
    rows.forEach(function (r) {
      var col = document.createElement("div"); col.className = "cad-col";
      var n = document.createElement("div"); n.className = "cad-n"; n.textContent = r[1] > 0 ? r[1] : "";
      var bar = document.createElement("div");
      bar.className = "cad-bar" + (r[1] === max ? " peak" : r[1] === 0 ? " zero" : "");
      bar.style.height = r[1] === 0 ? "2px" : Math.max(4, Math.round((r[1] / max) * 58)) + "px";
      bar.title = r[1] + " merged · week of " + r[0];
      var w = document.createElement("div"); w.className = "cad-w";
      w.textContent = new Date(r[0] + "T00:00:00Z").toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" }).toUpperCase();
      col.appendChild(n); col.appendChild(bar); col.appendChild(w); el.appendChild(col);
    });
  }
  (function () { var el = $("tempo-live"); if (el) { try { drawTempo(JSON.parse(el.getAttribute("data-floor"))); } catch (e) {} } })();
  function setAll(sel, v) { document.querySelectorAll(sel).forEach(function (e) { e.textContent = v; }); }
  // Exposed for the degraded-path test (tests/status-pulse.spec.ts); paint has no network.
  var paint = window.__paintPulse = function (p) {
    var bad = (p && p.degraded) || [];
    if (p.commit) { set("pl-commit", p.commit.sha); set("pl-commit-when", rel(p.commit.date)); }
    if (typeof p.commitsTotal === "number" && p.commitsTotal > 0) { var n = p.commitsTotal.toLocaleString(); set("pl-count", n); set("sv-commits", n); }
    if (typeof p.prsOpen === "number") { set("pl-prs", String(p.prsOpen)); set("pl-prs-sub", "open on main"); }
    if (p.deploy) { set("pl-deploy", String(p.deploy.state).toUpperCase()); set("pl-deploy-when", rel(p.deploy.date)); var e = $("pl-deploy"); if (e) e.style.color = p.deploy.state === "success" ? "var(--green)" : (p.deploy.state === "failure" || p.deploy.state === "error") ? "var(--red)" : "var(--gold)"; }
    tag("dg-pulse", !p.commit || !p.deploy || typeof p.prsOpen !== "number");
    var debtOk = p.debt && p.debt.total > 0 && p.debt.byStatus;
    if (debtOk) applyDebt(p.debt);
    if (p.items) applyItems(p.items);
    tag("dg-su", !debtOk || !p.items);
    if (p.risks) applyRisks(p.risks);
    tag("dg-risk", !p.risks);
    var tempoOk = p.tempo && p.tempo.length && p.tempo.some(function (w) { return w.merges > 0; });
    if (tempoOk) { drawTempo(p.tempo.map(function (w) { return [w.week, w.merges]; })); set("tempo-src", "LIVE"); }
    tag("dg-tempo", !tempoOk);
    var g = p.gates;
    if (g && g.calibration && g.goalMap) { setAll('[data-g="cal"]', g.calibration.n); setAll('[data-g="goal"]', g.goalMap.n); }
    tag("dg-gates", !(g && g.calibration && g.goalMap));
    if (p.evals) Object.keys(p.evals).forEach(function (k) { var e = document.querySelector('[data-eval="' + k + '"]'); if (e && p.evals[k]) e.textContent = String(p.evals[k]).toUpperCase(); });
    return bad;
  };
  function degradeAll(msg) {
    ["dg-pulse", "dg-su", "dg-risk", "dg-tempo", "dg-gates"].forEach(function (id) { tag(id, true); });
    ["pl-commit", "pl-deploy", "pl-prs", "pl-count"].forEach(function (id) { var e = $(id); if (e && /loading/.test(e.textContent)) e.textContent = "n/a"; });
    set("pulse-foot", msg);
  }
  async function all() {
    var rb = $("pulse-refresh"); if (rb) { rb.disabled = true; rb.setAttribute("aria-busy", "true"); }
    try {
      var r = await fetch(PULSE, { cache: "no-store" });
      if (!r.ok) throw 0;
      var p = await r.json();
      if (!p || p.ok === false) throw 0;
      paint(p);
      var t = p.updated ? new Date(p.updated) : null;
      set("pulse-foot", (t ? "data as of " + t.toLocaleString() : "updated") + " · cached ≤10 min · checked " + new Date().toLocaleTimeString());
    } catch (e) {
      degradeAll("live read unavailable · showing the last stamped floor · checked " + new Date().toLocaleTimeString());
    }
    finally { if (rb) { rb.disabled = false; rb.removeAttribute("aria-busy"); } }
  }
  // Live day-count from T0 (first commit day, 2026-04-09), counted in CALENDAR
  // days on America/New_York (ET) so it rolls over at ET midnight regardless of
  // the viewer's timezone… not at the commit's time of day. Pure date math, no
  // network. Also stamps the current ET wall-clock next to the era head.
  (function () {
    function etYMD(d) {
      // "YYYY-MM-DD" for the given instant in ET (handles EST/EDT automatically)
      return new Intl.DateTimeFormat("en-CA", { timeZone: "America/New_York",
        year: "numeric", month: "2-digit", day: "2-digit" }).format(d);
    }
    var todayET = etYMD(new Date());
    var t0 = Date.parse("2026-04-09T00:00:00Z");
    var today = Date.parse(todayET + "T00:00:00Z");
    var days = Math.max(0, Math.round((today - t0) / 86400000));
    set("stat-days", days); set("era-day", days); set("hero-day", days);
    var stamp = new Intl.DateTimeFormat("en-US", { timeZone: "America/New_York",
      month: "short", day: "numeric", year: "numeric",
      hour: "numeric", minute: "2-digit" }).format(new Date());
    // Intl gives the correct EST/EDT offset; label it "ET" so we're never wrong.
    set("et-now", stamp + " ET");
  })();
  all();
  var btn = $("pulse-refresh"); if (btn) btn.addEventListener("click", all);
  document.addEventListener("visibilitychange", function () { if (!document.hidden) all(); });
  setInterval(all, 120000);
})();
