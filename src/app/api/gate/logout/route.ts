import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { GATE_COOKIE } from "@/lib/statusgate";

/**
 * GET /api/gate/logout — drop the status gate cookie and return to the cover.
 * Lets a "real one" re-veil the surface (or hand the machine back its blindfold).
 */
export async function GET(req: NextRequest) {
  const res = NextResponse.redirect(new URL("/status-gate.html", req.nextUrl.origin), { status: 303 });
  res.cookies.set(GATE_COOKIE, "", { path: "/", maxAge: 0 });
  return res;
}
