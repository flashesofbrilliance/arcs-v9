-- decision_receipt is append-only (backlog row decision-receipt-append-only; Zach approved the rule in chat 2026-10-20,
-- "yes to both", with UPDATE refused as well as DELETE). NOT YET APPLIED: apply only after Zach's go on this file.
-- One-way door in practice: once applied, no session can edit or delete a receipt. A wrong receipt is corrected by a new
-- row whose supersedes column names the receipt_id it replaces. Revert (deliberate, visible):
--   drop trigger decision_receipt_append_only on public.decision_receipt;
--   drop function public.decision_receipt_refuse_change();
-- Rare legitimate removal (for example personal data written by mistake): a service-role session runs
--   alter table public.decision_receipt disable trigger decision_receipt_append_only;  ... ;  enable trigger ...
-- and files a receipt saying why.

alter table public.decision_receipt
  add column if not exists supersedes text references public.decision_receipt(receipt_id);
alter table public.decision_receipt
  add constraint decision_receipt_supersedes_not_self check (supersedes is null or supersedes <> receipt_id);
comment on column public.decision_receipt.supersedes is
  'receipt_id this row corrects; the old row stays. Append-only ledger (runtime/specs/decision-receipt/2026-10-20-append-only.sql)';

create or replace function public.decision_receipt_refuse_change() returns trigger
language plpgsql as $$
begin
  raise exception 'decision_receipt is append-only: % refused on %. Write a new row with supersedes = ''%'' instead.',
    tg_op, old.receipt_id, old.receipt_id
    using errcode = 'P0001';
end;
$$;

create trigger decision_receipt_append_only
  before update or delete on public.decision_receipt
  for each row execute function public.decision_receipt_refuse_change();
