import { auth } from "@/lib/auth"
import { redirect } from "next/navigation"

export default async function DashboardPage() {
  const session = await auth()
  if (!session?.user) redirect("/compass")

  return (
    <main style={{ minHeight: "100vh", background: "#020408", color: "#e2e8f0", fontFamily: "sans-serif", padding: "2rem" }}>
      <h1 style={{ color: "#00F0FF", fontSize: "1.5rem", marginBottom: "0.5rem" }}>Dashboard</h1>
      <p style={{ color: "#94a3b8", fontSize: "0.875rem" }}>
        Signed in as <strong style={{ color: "#e2e8f0" }}>{session.user.email}</strong>
      </p>
      <p style={{ marginTop: "2rem", color: "#475569", fontSize: "0.875rem" }}>
        HUD · Receipts · Patterns — coming Day 2–5
      </p>
    </main>
  )
}
