export const sent: unknown[] = []
export class Resend { emails = { send: async (m: unknown) => { sent.push(m); return { data: { id: "fake" } } } } }
