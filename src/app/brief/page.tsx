// Render through the fog to earned clarity.
// A brief opens from a specific receipt: /brief/[receiptId]. Bare /brief has no
// id to render, so send the navigator back to the compass rather than 404.
import { redirect } from "next/navigation"

export default function BriefIndex() {
  redirect("/dashboard")
}
