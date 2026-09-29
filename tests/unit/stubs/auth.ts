export let session: any = null
export const setSession = (s: any) => { session = s }
export const auth = async () => session
export const signIn = async () => {}
export const signOut = async () => {}
export const handlers = {}
