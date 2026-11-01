import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";
import jsxA11y from "eslint-plugin-jsx-a11y";

// jsx-a11y recommended (2026-10-08), at WARN while the 27 existing findings burn down; a rule moves to
// "error" once its count is zero. Ships with eslint-config-next, so no new dependency.
const a11yWarn = Object.fromEntries(Object.keys(jsxA11y.flatConfigs.recommended.rules).map((r) => [r, "warn"]));

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  { files: ["src/**/*.tsx"], rules: a11yWarn },
  // .cjs files are CommonJS by definition: require() is the only import they have (tools/readme-video, PR 1894).
  { files: ["**/*.cjs"], rules: { "@typescript-eslint/no-require-imports": "off" } },
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
