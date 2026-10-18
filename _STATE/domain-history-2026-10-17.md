# Domain-to-project history (Vercel), read 2026-10-17

Source: Vercel project domain lists for the two projects, `createdAt` per domain (the date the domain was attached to that project), via the Vercel API. Dates are UTC. An attach date is NOT the date DNS first pointed at Vercel and says nothing about what was served; it bounds when the project could first answer on that name.

## Projects
| Project | Domains today | First domain attached |
|---|---|---|
| arcs-v9 (prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9) | 99 | arcs-v9.vercel.app on 2026-06-02T21:07Z (the project's own creation time) |
| arcs-care (prj_cVMjIW1ElkddeqdyowuQi34P7KIs) | 1 (arcs-care.vercel.app only) | 2026-05-04T17:25Z |

The older arcs-care project has no custom domain today. Any custom domain it answered on in May 2026 has since been removed or moved: UNVERIFIED which, and when. The apex and www names were attached to arcs-v9 on 2026-06-13.

## Key attach dates on arcs-v9
| Name | Attached to arcs-v9 |
|---|---|
| arcs-v9.vercel.app | 2026-06-02T21:07Z |
| app.arcs.care | 2026-06-03T16:17Z |
| resume.arcs.care | 2026-06-05T19:46Z |
| www.arcs.care and arcs.care (308 to www) | 2026-06-13T16:53Z |
| chan.arcs.care | 2026-07-16T23:06Z |
| status.arcs.care | 2026-07-17T16:35Z |
| playground.arcs.care, monolith.arcs.care | 2026-08-11T16:49Z |
| good.arcs.care, germinate.arcs.care, rosetta-shell.arcs.care, arcs-field-scan.arcs.care | 2026-08-16T16:21Z |
| build.arcs.care | 2026-08-16T18:34Z |
| wing.arcs.care | 2026-08-21T03:26Z |
| blacksmith.arcs.care | 2026-09-02T17:14Z |
| vico.arcs.care | 2026-09-17T20:20Z |

## What this settles and what it does not
- **Settles (VERIFIED):** the oldest possible arcs-v9 deployment is the project's creation, 2026-06-02T21:07Z, so a deployment on 2026-05-28 cannot belong to arcs-v9 unless the project was deleted and recreated (not excluded). That supports belief FB3 (the 05-28 note is an arcs-care mix-up); the 05-28 production deployments belong to the arcs-care project.
- **Settles (VERIFIED):** app.arcs.care first pointed at arcs-v9 on 2026-06-03, matching the first deployments.
- **Does not settle:** which name served the May 2026 arcs-care deployments; what any name served before its attach date; DNS dates. Ask Zach or check the DNS provider history.
- **Note:** the playground and monolith names were attached on 2026-08-11, but the files they route to were committed earlier (the pf pages on 2026-07-15). Per the public-files note, files in `public/` are fetchable by filename on any attached host once deployed, so the 2026-07-15 deployment is the earlier serving bound for those pages, not the subdomain date.
