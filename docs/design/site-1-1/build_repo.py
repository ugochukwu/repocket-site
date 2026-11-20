# Builds repocket-site/index.html from the design page: repo head, self-hosted fonts, EN/DE spans, real links, repo footer.
import re,json,pathlib,subprocess
R=pathlib.Path(__file__).resolve().parents[3]
src=pathlib.Path(__file__).with_name('design-page.html').read_text()
old=subprocess.run(['git','-C',str(R),'show','origin/master:index.html'],capture_output=True,text=True).stdout
T=json.loads(pathlib.Path(__file__).with_name('strings.de.json').read_text())  # German for every English string on the page
css=src[src.index('<style>')+7:src.index('</style>')]
body=src[src.index('<svg width="0"'):src.index('<header class="top">')]+src[src.index('<main id="top">'):src.index('<footer>')]
js=src[src.index('<script>')+8:src.index('</script>')].strip()
lang_js=re.search(r"/\* German release:.*?\n",old,re.S).group(0).replace("document.querySelector('nav .wrap')","document.querySelector('.top nav')")
fonts='\n'.join(l for l in old.splitlines() if l.startswith('@font-face') and 'Space Mono' not in l or l.startswith('@font-face') and 'SpaceMono-700' in l)
# D-114: Recursive Sans Casual for money figures, self-hosted (assets/fonts/Recursive-latin-var.woff2); master does not carry it yet
fonts+='\n'+'@font-face{font-family:"Recursive";font-style:normal;font-weight:300 1000;font-display:swap;src:url("assets/fonts/Recursive-latin-var.woff2") format("woff2");unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD}'
def sub(a,b):
    global css
    assert a in css,a[:60]; css=css.replace(a,b,1)
sub('body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--ground)}\n','')
css=css.replace('"Avenir Next",','')
sub('*{box-sizing:border-box}','*{box-sizing:border-box}\nhtml{scroll-behavior:smooth}\n[data-lang="en"] [data-l="de"],[data-lang="de"] [data-l="en"]{display:none!important}')
sub('body{background:','body{margin:0;background:')
sub('.brand svg{width:36px;height:36px;border-radius:9px;flex:none}','.brand img{width:36px;height:36px;flex:none}\n.brand-lockup{display:flex;align-items:center;gap:18px}\n.mugo,.mugo-credit{display:inline-flex;align-items:center;font-family:"Space Mono",ui-monospace,SFMono-Regular,Menlo,monospace;font-weight:700;letter-spacing:.14em;text-transform:uppercase;text-decoration:none;white-space:nowrap;color:var(--ink2)}\n.mugo{gap:6px;font-size:10px}.mugo img{width:13px;height:13px;flex:none}\n.mugo-credit{gap:10px;font-size:12px}.mugo-credit img{width:20px;height:20px;flex:none}\n.mugo-credit-row{width:100%;display:flex;padding-top:18px}\n.lang{display:flex;padding:3px;border-radius:999px;background:var(--track);gap:2px}\n.lang button{all:unset;cursor:pointer;padding:6px 12px;border-radius:999px;font:600 13px var(--text);color:var(--ink)}\n.lang button[aria-pressed="true"]{background:var(--ink);color:var(--ground)}')
sub('.top nav a.nav-link{display:none}','.top nav a.nav-link,.mugo-label{display:none}')
sub('@media (prefers-reduced-motion:reduce){','@media (prefers-color-scheme:dark){.mugo img,.mugo-credit img{filter:brightness(0) invert(.85)}}\n@media (prefers-reduced-motion:reduce){\n  html{scroll-behavior:auto}')
body=body.replace('https://apps.apple.com/','https://apps.apple.com/app/id6809761332')
sp=lambda e,d:f'<span data-l="en">{e}</span><span data-l="de">{d}</span>'
left=[]
for e in sorted(T,key=len,reverse=True):
    if '>'+e+'<' in body: body=body.replace('>'+e+'<','>'+sp(e,T[e])+'<')
H='Know where your money goes.'; de=T[H].rsplit(' ',1)
assert '<h1>Know where your money <span class="sq">goes.</span></h1>' in body
body=body.replace('<h1>Know where your money <span class="sq">goes.</span></h1>','<h1>'+sp('Know where your money <span class="sq">goes.</span>',de[0]+' <span class="sq">'+de[1]+'</span>')+'</h1>')
body=body.replace('</svg>With the unlock</span>','</svg>'+sp('With the unlock','Mit der Freischaltung')+'</span>')
ger=iter(['Keiner','Keins']); body=re.sub(r'<dd>None</dd>',lambda m:'<dd>'+sp('None',next(ger))+'</dd>',body)
body=body.replace('€8.99<small>once</small>',sp('€8.99<small>once</small>','8,99 €<small>einmal</small>'))
# report prose left untranslated
for m in re.findall(r'<(?:h[123]|p|li|summary|dt)[^>]*>([^<]{4,})<',body): left.append(m)
desc="Repocket is an expense tracker for iPhone. Type the amount, tap a category, saved. No bank login, no subscription. Free with 10 categories, pay once for the rest."
title="Repocket · Know where your money goes"
head=old[:old.index('<style>')]
head=re.sub(r'<title>.*?</title>',f'<title>{title}</title>',head)
for k in ('name="description"','property="og:description"','name="twitter:description"'): head=re.sub('(<meta '+k+' content=")[^"]*',r'\g<1>'+desc,head)
for k in ('og:title','twitter:title'): head=re.sub('('+k+'" content=")[^"]*',r'\g<1>'+title,head)
head=head.replace('og.png?v=2','og.png?v=3')  # the 1.1 share image, so link previews refetch it
head=head.replace('<meta name="viewport"','<meta name="color-scheme" content="light dark">\n<meta name="viewport"')
nav='''<header class="top"><div class="w">
 <div class="brand-lockup">
  <a class="brand" href="#"><img src="assets/mark.svg" alt="">Repocket</a>
  <a class="mugo" href="https://mugoworks.com"><img src="assets/mark-on-light.svg" width="13" height="13" alt="mugo works mark"><span class="mugo-label">BY MUGO WORKS</span></a>
 </div>
 <nav aria-label="Site">
  <a class="nav-link" href="#price">'''+sp('Price','Preis')+'''</a>
  <a class="nav-link" href="#privacy">'''+sp('Privacy','Datenschutz')+'''</a>
  <a class="get small" href="https://apps.apple.com/app/id6809761332">'''+sp('Get the app','App laden')+'''</a>
 </nav>
</div></header>
'''
foot=old[old.index('<footer>'):old.index('</footer>')+9].replace('<footer><div class="wrap">','<footer><div class="w">')
# The How to guides and the press kit still show the 1.0 app, so nothing links to them until they are redone for 1.1.
for hidden in ('<a data-l="en" href="how-to/">How to</a>','<a href="press.html"><span data-l="en">Press kit</span><span data-l="de">Pressematerial</span></a>'):
    assert hidden in foot; foot=foot.replace(hidden,'')
foot='\n'.join(l for l in foot.split('\n') if l.strip())
out=head+'<style>\n'+fonts+'\n'+css.strip()+'\n</style>\n</head>\n<body>\n'+nav+body.rstrip()+'\n\n'+foot+'\n<script>\n(function(){\n '+lang_js+'})();\n'+js+'\n</script>\n</body>\n</html>\n'
(R/'index.html').write_text(out)
print(len(out),'dashes',len(re.findall('[–—]',out)),'untranslated:',left)
