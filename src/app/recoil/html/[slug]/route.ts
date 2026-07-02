import { NextRequest, NextResponse } from "next/server"
import fs from "node:fs"
import path from "node:path"

// Serves standalone HTML recoil reports from src/ui-kit/recoil-report/.
// Cookie gate is enforced upstream by middleware — this route trusts it.
export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params
  const safe = slug.replace(/[^a-zA-Z0-9_-]/g, "")
  const file = path.join(process.cwd(), "src", "ui-kit", "recoil-report", `${safe}.html`)

  if (!fs.existsSync(file)) {
    return new NextResponse("Not found", { status: 404 })
  }

  const html = fs.readFileSync(file, "utf-8")
  return new NextResponse(html, {
    headers: { "Content-Type": "text/html; charset=utf-8" },
  })
}
