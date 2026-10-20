-- Proof for 2026-10-20-append-only.sql. Runs inside one transaction and ROLLS BACK, so it leaves no rows behind.
-- Pass = the three DO blocks raise NOTICE 'ok ...' and none raises an error.
begin;
insert into public.decision_receipt (receipt_id, question, horizon, stakes, mode, what_confirmed, what_unconfirmed, operator, event_at, refs)
values ('test--append-only-probe--ZH', 'probe', 'today', 'low', 'QUICKMOVE', array['probe'], array['probe'], 'test', now(), array['test']);
do $$ begin
  update public.decision_receipt set question = 'edited' where receipt_id = 'test--append-only-probe--ZH';
  raise exception 'FAIL: update was allowed';
exception when sqlstate 'P0001' then raise notice 'ok: update refused';
end $$;
do $$ begin
  delete from public.decision_receipt where receipt_id = 'test--append-only-probe--ZH';
  raise exception 'FAIL: delete was allowed';
exception when sqlstate 'P0001' then raise notice 'ok: delete refused';
end $$;
do $$ begin
  insert into public.decision_receipt (receipt_id, question, horizon, stakes, mode, what_confirmed, what_unconfirmed, operator, event_at, refs, supersedes)
  values ('test--append-only-probe-fix--ZH', 'probe fix', 'today', 'low', 'QUICKMOVE', array['probe'], array['probe'], 'test', now(), array['test'], 'test--append-only-probe--ZH');
  raise notice 'ok: superseding insert accepted';
end $$;
rollback;
