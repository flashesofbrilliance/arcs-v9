<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{{TITLE}}</title>
<style>
{{TOKENS}}
{{BOARD_CSS}}
{{VARIANT_CSS}}
</style>
</head>
<body>
<main class="ob-wrap">
<header class="ob-head">
<p class="ob-label">Option board · {{SUBJECT}}</p>
<h1>{{TITLE}}</h1>
<p class="ob-lede">{{LEDE}}</p>
<p class="ob-howto">Click one option per block (click again to clear). A block you leave unpicked stays as it is now. Move the dials, then send or copy your picks from the bar at the bottom.</p>
</header>
{{DIALS}}
{{BLOCKS}}
</main>
<div class="ob-bar" role="region" aria-label="Your picks">
<div class="ob-bar-in">
<p class="ob-summary" id="ob-summary" aria-live="polite">No picks yet.</p>
<button type="button" class="ob-btn primary" id="ob-send">Send my picks</button>
<button type="button" class="ob-btn" id="ob-copy">Copy my picks</button>
</div>
</div>
<script type="application/json" id="ob-spec">{{SPEC_JSON}}</script>
<script>
{{BOARD_JS}}
</script>
</body>
</html>
