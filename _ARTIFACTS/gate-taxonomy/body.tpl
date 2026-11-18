<header class="top">
  <div class="wrap toprow">
    <span class="wordmark">ARCS</span>
    <span class="meta">Internal: design spec, recommendation and plan</span>
  </div>
</header>

<main class="wrap">

<section class="hero">
  <h1>The gate ladder</h1>
  <p class="lede">Every check that can stop a commit or a merge, built from the bottom up and mapped to the ARCS primitives it defends, so the decision structure can be tested instead of trusted.</p>
</section>

<section class="cr" aria-label="Cold read">
  <dl class="cr-slots">
    <dt class="section-label">Why</dt>
    <dd>Two gates were wrong today, and both errors surfaced only because someone looked. A gate system with no way to see its own mistakes keeps them.</dd>
    <dt class="section-label">What</dt>
    <dd>A ladder that derives each layer from the one below: atoms (single verdicts), molecules (gate scripts), organisms (the commit hook and each CI job), templates (the shape of a check) and pages; then a second ladder of primitives (the seven ROM primitives), operators (the periodic table) and protocols (commit, merge).</dd>
    <dt class="section-label">Why now</dt>
    <dd>The shadow eval landed today (PR 2350) and found {{fix_followed}} bypasses that a later fix followed, but it cannot say which primitive each one broke. That needs this mapping.</dd>
  </dl>
  <div class="cr-howwrap">
    <p class="section-label">How</p>
    <ol class="cr-how">
      <li class="cr-step"><p class="section-label">Before</p><p class="cr-when">Done, 2026-11-17</p><p class="cr-what">Ladder derived, backlog graph induced, this page generated from both.</p></li>
      <li class="cr-step"><p class="section-label">During</p><p class="cr-when">Next, your call</p><p class="cr-what">Rule {{templates_n}} templates to primitives, recorded as an ADR. {{ruling_downstream}} rows wait on it.</p></li>
      <li class="cr-step"><p class="section-label">After</p><p class="cr-when">Once replay exists</p><p class="cr-what">Run the order-effect and fractal-invariance experiment.</p></li>
    </ol>
  </div>
  <p class="callout cr-read"><b>How to read</b>The design spec says what each layer is and how it is derived. The recommendation holds the one decision that is yours. The plan is the dependency graph. The experiment tests whether the classification holds its shape. The limits say what the ladder cannot see.</p>
</section>

<section id="spec">
  <p class="section-label">Design spec</p>
  <h2>Two ladders, one rule: each layer comes from the one below</h2>
  <p class="lede">Nothing is declared from the top. A layer is computed from the layer under it, and a mapping exists only where the repo already holds evidence for it. Counts are generated from <code>runtime/specs/gate-taxonomy.json</code> and <code>_QUEUE/induced-backlog.jsonl</code>.</p>

  <div class="ladders">
    {{DESIGN_LADDER}}
    {{ARCS_LADDER}}
  </div>

  <h3>The six templates</h3>
  <p>A template is the reusable shape of a check, read mechanically from how the hook calls it. Ruling {{templates_n}} templates gives all {{atoms}} atoms a primitive, instead of {{atoms}} separate guesses.</p>
  <div class="scroll" tabindex="0" role="region" aria-label="Templates table">
    <table>
      <thead><tr><th>Template</th><th class="num">Atoms</th><th class="num">Molecules</th><th>Read from</th><th>Evidence in the hook</th></tr></thead>
      {{TEMPLATE_ROWS}}
    </table>
  </div>

  <h3>Invariants the ladder keeps</h3>
  <ul class="rules">
    <li><strong>Derived, never declared.</strong> Every layer is recomputed from its source; <code>--check</code> fails when the file differs from a rebuild.</li>
    <li><strong>Evidence or UNRULED.</strong> A primitive or operator is attached only where the hook, a ruling file or a real import says so. Absence is shown as a gap, never filled.</li>
    <li><strong>Label classes never merge.</strong> Replay-confirmed, human-labeled and model-labeled stay separate, so judgment is never reported as an outcome.</li>
    <li><strong>Provenance on every node.</strong> Each atom carries the sha that wrote its hook line; each molecule carries the commit that wired it and any ADR the repo already cites for it. An ADR is linked only where one is cited, so the gap is visible.</li>
    <li><strong>One document shape at every layer.</strong> <code>runtime/specs/gate-taxonomy-docs.jsonl</code> holds every node as the same record (id, layer, text, meta, parents, children, content hash). A blob store takes the file as is; a vector store embeds the text and re-embeds only what changed.</li>
    <li><strong>The tool is tested like a gate.</strong> Its own errors were found the same way: a warning regex matched a comment, 30 gates had no atoms, a generator was credited with 12 operators, a prose mention was counted as a page reader, and CI-only gates were missing. Each was fixed at the source.</li>
  </ul>
</section>

<section id="rec">
  <p class="section-label">Recommendation</p>
  <h2>Rule five templates now, split the sixth, and bind operators after</h2>
  <p class="lede">The mapping from template to primitive is a canon decision, so it is yours. Below are readings to react to, each marked as a suggestion, with how sure it is.</p>

  <div class="scroll" tabindex="0" role="region" aria-label="Suggested primitives table">
    <table>
      <thead><tr><th>Template</th><th>Suggested primitive</th><th>Why</th><th>Confidence</th></tr></thead>
      <tbody>
        <tr><td>derived-freshness</td><td>Kintsugi</td><td>A generated file is rebuilt from source; a hand patch fails. That is the no-silent-repair rule.</td><td><span class="pill hi">judgment, firm</span></td></tr>
        <tr><td>record-integrity</td><td>Hyperstition</td><td>A record's claims must exist on main before they are trusted: the Loki test applied to a cite.</td><td><span class="pill hi">judgment, firm</span></td></tr>
        <tr><td>gate</td><td>Hyperstition</td><td>Most are claim gates (a figure, a résumé line, a public share) that refuse an unproven claim.</td><td><span class="pill mid">judgment, medium</span></td></tr>
        <tr><td>lint</td><td>Kintsugi</td><td>A lint is a frustration gate: the cheapest check that fails a whole defect class. The hook already names Kintsugi here.</td><td><span class="pill mid">evidence plus judgment</span></td></tr>
        <tr><td>self-test</td><td>Golden Inchworm</td><td>A gate proving itself before it judges others is the three-pass rule turned inward. Weak reading.</td><td><span class="pill lo">judgment, weak</span></td></tr>
        <tr><td>check</td><td>split first</td><td>{{check_atoms}} atoms across {{check_molecules}} scripts with no shared shape. It is a leftover bucket, not a template. Splitting it before ruling avoids one ruling covering unrelated checks.</td><td><span class="pill lo">not rulable as is</span></td></tr>
      </tbody>
    </table>
  </div>

  <div class="findings">
    <div class="finding">
      <p class="section-label">Finding</p>
      <p><strong>Write-lock lives at the protocol layer, not in any atom.</strong> No hook check enforces a one-way door; the merge protocol does (safe_merge, the merge-commit setting, receipts). The fractal test in section 4 should expect some primitives to appear only at higher layers.</p>
    </div>
    <div class="finding">
      <p class="section-label">Finding</p>
      <p><strong>No gate uses an operator.</strong> The periodic table has an Immune (18), a Loki (23) and a Librarian (21), and none of the {{molecules}} gate scripts imports them. Either the gates are the operators in practice, or the operators are not yet load-bearing. That is row <code>gate-operator-binding</code>.</p>
    </div>
    <div class="finding">
      <p class="section-label">Position</p>
      <p><strong>TypeSafe classifies the residue only.</strong> Replay settles what history can settle; TypeSafe labels what is left and is graded against replay. It stays held: no key on this machine, and your egress rule allows only already-public text.</p>
    </div>
  </div>
</section>

<section id="plan">
  <p class="section-label">Implementation plan</p>
  <h2>{{rows_n}} rows, {{waves_n}} waves, one ruling on the critical path</h2>
  <p class="lede">The rows live in <code>_QUEUE/induced-backlog.jsonl</code>, epic C10 repo integrity and CI. A wave can start when everything it depends on is done.</p>

  <div class="scroll" tabindex="0" role="region" aria-label="Backlog graph">
    {{GRAPH}}
  </div>

  <div class="scroll" tabindex="0" role="region" aria-label="Backlog rows table">
    <table>
      <thead><tr><th>Row</th><th>Delivers</th><th>Done when</th></tr></thead>
      {{ROW_ROWS}}
    </table>
  </div>
</section>

<section id="experiment">
  <p class="section-label">Experiment</p>
  <h2>Does the classification hold its shape?</h2>
  <p class="lede">If the decision structure is built on self-similar invariants, a case should get the same label whichever order you measure in, and the same primitive at every level of the ladder. Two tests check that, scored by rules fixed before either one runs.</p>

  <div class="arms">
    <div class="arm">
      <p class="section-label">Test 1 · order effect</p>
      <h3>Classify, then replay. Replay, then classify.</h3>
      <p><strong>Arm A</strong> labels each bypass with no replay result in view, then replays it. <strong>Arm B</strong> replays first, then labels with the outcome in view. Each arm's classifier never sees the other arm's labels.</p>
      <p><strong>Reads:</strong> a label that moves between arms was hindsight, not classification. Arm A's agreement with replay is the classifier's real accuracy; arm B's extra agreement is how much the outcome bent the call.</p>
    </div>
    <div class="arm">
      <p class="section-label">Test 2 · fractal invariance</p>
      <h3>One case, three levels, one primitive?</h3>
      <p>Classify each case on its own at the atom, the molecule and the organism, with no level able to see another's label.</p>
      <p><strong>Reads:</strong> where the primitive changes with the level, the structure is not self-similar there. The write-lock finding predicts at least one such break: a primitive that exists only at the protocol layer.</p>
    </div>
  </div>

  <div class="scroll" tabindex="0" role="region" aria-label="Experiment scores table">
    <table>
      <thead><tr><th>Score</th><th>Rule, fixed in advance</th></tr></thead>
      <tbody>
        <tr><td>Accuracy</td><td>Arm A labels that match the replay verdict, over cases replay settles</td></tr>
        <tr><td>Hindsight shift</td><td>Cases whose label differs between arm A and arm B, over all cases</td></tr>
        <tr><td>Level disagreement</td><td>Cases whose primitive differs between any two levels, over all cases</td></tr>
        <tr><td>Classifiers</td><td>A local classifier first; TypeSafe as a third classifier only after the key and egress decision. Each scored separately, never pooled.</td></tr>
      </tbody>
    </table>
  </div>
</section>

<section id="limits">
  <p class="section-label">Limits</p>
  <h2>Three blind spots, stated</h2>
  <ul class="rules">
    <li><strong>Silent wrong passes.</strong> A gate that let something wrong through, never reverted, leaves no trace. The shadow eval's {{unrevealed}} unrevealed commits are the upper bound, not a pass count.</li>
    <li><strong>Gates outside the hook and CI.</strong> Skills, agents and manual gauntlets that judge work are not atoms here yet.</li>
    <li><strong>Templates are read from invocation shape.</strong> Two checks called the same way may defend different primitives; the split of the check bucket is where that shows first.</li>
  </ul>
  <p class="foot">Sources: <code>runtime/specs/gate-taxonomy.json</code>, <code>runtime/specs/gate-chains.json</code>, <code>_QUEUE/induced-backlog.jsonl</code>, <code>_PATTERNS/2026-11-17-gate-shadow-eval-prereg.md</code>. Generated by <code>scripts/gate_ladder_page.py</code> at {{generated_at}}.</p>
</section>

</main>
