export let session: unknown = null
export const setSession = (s: unknown) => { session = s }
export const auth = async () => session
export const signIn = async () => {}
export const signOut = async () => {}
export const handlers = {}
