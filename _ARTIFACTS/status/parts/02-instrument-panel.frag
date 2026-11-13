  <!-- 02 INSTRUMENT PANEL -->
  <div class="section" data-tone="gold" data-tldr="Twelve design principles set before the first feature, each enforced in code, plus the loop that keeps learning that they run.">
    <div class="section-head">
      <div class="section-n">02</div>
      <div class="section-label" style="color:var(--gold);border-color:rgba(255,215,0,0.35);background:rgba(255,215,0,0.06);">THE INSTRUMENT PANEL</div>
    </div>
    <div class="section-title">Twelve design principles, set before the first feature. Each one enforced, not aspirational.</div>
    <div class="section-body">
      An instrument you would trust in fog has to be calibrated before the flight, not during it. These are the
      principles the system was built on, and for each, the concrete place it is enforced.
    </div>
    <div class="gauge-grid">
      <div class="gauge"><div class="gauge-name" style="color:var(--cyan);">TRACEABILITY</div><div class="gauge-def">Every answer links back to its receipt. Every milestone on this page names its commit; the commit history is available on request.</div></div>
      <div class="gauge"><div class="gauge-name" style="color:var(--cyan);">TRANSPARENCY</div><div class="gauge-def">Reasoning shown, not just conclusions. The build record is kept in a private repository; commit history is available on request.</div></div>
      <div class="gauge"><div class="gauge-name" style="color:var(--cyan);">EXPLAINABILITY</div><div class="gauge-def">Plain-language readouts at every altitude. The legend at the bottom of this page is the rule, not a courtesy.</div></div>
      <div class="gauge"><div class="gauge-name" style="color:var(--green);">EVIDENCE GATING</div><div class="gauge-def">Features switch on at data thresholds, never on enthusiasm. The roadmap below runs on this.</div></div>
      <div class="gauge"><div class="gauge-name" style="color:var(--green);">SOURCE QUALITY GRADING</div><div class="gauge-def">Every input is rated before it is allowed to move a conclusion.</div></div>
      <div class="gauge"><div class="gauge-name" style="color:var(--green);">PROVENANCE</div><div class="gauge-def">Where each fact came from travels with the fact. The source labels on this page are the same machinery.</div></div>
      <div class="gauge"><div class="gauge-name" style="color:var(--gold);">ANTI-HALLUCINATION*</div><div class="gauge-def">The screen cannot show more certainty than the data earned. Shaky answers render blurry.</div></div>
      <div class="gauge"><div class="gauge-name" style="color:var(--gold);">ANTI-SYCOPHANCY</div><div class="gauge-def">Built to disagree with its operator. Challenge reviews killed four overclaims before one merge.</div></div>
      <div class="gauge"><div class="gauge-name" style="color:var(--gold);">BIAS DETECTION*</div><div class="gauge-def">Red-team your own argument before committing. Drift gets flagged, then normalized against baseline.</div></div>
      <div class="gauge"><div class="gauge-name" style="color:var(--steel);">INTEROPERABILITY</div><div class="gauge-def">Local-first, lowest lock-in: one tenant that works across AI runtimes, vendor swap behind one seam.</div></div>
      <div class="gauge"><div class="gauge-name" style="color:var(--steel);">ATOMIC DESIGN</div><div class="gauge-def">Small components, composed: a 43-operator library and one engine behind every surface.</div></div>
      <div class="gauge"><div class="gauge-name" style="color:var(--steel);">THE DATA MODEL</div><div class="gauge-def">The decision receipt: expected vs. actual, machine-readable. The atomic unit everything compounds on.</div></div>
    </div>

    <div class="flow-title">How those principles run as one loop</div>
    <div class="flow-sub">A question comes in while things are still foggy. The system checks it, writes down what it expects to happen, and then, once you know how it actually turned out, compares the two. What it learns makes the next call a little sharper. That is the whole engine; everything else is built on top of it.</div>
    <div class="flow-wrap">
      <button class="flow-expand" id="flowexpand" type="button">⤢ EXPAND</button>
      <svg class="flow-svg" viewBox="0 0 940 300" role="img" aria-label="ARCS architecture: question to compass pipeline to receipt to outcome to calibration, looping back sharper">
        <defs>
          <marker id="fa" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#7a8699"/></marker>
          <marker id="fg" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#00FF9D"/></marker>
        </defs>
        <!-- forward chain -->
        <g class="fl-node"><rect x="14" y="112" width="128" height="76" rx="10" fill="#0d1117" stroke="#1e293b"/><text x="78" y="140" class="fl-t">QUESTION</text><text x="78" y="162" class="fl-s">asked in fog,</text><text x="78" y="176" class="fl-s">under pressure</text></g>
        <path d="M146 150 H186" stroke="#475569" stroke-width="1.5" marker-end="url(#fa)"/>
        <g class="fl-node"><rect x="190" y="96" width="150" height="108" rx="10" fill="#0d1117" stroke="rgba(0,240,255,0.35)"/><text x="265" y="122" class="fl-t" fill="#00F0FF">L0–L5 PIPELINE*</text><text x="265" y="144" class="fl-s">source-graded ·</text><text x="265" y="158" class="fl-s">anti-hallucination ·</text><text x="265" y="172" class="fl-s">confidence-gated ·</text><text x="265" y="186" class="fl-s">red-teamed</text></g>
        <path d="M344 150 H384" stroke="#475569" stroke-width="1.5" marker-end="url(#fa)"/>
        <g class="fl-node"><rect x="388" y="112" width="132" height="76" rx="10" fill="#0d1117" stroke="rgba(255,215,0,0.35)"/><text x="454" y="140" class="fl-t" fill="#FFD700">RECEIPT</text><text x="454" y="162" class="fl-s">expected vs actual,</text><text x="454" y="176" class="fl-s">rendered at earned</text></g>
        <path d="M524 150 H564" stroke="#475569" stroke-width="1.5" marker-end="url(#fa)"/>
        <g class="fl-node"><rect x="568" y="112" width="128" height="76" rx="10" fill="#0d1117" stroke="#1e293b"/><text x="632" y="140" class="fl-t">OUTCOME</text><text x="632" y="162" class="fl-s">what actually</text><text x="632" y="176" class="fl-s">happened</text></g>
        <path d="M698 150 H738" stroke="#475569" stroke-width="1.5" marker-end="url(#fa)"/>
        <g class="fl-node"><rect x="742" y="96" width="150" height="108" rx="10" fill="#0d1117" stroke="rgba(0,255,157,0.35)"/><text x="817" y="126" class="fl-t" fill="#00FF9D">CALIBRATION</text><text x="817" y="150" class="fl-s">scored automatically,</text><text x="817" y="164" class="fl-s">no human in the loop.</text><text x="817" y="184" class="fl-s">shipped day 98.</text></g>
        <!-- feedback arc: calibration sharpens the next question -->
        <path d="M817 204 V250 H78 V188" fill="none" stroke="#00FF9D" stroke-width="1.5" stroke-dasharray="4 4" marker-end="url(#fg)" opacity="0.8"/>
        <text x="447" y="242" class="fl-loop" fill="#00FF9D">EVERY SCORED OUTCOME MAKES THE NEXT DECISION SHARPER · THE LOOP THAT KEEPS LEARNING</text>
      </svg>
    </div>
    <div class="flow-scrollhint">TAP ⤢ EXPAND TO SEE THE WHOLE LOOP</div>
    <div class="flow-footnote">*System in beta. Anti-hallucination, bias detection, and red-teaming are mechanisms enforced in the code, not results proven at scale: the sample size behind them is still small. Effectiveness pending peer review and independent verification, not just this page's say-so.</div>
  </div>

