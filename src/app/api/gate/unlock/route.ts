import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { signGate, checkPasscode, GATE_COOKIE, GATE_MAX_AGE } from "@/lib/statusgate";

/**
 * POST /api/gate/unlock — the status.arcs.care passcode door.
 *
 * The cover page (public/status-gate.html) POSTs its single passcode field here.
 * On a correct passcode we mint a signed cookie (see src/lib/statusgate.ts) and
 * 303-redirect to "/", which the middleware now lets through to status.html.
 * On a miss we bounce back to the cover with ?e=1 so it can show the error.
 *
 * Interim gate — swapped out when the MCP veil lands.
 */
export async function POST(req: NextRequest) {
  const form = await req.formData().catch(() => null);
  const passcode = form ? String(form.get("passcode") ?? "") : "";
  const origin = req.nextUrl.origin;

  if (!(await checkPasscode(passcode))) {
    return NextResponse.redirect(new URL("/status-gate.html?e=1", origin), { status: 303 });
  }

  const res = NextResponse.redirect(new URL("/", origin), { status: 303 });
  res.cookies.set(GATE_COOKIE, await signGate(), {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: GATE_MAX_AGE,
  });
  return res;
}
