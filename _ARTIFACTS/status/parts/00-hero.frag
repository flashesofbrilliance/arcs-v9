  <h1>Day 0: one empty commit.<br>Day <span id="hero-day">{{day}}</span>: a live product that grades itself.</h1>
  <div class="byline">Live build status, measured directly from the repository, updated live</div>
  <div class="lede">
    This is the real build history of <strong>ARCS</strong>, a decision intelligence platform I built solo, run
    in production, and <strong>documented from day one so a team could take it over without me in the room</strong>.
    Every number on this page comes from the repository itself. Every milestone names its real commit. The dial
    below lets you read the story at whatever depth you want: the one page version, or all the way down to the code.
  </div>

  <div class="era-head" style="color:var(--green);"><span class="era-tick" style="background:var(--green);"></span>BUILD TELEMETRY · DAY 0 → DAY <span id="era-day">{{day}}</span> · SINCE APR 2026 · AS OF <span id="et-now">{{asof}}</span></div>

  <div class="stats">
    <div class="stat"><div class="stat-val accent" id="sv-commits">{{commits}}</div><div class="stat-label">Commits · Day 0 to today</div></div>
    <div class="stat"><div class="stat-val" id="stat-days">{{day}}</div><div class="stat-label">Days · first commit to now</div></div>
    <div class="stat"><div class="stat-val">14+</div><div class="stat-label">Client surfaces · hours each</div></div>
    <div class="stat"><div class="stat-val accent">live</div><div class="stat-label">In production · app.arcs.care</div></div>
  </div>

  <div class="pulse" id="pulse">
    <div class="pulse-head">
      <span class="pulse-dot"></span>Live pulse
      <span class="pulse-src">server-side read · main</span><span class="dg" id="dg-pulse">degraded · floor shown</span>
      <button class="pulse-refresh" id="pulse-refresh" type="button" title="Refresh now" aria-label="Refresh live pulse">↻</button>
    </div>
    <div class="pulse-grid">
      <div class="pulse-cell"><div class="pl-k">Latest commit</div><div class="pl-v" id="pl-commit">loading…</div><div class="pl-sub" id="pl-commit-when"></div></div>
      <div class="pulse-cell"><div class="pl-k">Latest deploy</div><div class="pl-v" id="pl-deploy">loading…</div><div class="pl-sub" id="pl-deploy-when"></div></div>
      <div class="pulse-cell"><div class="pl-k">Open PRs</div><div class="pl-v" id="pl-prs">loading…</div><div class="pl-sub" id="pl-prs-sub"></div></div>
      <div class="pulse-cell"><div class="pl-k">Commits · main</div><div class="pl-v" id="pl-count">loading…</div><div class="pl-sub">total, live</div></div>
    </div>
    <div class="pulse-foot" id="pulse-foot">refreshes on load, on tab focus, and every 2 min · read server-side, cached ≤10 min</div>
  </div>

  <div class="legend-hint">Product terms look <b>like this</b>. Hover or tap for the plain meaning. Full legend at the bottom.</div>

  <div class="focus-bar">
    <span class="fb-label">Reading mode</span>
    <button class="focus-btn active" id="fb-focus">◇ FOCUS · ONE AT A TIME</button>
    <button class="focus-btn" id="fb-expand">▾ EXPAND ALL</button>
    <span class="fb-label" style="color:var(--faint);">click any section header to fold it</span>
  </div>

