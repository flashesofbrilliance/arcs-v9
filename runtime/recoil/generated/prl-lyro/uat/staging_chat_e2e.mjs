// PRL staging chat e2e — Playwright skeleton (2026-08-18). NOT YET RUN.
// Run: node staging_chat_e2e.mjs [fixtureName]   (default: runs all fixtures in order)
// QUOTA: each fixture burns a flow execution + Zapier tasks + a ZoomInfo credit. Run deliberately.
import { chromium } from 'playwright';
import { readFileSync } from 'fs';

const STAGING = 'https://wfaprlredev26.wpenginepowered.com/';
const SUGAR = process.env.SUGAR_URL ?? 'https://prlresinstest.sugarondemand.com';
const fixtures = JSON.parse(readFileSync(new URL('./fixtures.json', import.meta.url)));

async function sugarToken() {
  const r = await fetch(`${SUGAR}/rest/v11_5/oauth2/token`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ grant_type: 'password', client_id: 'sugar', platform: 'base',
      username: process.env.SUGAR_USER, password: process.env.SUGAR_PASS }),
  });
  if (!r.ok) throw new Error(`sugar auth ${r.status}`);
  return (await r.json()).access_token;
}

async function findLeadByEmail(token, email) {
  const u = `${SUGAR}/rest/v11_5/Leads?filter[0][email1]=${encodeURIComponent(email)}&fields=id,first_name,last_name,location_c,lead_source,title,description,date_modified`;
  const r = await fetch(u, { headers: { 'OAuth-Token': token } });
  return (await r.json()).records ?? [];
}

async function runChat(page, fx) {
  await page.goto(STAGING, { waitUntil: 'networkidle' });
  // TODO(selector): Tidio renders in an iframe — inspect on first run.
  const widget = page.frameLocator('#tidio-chat-iframe'); // TODO(selector): confirm iframe id
  await widget.locator('/* TODO(selector): open-chat button */').click();
  // The AI-Handoff flow asks 6 questions in order; answer each. Adjust waits to the flow's pacing.
  for (const answer of [fx.need, fx.name, fx.email, fx.phone, fx.company, fx.state]) {
    const input = widget.locator('/* TODO(selector): message input */');
    await input.waitFor({ state: 'visible', timeout: 20_000 });
    await input.fill(answer);
    await input.press('Enter');
    await page.waitForTimeout(2500); // TODO: replace with reply-message wait
  }
  await page.waitForTimeout(5000); // let the webhook fire
}

const [, , only] = process.argv;
const token = await sugarToken();
const browser = await chromium.launch({ headless: false }); // headed for first debug run
let failures = 0;
for (const fx of fixtures.filter(f => !only || f.fixture === only)) {
  const before = await findLeadByEmail(token, fx.email);
  const page = await browser.newPage();
  await runChat(page, fx);
  await page.close();
  // poll up to 90s for the lead to land/update
  let after = [], deadline = Date.now() + 90_000;
  while (Date.now() < deadline) {
    after = await findLeadByEmail(token, fx.email);
    if (fx.expect.dedup ? after.some(l => l.date_modified > (before[0]?.date_modified ?? '')) : after.length > before.length) break;
    await new Promise(r => setTimeout(r, 5000));
  }
  const lead = after.sort((a, b) => b.date_modified.localeCompare(a.date_modified))[0];
  const checks = {
    landed: !!lead,
    count: fx.expect.dedup ? after.length === before.length : after.length === before.length + 1,
    first_name: lead?.first_name === fx.expect.first_name,
    last_name: lead?.last_name === fx.expect.last_name,
    location_c: lead?.location_c === fx.expect.location_c,
    lead_source: lead?.lead_source === 'Chatbot',
  };
  const pass = Object.values(checks).every(Boolean);
  if (!pass) failures++;
  console.log(`${pass ? 'PASS' : 'FAIL'} ${fx.fixture}`, pass ? '' : checks, lead?.id ?? '(no lead)');
}
await browser.close();
process.exit(failures ? 1 : 0);
