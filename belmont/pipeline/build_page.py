#!/usr/bin/env python3
"""Render ../output/belmont_leads.html: a self-contained, phone-friendly browser for the lead lists
plus a Campaign mode (mailing households, status tracking, printable letters, CSV export).

Reads ../output/belmont_all_residential_scored.csv, ../output/summary.json and ../output/campaigns.json.
Publish with capabilities {db: {}, downloads: true}: statuses and sender settings live in the
artifact's shared database; without it the page falls back to this device's storage.
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
  --c-estate:#B25E09; --c-tax:#B3261E; --c-inherit:#7A4E00; --c-le:#3D6B2E; --c-good:#2E7D32; --pill-ink:#FFFFFF;
  --shadow:0 1px 2px rgba(23,33,48,.06),0 4px 14px rgba(23,33,48,.05);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#0E141B; --surface:#161E27; --ink:#E7ECF2; --muted:#97A3B1; --line:#283442; --line-strong:#3A4859;
    --accent:#8FB4E8; --accent-ink:#0E141B; --accent-soft:#1B2A3D; --focus:#8FB4E8;
    --c-country:#C08BE0; --c-state:#8FA8F0; --c-ma:#5FC4C4; --c-belmont:#9FB0C2; --c-unknown:#9AA3AE;
    --c-estate:#F0A85A; --c-tax:#F08A82; --c-inherit:#E0B463; --c-le:#8FCB7C; --c-good:#7FD08A; --pill-ink:#0E141B;
    --shadow:0 1px 2px rgba(0,0,0,.4);
  }
}
:root[data-theme="dark"]{
  --bg:#0E141B; --surface:#161E27; --ink:#E7ECF2; --muted:#97A3B1; --line:#283442; --line-strong:#3A4859;
  --accent:#8FB4E8; --accent-ink:#0E141B; --accent-soft:#1B2A3D; --focus:#8FB4E8;
  --c-country:#C08BE0; --c-state:#8FA8F0; --c-ma:#5FC4C4; --c-belmont:#9FB0C2; --c-unknown:#9AA3AE;
  --c-estate:#F0A85A; --c-tax:#F08A82; --c-inherit:#E0B463; --c-le:#8FCB7C; --c-good:#7FD08A; --pill-ink:#0E141B;
  --shadow:0 1px 2px rgba(0,0,0,.4);
}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:15px;line-height:1.45;margin:0}
.wrap{max-width:960px;margin:0 auto;padding-inline:16px;padding-block:0 48px}
header.top{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);border-bottom:1px solid var(--line);padding-block:10px 10px}
.bar{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}
h1{font-family:"IBM Plex Serif",Georgia,serif;font-weight:600;font-size:1.3rem;margin:0;letter-spacing:-.01em;text-wrap:balance;line-height:1.2}
.sub{color:var(--muted);font-size:.82rem;margin-top:2px}
.count{font-variant-numeric:tabular-nums;font-weight:600;color:var(--ink)}
.modes{display:inline-flex;border:1px solid var(--line-strong);border-radius:999px;overflow:hidden;background:var(--surface)}
.mode{border:0;background:transparent;color:var(--ink);font:inherit;font-size:.86rem;font-weight:500;padding:8px 14px;min-height:40px;cursor:pointer}
.mode[aria-selected="true"]{background:var(--accent);color:var(--accent-ink)}
.searchrow{display:flex;gap:8px;margin-top:10px;align-items:center}
.search{flex:1;min-width:0;width:100%;padding:11px 12px;border:1px solid var(--line-strong);border-radius:8px;background:var(--surface);color:var(--ink);font:inherit;font-size:16px}
.fbtn{display:none;align-items:center;gap:6px;min-height:40px;padding:6px 14px;border-radius:999px;border:1px solid var(--line-strong);background:var(--surface);color:var(--ink);font:inherit;font-size:.9rem;font-weight:500;cursor:pointer;white-space:nowrap}
.fbtn[aria-expanded="true"],.fbtn.active{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.panel{margin-top:12px;display:flex;flex-direction:column;gap:12px}
.panel-head,.apply{display:none}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid var(--line-strong);background:var(--surface);color:var(--ink);border-radius:999px;padding:7px 12px;min-height:36px;font:inherit;font-size:.86rem;cursor:pointer;line-height:1.2}
.chip[aria-pressed="true"]{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.chip .n{font-variant-numeric:tabular-nums;opacity:.75;margin-left:4px}
.selects{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.selects label,.sheet label,.ctl label{display:flex;flex-direction:column;gap:3px;font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
select{padding:9px 8px;min-height:40px;border:1px solid var(--line-strong);border-radius:6px;background:var(--surface);color:var(--ink);font:inherit;font-size:16px;max-width:100%}
button:focus-visible,select:focus-visible,input:focus-visible,textarea:focus-visible,a:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
.legend{display:flex;flex-wrap:wrap;gap:6px 14px;color:var(--muted);font-size:.78rem}
.legend span::before{content:"";display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--sw);margin-right:5px;vertical-align:0}
.about{color:var(--muted);font-size:.8rem;margin:0;max-width:70ch}
.btn{min-height:40px;padding:8px 14px;border-radius:8px;border:1px solid var(--line-strong);background:var(--surface);color:var(--ink);font:inherit;font-size:.88rem;font-weight:500;cursor:pointer}
.btn.primary{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.btn.warn{border-color:var(--c-tax);color:var(--c-tax)}
.actions{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.campbar{display:flex;flex-direction:column;gap:10px;margin-top:14px}
.progress{display:flex;flex-wrap:wrap;gap:6px 16px;color:var(--muted);font-size:.84rem;font-variant-numeric:tabular-nums}
.progress b{color:var(--ink)}
.notice{background:var(--accent-soft);color:var(--ink);border-radius:8px;padding:8px 12px;font-size:.84rem}
@media (max-width:699px){
  .fbtn{display:inline-flex}
  .panel{display:none;position:fixed;left:0;right:0;top:0;bottom:0;z-index:20;margin:0;background:var(--bg);overflow-y:auto;-webkit-overflow-scrolling:touch;overscroll-behavior:contain;padding:0 16px calc(env(safe-area-inset-bottom,0px) + 16px)}
  .panel.open{display:flex}
  .panel-head{display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:1;background:var(--bg);padding-block:calc(env(safe-area-inset-top,0px) + 12px) 10px;margin-inline:-16px;padding-inline:16px;border-bottom:1px solid var(--line)}
  .panel-head strong{font-size:1.05rem}
  .close{min-height:40px;padding:6px 14px;border-radius:999px;border:1px solid var(--line-strong);background:var(--surface);color:var(--ink);font:inherit;font-size:.9rem;cursor:pointer}
  .apply{display:block;position:sticky;bottom:0;width:100%;min-height:48px;margin-top:4px;padding:12px;border-radius:10px;border:0;background:var(--accent);color:var(--accent-ink);font:inherit;font-size:1rem;font-weight:600;cursor:pointer;box-shadow:var(--shadow)}
  html.noscroll,html.noscroll body{overflow:hidden;height:100%}
}
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
.card.camp .name{font-weight:600;font-size:1.05rem;margin-top:6px;line-height:1.3}
.mailblock{margin-top:8px;padding:8px 10px;border:1px dashed var(--line-strong);border-radius:8px;font-size:.92rem;line-height:1.35;display:flex;justify-content:space-between;gap:8px;align-items:flex-start}
.mini{flex:none;min-height:32px;padding:4px 10px;border-radius:6px;border:1px solid var(--line-strong);background:var(--surface);color:var(--ink);font:inherit;font-size:.78rem;cursor:pointer}
.props{margin-top:8px;font-size:.86rem;color:var(--muted);display:flex;flex-direction:column;gap:2px}
.props b{color:var(--ink);font-weight:500}
.ctl{display:grid;grid-template-columns:1fr auto;gap:8px;align-items:end;margin-top:10px}
textarea.notes{width:100%;margin-top:8px;min-height:44px;padding:8px 10px;border:1px solid var(--line-strong);border-radius:6px;background:var(--surface);color:var(--ink);font:inherit;font-size:16px;resize:vertical}
.sheet{margin-top:12px;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px;display:flex;flex-direction:column;gap:10px}
.sheet-head{display:flex;justify-content:space-between;align-items:center}
.sheet-head strong{font-size:1.05rem}
.sheet input,.sheet textarea{padding:9px 10px;border:1px solid var(--line-strong);border-radius:6px;background:var(--bg);color:var(--ink);font:inherit;font-size:16px}
.sheet textarea{min-height:220px;font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:13px;line-height:1.45}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}
.help{color:var(--muted);font-size:.8rem;margin:0}
.sheet label.checkrow{flex-direction:row;align-items:center;gap:6px;font-size:.85rem;text-transform:none;letter-spacing:0;color:var(--ink)}
.checkrow input{width:auto}
@media (max-width:699px){
  .sheet{position:fixed;left:0;right:0;top:0;bottom:0;z-index:20;margin:0;border:0;border-radius:0;overflow-y:auto;-webkit-overflow-scrolling:touch;overscroll-behavior:contain;padding:calc(env(safe-area-inset-top,0px) + 12px) 16px calc(env(safe-area-inset-bottom,0px) + 16px)}
}
footer{color:var(--muted);font-size:.8rem;margin-top:28px;border-top:1px solid var(--line);padding-top:14px;max-width:70ch}
footer a{color:var(--accent)}
#printarea{display:none}
@media print{
  body{background:#fff;color:#000}
  .wrap>*:not(#printarea){display:none!important}
  #printarea{display:block}
  .letter{page-break-after:always;break-after:page;font:12pt Georgia,"Times New Roman",serif;line-height:1.5;color:#000}
  .letter:last-child{page-break-after:auto;break-after:auto}
  .letter p{margin:0 0 11pt}
  .letter .from{font-size:9.5pt;margin-bottom:16pt}
  .letter ul{margin:0 0 11pt 18pt;padding:0}
}
@media (prefers-reduced-motion:no-preference){ .chip,.card,.btn{transition:background-color .12s,border-color .12s} }
</style>
<div class="wrap">
<header class="top">
  <div class="bar">
    <div>
      <h1>Belmont Absentee Owners</h1>
      <div class="sub">Showing <span class="count" id="shown">0</span> of <span class="count" id="total">0</span> <span id="unitword">records</span> · <span id="viewname">Non-owner-occupied</span></div>
    </div>
    <div class="modes" role="tablist" aria-label="Section">
      <button class="mode" role="tab" type="button" data-mode="leads" aria-selected="true">Leads</button>
      <button class="mode" role="tab" type="button" data-mode="campaign" aria-selected="false">Campaign</button>
    </div>
  </div>
  <div class="searchrow">
    <input class="search" id="q" type="search" placeholder="Search address, owner, mailing address or parcel ID" aria-label="Search" autocomplete="off">
    <button class="fbtn" id="fbtn" type="button" aria-expanded="false" aria-controls="panel">Filters</button>
  </div>
</header>
<section class="panel" id="panel" aria-label="Filters">
  <div class="panel-head"><strong>Filters</strong><button class="close" id="pclose" type="button">Done</button></div>
  <div class="chips" id="views" role="group" aria-label="Quick views"></div>
  <div class="selects">
    <label>Owner type<select id="otype"><option value="">All</option></select></label>
    <label>Property type<select id="ptype"><option value="">All</option></select></label>
    <label>Where the bill goes<select id="occ"><option value="">All</option></select></label>
    <label>Sort by<select id="sort"><option value="score">Priority score</option><option value="value">Assessed value</option><option value="years">Years since last transfer</option><option value="addr">Street address</option></select></label>
  </div>
  <div class="legend">
    <span style="--sw:var(--c-country)">Out of country</span><span style="--sw:var(--c-state)">Out of state</span><span style="--sw:var(--c-ma)">Elsewhere in MA</span><span style="--sw:var(--c-belmont)">Elsewhere in Belmont</span><span style="--sw:var(--c-unknown)">PO Box / unknown</span><span style="--sw:var(--c-estate)">Owner-occupied estate / life estate</span>
  </div>
  <p class="about">Belmont, MA properties whose tax bill is mailed away from the property, plus estate, life-estate and tax-taking records. Assessor extract __VINTAGE__ (fiscal 2024), built __BUILT__.</p>
  <button class="apply" id="papply" type="button">Show <span id="pcount">0</span> results</button>
</section>
<section class="campbar" id="campbar" hidden>
  <div class="selects"><label>Campaign<select id="camp"></select></label></div>
  <p class="about" id="campdesc"></p>
  <div class="chips" id="cstatus" role="group" aria-label="Status"></div>
  <div class="actions">
    <button class="btn primary" id="btn-print" type="button">Print letters for shown</button>
    <button class="btn" id="btn-csv" type="button">Save mailing list (CSV)</button>
    <button class="btn" id="btn-mark" type="button">Mark shown as Letter 1 sent</button>
    <button class="btn" id="btn-settings" type="button">Sender &amp; letter text</button>
  </div>
  <div class="progress" id="cprogress"></div>
  <div class="notice" id="cnotice" hidden></div>
</section>
<section class="sheet" id="settings" hidden aria-label="Sender and letter settings">
  <div class="sheet-head"><strong>Sender &amp; letter text</strong><button class="btn" id="settings-close" type="button">Close</button></div>
  <div class="grid2">
    <label>Your name<input id="s_sender_name" autocomplete="name"></label>
    <label>Company (optional)<input id="s_company"></label>
    <label>Phone<input id="s_phone" autocomplete="tel"></label>
    <label>Email<input id="s_email" autocomplete="email"></label>
    <label>Return address line 1<input id="s_return_address_1"></label>
    <label>Return address line 2<input id="s_return_address_2"></label>
    <label>Closing<input id="s_closing"></label>
    <label>Letter date (blank = today)<input id="s_letter_date"></label>
  </div>
  <label>Letter 1 body<textarea id="s_letter1"></textarea></label>
  <label>Letter 2 body (follow-up)<textarea id="s_letter2"></textarea></label>
  <p class="help">Merge fields: {{salutation}} {{contact_name}} {{first_names}} {{property_phrase}} {{property_address}} {{sender_name}} {{company}} {{phone}} {{email}} {{closing}} {{date}}. A line starting with "- " prints as a bullet.</p>
  <div class="actions">
    <button class="btn primary" id="settings-save" type="button">Save</button>
    <button class="btn" id="settings-reset" type="button">Reset letter text</button>
    <label class="checkrow"><input type="checkbox" id="s_which2"> Print letter 2 (follow-up) instead of letter 1</label>
  </div>
</section>
<main id="list" aria-live="polite"></main>
<footer>
  <p><strong>How occupancy is inferred.</strong> The assessor's owner mailing address (where the tax bill goes) is compared with the property address; a match means owner-occupied. Belmont has no owner-occupancy flag of its own. Ownership is as of the fiscal 2024 extract, the newest Belmont has published to MassGIS; verify in the town's <a href="https://www.belmont-ma.gov/229/Real-Estate-Database">Real Estate Database</a> before outreach.</p>
  <p><strong>Campaign tab.</strong> Owners at the same mailing address are combined into one household so nobody receives duplicate letters. Statuses and notes save to this page's shared database when opened in Claude, and to this device otherwise. A life-estate holder cannot sell alone: the family holding the remainder must sign too, so the letters invite them in. Keep outreach honest and unpressured; see the campaign README in the repository for Massachusetts rules.</p>
  <p><strong>Tax delinquency.</strong> Only one parcel has a published record: the town's <a href="https://www.belmont-ma.gov/2040/Notice-of-Tax-Taking">Notice of Tax Taking</a> for 12 Midland St (Feb 27, 2025). Belmont does not publish its delinquent list; request it from the Treasurer/Collector (treasurers@belmont-ma.gov) or search Instruments of Taking at the Middlesex South Registry of Deeds.</p>
  <p>Source: MassGIS Level 3 standardized assessors' parcels, town 026. Priority score = absentee distance + inherited-property signals (+10 for a tax taking).</p>
</footer>
<div id="printarea" aria-hidden="true"></div>
</div>
<script id="data" type="application/json">__DATA__</script>
<script id="campaigns" type="application/json">__CAMPAIGNS__</script>
<script>
(function(){
  var F = __FIELDS__;
  var I = {}; F.forEach(function(f,i){ I[f]=i; });
  var rows = JSON.parse(document.getElementById('data').textContent);
  var CAMP = JSON.parse(document.getElementById('campaigns').textContent);
  var STATUSES = CAMP.statuses;
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
  var state = {mode:'leads', view:'absentee', q:'', otype:'', ptype:'', occ:'', sort:'score', page:1, camp: CAMP.campaigns[0].id, cstatus:'', cpage:1};
  try { var saved = JSON.parse(localStorage.getItem('belmont-leads-filters')||'null'); if (saved && typeof saved==='object') { for (var k in state) if (k in saved && k!=='page' && k!=='cpage') state[k]=saved[k]; } } catch(e){}
  if (!CAMP.campaigns.some(function(c){ return c.id===state.camp; })) state.camp = CAMP.campaigns[0].id;
  function save(){ try { localStorage.setItem('belmont-leads-filters', JSON.stringify(state)); } catch(e){} }
  function el(tag, cls, text){ var e=document.createElement(tag); if (cls) e.className=cls; if (text!=null) e.textContent=text; return e; }
  function esc(s){ return String(s==null?'':s).replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function money(v){ v=Number(v); return v ? '$'+v.toLocaleString() : ''; }
  var $ = function(id){ return document.getElementById(id); };

  /* ---------- leads ---------- */
  function uniq(f){ var s={}; rows.forEach(function(r){ if (g(r,f)) s[g(r,f)]=1; }); return Object.keys(s).sort(); }
  function fill(id, f){ var sel=$(id); uniq(f).forEach(function(v){ var o=document.createElement('option'); o.value=v; o.textContent=v; sel.appendChild(o); }); sel.value=state[id]||''; }
  fill('otype','owner_type'); fill('ptype','property_type'); fill('occ','occupancy');
  $('sort').value = state.sort;
  $('q').value = state.q;
  var viewsEl = $('views');
  views.forEach(function(v){
    var b=document.createElement('button'); b.type='button'; b.className='chip'; b.dataset.id=v.id;
    var n=rows.filter(v.test).length;
    b.appendChild(el('span',null,v.label)); b.appendChild(el('span','n',n.toLocaleString()));
    b.addEventListener('click', function(){ state.view=v.id; state.page=1; save(); render(); });
    viewsEl.appendChild(b);
  });
  function occColor(o){ if (o.indexOf('out of country')>=0) return 'var(--c-country)'; if (o.indexOf('out of state')>=0) return 'var(--c-state)'; if (o.indexOf('elsewhere in MA')>=0) return 'var(--c-ma)'; if (o.indexOf('elsewhere in Belmont')>=0) return 'var(--c-belmont)'; if (o.indexOf('unknown')===0 || o.indexOf('unclear')>=0) return 'var(--c-unknown)'; return 'var(--c-estate)'; }
  function occLabel(o){ return o.replace('absentee - ','').replace('owner-occupied (tax bill goes to the property)','owner-occupied').replace('owner-occupied (other unit number of same building)','owner-occupied (same building)'); }
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
    meta.appendChild(el('span','mono','Parcel '+g(r,'parcel_id')));
    if (g(r,'deed_book')) meta.appendChild(el('span','mono','Bk '+g(r,'deed_book')+' Pg '+g(r,'deed_page')));
    if (g(r,'lat')) { var a=el('a',null,'Map'); a.href='https://maps.google.com/?q='+g(r,'lat')+','+g(r,'lon'); a.target='_blank'; a.rel='noopener'; meta.appendChild(a); }
    c.appendChild(meta);
    if (g(r,'tax_delinquent_detail')) { var d=el('div','meta'); d.style.color='var(--c-tax)'; d.textContent=g(r,'tax_delinquent_detail'); c.appendChild(d); }
    return c;
  }
  var PAGE = 100;
  function renderLeads(){
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
    $('total').textContent = rows.length.toLocaleString();
    $('shown').textContent = out.length.toLocaleString();
    $('unitword').textContent = 'records';
    $('pcount').textContent = out.length.toLocaleString();
    $('viewname').textContent = view.label;
    var active = (state.otype?1:0)+(state.ptype?1:0)+(state.occ?1:0)+(state.view!=='absentee'?1:0);
    var fb = $('fbtn'); fb.textContent = active ? 'Filters · '+active : 'Filters'; fb.classList.toggle('active', active>0);
    var list = $('list'); list.textContent='';
    if (!out.length) { list.appendChild(el('div','empty','No records match these filters.')); return; }
    var n = Math.min(out.length, PAGE*state.page);
    var frag = document.createDocumentFragment();
    for (var i=0;i<n;i++) frag.appendChild(card(out[i]));
    list.appendChild(frag);
    if (n < out.length) { var m=el('button','more','Show '+Math.min(PAGE,out.length-n)+' more of '+(out.length-n).toLocaleString()); m.type='button'; m.addEventListener('click', function(){ state.page++; render(); }); list.appendChild(m); }
  }

  /* ---------- campaign: storage ---------- */
  var use = (window.claude && typeof window.claude.use==='function') ? function(n){ return window.claude.use(n); } : function(){ return Promise.resolve(null); };
  var store = {db:null, dl:null, contacts:{}, settings:null, local:true, ready:false};
  var queues = {}, settingsQueue = Promise.resolve();
  function localLoad(){ try { var j = JSON.parse(localStorage.getItem('belmont-campaign')||'null'); if (j) { store.contacts = j.contacts||{}; store.settings = j.settings||null; } } catch(e){} }
  function localSave(){ try { localStorage.setItem('belmont-campaign', JSON.stringify({contacts:store.contacts, settings:store.settings})); } catch(e){} }
  function notice(msg, ms){ var n=$('cnotice'); n.textContent=msg; n.hidden=false; clearTimeout(notice.t); notice.t=setTimeout(function(){ n.hidden=true; }, ms||4000); }
  function contactState(id){ return store.contacts[id] || {status:'Not contacted', notes:''}; }
  function writeContact(h, patch){
    var cur = Object.assign({}, contactState(h.id), patch, {name:h.contact_name, campaign:h.campaign, updated_at:new Date().toISOString()});
    store.contacts[h.id] = cur;
    if (!store.db) { localSave(); return Promise.resolve(); }
    queues[h.id] = (queues[h.id]||Promise.resolve()).then(function(){ return store.db.doc('contacts/'+h.id).set(cur); }).catch(function(e){ notice('Could not save '+h.contact_name+': '+(e && e.message ? e.message : e), 6000); });
    return queues[h.id];
  }
  function settings(){ return Object.assign({}, CAMP.settings_default, {letter1: CAMP.templates.letter1, letter2: CAMP.templates.letter2}, store.settings||{}); }
  function writeSettings(s){
    store.settings = s;
    if (!store.db) { localSave(); return; }
    settingsQueue = settingsQueue.then(function(){ return store.db.doc('settings/campaign').set(s); }).catch(function(e){ notice('Could not save settings: '+(e && e.message ? e.message : e), 6000); });
  }
  function initStore(){
    localLoad();
    use('db').then(function(db){
      if (!db) { store.local = true; store.ready = true; render(); return; }
      store.db = db; store.local = false;
      db.collection('contacts').onSnapshot(function(snap){
        var c = {}; snap.docs.forEach(function(d){ c[d.id] = d.data(); }); store.contacts = c; store.ready = true; render();
      }, function(e){ notice('Live sync stopped ('+e.code+'). Reload the page to reconnect.', 8000); });
      db.doc('settings/campaign').onSnapshot(function(s){ if (s.exists) { store.settings = s.data(); fillSettings(); render(); } }, function(){});
    });
    use('downloads').then(function(dl){ store.dl = dl; });
  }

  /* ---------- campaign: rendering ---------- */
  var statusColor = {'Not contacted':'var(--c-unknown)','Letter 1 sent':'var(--c-state)','Letter 2 sent':'var(--c-state)','Postcard sent':'var(--c-state)','Replied':'var(--c-ma)','Interested':'var(--c-good)','Appointment set':'var(--c-good)','Offer made':'var(--c-good)','Not interested':'var(--c-belmont)','Do not contact':'var(--c-tax)','Sold / closed':'var(--c-country)'};
  var campSel = $('camp');
  CAMP.campaigns.forEach(function(c){ var o=document.createElement('option'); o.value=c.id; o.textContent=c.label+' ('+c.households.length+' households)'; campSel.appendChild(o); });
  campSel.value = state.camp;
  campSel.addEventListener('change', function(e){ state.camp=e.target.value; state.cpage=1; state.cstatus=''; save(); render(); });
  function currentCampaign(){ return CAMP.campaigns.filter(function(c){ return c.id===state.camp; })[0] || CAMP.campaigns[0]; }
  function shownHouseholds(){
    var c = currentCampaign(); var q = (state.q||'').trim().toUpperCase();
    return c.households.filter(function(h){
      var st = contactState(h.id).status || 'Not contacted';
      if (state.cstatus && st !== state.cstatus) return false;
      if (q) { var hay = (h.contact_name+' '+h.address_line_1+' '+h.city+' '+h.properties.map(function(p){ return p.address+' '+p.parcel_id; }).join(' ')+' '+h.owner_names_raw.join(' ')).toUpperCase(); if (hay.indexOf(q)<0) return false; }
      return true;
    });
  }
  function fmtDate(iso){ if (!iso) return ''; var d=new Date(iso); return isNaN(d) ? iso : d.toLocaleDateString(undefined,{month:'short',day:'numeric',year:'numeric'}); }
  function campCard(h){
    var st = contactState(h.id); var status = st.status || 'Not contacted';
    var c = el('article','card camp'); c.dataset.id = h.id;
    var row1 = el('div','row1');
    var pill = el('span','pill', status); pill.style.setProperty('--pc', statusColor[status]||'var(--c-unknown)'); row1.appendChild(pill);
    var sc = el('span','score'); sc.appendChild(document.createTextNode('priority ')); sc.appendChild(el('b',null,h.priority)); row1.appendChild(sc);
    c.appendChild(row1);
    c.appendChild(el('div','name', h.contact_name));
    var mb = el('div','mailblock');
    var addrText = [h.address_line_1, h.address_line_2, h.city+', '+h.state+' '+h.zip].filter(Boolean);
    var mt = el('div'); addrText.forEach(function(l,i){ if (i) mt.appendChild(document.createElement('br')); mt.appendChild(document.createTextNode(l)); }); mb.appendChild(mt);
    var cp = el('button','mini','Copy address'); cp.type='button'; cp.dataset.copy = h.contact_name+'\n'+addrText.join('\n'); mb.appendChild(cp);
    c.appendChild(mb);
    var props = el('div','props');
    h.properties.forEach(function(p){ var d=el('div'); d.appendChild(el('b',null,p.address)); d.appendChild(document.createTextNode(' · '+p.type+(p.assessed?' · '+money(p.assessed):'')+(p.is_home?' · their home':' · not owner-occupied'))); props.appendChild(d); });
    c.appendChild(props);
    var badges = el('div','badges');
    function badge(t, col){ var b=el('span','badge',t); b.style.setProperty('--bc', col); badges.appendChild(b); }
    if (h.life_estate) badge('Life estate', 'var(--c-le)');
    if (h.estate) badge('Estate / heirs', 'var(--c-estate)');
    if (h.et_al) badge('Multiple owners (et al)', 'var(--c-inherit)');
    if (h.care_of) badge('Bill sent c/o', 'var(--c-estate)');
    if (h.out_of_state) badge('Out of state', 'var(--c-state)'); else if (h.absentee) badge('Absentee', 'var(--c-ma)');
    if (h.kind==='organization') badge('Trust / entity', 'var(--c-belmont)');
    if (badges.childNodes.length) c.appendChild(badges);
    var ctl = el('div','ctl');
    var lab = el('label',null,'Status'); var sel = document.createElement('select'); sel.dataset.id = h.id;
    STATUSES.forEach(function(s){ var o=document.createElement('option'); o.value=s; o.textContent=s; sel.appendChild(o); }); sel.value = status; lab.appendChild(sel); ctl.appendChild(lab);
    var lb = el('button','btn','Letter'); lb.type='button'; lb.dataset.letter = h.id; ctl.appendChild(lb);
    c.appendChild(ctl);
    var ta = document.createElement('textarea'); ta.className='notes'; ta.dataset.id = h.id; ta.placeholder='Notes: who replied, family contacts, call outcomes...'; ta.value = st.notes||''; c.appendChild(ta);
    var meta = el('div','meta');
    if (st.letter1_at) meta.appendChild(el('span',null,'Letter 1 '+fmtDate(st.letter1_at)));
    if (st.letter2_at) meta.appendChild(el('span',null,'Letter 2 '+fmtDate(st.letter2_at)));
    if (st.status_at && status!=='Not contacted') meta.appendChild(el('span',null,status+' '+fmtDate(st.status_at)));
    meta.appendChild(el('span','mono', h.properties.map(function(p){ return p.parcel_id; }).join(', ')));
    c.appendChild(meta);
    return c;
  }
  var pendingRender = false;
  function renderCampaign(){
    var active = document.activeElement;
    if (active && active.tagName==='TEXTAREA' && $('list').contains(active)) { pendingRender = true; return; }
    var c = currentCampaign();
    $('campdesc').textContent = c.description + (store.ready ? (store.local ? ' Statuses save on this device only.' : ' Statuses sync through the shared database.') : ' Connecting to the shared database...');
    var counts = {}; c.households.forEach(function(h){ var s=contactState(h.id).status||'Not contacted'; counts[s]=(counts[s]||0)+1; });
    var cs = $('cstatus'); cs.textContent='';
    [''].concat(STATUSES).forEach(function(s){
      if (s && !counts[s]) return;
      var b=document.createElement('button'); b.type='button'; b.className='chip'; b.setAttribute('aria-pressed', state.cstatus===s ? 'true':'false');
      b.appendChild(el('span',null, s||'All')); b.appendChild(el('span','n', String(s ? counts[s] : c.households.length)));
      b.addEventListener('click', function(){ state.cstatus=s; state.cpage=1; save(); render(); }); cs.appendChild(b);
    });
    var out = shownHouseholds();
    $('total').textContent = c.households.length.toLocaleString();
    $('shown').textContent = out.length.toLocaleString();
    $('unitword').textContent = 'households';
    $('viewname').textContent = c.label + (state.cstatus ? ' · '+state.cstatus : '');
    var pr = $('cprogress'); pr.textContent='';
    var mailed = (counts['Letter 1 sent']||0)+(counts['Letter 2 sent']||0)+(counts['Postcard sent']||0)+(counts['Replied']||0)+(counts['Interested']||0)+(counts['Appointment set']||0)+(counts['Offer made']||0)+(counts['Not interested']||0)+(counts['Sold / closed']||0);
    [['households', c.households.length], ['contacted', mailed], ['replied or better', (counts['Replied']||0)+(counts['Interested']||0)+(counts['Appointment set']||0)+(counts['Offer made']||0)+(counts['Sold / closed']||0)], ['interested', (counts['Interested']||0)+(counts['Appointment set']||0)+(counts['Offer made']||0)], ['do not contact', counts['Do not contact']||0]].forEach(function(p){ var s=el('span'); s.appendChild(el('b',null,String(p[1]))); s.appendChild(document.createTextNode(' '+p[0])); pr.appendChild(s); });
    $('btn-mark').textContent = 'Mark shown as Letter 1 sent';
    var list = $('list'); list.textContent='';
    if (!out.length) { list.appendChild(el('div','empty','No households match.')); return; }
    var n = Math.min(out.length, PAGE*state.cpage);
    var frag = document.createDocumentFragment();
    for (var i=0;i<n;i++) frag.appendChild(campCard(out[i]));
    list.appendChild(frag);
    if (n < out.length) { var m=el('button','more','Show '+Math.min(PAGE,out.length-n)+' more of '+(out.length-n).toLocaleString()); m.type='button'; m.addEventListener('click', function(){ state.cpage++; render(); }); list.appendChild(m); }
  }

  /* ---------- campaign: letters, export ---------- */
  function todayLong(){ return new Date().toLocaleDateString('en-US',{month:'long',day:'numeric',year:'numeric'}); }
  function merge(tpl, h, s){
    var f = {salutation:h.salutation, contact_name:h.contact_name, first_names:h.first_names||h.contact_name, property_phrase:h.property_phrase, property_address:h.primary_property, address_line_1:h.address_line_1, address_line_2:h.address_line_2, city:h.city, state:h.state, zip:h.zip, date:s.letter_date||todayLong()};
    Object.keys(s).forEach(function(k){ if (typeof s[k]==='string' && !(k in f)) f[k]=s[k]; });
    return tpl.replace(/\{\{(\w+)\}\}/g, function(m,k){ return (k in f) ? f[k] : m; });
  }
  function letterHtml(h, which){
    var s = settings(); var body = merge(which===2 ? s.letter2 : s.letter1, h, s);
    var from = [s.sender_name, s.company, s.return_address_1, s.return_address_2, [s.phone, s.email].filter(Boolean).join('  |  ')].filter(function(x){ return x && !/^\[Your company/.test(x); });
    var html = '<article class="letter"><p class="from">'+from.map(esc).join('<br>')+'</p><p>'+esc(s.letter_date||todayLong())+'</p><p>'+[h.contact_name,h.address_line_1,h.address_line_2,h.city+', '+h.state+' '+h.zip].filter(Boolean).map(esc).join('<br>')+'</p>';
    body.trim().split(/\n\s*\n/).forEach(function(block){
      var lines = block.split('\n');
      if (lines.every(function(l){ return /^- /.test(l); })) html += '<ul>'+lines.map(function(l){ return '<li>'+esc(l.slice(2))+'</li>'; }).join('')+'</ul>';
      else html += '<p>'+lines.map(esc).join('<br>')+'</p>';
    });
    return html+'</article>';
  }
  function printLetters(list){
    if (!list.length) { notice('Nothing to print with the current filters.'); return; }
    var which = $('s_which2').checked ? 2 : 1;
    $('printarea').innerHTML = list.map(function(h){ return letterHtml(h, which); }).join('');
    setTimeout(function(){ window.print(); }, 50);
  }
  function csvFor(list){
    var cols = ['contact_id','full_name','salutation','first_names','last_name','address_line_1','address_line_2','city','state','zip','property_address','all_property_addresses','status','notes','life_estate','estate','absentee','out_of_state','priority_score','parcel_ids','owner_names_on_record','letter_property_phrase'];
    var q = function(v){ v = String(v==null?'':v); return /[",\n]/.test(v) ? '"'+v.replace(/"/g,'""')+'"' : v; };
    var lines = [cols.join(',')];
    list.forEach(function(h){ var st=contactState(h.id); var p0=h.properties[0];
      lines.push([h.id,h.contact_name,h.salutation,h.first_names,h.surname,h.address_line_1,h.address_line_2,h.city,h.state,h.zip,p0.address,h.properties.map(function(p){return p.address;}).join('; '),st.status||'Not contacted',st.notes||'',h.life_estate?'YES':'',h.estate?'YES':'',h.absentee?'YES':'',h.out_of_state?'YES':'',h.priority,h.properties.map(function(p){return p.parcel_id;}).join('; '),h.owner_names_raw.join('; '),h.property_phrase].map(q).join(',')); });
    return lines.join('\r\n');
  }
  function saveCsv(list){
    if (!list.length) { notice('Nothing to export with the current filters.'); return; }
    var name = 'belmont_'+state.camp+'_mailing_list.csv', data = csvFor(list);
    if (store.dl) {
      store.dl.save({filename:name, data:data}).then(function(){ notice('Mailing list saved ('+list.length+' households).'); }).catch(function(e){
        if (e && e.code==='declined') return;
        copyText(data, 'Saving is unavailable here; the CSV was copied to your clipboard instead.');
      });
    } else copyText(data, 'CSV for '+list.length+' households copied to your clipboard (paste into a spreadsheet).');
  }
  function copyText(text, okMsg){
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(function(){ notice(okMsg); }, function(){ notice('Could not copy. Select the text and copy it by hand.'); });
    else notice('Copying is not available in this view.');
  }
  var markArmed = null;
  function markShown(){
    var list = shownHouseholds().filter(function(h){ return (contactState(h.id).status||'Not contacted')!=='Do not contact'; });
    if (!list.length) { notice('Nothing to mark.'); return; }
    if (markArmed !== state.camp+':'+list.length) { markArmed = state.camp+':'+list.length; $('btn-mark').textContent = 'Tap again to mark '+list.length+' as Letter 1 sent'; setTimeout(function(){ markArmed=null; if ($('btn-mark')) $('btn-mark').textContent='Mark shown as Letter 1 sent'; }, 6000); return; }
    markArmed = null;
    var now = new Date().toISOString(), i = 0;
    (function next(){ if (i>=list.length) { notice(list.length+' households marked as Letter 1 sent.'); render(); return; }
      var h = list[i++]; var st = contactState(h.id);
      writeContact(h, {status:'Letter 1 sent', status_at:now, letter1_at: st.letter1_at||now}).then(next, next); })();
  }

  /* ---------- settings sheet ---------- */
  var SKEYS = ['sender_name','company','phone','email','return_address_1','return_address_2','closing','letter_date','letter1','letter2'];
  function fillSettings(){ var s = settings(); SKEYS.forEach(function(k){ var e=$('s_'+k); if (e && document.activeElement!==e) e.value = s[k]||''; }); }
  $('btn-settings').addEventListener('click', function(){ fillSettings(); $('settings').hidden=false; $('settings').scrollIntoView({block:'start'}); $('s_sender_name').focus(); });
  $('settings-close').addEventListener('click', function(){ $('settings').hidden=true; });
  $('settings-save').addEventListener('click', function(){ var s={}; SKEYS.forEach(function(k){ s[k]=$('s_'+k).value; }); writeSettings(s); $('settings').hidden=true; notice('Sender and letter text saved.'); });
  $('settings-reset').addEventListener('click', function(){ $('s_letter1').value = CAMP.templates.letter1; $('s_letter2').value = CAMP.templates.letter2; notice('Letter text reset to the default wording (not saved yet).'); });

  /* ---------- events ---------- */
  $('btn-print').addEventListener('click', function(){ printLetters(shownHouseholds()); });
  $('btn-csv').addEventListener('click', function(){ saveCsv(shownHouseholds()); });
  $('btn-mark').addEventListener('click', markShown);
  var noteTimers = {};
  $('list').addEventListener('change', function(e){
    var t = e.target; if (t.tagName!=='SELECT' || !t.dataset.id) return;
    var h = currentCampaign().households.filter(function(x){ return x.id===t.dataset.id; })[0]; if (!h) return;
    var now = new Date().toISOString(), patch = {status:t.value, status_at:now}; var st = contactState(h.id);
    if (t.value==='Letter 1 sent' && !st.letter1_at) patch.letter1_at = now;
    if (t.value==='Letter 2 sent' && !st.letter2_at) patch.letter2_at = now;
    patch.history = (st.history||[]).concat([{status:t.value, at:now}]).slice(-12);
    writeContact(h, patch); render();
  });
  $('list').addEventListener('input', function(e){
    var t = e.target; if (t.tagName!=='TEXTAREA' || !t.dataset.id) return;
    clearTimeout(noteTimers[t.dataset.id]);
    noteTimers[t.dataset.id] = setTimeout(function(){ var h = currentCampaign().households.filter(function(x){ return x.id===t.dataset.id; })[0]; if (h && (contactState(h.id).notes||'')!==t.value) writeContact(h, {notes:t.value}); }, 900);
  });
  $('list').addEventListener('focusout', function(e){
    var t = e.target; if (t.tagName!=='TEXTAREA' || !t.dataset.id) return;
    clearTimeout(noteTimers[t.dataset.id]);
    var h = currentCampaign().households.filter(function(x){ return x.id===t.dataset.id; })[0];
    if (h && (contactState(h.id).notes||'')!==t.value) writeContact(h, {notes:t.value});
    if (pendingRender) { pendingRender=false; setTimeout(render, 0); }
  });
  $('list').addEventListener('click', function(e){
    var b = e.target.closest ? e.target.closest('button') : null; if (!b) return;
    if (b.dataset.copy) copyText(b.dataset.copy, 'Address copied.');
    if (b.dataset.letter) { var h = currentCampaign().households.filter(function(x){ return x.id===b.dataset.letter; })[0]; if (h) printLetters([h]); }
  });
  Array.prototype.forEach.call(document.querySelectorAll('.mode'), function(b){ b.addEventListener('click', function(){ state.mode=b.dataset.mode; state.q=''; $('q').value=''; save(); render(); }); });
  var panel = $('panel'), fbtn = $('fbtn');
  function openPanel(){ panel.classList.add('open'); fbtn.setAttribute('aria-expanded','true'); document.documentElement.classList.add('noscroll'); panel.scrollTop = 0; $('pclose').focus(); }
  function closePanel(){ panel.classList.remove('open'); fbtn.setAttribute('aria-expanded','false'); document.documentElement.classList.remove('noscroll'); fbtn.focus(); }
  fbtn.addEventListener('click', function(){ panel.classList.contains('open') ? closePanel() : openPanel(); });
  $('pclose').addEventListener('click', closePanel);
  $('papply').addEventListener('click', function(){ closePanel(); window.scrollTo(0,0); });
  document.addEventListener('keydown', function(e){ if (e.key==='Escape') { if (panel.classList.contains('open')) closePanel(); if (!$('settings').hidden) $('settings').hidden=true; } });
  $('q').addEventListener('input', function(e){ state.q=e.target.value; state.page=1; state.cpage=1; save(); render(); });
  ['otype','ptype','occ','sort'].forEach(function(id){ $(id).addEventListener('change', function(e){ state[id]=e.target.value; state.page=1; save(); render(); }); });

  function render(){
    var camp = state.mode==='campaign';
    Array.prototype.forEach.call(document.querySelectorAll('.mode'), function(b){ b.setAttribute('aria-selected', b.dataset.mode===state.mode ? 'true':'false'); });
    $('campbar').hidden = !camp; panel.hidden = camp; fbtn.hidden = camp; if (!camp) $('settings').hidden = true;
    $('q').placeholder = camp ? 'Search names, mailing addresses, properties' : 'Search address, owner, mailing address or parcel ID';
    if (camp) renderCampaign(); else renderLeads();
  }
  render();
  initStore();
})();
</script>
"""


def main():
    rows = load_rows()
    summary = json.load(open(os.path.join(OUT, "summary.json")))
    camp = open(os.path.join(OUT, "campaigns.json"), encoding="utf-8").read()
    data = json.dumps(rows, separators=(",", ":")).replace("</", "<\\/")
    html = (TEMPLATE.replace("__DATA__", data).replace("__CAMPAIGNS__", camp.replace("</", "<\\/"))
            .replace("__FIELDS__", json.dumps(FIELDS))
            .replace("__VINTAGE__", summary["data_vintage"]).replace("__BUILT__", summary["built"]))
    path = os.path.join(OUT, "belmont_leads.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {path}: {len(rows)} lead records, {os.path.getsize(path)/1e6:.2f} MB")


if __name__ == "__main__":
    main()
