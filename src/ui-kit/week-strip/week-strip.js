/* Kit organism 72, week strip and chains. arcsWeekStrip(host, data, {pick}) replaces host's content.
   data: {weeks: [[week, monday, gates, chains[[date, sha, scope, break, repair, gate]], reversals[id], withheld]], max, beliefs, source}.
   Shading strength 0.75x (Zach's pick, 2026-11-13). Vanilla DOM, no dependencies. */
function arcsWeekStrip(host, data, opts) {
  var SHADE = 0.75, W = data.weeks, pick = opts && opts.pick !== undefined ? opts.pick : W.length - 1;
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }
  function cols() { return getComputedStyle(grid).gridTemplateColumns.split(' ').length; }
  function plural(n, one, many) { return n + " " + (n === 1 ? one : many); }
  function counts(w) {
    var s = plural(w[2], "gate", "gates") + " wired, " + plural(w[3].length + w[5], "chain", "chains");
    return w[5] ? s + " (" + w[5] + " not shown)" : s;
  }
  host.textContent = "";
  var grid = el("div", "ws-grid"), read = el("div", "ws-read"), head = el("div", "ws-rhead"), body = el("div"), cells = [];
  head.setAttribute("aria-live", "polite");
  read.appendChild(head);
  read.appendChild(body);
  grid.setAttribute("role", "group");
  grid.setAttribute("aria-label", "Weeks, oldest first");
  W.forEach(function (w, i) {
    var b = el("button", "ws-cell"), dots = el("span", "ws-dots");
    b.type = "button";
    b.tabIndex = -1;
    b.setAttribute("aria-label", w[2] + " " + w[1].replace(/ \d{4}$/, "") + ", week of " + w[1] + ": " + counts(w) + ", " + plural(w[4].length, "belief", "beliefs") + " reversed");
    b.style.background = "color-mix(in srgb, var(--cyan) " + Math.round(SHADE * (6 + 44 * w[2] / data.max)) + "%, var(--surface))";
    b.appendChild(el("span", "ws-n", String(w[2])));
    b.appendChild(document.createTextNode(" "));
    b.appendChild(el("span", "ws-mon", w[1].replace(/ \d{4}$/, "")));
    dots.setAttribute("aria-hidden", "true");
    [w[2], w[3].length + w[5], w[4].length].forEach(function (n, k) { if (n) dots.appendChild(el("span", "ws-dot ws-d" + k)); });
    b.appendChild(dots);
    b.addEventListener("click", function () { show(i); });
    b.addEventListener("keydown", function (e) {
      var j = { ArrowRight: i + 1, ArrowLeft: i - 1, ArrowDown: i + cols(), ArrowUp: i - cols(), Home: 0, End: W.length - 1 }[e.key];
      if (j === undefined) return;
      e.preventDefault();
      j = Math.max(0, Math.min(W.length - 1, j));
      show(j);
      cells[j].focus();
    });
    cells.push(b);
    grid.appendChild(b);
  });
  var key = el("ul", "ws-key");
  ["gates wired", "chains: a fix that added a gate", "beliefs reversed"].forEach(function (t, k) {
    var li = el("li");
    li.appendChild(el("span", "ws-dot ws-d" + k));
    li.appendChild(document.createTextNode(t));
    key.appendChild(li);
  });
  function step(k, v) {
    var s = el("div", "ws-step");
    s.appendChild(el("span", "ws-k", k));
    s.appendChild(v);
    return s;
  }
  function show(i) {
    var w = W[i];
    cells.forEach(function (c, j) { c.setAttribute("aria-pressed", String(j === i)); c.tabIndex = j === i ? 0 : -1; });
    head.textContent = "Week of " + w[1] + " · " + counts(w);
    body.textContent = "";
    if (w[4].length) {
      head.appendChild(document.createTextNode(" · "));
      var a = el("a", "", plural(w[4].length, "belief", "beliefs") + " reversed");
      a.title = w[4].join(", ");
      a.href = data.beliefs;
      head.appendChild(a);
    }
    if (!w[3].length) { body.appendChild(el("p", "ws-empty", w[5] ? "This week's chain is not shown on the public page." : "No fix commit added a gate this week.")); return; }
    var list = el("ul");
    list.style.listStyle = "none";
    w[3].forEach(function (c) {
      var li = el("li", "ws-chain"), brk = el("span", "ws-v");
      brk.appendChild(el("span", "ws-chip", c[2]));
      brk.appendChild(document.createTextNode(c[3]));
      li.appendChild(step("1 Break", brk));
      var fix = el("span", "ws-v", c[4] + " ");
      fix.appendChild(el("span", "ws-meta", c[1] + " · " + c[0]));
      li.appendChild(step("2 Repair", fix));
      li.appendChild(step("3 Gate", el("span", "ws-v ws-gate", c[5])));
      list.appendChild(li);
    });
    body.appendChild(list);
  }
  host.appendChild(grid);
  host.appendChild(key);
  host.appendChild(read);
  host.appendChild(el("p", "ws-src", data.source));
  show(pick);
}
