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
    var W = 640, H = 240, L = 44, R = 16, T = 16, B = 40;
    this.g = { W: W, H: H, L: L, R: R, T: T, B: B };
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    var dur = duration(player) || 1, self = this;
    this.x = function (t) { return L + (W - L - R) * (t / dur); };
    this.y = function (c) { return T + (H - T - B) * (1 - c); };
    [0, 0.5, 1].forEach(function (c) {
      el("line", { "class": "mf-grid", x1: L, x2: W - R, y1: self.y(c), y2: self.y(c) }, svg);
      el("text", { "class": "mf-axis", x: L - 8, y: self.y(c) + 4, "text-anchor": "end" }, svg).textContent = Math.round(c * 100) + "%";
    });
    el("text", { "class": "mf-axis", x: L, y: H - 8 }, svg).textContent = "0:00";
    el("text", { "class": "mf-axis", x: W - R, y: H - 8, "text-anchor": "end" }, svg).textContent = fmtT(dur);
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
    this.head = el("line", { "class": "mf-head", y1: T - 6, y2: H - B }, svg);
    this.dots = player.manifold.map(function (m, i) { return el("circle", { "class": "mf-dot " + SERIES[i % SERIES.length], r: 4 }, svg); });
  }
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
      var cells = [m.claim, Math.round(m.points[k] * 100) + "%", signed(m.D1[k]), signed(m.D2[k]), signed(m.D3[k])];
      cells.forEach(function (c, j) {
        var td = document.createElement(j === 0 ? "th" : "td");
        if (j === 0) { td.scope = "row"; var sw = document.createElement("span"); sw.className = "mf-sw " + SERIES[i % SERIES.length]; td.appendChild(sw); }
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
      var move = Math.round(first * 100) + "% → " + Math.round(last * 100) + "%";
      var li = document.createElement("li"), btn = document.createElement("button");
      btn.type = "button"; btn.className = "pl-ans";
      btn.innerHTML = '<span class="pl-ans-t"></span><span class="pl-ans-q"></span><span class="pl-ans-claim"><span class="mf-sw ' + SERIES[c.i % SERIES.length] + '"></span><span></span></span>';
      btn.querySelector(".pl-ans-t").textContent = fmtT(b.t_start) + ", " + b.speaker;
      btn.querySelector(".pl-ans-q").textContent = b.evidence ? "“" + b.evidence + "”" : b.summary;
      btn.querySelector(".pl-ans-claim span:last-child").textContent = m.claim + ": " + move;
      btn.setAttribute("aria-label", fmtT(b.t_start) + ", " + b.speaker + ": " + btn.querySelector(".pl-ans-q").textContent + ". " + m.claim + ", " + move + ". Jump there.");
      btn.addEventListener("click", function () { stop(); seek(b.t_start + 0.01); rowEls[c.k - 1].focus(); });
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
        btn.textContent = "";
        var t = document.createElement("span"); t.className = "pl-row-t"; t.textContent = fmtT(b.t_start); btn.appendChild(t);
        var body = document.createElement("span"); body.className = "pl-row-b"; btn.appendChild(body);
        var sum = document.createElement("span"); sum.className = "pl-row-s";
        sum.textContent = (at("beats") ? b.speaker + ": " : "") + b.summary; body.appendChild(sum);
        if (b.kairos && at("moments")) { var c = document.createElement("span"); c.className = "chip " + (LOCK[b.kairos.lock] || "cyan"); c.textContent = b.kairos.label + ", " + b.kairos.lock; body.appendChild(c); }
        if (cur && at("beats") && b.belief_deltas) b.belief_deltas.forEach(function (x) {
          var m = player.manifold.filter(function (mm) { return mm.belief === x.belief; })[0];
          var d = document.createElement("span"); d.className = "ref"; d.textContent = (m ? m.claim : x.belief) + " now " + Math.round(x.to * 100) + "%"; body.appendChild(d);
        });
        if (at("beats") && b.evidence) { var e = document.createElement("span"); e.className = "pl-quote"; e.textContent = "“" + b.evidence + "”"; body.appendChild(e); }
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
      if (i !== state.beat) { state.beat = i; paintRows(); }
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
