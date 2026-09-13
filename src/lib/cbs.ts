// CBS (Consonance-Burstiness-Symmetry) anti-slop scoring engine.
// Deterministic, zero-dependency, zero-telemetry: pure text-in / metrics-out.
// Spec: docs/sketches/PERPLEXITY-SKILL-ARCS-RECON.md, .claude/commands/cbs-anti-slop.md

const PATHOGEN_DICTIONARY = [
  "crucially",
  "delve",
  "nuanced approach",
  "synergy",
  "leverage",
  "robust",
  "seamless",
  "cutting-edge",
  "game-changer",
  "in today's fast-paced world",
  "it's important to note",
  "unlock the potential",
  "holistic",
  "paradigm shift",
  "at the end of the day",
  "moving forward",
  "circle back",
  "low-hanging fruit",
  "boil the ocean",
  "deep dive",
] as const;

// "not only X but Y" / "not X but it is Y" filler couplets.
const COUPLET_REGEX = /(?:not\s+(?:only\s+)?[\w\s,]+(?:but|it\s+is)\s+[\w\s]+)/gi;

// Physical-anchor patterns: concrete software nouns, timestamps, cost/token counts.
const PHYSICAL_ANCHOR_PATTERNS: RegExp[] = [
  /\b(slack|cli|grep|ram|api|git|json|sql|http|url|env|cpu|gpu|ssh|dns|css|html)\b/gi,
  /\b\d{4}-\d{2}-\d{2}\b/g, // ISO dates
  /\b\d{1,2}:\d{2}(:\d{2})?\b/g, // timestamps
  /\$\d+(\.\d+)?\b/g, // dollar amounts
  /\b\d+(\.\d+)?[kKmM]?\s?(tokens?|ms|sec|s|MB|GB|KB)\b/gi, // cost/perf counters
];

const VOCAB_DENSITY_FLOOR = 0.54;
const SENTENCE_VARIANCE_FLOOR = 35; // ΔL: max - min sentence length (words)

export interface CBSMetrics {
  wordCount: number;
  uniqueWordCount: number;
  vocabDensity: number;
  sentenceLengths: number[];
  sentenceVariance: number;
  sentenceStdDev: number;
  slopMatches: string[];
  coupletMatches: string[];
  physicalNounsCount: number;
  passed: boolean;
  score: number;
}

function tokenizeWords(text: string): string[] {
  const matches = text.toLowerCase().match(/[a-z0-9']+/g);
  return matches ?? [];
}

function splitSentences(text: string): string[] {
  return text
    .split(/(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
}

function countWordsInSentence(sentence: string): number {
  return tokenizeWords(sentence).length;
}

function stdDev(values: number[]): number {
  if (values.length === 0) return 0;
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const variance =
    values.reduce((a, b) => a + (b - mean) ** 2, 0) / values.length;
  return Math.sqrt(variance);
}

export function runCBSAnalysis(text: string): CBSMetrics {
  const words = tokenizeWords(text);
  const wordCount = words.length;
  const uniqueWordCount = new Set(words).size;
  const vocabDensity = wordCount > 0 ? uniqueWordCount / wordCount : 0;

  const sentences = splitSentences(text);
  const sentenceLengths = sentences.map(countWordsInSentence);
  const sentenceVariance =
    sentenceLengths.length > 0
      ? Math.max(...sentenceLengths) - Math.min(...sentenceLengths)
      : 0;
  const sentenceStdDev = stdDev(sentenceLengths);

  const lowerText = text.toLowerCase();
  const slopMatches = PATHOGEN_DICTIONARY.filter((phrase) =>
    lowerText.includes(phrase),
  );

  const coupletMatches = text.match(COUPLET_REGEX) ?? [];

  const physicalNounsCount = PHYSICAL_ANCHOR_PATTERNS.reduce(
    (count, pattern) => count + (text.match(pattern) ?? []).length,
    0,
  );

  const passed =
    vocabDensity >= VOCAB_DENSITY_FLOOR &&
    sentenceVariance >= SENTENCE_VARIANCE_FLOOR &&
    slopMatches.length === 0 &&
    coupletMatches.length === 0;

  // Composite score, 0-100: vocab density (40pt) + burstiness (30pt) +
  // pathogen/couplet penalty (30pt, subtractive).
  const vocabScore = Math.min(1, vocabDensity / VOCAB_DENSITY_FLOOR) * 40;
  const burstinessScore =
    Math.min(1, sentenceVariance / SENTENCE_VARIANCE_FLOOR) * 30;
  const penaltyScore = Math.max(
    0,
    30 - (slopMatches.length + coupletMatches.length) * 10,
  );
  const score = Math.round(vocabScore + burstinessScore + penaltyScore);

  return {
    wordCount,
    uniqueWordCount,
    vocabDensity,
    sentenceLengths,
    sentenceVariance,
    sentenceStdDev,
    slopMatches,
    coupletMatches,
    physicalNounsCount,
    passed,
    score,
  };
}
