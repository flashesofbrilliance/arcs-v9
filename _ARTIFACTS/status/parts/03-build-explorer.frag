  <!-- 03 BUILD EXPLORER -->
  <div class="section">
    <div class="section-head">
      <div class="section-n">03</div>
      <div class="section-label" style="color:var(--green);border-color:rgba(0,255,157,0.35);background:rgba(0,255,157,0.06);">THE BUILD, DAY 0 TO TODAY</div>
    </div>
    <div class="section-title">Pick your depth. The story stays the same, the detail changes.</div>
    <div class="section-body">
      <strong>The one page read</strong> shows 13 milestones, one plain sentence each. Each level down adds
      more events and more detail, until <strong>Commits</strong> names the commit behind each milestone.
      Each milestone that a stranger can check without my word carries a <strong>verify</strong> link to the live thing; the internal ones say so.
      Keys 1 to 5 work too.
    </div>

    <div class="tele-tabs">
      <button class="tele-tab active" data-tab="tempo">TEMPO · COMMITS PER WEEK</button>
      <button class="tele-tab" data-tab="hands">HANDS · WHO HELD THE PEN</button>
      <button class="tele-tab" data-tab="recent">RECENT · MERGES PER WEEK</button>
    </div>

    <div id="tab-tempo">
      <div class="cadence" id="cadence"></div>
      <div style="font-family:var(--mono);font-size:11px;color:var(--faint);letter-spacing:0.08em;text-align:center;margin-top:6px;">COMMITS PER WEEK, APRIL TO AUGUST · GOLD = THE QUIET STRETCH · GREEN = PEAK</div>
      <div class="unlock-chip" id="chip-design">⊙ APR–MAY: FIVE QUIET WEEKS · WHAT THE SILENCE WAS · TAP</div>
      <div class="unlock-card" id="unlock-design">
        <div class="unlock-title">THE GAP IS NOT A GAP. IT IS THE DESIGN BUILD.</div>
        <div class="unlock-body">One commit on Day 0, then the repository went quiet for five weeks, because the work moved to the drawing board. In that window I designed the <strong>brand system</strong>, the <strong>full design system</strong>, and the <strong>front-end component library</strong>: TypeScript components with Jest tests and linting wired for CI/CD, with Playwright end-to-end coverage next on the list. The decision-receipt concept and the product's written constitution were drafted in the same stretch. <strong>Code came second on purpose:</strong> when the repo woke up on Day 39, the entire working core landed in one push, because every piece already knew its place.</div>
      </div>
    </div>

    <div id="tab-recent" style="display:none;">
      <div class="cadence" id="tempo-live" data-floor='{{tempo_json}}'></div>
      <div style="font-family:var(--mono);font-size:11px;color:var(--faint);letter-spacing:0.08em;text-align:center;margin-top:6px;">PULL REQUESTS MERGED INTO MAIN PER WEEK · LAST 12 WEEKS · <span id="tempo-src">FROM GIT HISTORY</span><span class="dg" id="dg-tempo">degraded · floor shown</span></div>
    </div>

    <div id="tab-hands" style="display:none;">
      <div class="cond" id="cond"></div>
      <div class="cond-legend" id="condlegend"></div>
      <div class="cond-caption">THE SAME WEEKS, BY WHO HELD THE PEN · ONE HUMAN CONDUCTING FIVE GENERATIONS OF AI · 128 COMMITS FULLY BY HAND</div>
      <div class="unlock-chip" id="chip-frontier">⊙ JUL: THE ENSEMBLE ROTATES · TAP</div>
      <div class="unlock-card" id="unlock-frontier">
        <div class="unlock-title">BUILDING AT THE EDGE: WITH THE FRONTIER AS IT MOVES.</div>
        <div class="unlock-body">In the two weeks up to Day 98 the pen changes hands almost entirely: <strong>Sonnet 5 and Fable 5 take over within days of release</strong>, while the model that wrote most of the build rotates out. Swapping the strongest available intelligence into a live production system without breaking stride is its own discipline. The seams are clean because the receipts, tests, and handbook made every model start oriented, not initiated. The gray lane matters too: <strong>128 commits carry no AI co-author at all.</strong> The conductor still plays.</div>
      </div>
    </div>

    <div class="alt-bar" id="altbar">
      <button class="alt-btn active" data-alt="0">One Page<span class="k">1 · what changed</span></button>
      <button class="alt-btn" data-alt="1">Direction<span class="k">2 · why this path</span></button>
      <button class="alt-btn" data-alt="2">Process<span class="k">3 · how it ran</span></button>
      <button class="alt-btn" data-alt="3">Detail<span class="k">4 · the moves</span></button>
      <button class="alt-btn" data-alt="4">Commits<span class="k">5 · the code itself</span></button>
      <div class="alt-readout" id="readout"></div>
    </div>

    <div class="ms-list" id="mslist"></div>
  </div>

