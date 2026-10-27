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

  function BacklogGraph(svg, graph) {
    var nodes = graph.nodes.filter(function (n) { return n.wave !== null && n.wave !== undefined; });
    var byId = {}, kids = {};
    nodes.forEach(function (n) { byId[n.id] = n; kids[n.id] = 0; });
    nodes.forEach(function (n) { n.deps.forEach(function (d) { if (d in kids) kids[d]++; }); });
    var cl = clusters(nodes), cof = {};
    cl.forEach(function (ids, i) { ids.forEach(function (id) { cof[id] = i; }); });
    var waves = {};
    nodes.forEach(function (n) { (waves[n.wave] = waves[n.wave] || []).push(n); });
    Object.keys(waves).forEach(function (w) { waves[w].sort(function (a, b) { return cof[a.id] - cof[b.id] || (a.id < b.id ? -1 : 1); }); });
    var nw = Object.keys(waves).length, rows = Math.max.apply(null, Object.keys(waves).map(function (w) { return waves[w].length; }));
    var CW = 196, NW = 160, NH = 36, RH = 52, T = 34, L = 8;
    var W = L * 2 + CW * nw - (CW - NW), H = T + RH * rows + 8;
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    svg.style.minWidth = Math.min(W, 560) + "px";
    var pos = {};
    Object.keys(waves).forEach(function (w) {
      el("text", { "class": "bg-wave", x: L + CW * w, y: 18 }, svg).textContent = "Wave " + w + (w === "0" ? ", now" : "");
      waves[w].forEach(function (n, r) { pos[n.id] = { x: L + CW * w, y: T + RH * r }; });
    });
    var edges = el("g", {}, svg);
    nodes.forEach(function (n) {
      n.deps.forEach(function (d) {
        if (!pos[d]) return;
        var a = pos[d], b = pos[n.id], x1 = a.x + NW, y1 = a.y + NH / 2, x2 = b.x, y2 = b.y + NH / 2, mx = (x1 + x2) / 2;
        el("path", { "class": "bg-edge", d: "M" + x1 + " " + y1 + "C" + mx + " " + y1 + " " + mx + " " + y2 + " " + x2 + " " + y2 }, edges);
      });
    });
    nodes.forEach(function (n) {
      var p = pos[n.id], cls = "bg-node" + (n.ready_now ? " ready" : "") + (kids[n.id] > 1 ? " branch" : "");
      var g = el("g", { "class": cls, transform: "translate(" + p.x + " " + p.y + ")" }, svg);
      el("rect", { width: NW, height: NH, rx: 3 }, g);
      el("text", { "class": "bg-cl", x: 8, y: 14 }, g).textContent = String.fromCharCode(65 + cof[n.id]) + "  " + n.state.toLowerCase();
      var label = n.id.length > 22 ? n.id.slice(0, 21) + "…" : n.id;
      el("text", { "class": "bg-id", x: 8, y: 29 }, g).textContent = label;
      if (kids[n.id] > 1) el("circle", { "class": "bg-fork", cx: NW - 10, cy: 10, r: 4 }, g);
      el("title", {}, g).textContent = n.id + ", wave " + n.wave + ", " + n.state + ", tool " + n.tool + (n.ready_now ? ", can start now" : "") + (kids[n.id] > 1 ? ", branches to " + kids[n.id] + " rows" : "");
    });
    this.clusters = cl; this.kids = kids; this.nodes = nodes; this.waves = nw;
  }

  /* ---- recoil player page wiring ----------------------------------------------------------------- */
  function Player(rootEl, player) {
    var q = function (s) { return rootEl.querySelector(s); };
    var dur = duration(player), mf = new Manifold(q("[data-manifold]"), player);
    var state = { t: 0, dir: 1, playing: false, tempo: "real", detail: "beats", last: 0, beat: -1 };
    var scrub = q("[data-scrub]"), status = q("[data-status]"), playBtn = q("[data-play]");
    scrub.max = String(Math.round(dur));
    var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) playBtn.hidden = true;
    var LEVELS = ["gist", "moments", "beats", "motion", "full"];
    function at(level) { return LEVELS.indexOf(state.detail) >= LEVELS.indexOf(level); }

    var track = q("[data-track]");
    track.style.gridTemplateColumns = "64px repeat(" + player.beats.length + ", minmax(44px, 1fr))";
    track.style.minWidth = (64 + player.beats.length * 48) + "px";
    player.beats.forEach(function (b, i) {
      var btn = document.createElement("button");
      btn.type = "button"; btn.className = "sq" + (b.kairos ? " b" : ""); btn.textContent = String(i + 1);
      btn.setAttribute("aria-label", "Beat " + (i + 1) + ", " + b.speaker + (b.kairos ? ", kairos: " + b.kairos.label : ""));
      btn.addEventListener("click", function () { stop(); seek(b.t_start); });
      track.appendChild(btn);
    });
    var cells = track.querySelectorAll(".sq");

    function rate() {
      if (state.tempo === "max") return dur / 8;
      if (state.tempo === "real") return 1;
      var b = player.beats[beatAt(player, state.t)], len = b.t_end - b.t_start;
      return len / (b.kairos ? 12 : 6); /* slow mo dwells: 6 s a beat, 12 s on a kairos beat */
    }
    function seek(t) {
      state.t = clamp(t, 0, dur);
      scrub.value = String(Math.round(state.t));
      scrub.setAttribute("aria-valuetext", fmtT(state.t) + " of " + fmtT(dur));
      mf.seek(state.t);
      var i = beatAt(player, state.t);
      cells.forEach(function (c, k) { c.classList.toggle("now", k === i); c.setAttribute("aria-pressed", String(k === i)); });
      if (i !== state.beat) { state.beat = i; renderBeat(i); }
      readout(q("[data-readout]"), player, mf.index(state.t));
      q("[data-clock]").textContent = fmtT(state.t) + " / " + fmtT(dur);
    }
    function renderBeat(i) {
      var b = player.beats[i], box = q("[data-beat]");
      var rw = q("[data-readout-wrap]"); if (rw) rw.hidden = !at("motion");
      box.textContent = "";
      var head = document.createElement("div"); head.className = "pl-beat-head";
      var num = document.createElement("span"); num.className = "chip" + (b.kairos ? " " + (LOCK[b.kairos.lock] || "cyan") : ""); num.textContent = "Beat " + (i + 1);
      head.appendChild(num);
      if (at("beats")) { var who = document.createElement("span"); who.className = "ref"; who.textContent = b.speaker + ", " + fmtT(b.t_start) + " to " + fmtT(b.t_end); head.appendChild(who); }
      box.appendChild(head);
      var p = document.createElement("p"); p.className = "pl-summary"; p.textContent = b.summary; box.appendChild(p);
      if (b.kairos && at("moments")) {
        var k = document.createElement("p"); k.className = "led " + (b.kairos.lock === "locked" ? "on" : "");
        k.textContent = "Kairos: " + b.kairos.label + ". Write-lock " + b.kairos.lock + ".";
        box.appendChild(k);
      }
      if (at("full") && b.evidence) { var e = document.createElement("blockquote"); e.className = "pl-quote"; e.textContent = "“" + b.evidence + "”"; box.appendChild(e); }
      if (at("beats") && b.belief_deltas && b.belief_deltas.length) {
        var ul = document.createElement("ul"); ul.className = "pl-deltas";
        b.belief_deltas.forEach(function (x) {
          var m = player.manifold.filter(function (mm) { return mm.belief === x.belief; })[0];
          var li = document.createElement("li"); li.textContent = (m ? m.claim : x.belief) + ": now " + Math.round(x.to * 100) + "%";
          ul.appendChild(li);
        });
        box.appendChild(ul);
      }
    }
    function frame(now) {
      if (!state.playing) return;
      var dt = Math.min(0.1, (now - state.last) / 1000); state.last = now;
      seek(state.t + state.dir * rate() * dt);
      if ((state.dir > 0 && state.t >= dur) || (state.dir < 0 && state.t <= 0)) { stop(); say(state.dir > 0 ? "End of call." : "Back at the start."); return; }
      requestAnimationFrame(frame);
    }
    function start(dir) {
      state.dir = dir; state.playing = true; state.last = performance.now();
      if (dir > 0 && state.t >= dur) seek(0);
      if (dir < 0 && state.t <= 0) seek(dur);
      playBtn.textContent = "Pause"; playBtn.setAttribute("aria-pressed", "true");
      say(dir > 0 ? "Playing forward." : "Playing in reverse.");
      requestAnimationFrame(frame);
    }
    function stop() { state.playing = false; playBtn.textContent = "Play"; playBtn.setAttribute("aria-pressed", "false"); }
    function say(s) { status.textContent = s; }
    function step(n) { stop(); var i = clamp(beatAt(player, state.t) + n, 0, player.beats.length - 1); seek(player.beats[i].t_start); say("Beat " + (i + 1) + " of " + player.beats.length + "."); }

    var wantDir = 1;
    playBtn.addEventListener("click", function () { state.playing ? (stop(), say("Paused.")) : start(wantDir); });
    rootEl.querySelectorAll("[name=dir]").forEach(function (r) {
      r.addEventListener("change", function () { wantDir = +r.value; if (state.playing) start(wantDir); });
    });
    q("[data-back]").addEventListener("click", function () { step(-1); });
    q("[data-fwd]").addEventListener("click", function () { step(1); });
    scrub.addEventListener("input", function () { stop(); seek(+scrub.value); });
    rootEl.querySelectorAll("[name=tempo]").forEach(function (r) { r.addEventListener("change", function () { state.tempo = r.value; }); });
    rootEl.querySelectorAll("[name=detail]").forEach(function (r) {
      r.addEventListener("change", function () {
        state.detail = r.value; renderBeat(state.beat);
        rootEl.querySelectorAll(".rung").forEach(function (f) { f.classList.toggle("on", f.contains(r)); });
      });
    });
    rootEl.addEventListener("keydown", function (e) {
      if (e.target.matches("input[type=range], input[type=radio], button")) return;
      if (e.key === "ArrowRight") { step(1); e.preventDefault(); }
      if (e.key === "ArrowLeft") { step(-1); e.preventDefault(); }
    });
    drawRungs(rootEl, player);
    seek(0);
    say(reduce ? "Ready. Step with Back and Forward, the beat track, or the scrubber."
               : "Ready. Set direction and speed, then Play.");
  }

  /* Resolution ladder previews: the same manifold at three detail levels. */
  function drawRungs(rootEl, player) {
    var css = getComputedStyle(document.documentElement);
    rootEl.querySelectorAll(".rung canvas").forEach(function (cv) {
      var level = cv.getAttribute("data-level"), c = cv.getContext("2d"), w = cv.width, h = cv.height;
      c.fillStyle = css.getPropertyValue("--bg"); c.fillRect(0, 0, w, h);
      player.manifold.forEach(function (m, i) {
        var pts = level === "gist" ? [m.points[0], m.points[m.points.length - 1]]
          : level === "moments" ? [m.points[0]].concat(player.beats.map(function (b, k) { return b.kairos ? m.points[k + 1] : null; }).filter(function (v) { return v !== null; }), [m.points[m.points.length - 1]])
          : m.points;
        c.strokeStyle = css.getPropertyValue("--" + SERIES[i % SERIES.length]); c.lineWidth = 2; c.beginPath();
        pts.forEach(function (v, k) { var x = 6 + (w - 12) * k / (pts.length - 1), y = 6 + (h - 12) * (1 - v); k ? c.lineTo(x, y) : c.moveTo(x, y); });
        c.stroke();
        if (level === "full") pts.forEach(function (v, k) { c.fillStyle = c.strokeStyle; c.fillRect(6 + (w - 12) * k / (pts.length - 1) - 1.5, 6 + (h - 12) * (1 - v) - 1.5, 3, 3); });
      });
      if (level === "motion" || level === "full") {
        var dur = duration(player);
        player.beats.forEach(function (b) {
          if (!b.kairos) return;
          c.fillStyle = css.getPropertyValue("--" + (LOCK[b.kairos.lock] === "muted" ? "muted" : LOCK[b.kairos.lock])); c.fillRect(6 + (w - 12) * b.t_end / dur - 1, h - 8, 3, 6);
        });
      }
    });
  }

  root.ArcsRecoil = { Manifold: Manifold, BacklogGraph: BacklogGraph, Player: Player, readout: readout, clusters: clusters };
})(window);
