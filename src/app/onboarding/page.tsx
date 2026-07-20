"use client"

import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { surface, text, border } from "@/ui/tokens"
import { Wordmark } from "@/ui/Wordmark"
import { Button } from "@/ui/Button"

// Onboarding upload step — <30s, skippable (ADR-029). Store-only: no
// generation pipeline reads these files yet. The dashboard nudges anyone who
// hasn't completed or explicitly skipped, via a status check against
// GET /api/onboarding/upload.
//
// PDF is required, export is optional (per toolbar feedback DxUNiOM8XDu8 —
// previously either field alone unblocked submit, and once any upload
// existed the dashboard nudge never returned, leaving no way back in to add
// the missing piece). If the PDF is already on record (e.g. arriving via the
// dashboard's "Add export" nudge), that requirement is already satisfied.
export default function OnboardingPage() {
  const router = useRouter()
  const [pdf, setPdf] = useState<File | null>(null)
  const [exportZip, setExportZip] = useState<File | null>(null)
  const [pdfAlreadyOnFile, setPdfAlreadyOnFile] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch("/api/onboarding/upload")
      .then((r) => (r.ok ? r.json() : null))
      .then((s) => { if (s?.hasPdf) setPdfAlreadyOnFile(true) })
      .catch(() => {})
  }, [])

  const hasPdfRequirement = pdfAlreadyOnFile || !!pdf

  async function handleUpload() {
    if (!hasPdfRequirement) return
    setBusy(true)
    setError(null)
    try {
      const form = new FormData()
      if (pdf) form.append("pdf", pdf)
      if (exportZip) form.append("export", exportZip)
      const res = await fetch("/api/onboarding/upload", { method: "POST", body: form })
      if (!res.ok) throw new Error("upload failed")
      router.push("/dashboard")
    } catch {
      setError("Upload failed. You can try again from the dashboard later.")
      setBusy(false)
    }
  }

  async function handleSkip() {
    setBusy(true)
    try {
      await fetch("/api/onboarding/upload", { method: "PATCH" })
    } finally {
      router.push("/dashboard")
    }
  }

  return (
    <div style={{ background: surface.bg, minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
      <div style={{ maxWidth: 460, width: "100%" }}>
        <div style={{ marginBottom: 28 }}>
          <Wordmark />
        </div>

        <h1 style={{ fontSize: 22, fontWeight: 600, color: text.primary, margin: "0 0 8px" }}>
          Set up your profile
        </h1>
        <p style={{ fontSize: 14, color: text.secondary, lineHeight: 1.6, margin: "0 0 24px" }}>
          Takes under 30 seconds. Add your LinkedIn profile PDF. The full data export is
          optional and can be added anytime, including later from the dashboard. Skip now and
          do this anytime from the dashboard.
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: 14, marginBottom: 20 }}>
          <label style={{ display: "block", border: `1px solid ${border.subtle}`, borderRadius: 10, padding: "14px 16px", background: surface.panel, cursor: "pointer" }}>
            <div style={{ fontSize: 13, fontWeight: 500, color: text.primary, marginBottom: 4 }}>
              LinkedIn profile PDF{!pdfAlreadyOnFile && <span style={{ color: "#FF4D6D" }}> *</span>}
            </div>
            <div style={{ fontSize: 12, color: text.dimmed, marginBottom: pdf ? 8 : 0 }}>
              {pdf ? pdf.name : pdfAlreadyOnFile ? "Already on file. Upload again to replace it" : "From LinkedIn → your profile → “Save to PDF”"}
            </div>
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => setPdf(e.target.files?.[0] ?? null)}
              style={{ display: "none" }}
            />
          </label>

          <label style={{ display: "block", border: `1px solid ${border.subtle}`, borderRadius: 10, padding: "14px 16px", background: surface.panel, cursor: "pointer" }}>
            <div style={{ fontSize: 13, fontWeight: 500, color: text.primary, marginBottom: 4 }}>
              Full data export (.zip) <span style={{ color: text.dimmed, fontWeight: 400 }}>· optional</span>
            </div>
            <div style={{ fontSize: 12, color: text.dimmed, marginBottom: 8 }}>
              {exportZip ? exportZip.name : (
                <>
                  Get it directly:{" "}
                  <a
                    href="https://www.linkedin.com/mypreferences/d/download-my-data"
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    style={{ color: "#00F0FF", textDecoration: "underline" }}
                  >
                    linkedin.com/mypreferences/d/download-my-data
                  </a>
                </>
              )}
            </div>
            <input
              type="file"
              accept=".zip,application/zip"
              onChange={(e) => setExportZip(e.target.files?.[0] ?? null)}
              style={{ display: "none" }}
            />
          </label>
        </div>

        {error && (
          <p style={{ fontSize: 13, color: "#FF4D6D", margin: "0 0 16px" }}>{error}</p>
        )}

        <div style={{ display: "flex", gap: 10 }}>
          <Button variant="primary" disabled={busy || !hasPdfRequirement} onClick={handleUpload} style={{ flex: 1 }}>
            {busy ? "Uploading…" : "Upload & continue"}
          </Button>
          <Button variant="ghost" disabled={busy} onClick={handleSkip}>
            Skip for now
          </Button>
        </div>
      </div>
    </div>
  )
}
