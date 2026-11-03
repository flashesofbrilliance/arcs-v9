const { chromium } = require('/Users/zharris/arcs-v9/node_modules/playwright');
(async()=>{const b=await chromium.launch();
for (const s of ['dark','light']){const p=await b.newPage({viewport:{width:1200,height:600},colorScheme:s,reducedMotion:'reduce'});
await p.goto('file://'+__dirname+'/trust-boundary.svg');await p.screenshot({path:__dirname+`/tb-${s}.png`});}
await b.close();})();
