/* option-board: click one option per block, move the dials, send or copy the one-line picks.
   Reads the spec the builder embeds as <script type="application/json" id="ob-spec">.
   An unpicked block stays as it is now (the summary says so). If the page runs inside a
   widget host that defines window.sendPrompt, "Send my picks" posts the line there;
   otherwise it is copied, and also posted to a parent frame as {type:"option-board-picks"}. */
(function () {
  var spec = JSON.parse(document.getElementById("ob-spec").textContent);
  var picks = {}, dials = {};
  var root = document.documentElement;
  var out = document.getElementById("ob-summary");

  function fmt(n) { return (Math.round(n * 100) / 100).toString(); }

  function summary() {
    var parts = [];
    spec.blocks.forEach(function (b) { if (picks[b.id]) parts.push(b.label + " " + picks[b.id]); });
    var line = parts.length ? parts.join(", ") + "." : "No picks yet.";
    var rest = spec.blocks.length - parts.length;
    if (parts.length && rest) line += " Others unchanged.";
    (spec.dials || []).forEach(function (d) { line += " " + d.label + " " + fmt(dials[d.id]) + (d.unit || "") + "."; });
    return line;
  }
  function render() { out.textContent = summary(); }

  document.querySelectorAll(".ob-opt").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var b = btn.getAttribute("data-block"), k = btn.getAttribute("data-key");
      picks[b] = picks[b] === k ? undefined : k;
      document.querySelectorAll('.ob-opt[data-block="' + b + '"]').forEach(function (o) {
        var on = picks[b] === o.getAttribute("data-key");
        o.setAttribute("aria-pressed", on ? "true" : "false");
        o.querySelector(".ob-opt-pick").textContent = on ? "Picked" : "Pick";
      });
      render();
    });
  });

  (spec.dials || []).forEach(function (d) {
    var el = document.getElementById("dial-" + d.id), o = document.getElementById("dial-" + d.id + "-out");
    function set() {
      dials[d.id] = parseFloat(el.value);
      root.style.setProperty("--k-" + d.id, el.value);
      o.textContent = fmt(dials[d.id]) + (d.unit || "");
      render();
    }
    el.addEventListener("input", set);
    set();
  });

  function copy(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text).catch(function () { fallback(text); });
    }
    fallback(text);
  }
  function fallback(text) {
    var t = document.createElement("textarea");
    t.value = text; t.setAttribute("readonly", ""); t.style.position = "fixed"; t.style.opacity = "0";
    document.body.appendChild(t); t.select();
    try { document.execCommand("copy"); } catch (e) {}
    document.body.removeChild(t);
  }
  var sendBtn = document.getElementById("ob-send"), copyBtn = document.getElementById("ob-copy");
  var canSend = typeof window.sendPrompt === "function";
  if (!canSend) sendBtn.hidden = true;
  sendBtn.addEventListener("click", function () { window.sendPrompt(summary()); });
  copyBtn.addEventListener("click", function () {
    var s = summary();
    copy(s);
    try { if (window.parent !== window) window.parent.postMessage({ type: "option-board-picks", board: spec.id, text: s }, "*"); } catch (e) {}
    copyBtn.textContent = "Copied";
    setTimeout(function () { copyBtn.textContent = "Copy my picks"; }, 1500);
  });
  render();
})();
