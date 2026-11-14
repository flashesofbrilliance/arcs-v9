/* ARCS kit organism 69 strata-explorer: the year as stacked isometric planes you walk through.
   Event row: [id, lane, day since day0, label, gold seam 0|1, count, headline 0|1, url or ""].
   Data: the payload scripts/strata_explorer_build.py writes from runtime/specs/shipped-record.json.
   arcsStrata(host, data, {t, depth, fidelity}) replaces host's static list floor with the live explorer. Stdlib DOM, no deps.
   Controls are native range inputs (arrow keys, Home, End); the readout is a live region of links;
   nothing animates, so reduced motion needs no branch. Geometry is drawn in real pixels for the host's
   width, so 12px labels stay 12px on a phone. */
(function () {
  var NS = "http://www.w3.org/2000/svg";
  var WINDOW = 30, GRAIN_N = 3;
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
  function dayLabel(day0, d) {
    var t = new Date(Date.parse(day0 + "T00:00:00Z") + d * 864e5);
    return t.toISOString().slice(0, 10);
  }

  window.arcsStrata = function (host, data, opts) {
    opts = opts || {};
    var lanes = data.lanes, ev = data.events, max = data.max_day, uid = "st" + Math.random().toString(36).slice(2, 7);
    var byId = {};
    ev.forEach(function (e) { byId[e[0]] = e; });

    host.textContent = "";
    host.classList.add("strata");
    var ctl = h("div", "st-ctl");
    function range(label, min, maxv, val, help) {
      var wrap = h("div", "st-field");
      var lab = h("label", "st-flabel", label);
      lab.htmlFor = uid + help + "i";
      wrap.appendChild(lab);
      var i = document.createElement("input");
      i.type = "range"; i.min = min; i.max = maxv; i.value = val; i.step = 1; i.id = uid + help + "i";
      wrap.appendChild(i);
      var out = h("output", "st-out");
      out.id = uid + help;
      out.htmlFor = i.id;
      wrap.appendChild(out);
      ctl.appendChild(wrap);
      return { input: i, out: out };
    }
    var T = range("Walk time", 0, max, opts.t == null ? max : opts.t, "t");
    var A = range("Depth", 1, lanes.length, opts.depth || lanes.length, "a");
    var F = range("Fidelity", 0, 2, opts.fidelity == null ? 1 : opts.fidelity, "f");
    host.appendChild(ctl);

    var svg = el("svg", { role: "img", "aria-labelledby": uid + "title", class: "st-svg" });
    var title = el("title", { id: uid + "title" }, svg);
    var defs = el("defs", {}, svg);
    var pat = el("pattern", { id: uid + "g", width: 4, height: 4, patternUnits: "userSpaceOnUse", patternTransform: "rotate(45)" }, defs);
    el("rect", { width: 1.4, height: 4, class: "st-grain" }, pat);
    var layer = el("g", {}, svg);
    host.appendChild(svg);

    var read = h("div", "st-read");
    read.setAttribute("aria-live", "polite");
    host.appendChild(read);
    var key = h("ul", "st-key");
    lanes.forEach(function (l, i) {
      var li = h("li");
      var sw = h("span", "st-sw st-l" + i);
      sw.setAttribute("aria-hidden", "true");
      li.appendChild(sw);
      li.appendChild(document.createTextNode(l.label));
      key.appendChild(li);
    });
    var gl = h("li"), gs = h("span", "st-sw st-gold");
    gs.setAttribute("aria-hidden", "true");
    gl.appendChild(gs); gl.appendChild(document.createTextNode("Gold seam: a reversal that hardened into doctrine")); key.appendChild(gl);
    var nl = h("li"), ns = el("svg", { class: "st-grainsw", width: 12, height: 9, "aria-hidden": "true" }, nl);
    el("rect", { width: 12, height: 9, fill: "url(#" + uid + "g)" }, ns); // the chart's own hatch, as its legend
    nl.appendChild(document.createTextNode("Grain: under 3 events in the last 30 days, n printed")); key.appendChild(nl);
    host.appendChild(key);
    var src = h("p", "st-src", data.source);
    host.appendChild(src);

    function draw() {
      var t = +T.input.value, depth = +A.input.value, fid = +F.input.value;
      var W = Math.max(280, host.clientWidth || 640), narrow = W < 520;
      var x0 = narrow ? 8 : 96, dx = narrow ? 10 : 22, dy = narrow ? 46 : 40, top = narrow ? 34 : 24;
      var kx = (W - x0 - dx * (depth - 1) - 28) / max, ky = kx * 0.05;
      function P(d, l) { return [x0 + d * kx + l * dx, top + l * dy + d * ky]; }
      var H = Math.ceil(P(max, depth - 1)[1] + 40);
      svg.setAttribute("viewBox", "0 0 " + W + " " + H);
      svg.setAttribute("width", W); svg.setAttribute("height", H);
      while (layer.firstChild) layer.removeChild(layer.firstChild);

      // fidelity 1 shows headline events only (e[6]); 0 and 2 count or draw every event
      var shown = function (e) { return e[2] <= t && e[1] < depth && (fid !== 1 || e[6] === 1); };
      for (var l = 0; l < depth; l++) {
        var a = P(0, l), c = P(max, l);
        el("path", { d: "M" + (a[0] - 8) + "," + (a[1] - 12) + "L" + (c[0] - 8) + "," + (c[1] - 12) + "L" + (c[0] + 12) + "," + (c[1] + 8) + "L" + (a[0] + 12) + "," + (a[1] + 8) + "Z", class: "st-plane" }, layer);
        var lab = el("text", narrow ? { x: a[0] - 6, y: a[1] - 16, class: "st-lab st-t" + l } : { x: 4, y: a[1] + 4, class: "st-lab st-t" + l }, layer);
        lab.textContent = lanes[l].short;
        var rows = ev.filter(function (e) { return e[1] === l && shown(e); });
        if (fid === 0) {
          var mo = {};
          rows.forEach(function (e) { var m = dayLabel(data.day0, e[2]).slice(0, 7); mo[m] = (mo[m] || 0) + (e[5] || 1); });
          Object.keys(mo).forEach(function (m) {
            var d = Math.round((Date.parse(m + "-15T00:00:00Z") - Date.parse(data.day0 + "T00:00:00Z")) / 864e5);
            if (d > t) d = t;
            var p = P(Math.max(0, d), l), hgt = Math.min(dy - 14, 4 + Math.sqrt(mo[m]) * 4);
            el("rect", { x: p[0] - 4, y: p[1] - hgt, width: 8, height: hgt, class: "st-bar st-l" + l }, layer);
            var n = el("text", { x: p[0] + 6, y: p[1] - hgt + 9, class: "st-n" }, layer);
            n.textContent = mo[m];
          });
        } else {
          rows.forEach(function (e) {
            var p = P(e[2], l);
            el("circle", { cx: p[0], cy: p[1], r: e[4] ? 4 : 3, class: "st-dot st-l" + l + (e[4] ? " st-seam" : "") }, layer);
          });
        }
        var recent = ev.filter(function (e) { return e[1] === l && e[2] <= t && e[2] > t - WINDOW; }).length;
        if (recent < GRAIN_N) {
          var g0 = P(Math.max(0, t - WINDOW), l), g1 = P(t, l);
          el("path", { d: "M" + g0[0] + "," + (g0[1] - 7) + "L" + g1[0] + "," + (g1[1] - 7) + "L" + g1[0] + "," + (g1[1] + 7) + "L" + g0[0] + "," + (g0[1] + 7) + "Z", fill: "url(#" + uid + "g)", class: "st-grainband" }, layer);
          var gn = el("text", { x: g1[0] + 6, y: g1[1] + 4, class: "st-n" }, layer);
          gn.textContent = "n=" + recent;
        }
      }
      if (fid === 2) {
        data.links.forEach(function (k) {
          var p = byId[k[0]], q = byId[k[1]];
          if (!p || !q || p[1] >= depth || q[1] >= depth || p[2] > t || q[2] > t) return;
          var a = P(p[2], p[1]), b = P(q[2], q[1]), seam = k[2] === "repaired-by";
          el("path", { d: "M" + a[0] + "," + a[1] + "Q" + ((a[0] + b[0]) / 2) + "," + (Math.min(a[1], b[1]) - 16) + " " + b[0] + "," + b[1], class: seam ? "st-k st-kseam" : "st-k" }, layer);
        });
      }
      for (var m = 4; m <= 12; m++) {
        var md = Math.round((Date.UTC(2026, m - 1, 1) - Date.parse(data.day0 + "T00:00:00Z")) / 864e5);
        if (md < 0 || md > max) continue;
        var tp = P(md, depth - 1);
        el("line", { x1: tp[0] + 12, y1: tp[1] + 8, x2: tp[0] + 12, y2: tp[1] + 13, class: "st-tick" }, layer);
        var tl = el("text", { x: tp[0] + 12, y: tp[1] + 26, class: "st-tl" }, layer);
        tl.textContent = new Date(Date.UTC(2026, m - 1, 1)).toLocaleString("en", { month: "short", timeZone: "UTC" });
      }
      var c0 = P(t, 0), c1 = P(t, depth - 1);
      el("line", { x1: c0[0] - 8, y1: c0[1] - 14, x2: c1[0] + 12, y2: c1[1] + 10, class: "st-now" }, layer);

      var shownN = ev.filter(function (e) { return e[2] <= t && e[1] < depth; }).length;
      T.out.textContent = "through " + dayLabel(data.day0, t);
      A.out.textContent = depth + " of " + lanes.length + " layers";
      F.out.textContent = ["monthly counts", "headline events", "every event and link"][fid];
      [T, A, F].forEach(function (c) { c.input.setAttribute("aria-valuetext", c.out.textContent); });
      title.textContent = "The year to " + dayLabel(data.day0, t) + ": " + shownN + " cited events across " + depth + " layers.";

      var week = ev.filter(function (e) { return e[2] <= t && e[2] > t - 7 && e[1] < depth; });
      read.textContent = "";
      read.appendChild(h("p", "st-rhead", week.length ? "The 7 days to " + dayLabel(data.day0, t) : "Nothing dated in the 7 days to " + dayLabel(data.day0, t) + " in the shown layers."));
      var nav = h("p", "st-jump"), inLanes = ev.filter(function (e) { return e[1] < depth; });
      var prev = inLanes.filter(function (e) { return e[2] <= t - 7; }).pop(), next = inLanes.filter(function (e) { return e[2] > t; })[0];
      function jump(lbl, d) { var b = h("button", "st-btn", lbl); b.type = "button"; b.addEventListener("click", function () { T.input.value = d; draw(); T.input.focus(); }); nav.appendChild(b); }
      if (prev) jump("Earlier: " + dayLabel(data.day0, prev[2]), prev[2]);
      if (next) jump("Later: " + dayLabel(data.day0, next[2]), next[2]);
      if (t !== max) jump("Back to today", max);
      if (week.length) {
        var ul = h("ul", "st-rlist");
        week.slice(0, 8).forEach(function (e) {
          var li = h("li");
          var sw = h("span", "st-sw st-l" + e[1] + (e[4] ? " st-gold" : ""));
          sw.setAttribute("aria-hidden", "true");
          li.appendChild(sw);
          var txt = h("span", "st-rtext");
          var label = e[7] ? h("a", null, e[3]) : h("span", null, e[3]);
          if (e[7]) label.href = e[7];
          txt.appendChild(label);
          txt.appendChild(h("span", "st-meta", " " + lanes[e[1]].short + (e[4] ? ", gold seam" : "")));
          li.appendChild(txt);
          ul.appendChild(li);
        });
        read.appendChild(ul);
        if (week.length > 8) read.appendChild(h("p", "st-meta", (week.length - 8) + " more in this week."));
      }
      if (nav.firstChild) read.appendChild(nav);
    }
    [T, A, F].forEach(function (c) { c.input.addEventListener("input", draw); });
    if (window.ResizeObserver) new ResizeObserver(draw).observe(host); else window.addEventListener("resize", draw);
    draw();
    return { draw: draw, time: T.input, depth: A.input, fidelity: F.input };
  };
})();
