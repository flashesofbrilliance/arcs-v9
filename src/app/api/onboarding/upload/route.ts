import { NextRequest, NextResponse } from "next/server"
import { put } from "@vercel/blob"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"

// Onboarding upload step — store-only (see ADR-029). Accepts the LinkedIn
// profile PDF and/or the full data-export ZIP, puts them in Vercel Blob, and
// records pointers on ProfileUpload. No parsing happens here — the
// generation pipeline that reads these is still unbuilt (ADR-028).

// Status check — lets the dashboard nudge a user who hasn't uploaded or
// explicitly skipped yet, without forcing the onboarding step on every visit.
export async function GET() {
  const session = await auth()
  const userId = session?.user?.id
  if (!userId) {
    // Read-only status probe, fired from the dashboard for every visitor.
    // 200-with-nothing instead of 401: an anonymous visitor has no profile by
    // definition, and a 4xx here logs a browser console error on every page
    // view (which also trips the fe-smoke zero-console-errors gate). POST
    // (the mutation) keeps its 401.
    return NextResponse.json({ anonymous: true, hasPdf: false, hasExport: false, skipped: true, seen: false })
  }

  const upload = await prisma.profileUpload.findUnique({ where: { userId } })
  return NextResponse.json({
    hasPdf: !!upload?.pdfUrl,
    hasExport: !!upload?.exportUrl,
    skipped: !!upload?.skipped,
    seen: !!upload,
  })
}

export async function POST(req: NextRequest) {
  const session = await auth()
  const userId = session?.user?.id
  if (!userId) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 })
  }

  const form = await req.formData()
  const pdf = form.get("pdf") as File | null
  const exportZip = form.get("export") as File | null

  if (!pdf && !exportZip) {
    return NextResponse.json({ error: "no files provided" }, { status: 400 })
  }

  const [pdfBlob, exportBlob] = await Promise.all([
    pdf ? put(`profile-uploads/${userId}/profile.pdf`, pdf, { access: "private", addRandomSuffix: true }) : null,
    exportZip ? put(`profile-uploads/${userId}/export.zip`, exportZip, { access: "private", addRandomSuffix: true }) : null,
  ])

  const upload = await prisma.profileUpload.upsert({
    where: { userId },
    create: {
      userId,
      pdfUrl: pdfBlob?.url,
      exportUrl: exportBlob?.url,
      uploadedAt: new Date(),
    },
    update: {
      ...(pdfBlob ? { pdfUrl: pdfBlob.url } : {}),
      ...(exportBlob ? { exportUrl: exportBlob.url } : {}),
      uploadedAt: new Date(),
      skipped: false,
    },
  })

  return NextResponse.json({ ok: true, hasPdf: !!upload.pdfUrl, hasExport: !!upload.exportUrl })
}

// Skip — records that onboarding was seen and declined, so the dashboard can
// nudge later without re-showing the full step every visit.
export async function PATCH(req: NextRequest) {
  const session = await auth()
  const userId = session?.user?.id
  if (!userId) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 })
  }

  await prisma.profileUpload.upsert({
    where: { userId },
    create: { userId, skipped: true },
    update: { skipped: true },
  })

  return NextResponse.json({ ok: true })
}
