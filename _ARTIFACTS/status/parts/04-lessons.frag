  <!-- 03 LESSONS -->
  <div class="section" data-tone="gold" data-tldr="Where I was wrong and what changed: delete before you rebuild, enforce don&#x27;t decorate, honesty over polish.">
    <div class="section-head">
      <div class="section-n">04</div>
      <div class="section-label" style="color:var(--gold);border-color:rgba(255,215,0,0.35);background:rgba(255,215,0,0.06);">SIX LESSONS THE BUILD PAID FOR</div>
    </div>
    <div class="section-title">Where I was wrong, and what changed because of it.</div>
    <div class="learn-rows">
      <div class="learn">
        <div class="learn-title">Rules without enforcement are decoration.</div>
        <div class="learn-body">An audit of my own project found that none of its written engineering rules were actually enforced. One rule had been violated since day one. The fix: align the checks with the rules, then make it structural. Now a finding can only be closed by a working enforcement mechanism or a signed, dated exception.</div>
      </div>
      <div class="learn">
        <div class="learn-title">The textbook security setup would have protected nothing.</div>
        <div class="learn-body">The standard database permission pattern looks right in review, but in this system the app connects with an account that bypasses those permissions entirely. I chose a stricter setup that actually holds, and wrote down exactly why the "correct looking" option was rejected.</div>
      </div>
      <div class="learn">
        <div class="learn-title">When behavior and promises drift apart, delete first.</div>
        <div class="learn-body">Visitors without accounts were having their data saved quietly. Legal, but not what the product promised. I removed the saving entirely first, then rebuilt it as an explicit opt-in, and updated the public <span class="term" data-def="A public page of specific, checkable promises about how the product handles people's data. Updated and versioned like code, so changes are visible.">trust page</span> to match.</div>
      </div>
      <div class="learn">
        <div class="learn-title">Design documents can make things up too.</div>
        <div class="learn-body">A major architecture proposal went through an independent challenge review before being accepted. The review caught four overclaims, including a cited theorem that does not exist. The corrected version shipped. The flattering version did not.</div>
      </div>
      <div class="learn">
        <div class="learn-title">Stopping a change is a decision, not a failure.</div>
        <div class="learn-body">A config migration was halted midway when it became clear that finishing it would silently drop live production settings added by parallel work. The stop, the reason, and the conditions to resume were all written down. No forced merge, no regression.</div>
      </div>
      <div class="learn">
        <div class="learn-title">Documents record the past. Production is the truth.</div>
        <div class="learn-body">My own notes claimed two domains ran on two different codebases. A live check showed they had quietly merged onto one. New standing rule: any claim about what production is doing gets verified against production before anyone acts on it.</div>
      </div>
    </div>
  </div>

