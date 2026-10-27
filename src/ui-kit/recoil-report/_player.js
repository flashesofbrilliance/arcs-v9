/* ARCS recoil player: draws the belief manifold (34) and the backlog graph (35), and wires a recoil-player page.
   Data comes from  ./scripts/recoil --data <report.json> --format player  and
   python3 scripts/backlog_graph.py --json. No dependencies. Colors come from _tokens.css through CSS classes. */
(function (root) {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";
  var SERIES = ["cyan", "green", "gold", "violet", "magenta", "orange"];
  var LOCK = { locked: "green", pending: "gold", open: "cyan", released: "muted" };

  function el(tag, attrs, parent) {
    var n = document.createElementNS(NS, tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function fmtT(s) { s = Math.round(s); return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0"); }
  /* Signed change in percentage points, true minus sign; dir names the direction for colour and arrow. */
  function pts(a, b) {
    var d = Math.round(b * 100) - Math.round(a * 100);
    return { d: d, dir: d > 0 ? "up" : d < 0 ? "down" : "flat",
             text: d === 0 ? "no change" : (d > 0 ? "+" : "\u2212") + Math.abs(d) + " pts" };
  }
  /* Reversals: a belief whose step changes direction. Returns [{ from: k, at: k }] where point k is
     the first step that runs against the previous non-zero step (k - 1 indexes the beat). */
  function reversals(m) {
    var out = [], prev = 0, prevK = 0;
    for (var k = 1; k < m.points.length; k++) {
      var d = Math.round(m.points[k] * 100) - Math.round(m.points[k - 1] * 100);
      if (!d) continue;
      if (prev && (d > 0) !== (prev > 0)) out.push({ from: prevK, at: k, dir: d > 0 ? "up" : "down" });
      prev = d; prevK = k;
    }
    return out;
  }
  function signed(v) { return (v > 0 ? "+" : v < 0 ? "−" : "") + Math.abs(v).toFixed(2); }

  /* Index of the beat that holds time t (the last beat whose start is at or before t). */
  function beatAt(player, t) {
    var b = player.beats, i = 0;
    for (var k = 0; k < b.length; k++) if (b[k].t_start <= t) i = k;
    return i;
  }
  function duration(player) { var b = player.beats; return b.length ? b[b.length - 1].t_end : 0; }

  /* ---- 34 manifold ------------------------------------------------------------------------------- */
  function Manifold(svg, player) {
    this.svg = svg; this.p = player;
    var W = 640, H = 252, L = 44, R = 150, T = 20, B = 44;
    this.g = { W: W, H: H, L: L, R: R, T: T, B: B };
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    var dur = duration(player) || 1, self = this;
    this.x = function (t) { return L + (W - L - R) * (t / dur); };
    this.y = function (c) { return T + (H - T - B) * (1 - c); };
    [0, 0.5, 1].forEach(function (c) {
      el("line", { "class": "mf-grid", x1: L, x2: W - R, y1: self.y(c), y2: self.y(c) }, svg);
      el("text", { "class": "mf-axis", x: L - 8, y: self.y(c) + 4, "text-anchor": "end" }, svg).textContent = Math.round(c * 100) + "%";
    });
    el("text", { "class": "mf-axis", x: L, y: H - 22 }, svg).textContent = "0:00";
    el("text", { "class": "mf-axis", x: W - R, y: H - 22, "text-anchor": "end" }, svg).textContent = fmtT(dur);
    el("text", { "class": "mf-title", x: L + (W - L - R) / 2, y: H - 4, "text-anchor": "middle" }, svg).textContent = "Time in the call";
    el("text", { "class": "mf-title", x: 0, y: 10 }, svg).textContent = "Confidence: how likely we thought it was true";
    player.beats.forEach(function (b) {
      if (!b.kairos) return;
      var cx = self.x(b.t_end), col = LOCK[b.kairos.lock] || "cyan";
      el("line", { "class": "mf-pin " + col, x1: cx, x2: cx, y1: T, y2: H - B }, svg);
      var d = el("path", { "class": "mf-node " + col, d: "M" + cx + " " + (H - B + 4) + "l6 6-6 6-6-6z" }, svg);
      el("title", {}, d).textContent = b.kairos.label + " (" + b.kairos.lock + ")";
    });
    player.manifold.forEach(function (m, i) {
      var pts = m.points.map(function (c, k) {
        var t = k === 0 ? 0 : player.beats[k - 1].t_end;
        return self.x(t).toFixed(1) + "," + self.y(c).toFixed(1);
      });
      el("polyline", { "class": "mf-line " + SERIES[i % SERIES.length], points: pts.join(" ") }, svg);
    });
    /* direct labels at each line's end, nudged apart so they never overlap */
    var ends = player.manifold.map(function (m, i) { return { i: i, y: self.y(m.points[m.points.length - 1]), m: m }; })
      .sort(function (a, b) { return a.y - b.y; });
    for (var e = 1; e < ends.length; e++) if (ends[e].y - ends[e - 1].y < 26) ends[e].y = ends[e - 1].y + 26;
    ends.forEach(function (o) {
      var t = el("text", { "class": "mf-label " + SERIES[o.i % SERIES.length], x: W - R + 10, y: o.y - 2 }, svg);
      var words = o.m.claim.split(" "), a = [], b = [];
      words.forEach(function (w) { (a.join(" ").length + w.length < 18 && !b.length ? a : b).push(w); });
      el("tspan", { x: W - R + 10 }, t).textContent = a.join(" ");
      if (b.length) el("tspan", { x: W - R + 10, dy: 12 }, t).textContent = b.join(" ");
    });
    this.head = el("line", { "class": "mf-head", y1: T - 6, y2: H - B }, svg);
    this.dots = player.manifold.map(function (m, i) { return el("circle", { "class": "mf-dot " + SERIES[i % SERIES.length], r: 4 }, svg); });
  }
  /* Ring the point where a belief moved most, so a card and its spot on the chart read as one thing. */
  Manifold.prototype.mark = function (k, i) {
    var t = this.p.beats[k - 1].t_end, c = this.p.manifold[i].points[k];
    el("circle", { "class": "mf-ring " + SERIES[i % SERIES.length], cx: this.x(t), cy: this.y(c), r: 7 }, this.svg);
  };
  Manifold.prototype.seek = function (t) {
    var p = this.p, x = this.x(t), self = this;
    this.head.setAttribute("x1", x); this.head.setAttribute("x2", x);
    var k = this.index(t);
    p.manifold.forEach(function (m, i) {
      self.dots[i].setAttribute("cx", x); self.dots[i].setAttribute("cy", self.y(m.points[k]));
    });
  };
  /* Manifold point index at time t: 0 is the prior, i+1 is after beat i ends. */
  Manifold.prototype.index = function (t) {
    var k = 0; this.p.beats.forEach(function (b, i) { if (b.t_end <= t) k = i + 1; });
    return k;
  };

  /* Readout rows: confidence and D1 to D3 at index k. */
  function readout(tbody, player, k) {
    tbody.textContent = "";
    player.manifold.forEach(function (m, i) {
      var tr = document.createElement("tr");
      var ch = pts(m.points[0], m.points[k]);
      var cells = [m.claim, Math.round(m.points[k] * 100) + "%", ch.text, signed(m.D1[k]), signed(m.D2[k]), signed(m.D3[k])];
      cells.forEach(function (c, j) {
        var td = document.createElement(j === 0 ? "th" : "td");
        if (j === 0) { td.scope = "row"; var sw = document.createElement("span"); sw.className = "mf-sw " + SERIES[i % SERIES.length]; td.appendChild(sw); }
        if (j === 2) td.className = "pl-chg " + ch.dir;
        td.appendChild(document.createTextNode(c));
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
  }

  /* ---- 35 backlog graph -------------------------------------------------------------------------- */
  function clusters(nodes) {
    var parent = {};
    function find(a) { while (parent[a] !== a) a = parent[a] = parent[parent[a]]; return a; }
    nodes.forEach(function (n) { parent[n.id] = n.id; });
    nodes.forEach(function (n) { n.deps.forEach(function (d) { if (d in parent) parent[find(d)] = find(n.id); }); });
    var groups = {};
    nodes.forEach(function (n) { var r = find(n.id); (groups[r] = groups[r] || []).push(n.id); });
    return Object.keys(groups).map(function (k) { return groups[k]; }).sort(function (a, b) { return b.length - a.length; });
  }

  /* A cascade: columns are waves (what has to finish first). Click or press Enter on a row to mark it done;
     every row whose last blocker just finished lights up as "Ready now". */
  var WAVE_NAMES = ["Start now", "Next", "Then", "After that", "Last"];
  function BacklogGraph(svg, graph, onChange) {
    var nodes = graph.nodes.filter(function (n) { return n.wave !== null && n.wave !== undefined; });
    var byId = {}, kids = {}, done = {};
    nodes.forEach(function (n) { byId[n.id] = n; kids[n.id] = []; });
    nodes.forEach(function (n) { n.deps.forEach(function (d) { if (d in kids) kids[d].push(n.id); }); });
    var cl = clusters(nodes), cof = {};
    cl.forEach(function (ids, i) { ids.forEach(function (id) { cof[id] = i; }); });
    var waves = {}, maxW = 0;
    nodes.forEach(function (n) { (waves[n.wave] = waves[n.wave] || []).push(n); maxW = Math.max(maxW, n.wave); });
    var CW = 196, NW = 164, NH = 44, RH = 58, T = 34, L = 8, row = {};
    for (var w = 0; w <= maxW; w++) {
      var col = waves[w] || [];
      /* order each column by where its blockers sit, so lines run mostly straight */
      col.forEach(function (n) { n._k = n.deps.length ? n.deps.reduce(function (s, d) { return s + (row[d] || 0); }, 0) / n.deps.length : cof[n.id] * 100 + (n.ready_now ? 0 : 50); });
      col.sort(function (a, b) { return a._k - b._k || (a.id < b.id ? -1 : 1); });
      col.forEach(function (n, r) { row[n.id] = r; });
    }
    var rows = Math.max.apply(null, Object.keys(waves).map(function (k) { return waves[k].length; }));
    var W = L * 2 + CW * (maxW + 1) - (CW - NW), H = T + RH * rows + 8;
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    svg.style.minWidth = W + "px"; /* full size so every row stays a 44px target; the frame scrolls */
    var pos = {};
    Object.keys(waves).forEach(function (k) {
      el("text", { "class": "bg-wave", x: L + CW * k, y: 18 }, svg).textContent = WAVE_NAMES[Math.min(+k, WAVE_NAMES.length - 1)];
      waves[k].forEach(function (n) { pos[n.id] = { x: L + CW * k, y: T + RH * row[n.id] }; });
    });
    var edgeG = el("g", {}, svg), edges = [], gs = {};
    nodes.forEach(function (n) {
      n.deps.forEach(function (d) {
        if (!pos[d]) return;
        var a = pos[d], b = pos[n.id], x1 = a.x + NW, y1 = a.y + NH / 2, x2 = b.x, y2 = b.y + NH / 2, mx = (x1 + x2) / 2;
        edges.push({ from: d, path: el("path", { "class": "bg-edge", d: "M" + x1 + " " + y1 + "C" + mx + " " + y1 + " " + mx + " " + y2 + " " + x2 + " " + y2 }, edgeG) });
      });
    });
    function ready(n) {
      if (done[n.id]) return false;
      if (!n.deps.length) return n.ready_now;
      return n.deps.every(function (d) { return done[d] || !(d in byId); });
    }
    nodes.forEach(function (n) {
      var p = pos[n.id];
      var g = el("g", { "class": "bg-node", transform: "translate(" + p.x + " " + p.y + ")", tabindex: "0", role: "button" }, svg);
      el("rect", { width: NW, height: NH, rx: 3 }, g);
      g._st = el("text", { "class": "bg-cl", x: 10, y: 17 }, g);
      el("text", { "class": "bg-id", x: 10, y: 34 }, g).textContent = n.id.length > 22 ? n.id.slice(0, 21) + "…" : n.id;
      function act() { done[n.id] = !done[n.id]; paint(n.id); }
      g.addEventListener("click", act);
      g.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { act(); e.preventDefault(); } });
      gs[n.id] = g;
    });
    function paint(changed) {
      var fresh = [];
      nodes.forEach(function (n) {
        var g = gs[n.id], r = ready(n), isDone = !!done[n.id], wasReady = g.classList.contains("ready");
        var left = n.deps.filter(function (d) { return !done[d] && d in byId; }).length;
        g.setAttribute("class", "bg-node" + (isDone ? " done" : r ? " ready" : ""));
        g._st.textContent = isDone ? "Done" : r ? "Ready now" : left ? "Waits on " + left : "Not yet ripe";
        if (r && !wasReady && changed) fresh.push(n.id);
        g.setAttribute("aria-label", n.id + ". " + g._st.textContent + "." + (kids[n.id].length ? " Unlocks " + kids[n.id].length + "." : "") + (isDone ? " Press to undo." : " Press to mark done."));
      });
      edges.forEach(function (e) { e.path.setAttribute("class", "bg-edge" + (done[e.from] ? " lit" : "")); });
      if (onChange) onChange(changed, fresh, done);
    }
    paint(null);
    this.clusters = cl; this.kids = kids; this.nodes = nodes; this.waves = maxW + 1; this.done = done;
  }

  /* ---- recoil player page wiring ----------------------------------------------------------------- */
  /* The page answers first (what moved, and the moment that moved it), then offers one action: Play.
     On load it plays the whole call once at max recall and comes to rest at the end; with reduced motion
     it starts at rest. Space plays or pauses, the arrow keys step one moment. */
  function Player(rootEl, player) {
    var q = function (s) { return rootEl.querySelector(s); };
    var dur = duration(player), mf = new Manifold(q("[data-manifold]"), player);
    var LEVELS = ["gist", "moments", "beats", "motion", "full"];
    var state = { t: 0, dir: 1, playing: false, tempo: "max", detail: "beats", last: 0, beat: -1 };
    var scrub = q("[data-scrub]"), playBtn = q("[data-play]"), status = q("[data-status]");
    var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
    scrub.max = String(Math.round(dur));
    function at(level) { return LEVELS.indexOf(state.detail) >= LEVELS.indexOf(level); }

    /* The decision first: the next move, how sure, what it hinges on, and what would flip it. */
    var dec = q("[data-decide]");
    if (dec && player.decision) {
      var D = player.decision, claimOf = function (id) { var m = player.manifold.filter(function (x) { return x.belief === id; })[0]; return m; };
      var h = claimOf(D.hinges_on), F = player.flip, fm = F && claimOf(F.belief);
      var html = '<div class="pl-dec-main"><span class="pl-crumb"><span>Next move</span>' +
        (D.confidence != null ? '<span>Confidence ' + Math.round(D.confidence * 100) + '%</span>' : '') +
        (D.conviction ? '<span>Conviction ' + D.conviction.toLowerCase() + '</span>' : '') + '</span>' +
        '<p class="pl-dec-move"></p>' + (h ? '<p class="pl-dec-hinge"></p>' : '') + '</div>';
      if (F && fm) html += '<div class="pl-dec-flip"><span class="pl-crumb"><span>What would change it</span></span><p class="pl-dec-if"><b></b> <span></span></p><p class="pl-dec-need"></p></div>';
      dec.innerHTML = html;
      dec.querySelector(".pl-dec-move").textContent = D.move;
      if (h) dec.querySelector(".pl-dec-hinge").textContent = "Hinges on: " + h.claim + ", now " + Math.round(h.points[h.points.length - 1] * 100) + "%";
      if (F && fm) {
        var cur = fm.points[fm.points.length - 1], tgt = clamp(cur + F.delta_pts / 100, 0, 1), fc = pts(cur, tgt);
        var b = dec.querySelector(".pl-dec-if b"); b.textContent = fc.text; b.className = "pl-chg " + fc.dir;
        dec.querySelector(".pl-dec-if span").textContent = "on " + fm.claim + " (" + Math.round(cur * 100) + "% \u2192 " + Math.round(tgt * 100) + "%)";
        dec.querySelector(".pl-dec-need").textContent = "Listen for: " + F.would_need;
      }
      dec.hidden = false;
    }
    var revBeat = {}; /* beat index -> [{ claim, dir }] for the moment rows */
    player.manifold.forEach(function (m) { reversals(m).forEach(function (r) { (revBeat[r.at - 1] = revBeat[r.at - 1] || []).push({ m: m, dir: r.dir }); }); });

    /* The answer, in time order: for each belief, the moment that moved it most, what was heard, and the move. */
    var ans = q("[data-answer]"), cards = [];
    player.manifold.forEach(function (m, i) {
      var k = 1, big = 0;
      for (var j = 1; j < m.points.length; j++) { var d = Math.abs(m.points[j] - m.points[j - 1]); if (d > big) { big = d; k = j; } }
      cards.push({ m: m, i: i, k: k, b: player.beats[k - 1] });
    });
    cards.sort(function (x, y) { return x.b.t_start - y.b.t_start; });
    cards.forEach(function (c) {
      var m = c.m, b = c.b, first = m.points[0], last = m.points[m.points.length - 1];
      var f = Math.round(first * 100), t = Math.round(last * 100), lo = Math.min(f, t), hi = Math.max(f, t), ch = pts(first, last);
      var move = f + "% → " + t + "%";
      var li = document.createElement("li"), btn = document.createElement("button");
      btn.type = "button"; btn.className = "pl-ans " + SERIES[c.i % SERIES.length] + " " + ch.dir;
      btn.innerHTML = '<span class="pl-ans-t"><span></span><span></span><span class="pl-ruler" aria-hidden="true"><i></i></span></span><q class="pl-ans-q"></q>' +
        '<span class="pl-ans-claim"><span class="mf-sw ' + SERIES[c.i % SERIES.length] + '"></span><span></span></span>' +
        '<span class="pl-ans-delta"><b></b><span></span></span>' +
        '<span class="pl-move" aria-hidden="true"><span class="pl-move-track"><span class="pl-move-seg"></span><span class="pl-move-tail"></span><span class="pl-move-head"></span></span></span>';
      btn.querySelector(".pl-ans-delta b").textContent = ch.text; /* sign with the colour, never colour alone */
      var tt = btn.querySelectorAll(".pl-ans-t span");
      tt[0].textContent = fmtT(b.t_start); tt[1].textContent = b.speaker;
      btn.querySelector(".pl-ruler i").style.left = (100 * b.t_start / dur).toFixed(1) + "%";
      mf.mark(c.k, c.i); /* the same moment, ringed on the chart */
      btn.querySelector(".pl-ans-q").textContent = b.evidence || b.summary;
      btn.querySelector(".pl-ans-claim span:last-child").textContent = m.claim;
      var rv = reversals(m);
      if (rv.length) {
        var r0 = rv[0], cr = document.createElement("span"); cr.className = "pl-crumb pl-rev";
        var bt1 = player.beats[r0.from - 1], bt2 = player.beats[r0.at - 1];
        [["Reversed", "lock " + (r0.dir === "up" ? "green" : "red")],
         [(r0.dir === "up" ? "fell" : "rose") + " to " + Math.round(m.points[r0.from] * 100) + "% at " + fmtT(bt1.t_start), ""],
         [(r0.dir === "up" ? "rose" : "fell") + " to " + Math.round(m.points[r0.at] * 100) + "% at " + fmtT(bt2.t_start), ""]].forEach(function (x) {
          var sp = document.createElement("span"); sp.textContent = x[0]; if (x[1]) sp.className = x[1]; cr.appendChild(sp);
        });
        if (rv.length > 1) { var more = document.createElement("span"); more.textContent = "+" + (rv.length - 1) + " more"; cr.appendChild(more); }
        btn.querySelector(".pl-ans-claim").after(cr);
      }
      btn.querySelector(".pl-ans-delta span").textContent = move;
      btn.querySelector(".pl-move-seg").style.cssText = "left:" + lo + "%;width:" + (hi - lo) + "%";
      btn.querySelector(".pl-move-tail").style.left = f + "%";
      btn.querySelector(".pl-move-head").style.left = t + "%";
      btn.setAttribute("aria-label", fmtT(b.t_start) + ", " + b.speaker + ": " + (b.evidence || b.summary) + ". " + m.claim + ", " + ch.text + ", " + move + ". Jump there.");
      btn.addEventListener("click", function () { stop(); seek(b.t_start + 0.01); rowEls[c.k - 1].focus(); });
      c.el = btn;
      li.appendChild(btn); ans.appendChild(li);
    });

    /* The moments: the call as readable rows. The current row opens to show its detail. */
    var list = q("[data-moments]"), rowEls = [];
    player.beats.forEach(function (b, i) {
      var li = document.createElement("li"), btn = document.createElement("button");
      btn.type = "button"; btn.className = "pl-row" + (b.kairos ? " key" : "");
      btn.addEventListener("click", function () { stop(); seek(b.t_start + 0.01); });
      li.appendChild(btn); list.appendChild(li); rowEls.push(btn);
    });
    function paintRows() {
      player.beats.forEach(function (b, i) {
        var btn = rowEls[i], cur = i === state.beat;
        if (!at("moments") && !b.kairos && !cur && state.detail === "gist") { btn.parentNode.hidden = true; return; }
        btn.parentNode.hidden = false;
        btn.setAttribute("aria-current", cur ? "true" : "false");
        var mi = -1, best = 0; /* the row takes the colour of the belief this moment moved most */
        (b.belief_deltas || []).forEach(function (x) {
          player.manifold.forEach(function (mm, j) {
            if (mm.belief !== x.belief) return;
            var d = Math.abs(x.to - mm.points[i]); if (d > best) { best = d; mi = j; }
          });
        });
        /* hierarchy by size of move: a moment that moved a belief a lot, or a key moment, reads in full;
           a quiet moment collapses to one muted line unless it is the current one */
        var major = best >= 0.15 || !!b.kairos || !!revBeat[i], open = major || cur;
        btn.className = "pl-row " + (major ? "major" : "minor") + (mi >= 0 ? " " + SERIES[mi % SERIES.length] : "");
        btn.textContent = "";
        var t = document.createElement("span"); t.className = "pl-row-t"; t.textContent = fmtT(b.t_start); btn.appendChild(t);
        var body = document.createElement("span"); body.className = "pl-row-b"; btn.appendChild(body);
        if (b.kairos && at("moments")) {
          var cr = document.createElement("span"); cr.className = "pl-crumb";
          [["Key moment", ""], [b.kairos.label, ""], [b.kairos.lock, "lock " + (LOCK[b.kairos.lock] || "cyan")]].forEach(function (x) {
            var sp = document.createElement("span"); sp.textContent = x[0]; if (x[1]) sp.className = x[1]; cr.appendChild(sp);
          });
          body.appendChild(cr);
        }
        (revBeat[i] || []).forEach(function (r) {
          var rc = document.createElement("span"); rc.className = "pl-crumb pl-rev";
          [["Reversal", "lock " + (r.dir === "up" ? "green" : "red")], [r.m.claim, ""], [r.dir === "up" ? "turned up" : "turned down", ""]].forEach(function (x) {
            var sp = document.createElement("span"); sp.textContent = x[0]; if (x[1]) sp.className = x[1]; rc.appendChild(sp);
          });
          body.appendChild(rc);
        });
        if (open && at("beats") && b.evidence) { var e = document.createElement("q"); e.className = "pl-quote"; e.textContent = b.evidence; body.appendChild(e); }
        var sum = document.createElement("span"); sum.className = "pl-row-s";
        sum.textContent = (at("beats") ? b.speaker + ": " : "") + b.summary; body.appendChild(sum);
        if (open && at("beats") && b.belief_deltas) b.belief_deltas.forEach(function (x) {
          player.manifold.forEach(function (mm, j) {
            if (mm.belief !== x.belief) return;
            var ch = pts(mm.points[i], x.to);
            var d = document.createElement("span"); d.className = "pl-delta " + ch.dir;
            var nb = document.createElement("b"); nb.textContent = ch.text;
            d.appendChild(nb);
            d.appendChild(document.createTextNode(" " + mm.claim + ", " + Math.round(mm.points[i] * 100) + "% → " + Math.round(x.to * 100) + "%"));
            body.appendChild(d);
          });
        });
      });
      var rw = q("[data-readout-wrap]"); if (rw) rw.hidden = !at("motion");
    }

    function rate() {
      if (state.tempo === "max") return dur / 8;
      if (state.tempo === "real") return 1;
      var b = player.beats[beatAt(player, state.t)];
      return (b.t_end - b.t_start) / (b.kairos ? 12 : 6);
    }
    function seek(t) {
      state.t = clamp(t, 0, dur);
      scrub.value = String(Math.round(state.t));
      scrub.setAttribute("aria-valuetext", fmtT(state.t) + " of " + fmtT(dur));
      mf.seek(state.t);
      var i = beatAt(player, state.t);
      if (i !== state.beat) { state.beat = i; paintRows(); cards.forEach(function (c) { c.el.classList.toggle("on", c.k - 1 === i); }); }
      readout(q("[data-readout]"), player, mf.index(state.t));
      q("[data-clock]").textContent = fmtT(state.t) + " of " + fmtT(dur);
      status.textContent = "Moment " + (i + 1) + " of " + player.beats.length + ": " + player.beats[i].summary;
    }
    function frame(now) {
      if (!state.playing) return;
      var dt = Math.min(0.1, (now - state.last) / 1000); state.last = now;
      if (reduce) { /* no sweep: hold each moment, then jump to the next */
        state.hold = (state.hold || 0) + dt;
        if (state.hold < 1.6) return requestAnimationFrame(frame);
        state.hold = 0; var n = beatAt(player, state.t) + state.dir;
        if (n < 0 || n >= player.beats.length) { seek(state.dir > 0 ? dur : 0); return stop(); }
        seek(player.beats[n].t_start + 0.01);
      } else seek(state.t + state.dir * rate() * dt);
      if ((state.dir > 0 && state.t >= dur) || (state.dir < 0 && state.t <= 0)) return stop();
      requestAnimationFrame(frame);
    }
    function start() {
      if (state.dir > 0 && state.t >= dur) seek(0);
      if (state.dir < 0 && state.t <= 0) seek(dur);
      state.playing = true; state.last = performance.now(); state.hold = 0;
      playBtn.textContent = "Pause"; playBtn.setAttribute("aria-pressed", "true");
      requestAnimationFrame(frame);
    }
    function stop() { state.playing = false; playBtn.textContent = state.t >= dur && state.dir > 0 ? "Replay" : "Play"; playBtn.setAttribute("aria-pressed", "false"); }
    function toggle() { state.playing ? stop() : start(); }
    function step(n) { stop(); var i = clamp(beatAt(player, state.t) + n, 0, player.beats.length - 1); seek(player.beats[i].t_start + 0.01); }

    playBtn.addEventListener("click", toggle);
    q("[data-back]").addEventListener("click", function () { step(-1); });
    q("[data-fwd]").addEventListener("click", function () { step(1); });
    scrub.addEventListener("input", function () { stop(); seek(+scrub.value); });
    rootEl.querySelectorAll("[name=tempo]").forEach(function (r) { r.addEventListener("change", function () { state.tempo = r.value; }); });
    rootEl.querySelectorAll("[name=dir]").forEach(function (r) { r.addEventListener("change", function () { state.dir = +r.value; }); });
    rootEl.querySelectorAll("[name=detail]").forEach(function (r) { r.addEventListener("change", function () { state.detail = r.value; paintRows(); }); });
    document.addEventListener("keydown", function (e) {
      if (e.target.matches("input, textarea, select") || e.metaKey || e.ctrlKey || e.altKey) return;
      if (e.key === " " && !e.target.matches("button")) { toggle(); e.preventDefault(); }
      if (e.key === "ArrowRight") { step(1); e.preventDefault(); }
      if (e.key === "ArrowLeft") { step(-1); e.preventDefault(); }
    });
    seek(0); paintRows();
    if (reduce) { seek(dur); stop(); } else start(); /* the page moves on load, then rests on the answer */
  }

  root.ArcsRecoil = { Manifold: Manifold, BacklogGraph: BacklogGraph, Player: Player, readout: readout, clusters: clusters };
})(window);
