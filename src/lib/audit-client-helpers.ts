/**
 * previewAuditOutput — a one-line human-readable summary of the operator output.
 * Used in the context injection and the audit trace. Not the full structured output.
 */
export function previewAuditOutput(
  opName: string,
  output: Record<string, unknown>,
): string {
  switch (opName) {
    case "SAGE": {
      const nci = Number(output.nci_score ?? 0)
      const verdict = String(output.verdict ?? "n/a")
      const pci = Number(output.pci_score ?? 0)
      return `SAGE: NCI ${nci}/100 · verdict ${verdict} · PCI ${pci}`
    }
    case "LAB": {
      const threat = String(output.lab_threat_level ?? "n/a")
      const rec = String(output.lab_recommendation ?? "n/a")
      const posterior =
        Number(
          (output as Record<string, unknown>).bayesian_posterior_confidence ??
            (output.bayesian as Record<string, unknown>)?.posterior_confidence ??
            0,
        ) ?? 0
      return `LAB: threat ${threat} · rec ${rec} · bayesian posterior ${posterior.toFixed(2)}`
    }
    case "BAR": {
      const verdict = String(output.bar_verdict ?? "n/a")
      const ratio = Number(
        (output.asymmetry as Record<string, unknown>)?.asymmetry_ratio ??
          (output as Record<string, unknown>).asymmetry_ratio ??
          0,
      )
      const ruin =
        Boolean(
          (output.ruin as Record<string, unknown>)?.ruin_detected ??
            (output as Record<string, unknown>).ruin_detected ??
            false,
        ) ?? false
      return `BAR: verdict ${verdict} · asymmetry ${ratio.toFixed(2)}x · ruin ${ruin ? "DETECTED" : "clear"}`
    }
    case "KINTSUGI": {
      const pathogenCount =
        typeof output.pathogens === "object" && output.pathogens !== null
          ? (output.pathogens as unknown[]).length
          : Number(output.pathogen_count ?? 0)
      const repaired =
        Boolean(output.repaired ?? (output as Record<string, unknown>).is_repaired ?? false)
      const discount = Number(output.trust_discount ?? (output as Record<string, unknown>).kintsugi_trust_discount ?? 0)
      const discountStr = repaired ? ` · trust discount ${discount.toFixed(2)}` : ""
      return `KINTSUGI: pathogens ${pathogenCount} · repaired ${repaired}${discountStr}`
    }
    default:
      return `${opName}: output received (preview unavailable)`
  }
}

/**
 * operatorAdvisoryBlock — formats one operator's output as a short advisory block
 * to inject into the LLM's context. Kept terse — context is expensive and these are advisory.
 */
export function operatorAdvisoryBlock(
  opName: string,
  output: Record<string, unknown>,
): string {
  switch (opName) {
    case "SAGE": {
      const nci = Number(output.nci_score ?? 0)
      const pci = Number(output.pci_score ?? 0)
      const hci = Number(output.hci_score ?? 0)
      const classification = String(output.signal_classification ?? "n/a")
      const axioms = (output as Record<string, unknown>).axioms
      const axiomStr =
        typeof axioms === "object" && axioms !== null
          ? `axioms: clarity=${(axioms as Record<string, unknown>).clarity_before_curvature ?? "n/a"} · agency=${(axioms as Record<string, unknown>).agency_over_automation ?? "n/a"} · steps=${(axioms as Record<string, unknown>).minimum_steps_to_coherence ?? "n/a"} · kairos=${(axioms as Record<string, unknown>).kairos_over_neuroticism ?? "n/a"}`
          : "axioms: n/a"
      return `SAGE AUDIT: NCI=${nci} · PCI=${pci} · HCI=${hci} · signal=${classification}
${axiomStr}`
    }
    case "LAB": {
      const threat = String(output.lab_threat_level ?? "n/a")
      const rec = String(output.lab_recommendation ?? "n/a")
      const loki = (output as Record<string, unknown>).loki
      const lokiStr =
        typeof loki === "object" && loki !== null
          ? `loki: ${String((loki as Record<string, unknown>).challenge_statement ?? "n/a").slice(0, 160)}`
          : "loki: n/a"
      const posterior =
        Number(
          (output.bayesian as Record<string, unknown>)?.posterior_confidence ??
            (output as Record<string, unknown>).bayesian_posterior_confidence ??
            0,
        ) ?? 0
      return `LAB AUDIT: threat=${threat} · rec=${rec} · bayesian_posterior=${posterior.toFixed(2)}
${lokiStr}`
    }
    case "BAR": {
      const verdict = String(output.bar_verdict ?? "n/a")
      const baseline = (output as Record<string, unknown>).baseline
      const baselineStr =
        typeof baseline === "object" && baseline !== null
          ? `floor_nci=${(baseline as Record<string, unknown>).floor_nci ?? "n/a"} · floor_acceptable=${(baseline as Record<string, unknown>).floor_is_acceptable ?? "n/a"}`
          : "floor_nci=n/a"
      const asymmetry = (output as Record<string, unknown>).asymmetry
      const asymStr =
        typeof asymmetry === "object" && asymmetry !== null
          ? `asymmetry=${Number((asymmetry as Record<string, unknown>).asymmetry_ratio ?? 0).toFixed(2)}x · bet_quality=${(asymmetry as Record<string, unknown>).bet_quality ?? "n/a"} · kelly=${(asymmetry as Record<string, unknown>).kelly_fraction ?? "n/a"}`
          : "asymmetry=n/a"
      const ruin = (output as Record<string, unknown>).ruin
      const ruinStr =
        typeof ruin === "object" && ruin !== null && (ruin as Record<string, unknown>).ruin_detected === true
          ? `Ruin detected: ${String((ruin as Record<string, unknown>).ruin_scenario ?? "n/a").slice(0, 200)}`
          : "Ruin: clear"
      return `BAR AUDIT: verdict=${verdict}
${baselineStr}
${asymStr}
${ruinStr}`
    }
    case "KINTSUGI": {
      const pathogens = (output as Record<string, unknown>).pathogens
      const pathogenCount =
        typeof pathogens === "object" && pathogens !== null && Array.isArray(pathogens)
          ? pathogens.length
          : Number((output as Record<string, unknown>).pathogen_count ?? 0)
      const repaired =
        Boolean(output.repaired ?? (output as Record<string, unknown>).is_repaired ?? false)
      const discount = Number(
        output.trust_discount ?? (output as Record<string, unknown>).kintsugi_trust_discount ?? 0,
      )
      const pathogenSummary =
        typeof pathogens === "object" && pathogens !== null && Array.isArray(pathogens) && pathogens.length > 0
          ? pathogens
              .slice(0, 3)
              .map((p: unknown) => {
                if (typeof p === "object" && p !== null) {
                  return String((p as Record<string, unknown>).description ?? String(p))
                }
                return String(p)
              })
              .join("; ")
          : "no pathogens detected"
      return `KINTSUGI AUDIT: pathogens=${pathogenCount} · repaired=${repaired} · trust_discount=${discount.toFixed(2)}
${pathogenSummary.slice(0, 240)}`
    }
    default:
      return `${opName}: audit output (preview unavailable)`
  }
}
