# Phosphor real-device protocol (15 minutes)

Purpose: replace emulation with what a person does on a real phone or tablet. Run it on the device the child actually uses (an iPhone or iPad, Safari). Nothing leaves the device. Bring a second adult or a phone to time it.

## Before (2 minutes, grown-up)
1. Open https://dj.arcs.care on the device. Press Start on the grown-up dialog. Choose Parent mode (hold the button for 1.5 s), open Grown-up controls, switch Play log on. Switch back to Kid mode.
2. Close all other apps. Volume at about a third. Headphones off.
3. Note the device, the browser and the date.

## With the child (8 minutes, do not explain anything)
Hand over the device and say only: "this makes music, try it." Start a timer. Do not touch the screen, do not point.
Record, in order, with the time on the timer:
- the first thing they tap, and the time of the first sound they hear (target: under 5 seconds);
- every time they stop and look at you, or say "what does this do";
- every tap that did nothing, or a control they tried to drag or pinch that did not respond;
- every time they leave the page, rotate the device, or open a menu by accident;
- which of these they find without help: a pad, a preset, the picture changing, the Pads tray, a song of their own;
- the moment they stop (put it down, hand it back, lose interest).
Allow a second child or a grown-up to join if it happens naturally; note who held the device.

## Grown-up task (3 minutes)
Hold the Parent button, open Mix, and lower the maximum of one effect. Time it from the start (target: under 60 seconds). Note where you hesitate.

## After (2 minutes)
1. Parent mode, Grown-up controls, Play log: Copy log. Paste it to yourself.
2. `pbpaste | python3 scripts/phosphor_playlog_summary.py` on the laptop (or save the text and pass the path).
3. Compare with the notes: time to first sound, preset taps against slider moves, where the session stopped, errors.
4. Write three lines: what delighted them, what confused them, what you would remove.

## What counts as a defect
Anything the child tried that did nothing, any accidental exit, any sound that was too loud, any flicker that made you or them look away, any text they could not read, any control they could not reach with a thumb. File each as a backlog row with the device and the time.

## Honest limits
One child on one device is an anecdote, not a result. Run it with at least five children across two devices before changing the design on the strength of it.
