#!/usr/bin/env python3
"""Render ../output/belmont_leads.html: a self-contained, phone-friendly browser for the lead lists.

Reads ../output/belmont_all_residential_scored.csv and ../output/summary.json. Embeds every absentee,
unknown-occupancy, estate-owned, life-estate or tax-delinquent record as JSON; all filtering runs in
the browser, so the file works offline and as a published artifact.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "output")

FIELDS = ["property_address", "unit", "property_type", "owner_name", "owner_type", "mailing_address", "mailing_city",
          "mailing_state", "mailing_zip", "occupancy", "priority_score", "estate_or_heirs", "life_estate", "trust",
          "corporate", "care_of_mailing", "et_al_multiple_owners", "likely_inherited", "tax_delinquent", "owner_next_door",
          "last_sale_date", "last_sale_price", "last_sale_type", "years_since_last_sale", "assessed_total", "year_built",
          "units", "living_area_sqft", "parcel_id", "lat", "lon", "deed_book", "deed_page", "foreign_address_hint",
          "tax_delinquent_detail", "is_land"]
LAND_TYPES = {"Accessory land with improvement", "Developable residential land", "Potentially developable residential land",
              "Undevelopable residential land"}


def load_rows():
    rows = list(csv.DictReader(open(os.path.join(OUT, "belmont_all_residential_scored.csv"), encoding="utf-8")))
    keep = []
    for r in rows:
        if r["owner_type"].startswith("institutional"):
            continue
        if (r["occupancy"].startswith("absentee") or r["occupancy"].startswith("unknown") or r["estate_or_heirs"] == "YES"
                or r["life_estate"] == "YES" or r["tax_delinquent"] == "YES" or r["care_of_mailing"] == "YES"):
            r["is_land"] = "YES" if r["property_type"] in LAND_TYPES else ""
            keep.append([r[f] for f in FIELDS])
    return keep


TEMPLATE = r"""<title>Belmont Absentee Owners</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:wght@600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --bg:#F4F6F9; --surface:#FFFFFF; --ink:#172130; --muted:#5B6878; --line:#D8DFE7; --line-strong:#B8C3CF;
  --accent:#1F3A5F; --accent-ink:#FFFFFF; --accent-soft:#E3EBF5; --focus:#2F6FD6;
  --c-country:#6B2D8B; --c-state:#2F4FA3; --c-ma:#0F7B7B; --c-belmont:#4E5D6E; --c-unknown:#7A7F87;
  --c-estate:#B25E09; --c-tax:#B3261E; --c-inherit:#7A4E00; --c-le:#3D6B2E; --pill-ink:#FFFFFF;
  --shadow:0 1px 2px rgba(23,33,48,.06),0 4px 14px rgba(23,33,48,.05);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#0E141B; --surface:#161E27; --ink:#E7ECF2; --muted:#97A3B1; --line:#283442; --line-strong:#3A4859;
    --accent:#8FB4E8; --accent-ink:#0E141B; --accent-soft:#1B2A3D; --focus:#8FB4E8;
    --c-country:#C08BE0; --c-state:#8FA8F0; --c-ma:#5FC4C4; --c-belmont:#9FB0C2; --c-unknown:#9AA3AE;
    --c-estate:#F0A85A; --c-tax:#F08A82; --c-inherit:#E0B463; --c-le:#8FCB7C; --pill-ink:#0E141B;
    --shadow:0 1px 2px rgba(0,0,0,.4);
  }
}
:root[data-theme="dark"]{
  --bg:#0E141B; --surface:#161E27; --ink:#E7ECF2; --muted:#97A3B1; --line:#283442; --line-strong:#3A4859;
  --accent:#8FB4E8; --accent-ink:#0E141B; --accent-soft:#1B2A3D; --focus:#8FB4E8;
  --c-country:#C08BE0; --c-state:#8FA8F0; --c-ma:#5FC4C4; --c-belmont:#9FB0C2; --c-unknown:#9AA3AE;
  --c-estate:#F0A85A; --c-tax:#F08A82; --c-inherit:#E0B463; --c-le:#8FCB7C; --pill-ink:#0E141B;
  --shadow:0 1px 2px rgba(0,0,0,.4);
}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:15px;line-height:1.45;margin:0}
.wrap{max-width:960px;margin:0 auto;padding-inline:16px;padding-block:0 48px}
header.top{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);border-bottom:1px solid var(--line);padding-block:14px 10px}
h1{font-family:"IBM Plex Serif",Georgia,serif;font-weight:600;font-size:1.45rem;margin:0;letter-spacing:-.01em;text-wrap:balance}
.sub{color:var(--muted);font-size:.86rem;margin-top:2px}
.count{font-variant-numeric:tabular-nums;font-weight:600;color:var(--ink)}
.controls{display:flex;flex-direction:column;gap:10px;margin-top:12px}
.search{width:100%;padding:10px 12px;border:1px solid var(--line-strong);border-radius:8px;background:var(--surface);color:var(--ink);font:inherit;font-size:.95rem}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid var(--line-strong);background:var(--surface);color:var(--ink);border-radius:999px;padding:5px 11px;font:inherit;font-size:.82rem;cursor:pointer;line-height:1.2}
.chip[aria-pressed="true"]{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.chip .n{font-variant-numeric:tabular-nums;opacity:.75;margin-left:4px}
.selects{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}
.selects label{display:flex;flex-direction:column;gap:3px;font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
select{padding:7px 8px;border:1px solid var(--line-strong);border-radius:6px;background:var(--surface);color:var(--ink);font:inherit;font-size:.88rem}
button:focus-visible,select:focus-visible,input:focus-visible,a:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
.legend{display:flex;flex-wrap:wrap;gap:6px 14px;color:var(--muted);font-size:.78rem;margin-top:10px}
.legend span::before{content:"";display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--sw);margin-right:5px;vertical-align:0}
main{display:flex;flex-direction:column;gap:10px;margin-top:14px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 14px;box-shadow:var(--shadow)}
.card.tax{border-color:var(--c-tax);border-width:2px}
.row1{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}
.pill{display:inline-block;font-size:.72rem;font-weight:600;letter-spacing:.02em;padding:2px 8px;border-radius:999px;color:var(--pill-ink);background:var(--pc)}
.score{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:.78rem;color:var(--muted);white-space:nowrap}
.score b{color:var(--ink);font-weight:500}
.addr{font-weight:600;font-size:1.05rem;margin-top:6px;line-height:1.3}
.addr small{font-weight:400;color:var(--muted);font-size:.85rem;margin-left:6px}
.kv{display:grid;grid-template-columns:auto 1fr;gap:2px 10px;margin-top:6px;font-size:.9rem}
.kv dt{color:var(--muted);font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;padding-top:3px}
.kv dd{margin:0}
.kv dd .otype{display:block;color:var(--muted);font-size:.78rem}
.badges{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}
.badge{font-size:.72rem;padding:2px 7px;border-radius:5px;border:1px solid var(--bc);color:var(--bc);font-weight:500}
.meta{display:flex;flex-wrap:wrap;gap:4px 14px;margin-top:8px;color:var(--muted);font-size:.8rem;font-variant-numeric:tabular-nums}
.meta a{color:var(--accent);text-decoration:none;font-weight:500}
.meta a:hover{text-decoration:underline}
.mono{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:.78rem}
.more{align-self:center;margin-top:6px;padding:10px 18px;border-radius:8px;border:1px solid var(--line-strong);background:var(--surface);color:var(--ink);font:inherit;cursor:pointer}
.empty{color:var(--muted);text-align:center;padding:30px 0}
footer{color:var(--muted);font-size:.8rem;margin-top:28px;border-top:1px solid var(--line);padding-top:14px;max-width:70ch}
footer a{color:var(--accent)}
@media (min-width:700px){ .controls{flex-direction:column} .kv{grid-template-columns:auto 1fr auto 1fr} }
@media (prefers-reduced-motion:no-preference){ .chip,.card{transition:background-color .12s,border-color .12s} }
</style>
<div class="wrap">
<header class="top">
  <h1>Belmont Absentee Owners</h1>
  <div class="sub">Belmont, MA properties whose tax bill is mailed away from the property, plus estate, life-estate and tax-taking records. Assessor extract __VINTAGE__ (fiscal 2024), built __BUILT__. Showing <span class="count" id="shown">0</span> of <span class="count" id="total">0</span> records.</div>
  <div class="controls">
    <input class="search" id="q" type="search" placeholder="Search address, owner, mailing address or parcel ID" aria-label="Search" autocomplete="off">
    <div class="chips" id="views" role="group" aria-label="Quick views"></div>
    <div class="selects">
      <label>Owner type<select id="otype"><option value="">All</option></select></label>
      <label>Property type<select id="ptype"><option value="">All</option></select></label>
      <label>Where the bill goes<select id="occ"><option value="">All</option></select></label>
      <label>Sort by<select id="sort"><option value="score">Priority score</option><option value="value">Assessed value</option><option value="years">Years since last transfer</option><option value="addr">Street address</option></select></label>
    </div>
  </div>
  <div class="legend">
    <span style="--sw:var(--c-country)">Out of country</span><span style="--sw:var(--c-state)">Out of state</span><span style="--sw:var(--c-ma)">Elsewhere in MA</span><span style="--sw:var(--c-belmont)">Elsewhere in Belmont</span><span style="--sw:var(--c-unknown)">PO Box / unknown</span><span style="--sw:var(--c-estate)">Owner-occupied estate / life estate</span>
  </div>
</header>
<main id="list" aria-live="polite"></main>
<footer>
  <p><strong>How occupancy is inferred.</strong> The assessor's owner mailing address (where the tax bill goes) is compared with the property address; a match means owner-occupied. Belmont has no owner-occupancy flag of its own. Ownership is as of the fiscal 2024 extract, the newest Belmont has published to MassGIS; verify in the town's <a href="https://www.belmont-ma.gov/229/Real-Estate-Database">Real Estate Database</a> before outreach.</p>
  <p><strong>Tax delinquency.</strong> Only one parcel has a published record: the town's <a href="https://www.belmont-ma.gov/2040/Notice-of-Tax-Taking">Notice of Tax Taking</a> for 12 Midland St (Feb 27, 2025). Belmont does not publish its delinquent list; request it from the Treasurer/Collector (treasurers@belmont-ma.gov) or search Instruments of Taking at the Middlesex South Registry of Deeds.</p>
  <p>Source: MassGIS Level 3 standardized assessors' parcels, town 026. Priority score = absentee distance + inherited-property signals (+10 for a tax taking).</p>
</footer>
</div>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  var F = __FIELDS__;
  var I = {}; F.forEach(function(f,i){ I[f]=i; });
  var rows = JSON.parse(document.getElementById('data').textContent);
  var g = function(r,f){ return r[I[f]]; };
  var land = function(r){ return g(r,'is_land')==='YES'; };
  var views = [
    {id:'absentee', label:'Non-owner-occupied', test:function(r){ return !land(r) && g(r,'occupancy').indexOf('absentee')===0; }},
    {id:'inherited', label:'Likely inherited', test:function(r){ return !land(r) && g(r,'likely_inherited')==='YES' && g(r,'occupancy').indexOf('absentee')===0; }},
    {id:'people', label:'Individuals & trusts', test:function(r){ return !land(r) && g(r,'occupancy').indexOf('absentee')===0 && g(r,'owner_type')!=='LLC / corporate'; }},
    {id:'state', label:'Out of state', test:function(r){ return !land(r) && g(r,'occupancy').indexOf('out of state')>=0; }},
    {id:'country', label:'Out of country', test:function(r){ return !land(r) && g(r,'occupancy').indexOf('out of country')>=0; }},
    {id:'ma', label:'Elsewhere in MA', test:function(r){ return !land(r) && g(r,'occupancy').indexOf('elsewhere in MA')>=0; }},
    {id:'belmont', label:'Elsewhere in Belmont', test:function(r){ return !land(r) && g(r,'occupancy').indexOf('elsewhere in Belmont')>=0; }},
    {id:'estate', label:'Estate & heirs', test:function(r){ return !land(r) && (g(r,'estate_or_heirs')==='YES' || g(r,'care_of_mailing')==='YES'); }},
    {id:'le', label:'Life-estate watchlist', test:function(r){ return !land(r) && g(r,'life_estate')==='YES'; }},
    {id:'pobox', label:'PO Box in Belmont / unknown', test:function(r){ return !land(r) && g(r,'occupancy').indexOf('unknown')===0; }},
    {id:'tax', label:'Tax taking on record', test:function(r){ return g(r,'tax_delinquent')==='YES'; }},
    {id:'land', label:'Vacant land', test:function(r){ return land(r); }},
    {id:'all', label:'Everything', test:function(){ return true; }}
  ];
  var state = {view:'absentee', q:'', otype:'', ptype:'', occ:'', sort:'score', page:1};
  try { var saved = JSON.parse(localStorage.getItem('belmont-leads-filters')||'null'); if (saved && typeof saved==='object') { for (var k in state) if (k in saved && k!=='page') state[k]=saved[k]; } } catch(e){}
  function save(){ try { localStorage.setItem('belmont-leads-filters', JSON.stringify(state)); } catch(e){} }

  function uniq(f){ var s={}; rows.forEach(function(r){ if (g(r,f)) s[g(r,f)]=1; }); return Object.keys(s).sort(); }
  function fill(id, f){ var sel=document.getElementById(id); uniq(f).forEach(function(v){ var o=document.createElement('option'); o.value=v; o.textContent=v; sel.appendChild(o); }); sel.value=state[id]||''; }
  fill('otype','owner_type'); fill('ptype','property_type'); fill('occ','occupancy');
  document.getElementById('sort').value = state.sort;
  document.getElementById('q').value = state.q;

  var viewsEl = document.getElementById('views');
  views.forEach(function(v){
    var b=document.createElement('button'); b.type='button'; b.className='chip'; b.dataset.id=v.id;
    var n=rows.filter(v.test).length;
    b.innerHTML='<span></span><span class="n"></span>'; b.firstChild.textContent=v.label; b.lastChild.textContent=n.toLocaleString();
    b.addEventListener('click', function(){ state.view=v.id; state.page=1; save(); render(); });
    viewsEl.appendChild(b);
  });

  function money(v){ v=Number(v); return v ? '$'+v.toLocaleString() : ''; }
  function occColor(o){ if (o.indexOf('out of country')>=0) return 'var(--c-country)'; if (o.indexOf('out of state')>=0) return 'var(--c-state)'; if (o.indexOf('elsewhere in MA')>=0) return 'var(--c-ma)'; if (o.indexOf('elsewhere in Belmont')>=0) return 'var(--c-belmont)'; if (o.indexOf('unknown')===0 || o.indexOf('unclear')>=0) return 'var(--c-unknown)'; return 'var(--c-estate)'; }
  function occLabel(o){ return o.replace('absentee - ','').replace('owner-occupied (tax bill goes to the property)','owner-occupied').replace('owner-occupied (other unit number of same building)','owner-occupied (same building)'); }
  function el(tag, cls, text){ var e=document.createElement(tag); if (cls) e.className=cls; if (text!=null) e.textContent=text; return e; }

  function card(r){
    var c = el('article','card'+(g(r,'tax_delinquent')==='YES'?' tax':''));
    var row1 = el('div','row1');
    var pill = el('span','pill', occLabel(g(r,'occupancy'))); pill.style.setProperty('--pc', occColor(g(r,'occupancy'))); row1.appendChild(pill);
    var sc = el('span','score'); sc.appendChild(document.createTextNode('score ')); sc.appendChild(el('b',null,g(r,'priority_score'))); row1.appendChild(sc);
    c.appendChild(row1);
    var addr = el('div','addr', g(r,'property_address')); addr.appendChild(el('small',null,g(r,'property_type'))); c.appendChild(addr);
    var kv = el('dl','kv');
    kv.appendChild(el('dt',null,'Owner')); var od=el('dd',null,g(r,'owner_name')); od.appendChild(el('small','otype',g(r,'owner_type'))); kv.appendChild(od);
    var mail = [g(r,'mailing_address'), [g(r,'mailing_city'), g(r,'mailing_state'), g(r,'mailing_zip')].filter(Boolean).join(' ')].filter(Boolean).join(', ');
    kv.appendChild(el('dt',null,'Bill goes to')); kv.appendChild(el('dd',null, mail || '(no mailing address on file)'));
    c.appendChild(kv);
    var badges = el('div','badges');
    function badge(t, col){ var b=el('span','badge',t); b.style.setProperty('--bc', col); badges.appendChild(b); }
    if (g(r,'tax_delinquent')==='YES') badge('Tax taking on record', 'var(--c-tax)');
    if (g(r,'likely_inherited')==='YES') badge('Likely inherited / family transfer', 'var(--c-inherit)');
    if (g(r,'estate_or_heirs')==='YES') badge('Estate / heirs', 'var(--c-estate)');
    if (g(r,'life_estate')==='YES') badge('Life estate', 'var(--c-le)');
    if (g(r,'trust')==='YES') badge('Trust', 'var(--c-belmont)');
    if (g(r,'care_of_mailing')==='YES') badge('Bill sent c/o', 'var(--c-estate)');
    if (g(r,'et_al_multiple_owners')==='YES') badge('Multiple owners (et al)', 'var(--c-inherit)');
    if (g(r,'foreign_address_hint')) badge('Abroad: '+g(r,'foreign_address_hint'), 'var(--c-country)');
    if (g(r,'owner_next_door')==='YES') badge('Owner next door', 'var(--c-unknown)');
    if (g(r,'last_sale_type') && g(r,'last_sale_type').indexOf('nominal')===0) badge('Last transfer at nominal price', 'var(--c-inherit)');
    if (badges.childNodes.length) c.appendChild(badges);
    var meta = el('div','meta');
    if (g(r,'assessed_total')) meta.appendChild(el('span',null,'Assessed '+money(g(r,'assessed_total'))));
    if (g(r,'year_built')) meta.appendChild(el('span',null,'Built '+g(r,'year_built')));
    if (g(r,'last_sale_date')) meta.appendChild(el('span',null,'Last transfer '+g(r,'last_sale_date').slice(0,4)+(g(r,'years_since_last_sale')!==''?' ('+g(r,'years_since_last_sale')+' yrs)':'')+(Number(g(r,'last_sale_price'))>100?' '+money(g(r,'last_sale_price')):'')));
    if (g(r,'living_area_sqft')) meta.appendChild(el('span',null,Number(g(r,'living_area_sqft')).toLocaleString()+' sq ft'));
    var pid = el('span','mono','Parcel '+g(r,'parcel_id')); meta.appendChild(pid);
    if (g(r,'deed_book')) meta.appendChild(el('span','mono','Bk '+g(r,'deed_book')+' Pg '+g(r,'deed_page')));
    if (g(r,'lat')) { var a=el('a',null,'Map'); a.href='https://maps.google.com/?q='+g(r,'lat')+','+g(r,'lon'); a.target='_blank'; a.rel='noopener'; meta.appendChild(a); }
    c.appendChild(meta);
    if (g(r,'tax_delinquent_detail')) { var d=el('div','meta'); d.style.color='var(--c-tax)'; d.textContent=g(r,'tax_delinquent_detail'); c.appendChild(d); }
    return c;
  }

  var PAGE = 100;
  function render(){
    var view = views.filter(function(v){ return v.id===state.view; })[0] || views[0];
    var q = state.q.trim().toUpperCase();
    var out = rows.filter(function(r){
      if (!view.test(r)) return false;
      if (state.otype && g(r,'owner_type')!==state.otype) return false;
      if (state.ptype && g(r,'property_type')!==state.ptype) return false;
      if (state.occ && g(r,'occupancy')!==state.occ) return false;
      if (q) { var hay=(g(r,'property_address')+' '+g(r,'owner_name')+' '+g(r,'mailing_address')+' '+g(r,'mailing_city')+' '+g(r,'parcel_id')).toUpperCase(); if (hay.indexOf(q)<0) return false; }
      return true;
    });
    out.sort(function(a,b){
      if (state.sort==='value') return Number(g(b,'assessed_total'))-Number(g(a,'assessed_total'));
      if (state.sort==='years') return (Number(g(b,'years_since_last_sale'))||0)-(Number(g(a,'years_since_last_sale'))||0);
      if (state.sort==='addr') { var sa=g(a,'property_address').replace(/^[\d\-A-Z]+\s/,''), sb=g(b,'property_address').replace(/^[\d\-A-Z]+\s/,''); return sa<sb?-1:sa>sb?1:0; }
      return Number(g(b,'priority_score'))-Number(g(a,'priority_score')) || (g(a,'property_address')<g(b,'property_address')?-1:1);
    });
    Array.prototype.forEach.call(viewsEl.children, function(b){ b.setAttribute('aria-pressed', b.dataset.id===state.view ? 'true' : 'false'); });
    document.getElementById('total').textContent = rows.length.toLocaleString();
    document.getElementById('shown').textContent = out.length.toLocaleString();
    var list = document.getElementById('list'); list.textContent='';
    if (!out.length) { list.appendChild(el('div','empty','No records match these filters.')); return; }
    var n = Math.min(out.length, PAGE*state.page);
    var frag = document.createDocumentFragment();
    for (var i=0;i<n;i++) frag.appendChild(card(out[i]));
    list.appendChild(frag);
    if (n < out.length) { var m=el('button','more','Show '+Math.min(PAGE,out.length-n)+' more of '+(out.length-n).toLocaleString()); m.type='button'; m.addEventListener('click', function(){ state.page++; render(); }); list.appendChild(m); }
  }
  document.getElementById('q').addEventListener('input', function(e){ state.q=e.target.value; state.page=1; save(); render(); });
  ['otype','ptype','occ','sort'].forEach(function(id){ document.getElementById(id).addEventListener('change', function(e){ state[id]=e.target.value; state.page=1; save(); render(); }); });
  render();
})();
</script>
"""


def main():
    rows = load_rows()
    summary = json.load(open(os.path.join(OUT, "summary.json")))
    data = json.dumps(rows, separators=(",", ":")).replace("</", "<\\/")
    html = (TEMPLATE.replace("__DATA__", data).replace("__FIELDS__", json.dumps(FIELDS))
            .replace("__VINTAGE__", summary["data_vintage"]).replace("__BUILT__", summary["built"]))
    path = os.path.join(OUT, "belmont_leads.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {path}: {len(rows)} records, {os.path.getsize(path)/1e6:.2f} MB")


if __name__ == "__main__":
    main()
