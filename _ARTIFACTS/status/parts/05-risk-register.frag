  <!-- 04 RISK REGISTER -->
  <div class="section" data-tone="red" data-tldr="What I&#x27;d tell a board today: single-operator context, gated features, vendor concentration, each with its mitigation.">
    <div class="section-head">
      <div class="section-n">05</div>
      <div class="section-label" style="color:var(--red);border-color:rgba(255,77,109,0.35);background:rgba(255,77,109,0.06);">RISK REGISTER, CURRENT AND HONEST</div>
    </div>
    <div class="section-title">What I would tell a board about this system today.<span class="dg" id="dg-risk">degraded · floor shown</span></div>
    <table class="risk-table">
      <thead><tr><th>Risk</th><th class="hide-m">Mitigation</th><th>Sev</th><th>Status</th></tr></thead>
      <tbody>
        <tr>
          <td><strong>One person holds all the context.</strong></td>
          <td class="hide-m">Everything is written down as it happens: 859 annotated commits, 272 decision records, versioned handoff notes. Built so a team could take over without me in the room.</td>
          <td><span class="chip high">HIGH</span></td>
          <td><span class="chip mit">MITIGATED BY DESIGN</span></td>
        </tr>
        <tr>
          <td><strong>Not enough real usage data yet</strong> to switch on the most advanced features responsibly.</td>
          <td class="hide-m">Those features are built and tested but deliberately switched off until enough real data exists to measure them against. No feature ships on faith.</td>
          <td><span class="chip med">MED</span></td>
          <td><span class="chip gated">GATED, ON PURPOSE</span></td>
        </tr>
        <tr>
          <td><strong>The core AI runs on a single vendor.</strong></td>
          <td class="hide-m">The full decision engine also exists as a standalone, vendor-free implementation (~21.9K lines of plain Python). The vendor connection sits behind one seam and can be swapped.</td>
          <td><span class="chip med">MED</span></td>
          <td><span class="chip open">OPEN, HEDGE BUILT</span></td>
        </tr>
        <tr>
          <td><strong>Written standards drifted from what the checks enforced.</strong></td>
          <td class="hide-m">Found by self-audit, then fixed structurally: every audit finding now closes through a real enforcement mechanism or a dated exception. The gap cannot silently reopen.</td>
          <td><span class="chip med">MED</span></td>
          <td><span class="chip mit">MITIGATED</span></td>
        </tr>
        <tr>
          <td><strong>The quality score is still self-graded</strong> until enough outcomes accumulate to calibrate it.</td>
          <td class="hide-m">Every score is logged with its decision, but calibration needs outcomes, and an outcome is logged only when a person answers the debrief. As of Nov 4, 2026, none has come from an outside user. The outcome-tracking loop that shipped on Day 98 is the correction signal.</td>
          <td><span class="chip low">LOW</span></td>
          <td><span class="chip gated">GATED ON DATA</span></td>
        </tr>
        <tr>
          <td><strong>One production credential was set by hand</strong> and needs scheduled rotation.</td>
          <td class="hide-m">Known, documented in the decision record that created it, rotation procedure written and calendared.</td>
          <td><span class="chip low">LOW</span></td>
          <td><span class="chip open">OPEN, SCHEDULED</span></td>
        </tr>
        <tr data-risk="spend-cap">
          <td><strong>API keys on a retired, capped account</strong> still need clearing.</td>
          <td class="hide-m">Production, CI and local development already run on the new account. The remaining old copies are listed privately and are revoked once moved.</td>
          <td><span class="chip med" data-r="sev">MED</span></td>
          <td><span class="chip open" data-r="status">AWAITING DECISION</span></td>
        </tr>
        <tr data-risk="write-lock">
          <td><strong>Irreversible changes rely on an advisory lock.</strong></td>
          <td class="hide-m">One-way-door decisions are declared before commit; enforcement turns blocking once every merge path uses it.</td>
          <td><span class="chip med" data-r="sev">MED</span></td>
          <td><span class="chip open" data-r="status">AWAITING DECISION</span></td>
        </tr>
        <tr data-risk="ci-spend">
          <td><strong>Automated code review was the largest share of AI spend.</strong></td>
          <td class="hide-m">Moved to a cheaper model tier, an estimated two thirds less, and the first review on it ran clean. Caching and batching were measured and left off: at this volume they would not pay for themselves.</td>
          <td><span class="chip med" data-r="sev">MED</span></td>
          <td><span class="chip mit" data-r="status">RESOLVED</span></td>
        </tr>
      </tbody>
    </table>
  </div>

