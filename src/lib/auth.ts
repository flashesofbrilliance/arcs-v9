import NextAuth from "next-auth"
import Resend from "next-auth/providers/resend"
import { Resend as ResendClient } from "resend"
import { PrismaAdapter } from "@auth/prisma-adapter"
import { prisma } from "@/lib/db"
import { welcomeEmail } from "@/emails/welcomeEmail"

export const { auth, handlers, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  logger: {
    error(code, ...message) {
      console.error("[auth:full-error]", code, JSON.stringify(message, null, 2))
    },
  },
  providers: [
    Resend({
      apiKey: process.env.AUTH_RESEND_KEY,
      from: "ARCS <noreply@arcs.care>",
      // The magic-link email IS the branded welcome card. The one-time sign-in
      // URL becomes the CTA (clicking it verifies + lands on the compass).
      // Auth.js still owns token generation/storage — this only sends the email.
      async sendVerificationRequest({ identifier: email, url, provider, token }) {
        const { subject, html } = welcomeEmail({ ctaUrl: url, ctaLabel: "Sign in to ARCS →", token })
        const resend = new ResendClient(process.env.AUTH_RESEND_KEY)
        const { error } = await resend.emails.send({
          from: provider.from as string,
          to: email,
          subject,
          html,
        })
        if (error) throw new Error(`Resend sendVerificationRequest failed: ${JSON.stringify(error)}`)
      },
    }),
  ],
  pages: {
    signIn: "/compass",
  },
  callbacks: {
    session({ session, user }) {
      session.user.id = user.id
      return session
    },
  },
})
