/* Two-band inference ledger + belief timelines + JSON export. Data-driven: renders from a global
   DATA object the generator injects (SSOT -> render). Export filename {{EXPORT_FILE}} is substituted. */
(function(){
  if(typeof DATA==='undefined')return;
  function cc(v){return v>=0.8?'var(--green)':v>=0.55?'var(--gold)':v>=0.35?'var(--steel)':'var(--red)';}
  function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
  var band='pub';
  function renderLedger(){
    var host=document.getElementById('ledger');if(!host)return;
    var rows=DATA.reads.filter(function(r){return r.band===band;});
    host.innerHTML=rows.map(function(r,ix){
      var conv=r.conviction||'stable';
      return '<div class="row '+(r.band==='res'?'res':'pub')+'" data-i="'+ix+'">'
        +'<div class="rtop"><div class="concl">'+esc(r.conclusion)+'</div>'
        +'<div class="bandtag">'+(r.band==='res'?'reserved':'public')+'</div></div>'
        +'<div class="meters"><div class="mtr"><div class="ml"><span>Confidence</span><span class="mv">'+r.confidence.toFixed(2)+'</span></div>'
        +'<div class="bar"><i style="width:'+Math.round(r.confidence*100)+'%;background:'+cc(r.confidence)+';"></i></div></div>'
        +'<span class="conv '+conv+'">'+conv+'</span></div>'
        +'<button class="togg" data-t="'+ix+'">show the chain</button>'
        +'<div class="chain"><div><div class="ck">clue</div><div class="cv">'+esc(r.clue)+'</div></div>'
        +'<div><div class="ck">inference</div><div class="cv">'+esc(r.inference)+'</div></div>'
        +(r.source?'<div class="src">grounded in: "'+esc(r.source)+'"</div>':'')
        +(r.disclosure?'<div class="ck" style="color:var(--gold);">'+esc(r.disclosure)+'</div>':'')
        +'</div></div>';
    }).join('');
    host.querySelectorAll('.togg').forEach(function(b){b.addEventListener('click',function(){
      var row=b.closest('.row');row.classList.toggle('open');
      b.textContent=row.classList.contains('open')?'hide the chain':'show the chain';});});
  }
  function renderBeliefs(){
    var host=document.getElementById('beliefs');if(!host||!DATA.beliefs)return;
    host.innerHTML=DATA.beliefs.map(function(b){
      return '<div class="evo"><div class="el">'+esc(b.label)+'</div>'
        +(b.moved_by?'<div class="ck" style="margin-bottom:8px;color:var(--dimmed);">moved by: '+esc(b.moved_by)+'</div>':'')
        +'<div class="tl">'+b.points.map(function(p){
          return '<div class="tp"><div class="tt">'+esc(p.t)+'</div><div class="tc">'+esc(p.note)+'</div><div class="tcf">'+p.conf.toFixed(2)+'</div></div>';
        }).join('')+'</div></div>';
    }).join('');
  }
  var seg=document.getElementById('bandseg');
  if(seg)seg.querySelectorAll('button').forEach(function(btn){btn.addEventListener('click',function(){
    seg.querySelectorAll('button').forEach(function(x){x.classList.remove('on');});btn.classList.add('on');
    band=btn.getAttribute('data-band');renderLedger();});});
  var ex=document.getElementById('export');
  if(ex)ex.addEventListener('click',function(){
    var blob=new Blob([JSON.stringify(DATA,null,2)],{type:'application/json'});
    var u=URL.createObjectURL(blob);var a=document.createElement('a');a.href=u;a.download='{{EXPORT_FILE}}';a.click();URL.revokeObjectURL(u);});
  var xa=document.getElementById('expand');
  if(xa)xa.addEventListener('click',function(){
    var open=document.querySelectorAll('.row.open').length===0;
    document.querySelectorAll('.row').forEach(function(r){r.classList.toggle('open',open);});
    document.querySelectorAll('.togg').forEach(function(b){b.textContent=open?'hide the chain':'show the chain';});
    xa.textContent=open?'collapse all':'expand all';});
  renderLedger();renderBeliefs();
})();
