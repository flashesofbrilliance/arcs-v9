#!/usr/bin/env python3
"""PRL page factory — stamp a family-conformant status page from a JSON spec.
Usage: python3 generate.py spec.json > public/prl-status-<seg>.html
Atoms/molecules live in atoms.css (extracted from the live reference page).
Zero deps, zero LLM. The spec is the only thing that varies; the design system is frozen.
"""
import json, sys, html, pathlib

HERE = pathlib.Path(__file__).parent
CSS = (HERE/'atoms.css').read_text()
SEGS = [('','Overview'),('/status/progress','Progress'),('/status/crm','CRM routing'),
        ('/status/troubleshooting','Web forms'),('/status/tidio','Tidio delivery'),
        ('/status/atlas','Atlas'),('/status/build','Build')]

def nav(self_path):
    out=[]
    for p,label in SEGS:
        href='https://prl.arcs.care'+p
        here=' class="here"' if p==self_path else ''
        out.append(f'    <a{here} href="{href}">{label}</a>')
    return '<nav class="family">\n'+'\n'.join(out)+'\n  </nav>'

def row(r):  # molecule: checklist row
    return (f'  <div class="row"><span class="mark {r.get("markclass","go")}">{r.get("mark","&#10003;")}</span>'
            f'<div class="item"><b>{r["title"]}</b><span class="sub">{r["sub"]}</span></div>'
            f'<span class="stat {r.get("statclass","ok")}">{r["stat"]}</span></div>')

def table(t):  # molecule: card-stacking table
    head=''.join(f'<th>{h}</th>' for h in t['headers'])
    body='\n'.join('      <tr>'+''.join(f'<td class="{c.get("cls","")}">{c["text"]}</td>' for c in r)+'</tr>' for r in t['rows'])
    return f'  <div class="tblwrap"><table>\n    <thead><tr>{head}</tr></thead>\n    <tbody>\n{body}\n    </tbody>\n  </table></div>'

def section(sec):  # organism: labeled glass panel
    inner = '\n'.join(row(r) for r in sec.get('rows',[]))
    if 'table' in sec: inner += ('\n' if inner else '')+table(sec['table'])
    return (f'<div class="checklist"><div class="wrap">\n  <div class="label">{sec["label"]}</div>\n{inner}\n</div></div>')

def page(spec):  # template -> page
    seg=spec['seg']; self_path=f'/status/{seg}' if seg else ''
    sibs=' &middot; '.join(f'<a href="https://prl.arcs.care{p}">{p or "/overview"}</a>'.replace(f'>{p}<',f'>/{p.split("/")[-1]}<') if p else f'<a href="https://prl.arcs.care">/overview</a>' for p,_ in SEGS if p!=self_path)
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{spec['title_tag']}</title>
<style>{CSS}</style>
<script>window.va=window.va||function(){{(window.vaq=window.vaq||[]).push(arguments)}}</script>
<script defer src="/_vercel/insights/script.js"></script>

<header><div class="wrap">
  <div class="kick"><span class="dot"></span>PRL Resins &middot; Chatbot Program</div>
  <h1>{spec['h1']}</h1>
  <div class="meta">{spec['meta']}</div>
</div></header>
<div class="navbar"><div class="wrap">
{nav(self_path)}
</div></div>
<div class="bluf"><div class="wrap">
  <p style="margin:0;font-size:20px;line-height:1.55">{spec['bluf']}</p>
</div></div>

{chr(10).join(section(s) for s in spec['sections'])}

<footer><div class="wrap">PRL Resins chatbot program &middot; prl.arcs.care{self_path or ""} &middot; siblings: {sibs}</div></footer>
'''

if __name__=='__main__':
    spec=json.load(open(sys.argv[1]))
    sys.stdout.write(page(spec))
