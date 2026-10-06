import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
    // Static prototypes served as files (compass-kit, observatory demo): their
    // components are script-tag globals and carry no build, so React lint rules
    // misreport them. Not part of the Next.js app.
    "public/**",
    // Deliberately malicious / benign sample repos used as inputs to the
    // sbom-payload-scan skill's evals. They must stay byte-for-byte as authored.
    ".claude/skills/sbom-payload-scan/evals/fixtures/**",
  ]),
]);

export default eslintConfig;
