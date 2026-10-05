"use client"

import { Analytics } from "@vercel/analytics/next"
import { SpeedInsights } from "@vercel/speed-insights/next"

// Share links carry their secret in the URL fragment (/shared/brief#<token>,
// /brief/share#<payload>). Strip any fragment before an event leaves the page,
// so the privacy of both links does not rest on the scripts' default URL capture.
function stripFragment<E extends { url: string }>(event: E): E {
  const i = event.url.indexOf("#")
  return i === -1 ? event : { ...event, url: event.url.slice(0, i) }
}

export function VercelTelemetry() {
  return (
    <>
      <Analytics beforeSend={stripFragment} />
      <SpeedInsights beforeSend={stripFragment} />
    </>
  )
}
