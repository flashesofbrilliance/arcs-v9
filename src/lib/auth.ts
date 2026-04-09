import NextAuth from "next-auth"
import { PrismaAdapter } from "@auth/prisma-adapter"
import Resend from "next-auth/providers/resend"
import { db } from "@/lib/db"

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(db),
  providers: [
    Resend({
      from: "ARCS <receipts@arcs.so>",
    }),
  ],
  pages: {
    signIn: "/compass",
    verifyRequest: "/compass",
  },
  callbacks: {
    session({ session, user }) {
      session.user.id = user.id
      // @ts-expect-error — tier is a custom field on User
      session.user.tier = user.tier
      return session
    },
  },
})
