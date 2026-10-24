-- Applied 2026-10-20 to Supabase project xbbpiryokswwvcrcutge via apply_migration "decision_receipt_job_tool_ids".
-- Zach approved in chat ("go ahead with the schema change"). Backlog row jtbd-graph-s5-feedback, gate 1. ADR-089.
-- Two-way door: both columns nullable; existing rows and writers unaffected. Revert: drop the two constraints, then the columns.
alter table public.decision_receipt
  add column if not exists job_id text,
  add column if not exists tool_id text;
alter table public.decision_receipt
  add constraint decision_receipt_job_id_form check (job_id is null or job_id ~ '^job:[a-z]+:.+'),
  add constraint decision_receipt_tool_id_form check (tool_id is null or tool_id ~ '^tool:[a-z]+:.+');
comment on column public.decision_receipt.job_id is 'JTBD graph job atom id (job:<source>:<key>), ADR-089; null when no graph job applies';
comment on column public.decision_receipt.tool_id is 'JTBD graph tool atom id actually used (tool:<kind>:<name>), ADR-089; null when none';
