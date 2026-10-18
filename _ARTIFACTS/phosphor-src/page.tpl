<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<!-- @arcs-template: instrument-lab -->
<!-- @arcs-mode: operate -->
<title>Phosphor</title>
<style>
<!--@style.css-->
</style>
</head>
<body>
<main class="lane">
<header class="bar">
  <div class="mark"><b>ARCS</b> &nbsp;/&nbsp; Phosphor</div>
  <div class="row"><div class="mdsw" role="group" aria-label="Who is playing"><button class="btn" type="button" id="mdKid" aria-pressed="true">Kid</button><button class="btn" type="button" id="mdParent" aria-pressed="false" aria-describedby="mdhint">Parent</button></div><span class="vh" id="mdhint">Hold for one and a half seconds to open parent mode</span><button class="btn" id="glitchsw" type="button" aria-pressed="true" title="Glitch on or off. Off stops every glitch effect from starting.">Glitch on</button><button class="btn" id="skinb" type="button" aria-pressed="false">Pocket skin</button><button class="btn svchip" id="svchip" type="button" hidden aria-controls="wp" title="This window cannot keep your settings. Copy a waypoint to keep your place.">Not saved here</button><div class="stage">Stays on your computer</div></div>
</header>

<section class="hero" aria-labelledby="h1">
  <h1 id="h1">Music, drawn as <em>light</em>.</h1>
  <p class="lede">Pick a song. Press play. Watch it turn into light. Your song stays on your computer.</p>

  <div class="inst" role="group" aria-label="Visualizer">
  <div class="deck" id="deck">
    <div class="frame" id="frame">
      <span class="tag" id="tag">Scope</span>
      <button class="fsb zmb" id="zin" type="button" aria-label="Zoom in" style="right:60px"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M12 5v14M5 12h14" fill="none" stroke="currentColor" stroke-width="2"/></svg></button><button class="fsb zmb" id="zout" type="button" aria-label="Zoom out" style="right:112px"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M5 12h14" fill="none" stroke="currentColor" stroke-width="2"/></svg></button>
      <button class="fsb" id="fsb" type="button" aria-label="Full screen" aria-pressed="false"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg></button>
      <canvas id="cv" width="1280" height="360" aria-label="Audio visualization"></canvas>
      <div class="seqo" id="seqo">
        <div class="row"><button class="btn" type="button" id="hrun" aria-pressed="false">Run steps</button><button class="btn" type="button" id="hclr">Clear</button><label class="tpl" for="hsnap">Snap to</label><select class="txt" id="hsnap" style="width:auto"><option value="beat">Beat</option><option value="onset">Hits</option><option value="valley">Quiet spots</option><option value="edge">Slice edges</option></select></div>
        <div class="sqwrap" id="seqf"></div>
      </div>
      <div class="hud" id="hud">
        <button class="btn" type="button" id="hplay">Play</button>
        <input type="range" id="hscrub" min="0" max="1000" value="0" aria-label="Scrub playback">
        <span class="clock" id="hclock">0:00</span>
        <button class="btn" type="button" id="hexit">Exit</button><button class="btn" type="button" id="hej" hidden>Eject: hold 3 s</button>
        <div class="hudk">
          <button class="bb sm" type="button" data-km="0">Wiggle</button><button class="bb sm" type="button" data-km="1">Bars</button><button class="bb sm" type="button" data-km="2">Ring</button><button class="bb sm" type="button" data-km="3">Rainbow</button><button class="bb sm" type="button" data-km="4">Sun</button>
          <button class="bb sm" type="button" id="hcol">Colors</button><button class="bb sm" type="button" id="hzoom">Zoom</button><button class="bb sm" type="button" id="hwob">Wobble</button>
          <button class="bb sm" type="button" id="hsteps" data-min="3" aria-pressed="false">Steps</button><button class="bb sm" type="button" id="hperf" data-min="3" aria-pressed="false">~ Keys</button>
          <button class="bb sm sp" type="button" id="hspace">Space</button>
        </div>
      </div>
    </div>
  <p class="first" id="first">Press Play to hear the demo, or add your own song.</p>
  <div class="prog" id="prog" hidden><i></i></div>
  <div class="nkeys" id="nkeys" role="group" aria-label="Notes, keys 1 to equals" hidden></div>
  </div>
  <div class="genome" id="genome" data-min="2">
    <canvas id="gcv" width="760" height="100" role="img" aria-label="Genome ribbon: the song's DNA above the look's RNA, one codon per beat"></canvas>
    <div class="gtxt"><p class="hint" id="gline" aria-live="off">Play a song to read its genome.</p><button class="btn" type="button" id="grecipe">Copy recipe</button><button class="btn" type="button" id="wpopen" aria-controls="wp">Waypoint</button></div>
  </div>
  <div class="wp" id="wp" hidden>
    <p class="hint" id="wphint">A waypoint is your place: the look, level, steps and where you are in the song. Copy it to keep it, paste one to come back to it.</p>
    <textarea class="txt" id="wpbox" rows="4" spellcheck="false" aria-label="Waypoint text" placeholder="Paste a waypoint here"></textarea>
    <div class="row"><button class="btn" type="button" id="wpcopy">Copy waypoint</button><button class="btn" type="button" id="wpapply">Apply</button><button class="btn" type="button" id="wpclose">Close</button></div>
    <p class="hint" id="wpmsg" role="status"></p>
  </div>
  <div class="mixer" id="mixer" data-min="4">
    <div class="mxh"><span class="tpl">Mixer</span><span class="hint" id="mxa">Deck A is the song above.</span></div>
    <div class="row"><span class="tpl">Deck B</span><button class="btn" type="button" id="dbpick">Choose a file</button><input type="file" id="dbfile" accept="audio/*,video/*,.mp3,.m4a,.mp4,.wav,.aac,.ogg,.flac" hidden><span class="hint" id="dbinfo">Load a second song to mix.</span></div>
    <div class="sl"><button class="btn" type="button" id="dbplay">Play B</button><button class="btn" type="button" id="dbcue">Cue</button><button class="btn" type="button" id="dbsync">Sync</button><button class="btn" type="button" id="dbhalf">Half</button><button class="btn" type="button" id="dbdbl">Double</button><button class="btn" type="button" id="dbalign">Align</button><button class="btn" type="button" id="dbback">Back 10 ms</button><button class="btn" type="button" id="dbfwd">Forward 10 ms</button></div>
    <div class="mxf">
      <div><div class="ctl-label"><span>Deck A level</span><output id="mxlao">100</output></div><input type="range" id="mxla" min="0" max="100" step="1" value="100" aria-label="Deck A level"></div>
      <div><div class="ctl-label"><span>Crossfader</span><output id="mxxo">A</output></div><input type="range" id="mxx" min="-100" max="100" step="1" value="-100" aria-label="Crossfader, A on the left and B on the right"></div>
      <div><div class="ctl-label"><span>Deck B level</span><output id="mxlbo">100</output></div><input type="range" id="mxlb" min="0" max="100" step="1" value="100" aria-label="Deck B level"></div>
    </div>
    <div class="mxs">
      <div><div class="ctl-label"><span>Curve</span></div><div class="seg" role="radiogroup" aria-label="Crossfader curve"><input type="radio" name="mxc" id="mxc0" value="smooth" checked><label for="mxc0">Smooth</label><input type="radio" name="mxc" id="mxc1" value="sharp"><label for="mxc1">Sharp</label></div></div>
      <div><div class="ctl-label"><span>Picture follows</span></div><div class="seg" role="radiogroup" aria-label="Picture follows"><input type="radio" name="mxp" id="mxp0" value="A" checked><label for="mxp0">A</label><input type="radio" name="mxp" id="mxp1" value="mix"><label for="mxp1">Mix</label><input type="radio" name="mxp" id="mxp2" value="B"><label for="mxp2">B</label></div></div>
    </div>
    <canvas id="mxcv" width="760" height="84" role="img" aria-label="Both decks' DNA strands at their current beats, A above and B below"></canvas>
    <p class="hint" id="mxmsg" role="status">Sync changes B's pitch a little, because it plays faster or slower. There is no time-stretch and no key lock yet.</p>
  </div>
  <div class="pins" id="pins" data-min="2">
    <div class="mxh"><span class="tpl">Pins</span><label class="check" style="grid-template-columns:22px auto"><input type="checkbox" id="cuesOn"><span>Cues armed</span></label></div>
    <p class="hint">A pin saves this moment: the look and the rhythm around it, with a key that proves it was not changed. A note only remembers. A cue puts the look back when the song reaches it, and only when you arm it.</p>
    <div class="sl"><input class="txt" id="pinnote" type="text" maxlength="140" autocomplete="off" placeholder="Comment for this moment" aria-label="Comment for this pin" style="flex:1 1 200px;width:auto"><div class="seg" role="radiogroup" aria-label="Pin kind" style="width:auto"><input type="radio" name="pk" id="pk0" value="note" checked><label for="pk0">Note</label><input type="radio" name="pk" id="pk1" value="cue"><label for="pk1">Cue</label></div></div>
    <div class="sl"><label class="check" style="grid-template-columns:22px auto"><input type="checkbox" id="pinanchor"><span>Beat anchor (a true beat)</span></label><button class="btn" type="button" id="pinadd">Pin this moment</button><input class="txt" id="pinbeats" type="text" inputmode="numeric" placeholder="Beats between anchors: one number, or 16, 16, 16 for a tempo map (blank = estimate)" aria-label="Beats between anchors, a single number for the whole span or a comma list for a tempo map, blank to estimate" style="flex:1 1 220px;width:auto"><button class="btn" type="button" id="pinuse">Use anchors</button><button class="btn" type="button" id="pinmap">Make a tempo map</button></div>
    <ul class="pinlist" id="pinlist" aria-label="Pins for this song"></ul>
    <div class="sl"><button class="btn" type="button" id="pincopy">Copy pins</button><button class="btn" type="button" id="pinapply">Apply pasted pins</button></div>
    <textarea class="txt" id="pinbox" rows="3" spellcheck="false" aria-label="Pins text" placeholder="Paste pins here"></textarea>
    <p class="hint" id="pinmsg" role="status"></p>
  </div>
  <div class="seg" id="srcseg" data-lane="narrow" role="radiogroup" aria-label="Song or Sing">
    <input type="radio" name="src" id="srcA" value="song" checked><label for="srcA">Song</label>
    <input type="radio" name="src" id="srcB" value="sing"><label for="srcB">Sing</label>
  </div>
  <div class="singbox" id="singbox" hidden>
    <button class="rec" id="rec" type="button" data-s="off"><span class="recdot" id="recdot"></span><span id="reclbl">Sing</span></button>
    <div class="row"><button class="btn" id="undo" type="button">Undo</button><button class="btn" id="clr" type="button">Start over</button><button class="btn" id="ovr" type="button">Sing over this song</button><button class="btn" id="dbtrim" type="button">Start on the downbeat</button><button class="btn" id="clk" type="button" aria-pressed="false">Click</button><select class="txt" id="bpm" style="width:auto" aria-label="Click speed"><option value="80">80</option><option value="100" selected>100</option><option value="120">120</option></select></div>
    <p class="first" id="recmsg">Headphones work best, so the loop does not hear itself.</p>
  </div>
  <div class="kid" id="kid" data-src="song">
    <button class="bb" type="button" data-km="0">Wiggle</button><button class="bb" type="button" data-km="1">Bars</button><button class="bb" type="button" data-km="2">Ring</button><button class="bb" type="button" data-km="3">Rainbow</button><button class="bb" type="button" data-km="4">Sun</button>
    <button class="bb" type="button" id="kcol">Colors</button><button class="bb" type="button" id="kzoom">Zoom</button><button class="bb" type="button" id="kwob">Wobble</button><button class="bb" type="button" id="kfs">Big screen</button>
  </div>
  <div class="kid presets" id="presets" role="group" aria-label="Say a word">
    <button class="bb sm" type="button" data-pre="rain">Rain</button><button class="bb sm" type="button" data-pre="robot">Robot</button><button class="bb sm" type="button" data-pre="party">Party</button><button class="bb sm" type="button" data-pre="sleepy">Sleepy</button><button class="bb sm" type="button" data-pre="dino">Dino</button><button class="bb sm" type="button" data-pre="plain">Plain</button><button class="bb sm" type="button" id="notesb" aria-pressed="false">Notes</button>
  </div>
  <div class="stk" id="stk" role="list" aria-label="Stickers"></div>
  <p class="first" id="pkmode" hidden></p>
  <p class="first" id="toast" role="status" hidden></p>
  <details class="grown" id="grown" data-min="2">
    <summary>Grown-up controls</summary>
  <div class="chap" id="chap" aria-label="Chapters"></div>
  <div class="src">
    <div>
            <div class="row"><button class="btn" id="pick" type="button">Choose a file</button><button class="btn" id="twinb" type="button" disabled>Save as twin</button><button class="btn" id="midib" type="button" aria-pressed="false">MIDI</button></div>
            <p class="hint" id="midih" hidden></p>
            <div id="twinform" hidden>
              <div class="ctl-label"><label for="tt">Title</label></div><input class="txt" id="tt" type="text" autocomplete="off">
              <div class="ctl-label"><label for="tc">Credit line</label></div><input class="txt" id="tc" type="text" autocomplete="off" placeholder="Made with Suno">
              <div class="ctl-label"><label for="tl">Link (optional)</label></div><input class="txt" id="tl" type="url" autocomplete="off" placeholder="https://">
              <p class="hint" id="tprov"></p>
              <div class="row"><button class="btn" id="tsave" type="button">Save twin</button><button class="btn" id="tcancel" type="button">Cancel</button></div>
            </div>
            <input type="file" id="file" accept="audio/*,video/*,.mp3,.m4a,.mp4,.wav,.aac,.ogg,.flac" hidden>
            <p class="hint" style="margin-top:8px">Drop a file on the picture, or choose one. A twin saves the song and this player as one HTML file on your device.</p>
          </div>
  </div>

  <p class="readout" id="readout"><span class="ro"><b id="now">0% level</b> <span id="nowsub"></span></span><span class="ro">Chapter <b id="chnow">I</b> <span id="chsub"></span></span><span class="ro"><b id="src">Demo signal</b> <span id="srcsub"></span></span></p>
    <div class="panel" id="ctl">
      <details class="grp" name="grp" open data-min="2">
        <summary>Zoom</summary>
        <div class="gb">
          <div class="vh" aria-hidden="true">
            <input type="radio" name="mode" id="m0" value="0" checked tabindex="-1"><input type="radio" name="mode" id="m1" value="1" tabindex="-1"><input type="radio" name="mode" id="m2" value="2" tabindex="-1"><input type="radio" name="mode" id="m3" value="3" tabindex="-1"><input type="radio" name="mode" id="m4" value="4" tabindex="-1">
          </div>
          <div>
            <div class="ctl-label"><span>Mode and zoom</span><output id="zso">Scope 1 of 5</output></div>
            <div class="pads" id="pads" role="group" aria-label="Mode and zoom stage"></div>
            <p class="hint" style="margin-top:6px">Pick a mode by its name. Keypad columns match: swipe down one to zoom in.</p>
          </div>
        </div>
      </details>
      <details class="grp" name="grp" data-min="2">
        <summary>Resolution</summary>
        <div class="gb">
          <div>
            <div class="ctl-label"><label for="res">Resolution</label><output id="reso">vector</output></div>
            <input type="range" id="res" min="1" max="9" step="1" value="9">
          </div>
          <label class="check"><input type="checkbox" id="chsharp"><span>Chapters sharpen the picture, coarse to fine.</span></label>
          <div>
            <label class="check"><input type="checkbox" id="rloop"><span>Auto-loop resolution on the beat. Needs a tempo, falls back to 120 BPM.</span></label>
            <div class="ctl-label" style="margin-top:10px"><span>Loop length</span><output id="rlo">2 bars, up</output></div>
            <div class="seg" role="radiogroup" aria-label="Loop length">
              <input type="radio" name="rb" id="rb0" value="1"><label for="rb0">1 bar</label>
              <input type="radio" name="rb" id="rb1" value="2" checked><label for="rb1">2 bars</label>
              <input type="radio" name="rb" id="rb2" value="4"><label for="rb2">4 bars</label>
              <input type="radio" name="rb" id="rb3" value="8"><label for="rb3">8 bars</label>
            </div>
            <div class="seg" role="radiogroup" aria-label="Loop direction" style="margin-top:8px">
              <input type="radio" name="rd" id="rd0" value="up" checked><label for="rd0">Forward</label>
              <input type="radio" name="rd" id="rd1" value="down"><label for="rd1">Backward</label>
              <input type="radio" name="rd" id="rd2" value="pp"><label for="rd2">Forward and back</label>
            </div>
          </div>
        </div>
      </details>
      <details class="grp" name="grp" data-min="2">
        <summary>Look</summary>
        <div class="gb">
          <label class="check"><input type="checkbox" id="calm" checked><span>Calm: limits how fast bars and rings can jump. Turn off for fast, live playing.</span></label>
          <div>
            <div class="ctl-label"><span>Curve</span><output id="cuo">linear</output></div>
            <div class="seg" role="radiogroup" aria-label="Curve">
              <input type="radio" name="cu" id="cu0" value="lin" checked><label for="cu0">Linear</label>
              <input type="radio" name="cu" id="cu1" value="log"><label for="cu1">Log</label>
              <input type="radio" name="cu" id="cu2" value="exp"><label for="cu2">Exp</label>
              <input type="radio" name="cu" id="cu3" value="s"><label for="cu3">S</label>
            </div>
            <input type="range" id="cua" min="0" max="100" step="1" value="0" aria-label="Curve amount">
          </div>
          <div>
            <div class="ctl-label"><label for="palsel">Palette swap</label></div>
            <select class="txt" id="palsel"><option value="orig">Original</option><option value="arcs">ARCS</option><option value="phosphor">Phosphor green</option><option value="amber">Amber CRT</option><option value="indigo">Indigo and paper</option><option value="heat">Heat</option><option value="mono">Mono</option></select>
          </div>
          <label class="check"><input type="checkbox" id="inv"><span>Invert (key I)</span></label>
          <div>
            <div class="ctl-label"><label for="pal">Tones</label><output id="palo">8 bit, off</output></div>
            <input type="range" id="pal" min="1" max="8" step="1" value="8">
            <div class="seg" role="radiogroup" aria-label="Tone method" style="margin-top:8px">
              <input type="radio" name="pm" id="pP" value="plain" checked><label for="pP">Plain steps</label>
              <input type="radio" name="pm" id="pW" value="wood"><label for="pW">Woodblock</label>
            </div>
          </div>
          <label class="check"><input type="checkbox" id="crt"><span>CRT lines</span></label>
        </div>
      </details>
      <details class="grp" name="grp" data-min="3">
        <summary>Glitch</summary>
        <div class="gb">
          <div class="row" id="gpre" role="group" aria-label="Glitch presets"><button class="btn" type="button" data-gp="water">Underwater</button><button class="btn" type="button" data-gp="robot">Robot</button><button class="btn" type="button" data-gp="tv">Broken TV</button><button class="btn" type="button" data-gp="space">Space echo</button><button class="btn" type="button" data-gp="heavy">Heavy</button><button class="btn" type="button" data-gp="clean">Clean</button></div>
          <p class="hint" id="gphint">Pick a look and sound. Tap it again to turn it off.</p>
          <label class="check"><input type="checkbox" id="perf"><span>Perform keys (backtick). Hold: Z stutter, X freeze, C tear, V RGB split, B blocks.</span></label>
          <div class="row" id="gpads">
            <button class="btn" type="button" data-g="stutter">Stutter</button><button class="btn" type="button" data-g="freeze">Freeze</button><button class="btn" type="button" data-g="tear">Tear</button><button class="btn" type="button" data-g="rgb">RGB</button><button class="btn" type="button" data-g="blocks">Blocks</button><button class="btn" type="button" data-g="crush">Crush</button><button class="btn" type="button" data-g="dist">Distort</button><button class="btn" type="button" data-g="echo">Echo</button><button class="btn" type="button" data-g="room">Room</button><button class="btn" type="button" data-g="shim">Shimmer</button><button class="btn" type="button" data-g="sweep">Sweep</button><button class="btn" type="button" data-g="gold">Gold</button><button class="btn" type="button" data-g="gate" title="Hold to run the rhythm gate (key G). With Latch it stays on.">Gate</button><button class="btn" type="button" id="glatch" aria-pressed="false" title="Latch: a press stays on until you press it again, so effects stack">Latch</button>
          </div>
          <div>
            <div class="ctl-label"><span>Rhythm gate</span><output id="fxgo">off, always on</output></div>
            <div class="seg" role="radiogroup" aria-label="Gate">
              <input type="radio" name="fxg" id="fg0" value="off" checked><label for="fg0">Off</label>
              <input type="radio" name="fxg" id="fg1" value="level"><label for="fg1">Loud hits</label>
              <input type="radio" name="fxg" id="fg2" value="beat"><label for="fg2">Square</label>
              <input type="radio" name="fxg" id="fg3" value="tri"><label for="fg3">Triangle</label>
              <input type="radio" name="fxg" id="fg4" value="bar"><label for="fg4">Downbeat</label>
              <input type="radio" name="fxg" id="fg5" value="seed"><label for="fg5">Song rhythm</label>
            </div>
            <div class="ctl-label" style="margin-top:8px"><label for="fxdep">Gate depth</label><output id="fxdepo">100%</output></div>
            <input type="range" id="fxdep" min="0" max="100" step="1" value="100" aria-label="Gate depth, how far the effect level drops">
            <div class="ctl-label" style="margin-top:8px"><label for="fxlag">Lay back</label><output id="fxlago">on the beat</output></div>
            <input type="range" id="fxlag" min="0" max="35" step="1" value="0" aria-label="Lay back, how far behind the beat the gate edges fall">
            <input type="range" id="fxthr" min="-40" max="-6" step="1" value="-20" aria-label="Loudness threshold in decibels" style="margin-top:8px">
            <div class="seg" role="radiogroup" aria-label="Gate rate" style="margin-top:8px">
              <input type="radio" name="fxd" id="fdq" value="1"><label for="fdq">1/4</label>
              <input type="radio" name="fxd" id="fd0" value="2"><label for="fd0">1/8</label>
              <input type="radio" name="fxd" id="fd1" value="4" checked><label for="fd1">1/16</label>
              <input type="radio" name="fxd" id="fd2" value="8"><label for="fd2">1/32</label>
            </div>
          </div>
          <div>
            <div class="ctl-label"><label for="gamt">Amount</label><output id="gamo">60%</output></div>
            <input type="range" id="gamt" min="5" max="100" step="1" value="60">
          </div>
          <div>
            <div class="ctl-label"><span>Picture strength</span><output id="gsto">Soft</output></div>
            <div class="seg" role="radiogroup" aria-label="Picture strength">
              <input type="radio" name="gst" id="gs0" value="1" checked><label for="gs0">Soft</label>
              <input type="radio" name="gst" id="gs1" value="2"><label for="gs1">Medium</label>
              <input type="radio" name="gst" id="gs2" value="3.5"><label for="gs2">Strong</label>
            </div>
            <p class="hint">A flash limit is always on: no more than two flashes a second, and it steps back to Soft if the picture starts to flash.</p>
          </div>
          <div>
            <div class="ctl-label"><span>Stutter size</span><output id="gmo">off</output></div>
            <div class="seg" role="radiogroup" aria-label="Stutter size">
              <input type="radio" name="ss" id="ss0" value="0.0625"><label for="ss0">1/16 beat</label>
              <input type="radio" name="ss" id="ss1" value="0.125" checked><label for="ss1">1/8 beat</label>
              <input type="radio" name="ss" id="ss2" value="0.25"><label for="ss2">1/4 beat</label>
            </div>
          </div>
        </div>
      </details>
      <details class="grp" name="grp" data-min="3">
        <summary>Steps</summary>
        <div class="gb">
          <label class="check"><input type="checkbox" id="sqon"><span>Run the steps while the song plays.</span></label>
          <div class="sqwrap" id="seqg"></div>
          <div>
            <div class="ctl-label"><span>Snap to</span><output id="sqo">beat</output></div>
            <div class="seg" role="radiogroup" aria-label="Snap to">
              <input type="radio" name="sqq" id="sq0" value="beat" checked><label for="sq0">Beat</label>
              <input type="radio" name="sqq" id="sq1" value="onset"><label for="sq1">Hits</label>
              <input type="radio" name="sqq" id="sq2" value="valley"><label for="sq2">Quiet</label>
              <input type="radio" name="sqq" id="sq3" value="edge"><label for="sq3">Slice edges</label>
            </div>
          </div>
          <div>
            <div class="ctl-label"><span>Feel</span><output id="swo">straight</output></div>
            <div class="seg" role="radiogroup" aria-label="Feel">
              <input type="radio" name="sw" id="sw0" value="50" checked><label for="sw0">Straight</label>
              <input type="radio" name="sw" id="sw1" value="58"><label for="sw1">Light</label>
              <input type="radio" name="sw" id="sw2" value="67"><label for="sw2">Shuffle</label>
              <input type="radio" name="sw" id="sw3" value="75"><label for="sw3">Hard</label>
            </div>
            <p class="hint">Delays every other step. Shuffle is the triplet feel.</p>
          </div>
          <div>
            <div class="ctl-label"><span>Tighten my notes</span><output id="tzo">as played</output></div>
            <input type="range" id="tz" min="0" max="100" step="1" value="0" aria-label="Tighten my notes">
            <p class="hint">Moves a note press toward the next step. At the top it lands exactly on the groove.</p>
          </div>
          <div>
            <div class="ctl-label"><span>Stays on</span></div>
            <div class="seg" role="radiogroup" aria-label="Stays on">
              <input type="radio" name="sqg" id="sg0" value="0.25"><label for="sg0">Short</label>
              <input type="radio" name="sqg" id="sg1" value="0.5" checked><label for="sg1">Half</label>
              <input type="radio" name="sqg" id="sg2" value="1"><label for="sg2">Full</label>
            </div>
            <div class="seg" role="radiogroup" aria-label="Loop length" style="margin-top:8px">
              <input type="radio" name="sqb" id="sb0" value="1" checked><label for="sb0">1 bar</label>
              <input type="radio" name="sqb" id="sb1" value="2"><label for="sb1">2 bars</label>
              <input type="radio" name="sqb" id="sb2" value="4"><label for="sb2">4 bars</label>
            </div>
          </div>
          <div class="row"><button class="btn" type="button" id="sqclr">Clear steps</button><button class="btn tapb" type="button">Tap tempo</button><button class="btn dbb" type="button">Downbeat here</button></div>
          <p class="hint">Tap a square to add an effect on that step. The Zoom row counts up through the zoom stages. Snap to decides where the step really lands: on the beat, on a hit in the song, in a quiet spot, or on the edge of a slice you cut.</p>
        </div>
      </details>
      <details class="grp" name="grp" id="kmap" data-min="4">
        <summary>Keys</summary>
        <div class="gb">
          <p class="hint">Space play. F full screen. 1 to 4 mode. Brackets resolution. Left and right arrows palette. Comma and period jump to snap points.</p>
          <div class="row"><button class="btn" type="button" id="sessrec" aria-pressed="false">Record my session</button><button class="btn" type="button" id="forget">Forget everything saved here</button></div>
          <p class="hint" id="sesshint">Saves a video with sound and a list of what you touched to your Downloads. Nothing is uploaded.</p>
          <label class="check"><input type="checkbox" id="fullvol"><span>Full volume for grown-ups. Turns off the kids' volume limit.</span></label>
          <p class="hint" id="lastkey">Press any key to see its code.</p>
          <div class="row"><button class="btn" type="button" id="plogb">Copy play log</button><button class="btn" type="button" data-learn="0">Learn Scope</button><button class="btn" type="button" data-learn="1">Learn Bars</button><button class="btn" type="button" data-learn="2">Learn Radial</button><button class="btn" type="button" data-learn="3">Learn Spectro</button><button class="btn" type="button" id="resetkeys">Reset keys</button></div>
          <p class="hint" id="learnhint"></p>
        </div>
      </details>
    </div>
  </details>
  </div>

  <div class="sheet" data-min="4">
    <h2>The next eight bars</h2>
    <div class="sl" style="margin-top:0"><button class="btn" type="button" id="barplay" aria-pressed="false">Play preview</button><span class="hint" id="barinfo">Load a song to see its next eight bars.</span></div>
    <canvas id="barview" width="256" height="144" role="img" aria-label="Stop-motion preview of the next eight bars"></canvas>
    <div class="bars" id="bars"></div>
    <p class="note" id="barnote">Each picture is the song at the start of one of the next eight bars, drawn with your current look. A mark shows a pin inside that bar. Click a picture to jump there. It shows the look you have now, not moves you have not made yet.</p>
    <details class="lesson"><summary>Resolution lesson</summary>
    <div class="rungs" id="rungs"></div>
    <p class="note" id="rungnote">Each picture is the current frame at that rung. Above 480p the small pictures look alike.</p></details>
  </div>
</section>

<section class="alts" aria-label="Details">
  <details class="alt" id="slices" data-min="4">
    <summary><span class="alt-n">Sampler</span><span class="alt-t">Slices and snap points</span><span class="alt-go" aria-hidden="true">+</span><span class="alt-s">Cut the song where a cut sounds clean, then see which slices flow into each other.</span></summary>
    <div class="alt-body">
      <canvas id="strip" class="strip" width="1200" height="88" tabindex="0" aria-label="Slice strip. Drag to cut a slice. Comma and period jump between snap points. Enter marks a slice start, then end."></canvas>
      <div class="sl" id="zoomrow">
        <button class="btn" type="button" id="szout">Zoom out</button><button class="btn" type="button" id="szin">Zoom in</button><button class="btn" type="button" id="zfit">Whole song</button>
        <input type="range" id="zpan" min="0" max="1000" step="1" value="0" aria-label="Move the view" style="flex:1 1 160px;width:auto">
        <span class="hint" id="zlab"></span>
      </div>
      <div class="sl" id="autorow">
        <div class="seg" role="radiogroup" aria-label="How many slices" style="min-width:240px;flex:0 1 280px">
          <input type="radio" name="ahn" id="ah0" value="8"><label for="ah0">Few</label>
          <input type="radio" name="ahn" id="ah1" value="16" checked><label for="ah1">Some</label>
          <input type="radio" name="ahn" id="ah2" value="32"><label for="ah2">Many</label>
        </div>
        <button class="btn" type="button" id="ash">Slice at hits</button>
        <div class="seg" role="radiogroup" aria-label="Note length" style="min-width:240px;flex:0 1 280px">
          <input type="radio" name="abd" id="ab0" value="1"><label for="ab0">1/4</label>
          <input type="radio" name="abd" id="ab1" value="2" checked><label for="ab1">1/8</label>
          <input type="radio" name="abd" id="ab2" value="4"><label for="ab2">1/16</label>
        </div>
        <button class="btn" type="button" id="asb">Slice on the beat</button>
      </div>
      <div class="sl" id="tmrow">
        <button class="btn tapb" type="button">Tap tempo</button><button class="btn dbb" type="button">Downbeat here</button>
        <label class="tpl" for="sbpm">Song BPM</label><input class="txt" id="sbpm" type="number" min="40" max="240" step="1" style="width:92px">
        <label class="tpl" for="tbpm">Play at BPM</label><input class="txt" id="tbpm" type="number" min="40" max="240" step="1" style="width:92px">
        <button class="btn" type="button" id="spl">Play slices at that tempo</button>
      </div>
      <div class="sl" id="bcrow">
        <button class="btn" type="button" id="bcb" aria-pressed="false">Hear the beat</button><button class="btn" type="button" id="bchalf">Half</button><button class="btn" type="button" id="bcdbl">Double</button><button class="btn" type="button" id="bcearly">Earlier</button><button class="btn" type="button" id="bclate">Later</button>
        <span class="hint" id="bcinfo"></span>
      </div>
      <p class="hint" id="sphint">Auto slice and tempo play work on the part of the song you can see. Tempo play keeps the pitch and moves the slices, like ReCycle.</p>
      <div class="sl" id="sl">
        <div class="seg" role="radiogroup" aria-label="Snap strength" style="min-width:300px;flex:0 1 360px">
          <input type="radio" name="snap" id="s0" value="0"><label for="s0">Off</label>
          <input type="radio" name="snap" id="s1" value="0.06"><label for="s1">Soft</label>
          <input type="radio" name="snap" id="s2" value="0.12" checked><label for="s2">Medium</label>
          <input type="radio" name="snap" id="s3" value="0.2"><label for="s3">Strong</label>
        </div>
        <button class="btn" type="button" id="solve">Solve order</button>
        <button class="btn" type="button" id="clearsl">Clear</button>
        <span class="hint" id="slhint">Drag on the strip to cut a slice. Hold Alt to skip the magnets.</span>
      </div>
      <div class="sl" id="slist" aria-label="Slices"></div>
      <p class="mag" id="magro"></p>
    </div>
  </details>
  <details class="alt" data-min="2">
    <summary><span class="alt-n">Depth</span><span class="alt-t">How it works</span><span class="alt-go" aria-hidden="true">+</span><span class="alt-s">Analysis, determinism, the ladder, and what stays on your device.</span></summary>
    <div class="alt-body">
      <p>The page decodes your file with the browser, mixes it to mono, and measures it once: a 2048-point FFT at 30 frames a second, 64 bands from 40 Hz to 16 kHz on a log scale, a loudness value, and a measure of how much the spectrum changes between frames. A novelty curve compares the 8 seconds before each moment with the 8 seconds after; its peaks are the chapters.</p>
      <p>After that, every picture is a pure function of those measurements and the time. Nothing is stored in the picture, so scrubbing back gives exactly the same frame. Playback follows the audio clock, so sound and picture stay together.</p>
      <p>The ladder runs from a single pixel, which is the average of the frame, through 256 by 144 (the 8-bit rung) up to 7680 by 4320, and ends at vector, where the scene is drawn analytically with no pixel grid. While playing, the picture is drawn at 1920 by 1080 at most; when you pause, it is redrawn once at the rung you chose, if your device can make a canvas that large.</p>
      <p>Your file is read in this page and nowhere else. It is not uploaded, and no audio is stored in this page.</p>
    </div>
  </details>
</section>

<footer>
  <p id="foot1">The default demo signal is generated in this page from sine waves and noise. It is not a recording.</p>
  <p>Not a MilkDrop-style shader engine: these are four drawing modes over the measured spectrum.</p>
</footer>
</main>
<div id="dock" role="region" aria-label="Player">
  <div class="dkmain">
    <button class="dkplay" type="button" id="play">Play</button>
    <div class="lcd"><div class="lcdrow"><i class="led" id="dled"></i><div class="lcdtxt"><div class="lcdt" id="dtitle"></div><div class="lcds" id="dspec"></div></div><span class="lcdtime clock" id="clock">0:00 / 0:00</span></div></div>
    <button class="btn dkup" type="button" id="kpick">Add song</button>
  </div>
  <div class="dkscrub"><input type="range" id="scrub" min="0" max="1000" value="0" aria-label="Scrub playback"><div class="pinbar" id="pinbar" aria-hidden="true"></div></div>
  <div class="dkrow"><button class="btn dkhide" type="button" id="dkhide" aria-label="Hide the player">Hide</button><button class="btn" type="button" id="dkfx" aria-expanded="false" aria-controls="fxtray" data-min="4">Mix</button><button class="btn dkej" type="button" id="eject" aria-pressed="false" title="Hold for 3 seconds to lock or unlock Kid mode full screen">Eject: hold 3 s</button><button class="btn" type="button" id="back" hidden>Back</button><button class="btn" type="button" id="fwd" hidden>Forward</button><span class="hint" role="status" id="status"></span></div>
</div>
<div id="fxtray" role="group" aria-label="Effect levels and limits" data-min="4" hidden></div>
<div id="consent" role="dialog" aria-modal="true" aria-labelledby="cstitle" hidden>
  <div class="csbox">
    <h2 id="cstitle">Before you start</h2>
    <p>Phosphor turns a song into moving light. The songs you pick and everything you play stay on this device. Nothing is sent anywhere or counted.</p>
    <p><b>Loud sound.</b> Start with the volume low, especially with headphones.</p>
    <p><b>Flashing light.</b> Some effects flash. A limit keeps them under three flashes a second, but if you or your child are sensitive to flashing light, turn Glitch off at the top of the page or skip it.</p>
    <p><b>Grown-ups first.</b> A grown-up should press Start. Kid mode keeps little hands away from the grown-up controls.</p>
    <button class="btn csgo" type="button" id="csgo">I am a grown-up. Start.</button>
  </div>
</div>
<button class="btn" type="button" id="dkbump" aria-label="Show the player">Player</button>
<script>
<!--@app.js-->
</script>
</body>
</html>
