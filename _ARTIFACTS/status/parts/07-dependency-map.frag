  <!-- 06 DEPENDENCY MAP -->
  <div class="section" data-tone="cyan" data-tldr="The whole roadmap hangs on one dependency, scored outcomes, and it shipped on Day 98.">
    <div class="section-head">
      <div class="section-n">07</div>
      <div class="section-label" style="color:var(--cyan);border-color:rgba(0,240,255,0.35);background:rgba(0,240,255,0.06);">DEPENDENCY MAP</div>
    </div>
    <div class="section-title">The whole roadmap hangs on one dependency. It shipped on Day 98.<span class="dg" id="dg-gates">degraded · floor shown</span></div>
    <div class="section-body">
      Almost everything above waits on the same thing: real decisions with scored outcomes. The loop that
      produces them went live on Day 98. From here the pieces began to compound: the month since is the milestones below, and the next frontier is choreographing them into deep multi-agent orchestration.
    </div>
    <div class="dep-map">
      <div class="dep-node live">
        <div class="dep-status" style="color:var(--green);">LIVE TODAY</div>
        <div class="dep-name">Self-grading loop</div>
        <div class="dep-desc">Checks every prediction against what actually happened, automatically.</div>
      </div>
      <div class="dep-arrow">↓ <span>produces</span></div>
      <div class="dep-node live">
        <div class="dep-status" style="color:var(--green);">ACCUMULATING NOW</div>
        <div class="dep-name">Calibration data</div>
        <div class="dep-desc">Every decision plus its scored outcome. Builds itself through normal use. This is the single upstream dependency for everything below. <span class="gate-n">Today: <b data-g="cal">0</b> of {{gate_cal}} closed outcomes from outside users.</span></div>
      </div>
      <div class="dep-arrow">↓ <span>unlocks, at each volume threshold</span></div>
      <div class="dep-fan">
        <div class="dep-node next">
          <div class="dep-status" style="color:var(--gold);">NEXT</div>
          <div class="dep-name">Timing detection</div>
          <div class="dep-desc">Needs: 100 real decisions. Machinery already built. <span class="gate-n">Today: <b data-g="goal">10</b> of {{gate_goal}} from outside users.</span></div>
        </div>
        <div class="dep-node later">
          <div class="dep-status" style="color:var(--steel);">LATER</div>
          <div class="dep-name">Live goal map</div>
          <div class="dep-desc">Needs: 100+ recorded decisions to measure a baseline against. <span class="gate-n">Today: <b data-g="goal">10</b> of {{gate_goal}} from outside users.</span></div>
        </div>
        <div class="dep-node later">
          <div class="dep-status" style="color:var(--steel);">LATER</div>
          <div class="dep-name">Team and org layers</div>
          <div class="dep-desc">Needs: goal map live first, plus multi-person usage data.</div>
        </div>
      </div>
      <div class="dep-solo">
        <div class="dep-node next" style="max-width:400px;margin:0 auto;">
          <div class="dep-status" style="color:var(--gold);">NEXT · NO DATA GATE</div>
          <div class="dep-name">Adjacent questions</div>
          <div class="dep-desc">The one item with no upstream dependency. Blocked only by build time, so it is the natural next build.</div>
        </div>
      </div>
    </div>
  </div>

