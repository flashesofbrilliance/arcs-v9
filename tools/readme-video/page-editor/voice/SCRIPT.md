# Live page editor walkthrough narration

One section per card. Each must equal that card's `v` in build.cjs (rule R0). Source: src/ui-kit/tabbed-brief/README.md, Tuning by hand (internal only). Audience: Zach, as a cold learner. Register: inquisitive, erudite, minimal, laconic.

## 01

A live page editor. Move the sliders and edit the text on the page itself. A built page is never edited by hand, so the change goes to its source. Two ways in: the builder, or the bookmarklet.

## 02

Route one. Run the page’s builder with the tune flag. It writes an internal copy, and refuses the public folder. Serve that folder, then open the copy with tune and edit in the address. The same two flags work on every page builder.

## 03

Double-click text to edit it. Move the sliders. Then copy what changed: the edits, the JSON patch, the CSS line, or a breadcrumb’s versions. Save it to a file, and run the same builder with apply. It validates, then rebuilds. If any part is refused, nothing is written.

## 04

Where does each change land? Text goes back to the first source that holds it. Tokens and wrapping go to the place the builder names, usually a tuned block; a page with no tuner tokens refuses them. Computed text is in no source, so it is refused, and named.

## 05

Route two. Run tune serve, open its local page, and drag the bookmarklet to your bookmarks bar. Click it on any page; the page never carries the tuner. Copy your edits, then apply them by URL. Built by a script? It refuses, and names the script.

## 06

What stops a bad write? Old text must be found exactly once in the source, or nothing is written. The page gate, in counterpart mode, fails any page that still carries the tuner. And a moved container width is reported, set in source by hand. It is not written.
