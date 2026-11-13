  <!-- 10 EVALS & FALSIFIABILITY -->
  <div class="section" data-tone="gold" data-tldr="Every headline claim, with the result that would kill it.">
    <div class="section-head">
      <div class="section-n">09</div>
      <div class="section-label" style="color:var(--gold);border-color:rgba(255,215,0,0.35);background:rgba(255,215,0,0.06);">EVALS &amp; FALSIFIABILITY</div>
    </div>
    <div class="section-title">Every headline claim, with the result that would kill it.</div>
    <div class="section-body" style="margin-bottom:0"><p class="su-lead">Status reads <strong>not run</strong> until the receipt efficacy loop has scored outcomes to test against. No claim below has been tested yet. Four of the six were struck from the papers that made them on Oct 17, 2026, because no data supports them; they stay listed, marked struck, so the withdrawal is visible.</p></div>
    <div class="section-body">
      <p class="su-lead">The papers make sharp numeric claims… so each is falsifiable. Publishing the tests turns marketing numbers into defensible science and de-risks both the patents and the raise.</p>
      <div class="su-tw">
        <table class="su-t">
          <thead><tr><th>Claim</th><th class="n">Metric</th><th>Pre-registered test</th><th>Kill criterion</th><th>Status</th></tr></thead>
          <tbody>
            <tr><td class="c">Accuracy scales with receipts<small>YP §2.4</small></td><td class="metric">68→87%</td><td>Time-ordered backtest at 1k/10k/100k; CI vs actuals</td><td class="kill">flat or &lt;80% at 100k</td><td><span class="chip high" data-eval="1">STRUCK OCT 17</span></td></tr>
            <tr><td class="c">Honest calibration<small>YP §2.4</small></td><td class="metric">χ² p&lt;.01</td><td>Reliability diagram + Brier score</td><td class="kill">curve off diagonal</td><td><span class="chip high" data-eval="2">STRUCK OCT 17</span></td></tr>
            <tr><td class="c">Beats human experts<small>YP §2.4</small></td><td class="metric">76%</td><td>Blinded head-to-head on unseen briefs</td><td class="kill">win rate ≤ 50%</td><td><span class="chip high" data-eval="3">STRUCK OCT 17</span></td></tr>
            <tr><td class="c">2nd-deriv predicts cascades<small>WP §2.1</small></td><td class="metric">78%@24h</td><td>Labeled backtest, 10k events vs velocity baseline</td><td class="kill">no lift; lead ≤ 0</td><td><span class="chip open" data-eval="4">NOT RUN</span></td></tr>
            <tr><td class="c">Phase-cancel lifts ROAS<small>WP §2.1</small></td><td class="metric">+35%</td><td>Randomized A/B: optimized vs naïve spacing</td><td class="kill">ROAS delta CI crosses 0</td><td><span class="chip open" data-eval="5">NOT RUN</span></td></tr>
            <tr><td class="c">Network effect A(N) log<small>YP §6.2</small></td><td class="metric">λ≈1.2e-5</td><td>Fit across cohorts; forecast held-out cohort</td><td class="kill">fails held-out within CI</td><td><span class="chip high" data-eval="6">STRUCK OCT 17</span></td></tr>
          </tbody>
        </table>
      </div>
      <div class="su-note"><b>Make evals credible before publishing</b>Pre-register each design on OSF or AsPredicted (hypothesis, primary endpoint, kill criterion) before looking at outcomes; one endpoint per claim, multiplicity-corrected; release the backtest harness + de-identified receipts so results replicate.</div>
      <div class="su-sub">Peer review · collaborators · funding</div>
      <div class="su-icards">
        <div class="su-ic"><div class="cat">Peer review</div><ul>
          <li>Marketing Science / JMR<span>abductive marketing, network effects</span></li>
          <li>KDD · WWW · NeurIPS<span>prediction, federated, causal ML</span></li>
          <li>Management Science<span>decision-receipt framing</span></li>
          <li>arXiv · SSRN<span>preprint… dated public record</span></li>
        </ul></div>
        <div class="su-ic"><div class="cat">Institutes</div><ul>
          <li>Marketing Science Institute<span>funds academic marketing research</span></li>
          <li>Ehrenberg-Bass<span>evidence-based marketing… direct fit</span></li>
          <li>Wharton Customer Analytics<span>corporate-data competitions</span></li>
          <li>MIT IDE · Stanford HAI<span>platform economics + AI eval</span></li>
        </ul></div>
        <div class="su-ic fund"><div class="cat">Funding… non-dilutive</div><ul>
          <li>NSF SBIR/STTR<span>America's Seed Fund; deep tech</span></li>
          <li>NSF CISE / Convergence<span>research grant w/ academic PI</span></li>
          <li>Sloan Foundation<span>metascience, digital economics</span></li>
          <li>Schmidt Sciences · NBER<span>AI-for-science; working papers</span></li>
        </ul></div>
      </div>
      <div class="su-note gold"><b>Sequencing</b>File the Tier-1 provisionals (or confirm existing filings) <strong>before</strong> the arXiv/SSRN preprint… a preprint is a public disclosure that restarts the same §102 clock. Patent first, publish second, then approach institutes and grant programs with a dated filing + a pre-registered eval in hand.</div>
    </div>
  </div>

