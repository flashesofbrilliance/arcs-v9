import { test } from "node:test"
import assert from "node:assert/strict"
import { mintToken, hashToken, isTokenShaped, sharePath } from "../../src/lib/briefShare.ts"

test("minted tokens are 32 bytes of base64url and pass the shape check", () => {
  const t = mintToken()
  assert.equal(Buffer.from(t, "base64url").length, 32)
  assert.ok(isTokenShaped(t))
  assert.notEqual(mintToken(), t)
})

test("shape check rejects receipt ids, padding and path tricks", () => {
  for (const bad of ["", "cm1abc", "a".repeat(42), "a".repeat(44), "a".repeat(42) + "=", "../" + "a".repeat(40)]) {
    assert.equal(isTokenShaped(bad), false, bad)
  }
})

test("only the hash is stored and it is not the token", () => {
  const t = mintToken()
  assert.match(hashToken(t), /^[0-9a-f]{64}$/)
  assert.notEqual(hashToken(t), t)
  assert.equal(hashToken(t), hashToken(t))
})

test("share path carries the token in the fragment, never the path", () => {
  const t = mintToken()
  const p = sharePath(t)
  assert.equal(p.split("#")[0], "/shared/brief")
  assert.equal(p.split("#")[1], t)
})
