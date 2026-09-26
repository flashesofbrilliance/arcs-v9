'use client'

// Global error boundary. In the App Router this REPLACES the root layout when a
// render error escapes every nested boundary, so it must render its own <html>/<body>
// and must NOT depend on any app provider/context (that is precisely what breaks the
// synthetic /_global-error prerender with "Cannot read properties of null (useContext)").
// Self-contained + inline styles only (project rule), ARCS palette.

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#020408",
          color: "#e2e8f0",
          fontFamily:
            "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
        }}
      >
        <main
          style={{
            maxWidth: 420,
            padding: "2rem",
            textAlign: "center",
          }}
        >
          <p
            style={{
              margin: 0,
              fontSize: "0.75rem",
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              color: "#64748b",
            }}
          >
            The instrument lost signal
          </p>
          <h1
            style={{
              margin: "0.75rem 0 0.5rem",
              fontSize: "1.5rem",
              fontWeight: 500,
              color: "#f1f5f9",
            }}
          >
            Something went wrong.
          </h1>
          <p
            style={{
              margin: "0 0 1.5rem",
              fontSize: "0.9rem",
              lineHeight: 1.5,
              color: "#94a3b8",
            }}
          >
            The terrain didn&rsquo;t render. This is on our side, not yours. Try again,
            and if it keeps happening the fog is ours to clear.
          </p>
          <button
            type="button"
            onClick={() => reset()}
            style={{
              appearance: "none",
              cursor: "pointer",
              border: "1px solid #1e293b",
              background: "#0d1117",
              color: "#00F0FF",
              padding: "0.625rem 1.25rem",
              fontSize: "0.85rem",
              fontWeight: 500,
              borderRadius: 6,
            }}
          >
            Try again
          </button>
          {error?.digest ? (
            <p
              style={{
                margin: "1.5rem 0 0",
                fontSize: "0.7rem",
                color: "#475569",
                fontFamily: "ui-monospace, SFMono-Regular, monospace",
              }}
            >
              ref {error.digest}
            </p>
          ) : null}
        </main>
      </body>
    </html>
  )
}
