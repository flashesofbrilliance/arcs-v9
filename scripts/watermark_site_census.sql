-- Watermark site census (anti-distillation ruling 8, 2026-10-20). READ ONLY.
-- Counts, per stored receipt, how many of 40 CANDIDATE substitution sites are
-- active (either variant of the pair appears as a whole word in the output
-- prose). Returns aggregates only; no receipt text, id or user is selected.
-- The 40 pairs are a candidate list for measurement, not the final site set.
-- Pre-registered bar (audit C3): median active sites per answer >= 32.
-- Run: supabase db query --linked -f scripts/watermark_site_census.sql
with sites as (
  select unnest(array[
    'so|so that','next|then','first|initially','by|before','because|since','but|yet',
    'also|too','and then|after that','about|around','need|require','help|support',
    'use|apply','start|begin','end|finish','show|reveal','keep|hold','choose|pick',
    'try|attempt','enough|sufficient','mostly|largely','often|usually','maybe|perhaps',
    'big|large','fast|quick','hard|difficult','simple|plain','clear|obvious',
    'risk|danger','cost|price','plan|approach','step|move','build|make','check|verify',
    'ask|request','buy|purchase','get|obtain','look at|examine','while|whereas',
    'although|though','rather|instead'
  ]) as p
), r as (
  select id, lower(coalesce("trueNorth",'') || ' ' || coalesce("whyBullets",'') || ' ' || coalesce("atgTributaries",'')) as t
  from "Receipt"
), c as (
  select r.id, count(*) filter (where r.t ~ ('\m(' || s.p || ')\M')) as n
  from r cross join sites s group by r.id
)
select count(*) as receipts,
       min(n) as min_sites, percentile_cont(0.25) within group (order by n) as p25,
       percentile_cont(0.5) within group (order by n) as median,
       percentile_cont(0.75) within group (order by n) as p75, max(n) as max_sites,
       round(avg(n)::numeric, 2) as mean_sites,
       count(*) filter (where n >= 32) as receipts_at_or_over_32,
       (select count(*) from sites) as candidate_sites
from c;
