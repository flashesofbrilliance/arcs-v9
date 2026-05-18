// Auth disabled for local dev — re-enable when ready for multi-user
export const auth = async () => null
export const signIn = async () => {}
export const signOut = async () => {}
export const handlers = { GET: () => new Response("auth disabled"), POST: () => new Response("auth disabled") }
