/**
 * The subtenant roster for the live field board on status.arcs.care.
 *
 * These are all `*.arcs.care` hosts declared as host-rewrites in next.config.ts.
 * They are NOT separate deployments — every one is served by the single arcs-v9
 * Vercel production deployment via a rewrite. So the board shows ONE shared
 * deploy state (from /api/field's Vercel call) and per-host LIVENESS here.
 *
 * Keep in sync with next.config.ts `beforeFiles` host rules. `group` only drives
 * visual clustering on the board; `label` is the display name.
 */
export interface FieldHost {
  host: string;
  label: string;
  group: string;
}

export const FIELD_HOSTS: FieldHost[] = [
  // Public / core
  { host: "app.arcs.care", label: "app · the product", group: "core" },
  { host: "arcs.care", label: "arcs.care", group: "core" },
  { host: "status.arcs.care", label: "status · this page", group: "core" },
  { host: "chan.arcs.care", label: "chan", group: "core" },
  { host: "resume.arcs.care", label: "resume", group: "core" },

  // Omakase / venue
  { host: "omakase.arcs.care", label: "omakase", group: "omakase" },
  { host: "louisville.arcs.care", label: "louisville", group: "omakase" },
  { host: "jeben.arcs.care", label: "jeben", group: "omakase" },

  // Yuri family
  { host: "yuri.arcs.care", label: "yuri", group: "yuri" },
  { host: "yuri-codex.arcs.care", label: "yuri · codex", group: "yuri" },
  { host: "yuri-diamond.arcs.care", label: "yuri · diamond", group: "yuri" },
  { host: "yuri-receipt.arcs.care", label: "yuri · receipt", group: "yuri" },
  { host: "yuri-profile.arcs.care", label: "yuri · profile", group: "yuri" },
  { host: "yuri-recoil.arcs.care", label: "yuri · recoil", group: "yuri" },
  { host: "yuri-war.arcs.care", label: "yuri · war", group: "yuri" },
  { host: "yuri-ext.arcs.care", label: "yuri · ext", group: "yuri" },
  { host: "yuri-demo.arcs.care", label: "yuri · demo", group: "yuri" },
  { host: "yuri-sample.arcs.care", label: "yuri · sample", group: "yuri" },

  // Robin family
  { host: "robin.arcs.care", label: "robin", group: "robin" },
  { host: "robin-codex.arcs.care", label: "robin · codex", group: "robin" },
  { host: "robin-receipt.arcs.care", label: "robin · receipt", group: "robin" },
  { host: "robin-profile.arcs.care", label: "robin · profile", group: "robin" },

  // Joe family
  { host: "joe.arcs.care", label: "joe", group: "joe" },
  { host: "joe-ext.arcs.care", label: "joe · ext", group: "joe" },
  { host: "joe-war.arcs.care", label: "joe · war", group: "joe" },

  // Julia family
  { host: "julia.arcs.care", label: "julia", group: "julia" },
  { host: "julia-ext.arcs.care", label: "julia · ext", group: "julia" },

  // Todd / PRL
  { host: "todd-call.arcs.care", label: "todd-call", group: "todd" },
  { host: "prl.arcs.care", label: "prl", group: "todd" },

  // Ahmed
  { host: "ahmed.arcs.care", label: "ahmed", group: "ahmed" },
  { host: "ahmed-ext.arcs.care", label: "ahmed · ext", group: "ahmed" },

  // Other counterparts / call briefs
  { host: "daniel.arcs.care", label: "daniel", group: "briefs" },
  { host: "danny.arcs.care", label: "danny", group: "briefs" },
  { host: "peter.arcs.care", label: "peter", group: "briefs" },
  { host: "vishal.arcs.care", label: "vishal", group: "briefs" },
  { host: "kelly-interview.arcs.care", label: "kelly", group: "briefs" },
  { host: "labella.arcs.care", label: "labella", group: "briefs" },
  { host: "labelle.arcs.care", label: "labelle", group: "briefs" },
  { host: "jalaja.arcs.care", label: "jalaja", group: "briefs" },
  { host: "ayesha.arcs.care", label: "ayesha", group: "briefs" },
  { host: "kiko.arcs.care", label: "kiko", group: "briefs" },
  { host: "lewoof.arcs.care", label: "lewoof", group: "briefs" },
  { host: "thetrueai.arcs.care", label: "thetrueai", group: "briefs" },
];
