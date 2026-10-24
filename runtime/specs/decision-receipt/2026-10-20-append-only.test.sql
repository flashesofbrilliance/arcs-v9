-- Proof for 2026-10-20-append-only.sql (passed 2026-10-20 on the live table).
-- One statement: it inserts a probe, tries UPDATE and DELETE (both must be refused), inserts a superseding row, then RAISES
-- on purpose so the whole statement rolls back. The trigger forbids deleting the probe, so rollback is the only clean exit.
-- Pass = the error text reads: ok: update refused | ok: delete refused | ok: superseding insert accepted
do $$
declare r text := '';
begin
  insert into public.decision_receipt (receipt_id, question, horizon, stakes, mode, what_confirmed, what_unconfirmed, operator, event_at, refs)
  values ('test--append-only-probe--ZH', 'probe', 'today', 'low', 'QUICKMOVE', array['probe'], array['probe'], 'test', now(), array['test']);
  begin
    update public.decision_receipt set question = 'edited' where receipt_id = 'test--append-only-probe--ZH';
    r := r || 'FAIL: update was allowed | ';
  exception when sqlstate 'P0001' then r := r || 'ok: update refused | ';
  end;
  begin
    delete from public.decision_receipt where receipt_id = 'test--append-only-probe--ZH';
    r := r || 'FAIL: delete was allowed | ';
  exception when sqlstate 'P0001' then r := r || 'ok: delete refused | ';
  end;
  begin
    insert into public.decision_receipt (receipt_id, question, horizon, stakes, mode, what_confirmed, what_unconfirmed, operator, event_at, refs, supersedes)
    values ('test--append-only-probe-fix--ZH', 'probe fix', 'today', 'low', 'QUICKMOVE', array['probe'], array['probe'], 'test', now(), array['test'], 'test--append-only-probe--ZH');
    r := r || 'ok: superseding insert accepted';
  exception when others then r := r || 'FAIL: superseding insert refused: ' || sqlerrm;
  end;
  raise exception 'PROOF (rolled back by design): %', r;
end $$;
