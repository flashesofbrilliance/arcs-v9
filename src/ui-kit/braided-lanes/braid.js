/* ARCS kit organism 72 braided-lanes: reversals as one flat lane per scope, time on x, braided by repaired-by arcs.
   Data: the payload scripts/braided_lanes_build.py writes from runtime/specs/shipped-record.json.
     start   ISO Monday of week 0; weeks = number of weeks; as_of = the record's date
     commits[w]  commits on main in week w; receipts[w]  decision receipts in week w, null where none were recorded
     lanes[]  {key, label, def, n}; events[] [id, lane index, day since start, gold 0|1]; links[] [from, to]
   arcsBraid(host, data, {w0, w1}) replaces host's static floor with the live chart. Stdlib DOM, no deps.
   The window is two native range inputs (arrow keys, Home, End). Each lane is one tab stop; arrow keys move between dots
   (left/right in a lane, up/down across lanes), and the focused, pointed or tapped dot fills a live readout.
   A lane with fewer than 3 events in the window renders as grain and prints n. Nothing animates. */
(function () {
  var NS = "http://www.w3.org/2000/svg", DAY = 864e5, GRAIN_N = 3;
  var MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  function el(tag, attrs, parent) {
    var n = document.createElementNS(NS, tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  function h(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function txt(p, x, y, s, cls, anchor) {
    var t = el("text", { x: x, y: y, class: cls }, p);
    if (anchor) t.setAttribute("text-anchor", anchor);
    t.textContent = s;
    return t;
  }
  function fmtDate(t) { var d = new Date(t); return d.getUTCDate() + " " + MON[d.getUTCMonth()] + " " + d.getUTCFullYear(); }
  function num(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ","); }

  window.arcsBraid = function (host, data, opts) {
    opts = opts || {};
    var t0 = Date.parse(data.start + "T00:00:00Z"), end = Date.parse(data.as_of + "T00:00:00Z") + DAY;
    var last = data.weeks - 1, uid = "bl" + Math.random().toString(36).slice(2, 7);
    var byId = {};
    data.events.forEach(function (e) { byId[e[0]] = e; });
    var repairs = {};
    data.links.forEach(function (l) { (repairs[l[0]] = repairs[l[0]] || []).push(["repaired by", l[1]]); (repairs[l[1]] = repairs[l[1]] || []).push(["repairs", l[0]]); });

    host.textContent = "";
    host.classList.add("braid");
    var svg = el("svg", { role: "group", "aria-labelledby": uid + "t", class: "bl-svg" });
    var title = el("title", { id: uid + "t" }, svg);
    var defs = el("defs", {}, svg);
    var pat = el("pattern", { id: uid + "h", width: 6, height: 6, patternUnits: "userSpaceOnUse", patternTransform: "rotate(45)" }, defs);
    el("line", { x1: 0, y1: 0, x2: 0, y2: 6, class: "bl-hatch" }, pat);
    var gp = el("pattern", { id: uid + "g", width: 4, height: 4, patternUnits: "userSpaceOnUse" }, defs);
    el("circle", { cx: 1, cy: 1, r: 0.7, class: "bl-grain" }, gp);
    el("circle", { cx: 3, cy: 3, r: 0.6, class: "bl-grain" }, gp);
    var g = el("g", {}, svg);
    host.appendChild(svg);

    var brush = h("div", "bl-brush");
    var lab = h("span", "bl-flabel", "Window");
    lab.id = uid + "wl";
    brush.appendChild(lab);
    function range(val, name) {
      var i = document.createElement("input");
      i.type = "range"; i.min = 0; i.max = last; i.step = 1; i.value = val;
      i.setAttribute("aria-label", name);
      i.setAttribute("aria-describedby", uid + "wo");
      brush.appendChild(i);
      return i;
    }
    var A = range(opts.w0 == null ? 0 : opts.w0, "Window start, by week");
    var B = range(opts.w1 == null ? last : opts.w1, "Window end, by week");
    var out = h("output", "bl-out");
    out.id = uid + "wo";
    brush.appendChild(out);
    host.appendChild(brush);

    var key = h("p", "bl-key", "Gold ring: the fix became a standing rule. Curve: a later reversal repaired an earlier one. Grain: under 3 events in the window, n printed.");
    host.appendChild(key);
    var read = h("p", "bl-read");
    read.setAttribute("aria-live", "polite");
    host.appendChild(read);
    var src = h("p", "bl-src", data.source);
    host.appendChild(src);
    var idle = "Focus or point at a dot to read it. Tab reaches each lane; arrow keys move between dots.", picked = null;

    function say(e) {
      picked = e[0];
      var ln = data.lanes[e[1]], when = fmtDate(t0 + e[2] * DAY);
      read.textContent = "";
      var b = h("b", null, ln.label + ", belief " + e[0].replace(/^F/, "#"));
      read.appendChild(b);
      var s = ", " + when + ". " + ln.def + " A belief held here met a runnable test and failed it. " +
        (e[3] ? "It changed the rulebook: the fix is now a standing rule." : "Fixed where it happened; no standing rule changed.");
      (repairs[e[0]] || []).forEach(function (r) { s += " " + (r[0] === "repairs" ? "It repairs belief " : "Later repaired by belief ") + r[1].replace(/^F/, "#") + "."; });
      read.appendChild(document.createTextNode(s));
    }

    function draw() {
      var a = +A.value, z = +B.value;
      if (z - a < 2) { if (document.activeElement === A) a = Math.max(0, z - 2); else z = Math.min(last, a + 2); if (z - a < 2) a = z - 2; A.value = a; B.value = z; }
      var w0 = t0 + a * 7 * DAY, w1 = Math.min(end, t0 + (z + 1) * 7 * DAY);
      out.textContent = fmtDate(w0) + " to " + fmtDate(w1 - DAY);
      while (g.firstChild) g.removeChild(g.firstChild);
      var keep = picked;
      read.textContent = idle;
      picked = null;

      var W = Math.max(280, Math.round(host.clientWidth || 640)), narrow = W < 520;
      var L = narrow ? 0 : 116, NC = narrow ? 8 : 92, X0 = L + 8, X1 = W - NC;
      var lh = narrow ? 40 : 28, rh = narrow ? 40 : 30;
      function xs(t) { return X0 + (t - w0) / (w1 - w0) * (X1 - X0); }
      host.style.setProperty("--bl-lc", (narrow ? 48 : X0) + "px");
      host.style.setProperty("--bl-nc", (narrow ? 0 : NC) + "px");

      // Activity ribbon: two sparkline rows, each with its own peak for the window.
      var y = 0;
      [["Commits / week", data.commits, "bl-commits"], ["Receipts / week", data.receipts, "bl-receipts"]].forEach(function (row) {
        var vals = row[1], top = y + (narrow ? 16 : 4), hgt = rh - (narrow ? 20 : 8), peak = 0, pts = [], gaps = [];
        for (var w = a; w <= z; w++) { if (vals[w] != null && vals[w] > peak) peak = vals[w]; }
        for (w = a; w <= z; w++) {
          var cx = xs(Math.min(w1, Math.max(w0, t0 + (w + 0.5) * 7 * DAY)));
          if (vals[w] == null) { gaps.push(w); continue; }
          pts.push(cx.toFixed(1) + "," + (top + hgt - (peak ? vals[w] / peak * hgt : 0)).toFixed(1));
        }
        txt(g, narrow ? X0 : 0, narrow ? y + 11 : y + rh / 2 + 4, row[0], "bl-name " + row[2] + "-l");
        txt(g, W, narrow ? y + 11 : y + rh / 2 + 4, pts.length ? "peak " + num(peak) : "none", "bl-meta", "end");
        // Weeks with no recorded count are hatched, never drawn as zero.
        var run = null;
        gaps.concat([null]).forEach(function (w2) {
          if (run && (w2 == null || w2 !== run[1] + 1)) {
            var gx0 = xs(Math.max(w0, t0 + run[0] * 7 * DAY)), gx1 = xs(Math.min(w1, t0 + (run[1] + 1) * 7 * DAY));
            el("rect", { x: gx0, y: top, width: Math.max(1, gx1 - gx0), height: hgt, fill: "url(#" + uid + "h)" }, g);
            if (gx1 - gx0 > 140) txt(g, gx0 + 4, top + hgt - 2, run[1] < data.first_receipt_week ? "no receipt ledger yet" : "not recorded", "bl-meta");
            run = null;
          }
          if (w2 != null) run = run ? [run[0], w2] : [w2, w2];
        });
        if (pts.length > 1) el("polyline", { points: pts.join(" "), class: "bl-spark " + row[2] }, g);
        y += rh;
      });
      y += 8;

      // Lanes. Solid lanes (3 or more events in all) first, then a divider and the thin ones.
      var inWin = data.events.filter(function (e) { var t = t0 + e[2] * DAY; return t >= w0 && t < w1; });
      var count = data.lanes.map(function () { return 0; });
      inWin.forEach(function (e) { count[e[1]]++; });
      var order = data.lanes.map(function (l, i) { return i; });
      var solid = order.filter(function (i) { return data.lanes[i].n >= GRAIN_N; }), thin = order.filter(function (i) { return data.lanes[i].n < GRAIN_N; });
      var pos = {}, gridTop = y, ticks = el("g", {}, g), arcs = el("g", {}, g);
      function lanes(list) {
        list.forEach(function (i) {
          var ln = data.lanes[i], cy = y + lh / 2 + (narrow ? 6 : 0), grain = count[i] < GRAIN_N;
          var lg = el("g", { class: "bl-c-" + ln.key + (grain ? " bl-thin" : "") }, g);
          if (grain) {
            el("rect", { x: X0, y: cy - 10, width: X1 - X0, height: 20, rx: 3, class: "bl-grainband" }, lg);
            el("rect", { x: X0, y: cy - 10, width: X1 - X0, height: 20, rx: 3, class: "bl-grainfill", fill: "url(#" + uid + "g)" }, lg);
          }
          el("line", { x1: X0, x2: X1, y1: cy, y2: cy, class: "bl-rule" }, lg);
          var nm = txt(lg, narrow ? X0 : 0, narrow ? y + 11 : cy + 4, ln.label, "bl-name");
          nm.setAttribute("fill", "currentColor"); nm.setAttribute("stroke", "none");
          txt(g, W, narrow ? y + 11 : cy + 4, "n=" + count[i] + (count[i] !== ln.n ? " of " + ln.n : "") + (grain ? " · grain" : ""), grain ? "bl-n" : "bl-meta", "end");
          var seen = {};
          inWin.filter(function (e) { return e[1] === i; }).forEach(function (e) {
            var k = seen[e[2]] = (seen[e[2]] || 0) + 1, off = (k % 2 ? 1 : -1) * Math.floor(k / 2) * 7;
            var x = xs(t0 + (e[2] + 0.5) * DAY) + off;
            pos[e[0]] = [x, cy];
            var eg = el("g", { class: "bl-ev", tabindex: k === 1 && !lg.querySelector(".bl-ev") ? 0 : -1, role: "img",
              "aria-label": ln.label + ", belief " + e[0].replace(/^F/, "#") + ", " + fmtDate(t0 + e[2] * DAY) + (e[3] ? ", changed the rulebook" : "") }, lg);
            eg.dataset.id = e[0];
            el("circle", { cx: x, cy: cy, r: 11, class: "bl-hit" }, eg);
            if (e[3]) el("circle", { cx: x, cy: cy, r: 7.5, class: "bl-ring" }, eg);
            el("circle", { cx: x, cy: cy, r: 4.5, class: "bl-dot" }, eg);
            function on() { var o = g.querySelector(".bl-on"); if (o) o.classList.remove("bl-on"); eg.classList.add("bl-on"); say(e); }
            eg.addEventListener("focus", on); eg.addEventListener("mouseenter", on); eg.addEventListener("click", on);
            if (keep === e[0]) { eg.classList.add("bl-on"); say(e); }
          });
          y += lh;
        });
      }
      lanes(solid);
      if (thin.length) {
        y += 6;
        el("line", { x1: 0, x2: W, y1: y, y2: y, class: "bl-div" }, g);
        txt(g, 0, y + 16, "Thin evidence, under " + GRAIN_N + " events in all", "bl-meta");
        y += 22;
        lanes(thin);
      }

      // Repaired-by arcs, drawn over the lanes, only when both ends are in the window.
      data.links.forEach(function (l) {
        var p = pos[l[0]], q = pos[l[1]];
        if (!p || !q) return;
        var lift = Math.min(p[1], q[1]) - Math.max(14, Math.abs(q[0] - p[0]) * 0.25);
        var arc = el("path", { d: "M" + p[0] + " " + p[1] + " C" + p[0] + " " + lift + " " + q[0] + " " + lift + " " + q[0] + " " + q[1], class: "bl-arc" }, arcs);
        el("title", {}, arc).textContent = "Belief " + l[0] + " repaired by belief " + l[1];
      });

      // Month ticks: lines sit behind the lanes, labels under the last one.
      y += 6;
      var c = new Date(w0), m = Date.UTC(c.getUTCFullYear(), c.getUTCMonth() + 1, 1), step = narrow ? 2 : 1, k = 0;
      for (; m < w1; m = Date.UTC(new Date(m).getUTCFullYear(), new Date(m).getUTCMonth() + 1, 1), k++) {
        var x = xs(m);
        el("line", { x1: x, x2: x, y1: gridTop, y2: y, class: "bl-tick" }, ticks);
        if (k % step === 0) txt(g, x, y + 14, MON[new Date(m).getUTCMonth()], "bl-meta", "middle");
      }
      y += 20;
      svg.setAttribute("viewBox", "0 0 " + W + " " + y);
      svg.setAttribute("width", W);
      svg.setAttribute("height", y);
      title.textContent = inWin.length + " reversals across " + data.lanes.length + " domains, " + out.textContent +
        ", with weekly commits and decision receipts above. " + inWin.filter(function (e) { return e[3]; }).length + " changed the rulebook.";
    }
    svg.addEventListener("keydown", function (ev) {
      var cur = ev.target.closest && ev.target.closest(".bl-ev");
      if (!cur || ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Home", "End"].indexOf(ev.key) < 0) return;
      var lane = cur.parentNode, mine = [].slice.call(lane.querySelectorAll(".bl-ev")), next = null;
      if (ev.key === "ArrowLeft") next = mine[mine.indexOf(cur) - 1];
      else if (ev.key === "ArrowRight") next = mine[mine.indexOf(cur) + 1];
      else if (ev.key === "Home") next = mine[0];
      else if (ev.key === "End") next = mine[mine.length - 1];
      else {
        var lanes = [].slice.call(svg.querySelectorAll("g[class^='bl-c-']")).filter(function (l) { return l.querySelector(".bl-ev"); });
        var to = lanes[lanes.indexOf(lane) + (ev.key === "ArrowDown" ? 1 : -1)];
        next = to && to.querySelector(".bl-ev");
      }
      if (!next) return;
      ev.preventDefault();
      cur.setAttribute("tabindex", -1);
      [].forEach.call(next.parentNode.querySelectorAll(".bl-ev"), function (n) { n.setAttribute("tabindex", -1); });
      next.setAttribute("tabindex", 0);
      next.focus();
    });
    A.addEventListener("input", draw);
    B.addEventListener("input", draw);
    draw();
    if (window.ResizeObserver) {
      var lw = host.clientWidth;
      new ResizeObserver(function () { if (Math.abs(host.clientWidth - lw) > 4) { lw = host.clientWidth; draw(); } }).observe(host);
    }
  };
})();
