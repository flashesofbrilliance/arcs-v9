// The ONLY place app code gets a Claude model id. Source of truth: runtime/specs/models.json.
// Name a role, never an id (scripts/model_id_gate.py blocks hardcoded ids at pre-commit).
import registry from "../../runtime/specs/models.json" with { type: "json" };

export type ModelRole = keyof typeof registry.roles;

export function model(role: ModelRole): string {
  return registry.roles[role].model;
}
