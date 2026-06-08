#!/usr/bin/env python3
import json, html
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "news.json"
OUT = ROOT / "index.html"

DEFAULT_SOURCES = [
    {"name": "La Nuova Sardegna", "url": "https://www.lanuovasardegna.it/"},
    {"name": "L'Unione Sarda", "url": "https://www.unionesarda.it/"},
    {"name": "Cronache Nuoresi", "url": "https://www.cronachenuoresi.it/"},
]

def load_data():
    if DATA.exists():
        return json.loads(DATA.read_text(encoding="utf-8"))
    return {"updated_at": "", "items": []}

def esc(x):
    return html.escape(str(x or ""), quote=True)

def render_item(item, index):
    section = item.get('section', 'News')
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in item.get("tags", [])[:3])
    sources = item.get("sources", [])
    variants = item.get("variants", [])
    links = "".join(
        f'<a class="source-link" href="{esc(src.get("url"))}" target="_blank" rel="noopener">{esc(src.get("name", "fonte"))}</a>'
        for src in sources[:4]
    )
    primary = esc(sources[0].get('url')) if sources else '#'
    grouped_count = int(item.get('grouped_count') or len(variants) or 1)
    grouped_badge = f'<span class="grouped-badge">Raggruppa {grouped_count} articoli</span>' if grouped_count > 1 else ''
    variants_html = ''
    if grouped_count > 1 and variants:
        variant_rows = ''.join(
            f'<li><a href="{esc(v.get("url"))}" target="_blank" rel="noopener">{esc(v.get("title"))}</a><span>{esc(v.get("source"))} · {esc(v.get("time"))}</span></li>'
            for v in variants[:6]
        )
        variants_html = f'<details class="variants"><summary>Articoli collegati</summary><ul>{variant_rows}</ul></details>'
    return f"""
<article class="article-row">
  <a class="article-number" href="{primary}" target="_blank" rel="noopener">{index + 1:02d}</a>
  <div class="article-body">
    <div class="article-meta">
      <span>{esc(section)}</span>
      <span>{esc(item.get('time', ''))}</span>
      <span>{len(sources)} fonti</span>
      {grouped_badge}
    </div>
    <h2><a href="{primary}" target="_blank" rel="noopener">{esc(item.get('title', 'Senza titolo'))}</a></h2>
    <p class="summary">{esc(item.get('summary', ''))}</p>
    <p class="why"><strong>Perché conta:</strong> {esc(item.get('why', 'Da monitorare.'))}</p>
    {variants_html}
    <div class="article-bottom">
      <div class="tags">{tags}</div>
      <div class="sources">{links}</div>
    </div>
  </div>
</article>"""

def render_fuel(fuel):
    if not fuel:
        return ''
    groups = fuel.get('groups') or []
    # Backward compatibility with the previous benzina-only shape.
    if not groups and fuel.get('items'):
        groups = [{
            'kind': 'benzina',
            'title': fuel.get('title', 'Benzina'),
            'summary': fuel.get('summary', ''),
            'items': fuel.get('items', []),
        }]
    groups = [g for g in groups if g.get('items')]
    if not groups:
        return ''

    group_html = []
    for group in groups[:2]:
        cards = []
        for item in group.get('items', [])[:5]:
            cards.append(f"""
            <li>
              <strong>{esc(item.get('price', ''))} €/L</strong>
              <span>{esc(item.get('brand', ''))} · {esc(item.get('mode', ''))} · {esc(item.get('distance_km', ''))} km</span>
              <small>{esc(item.get('address', ''))}, {esc(item.get('city', ''))} · agg. {esc(item.get('updated', ''))}</small>
            </li>""")
        group_html.append(f"""
        <div class="fuel-group fuel-{esc(group.get('kind', 'carburante'))}">
          <h3>{esc(group.get('title', 'Carburante'))}</h3>
          <p>{esc(group.get('summary', 'Prezzi rilevati vicino a Nuoro.'))}</p>
          <ol>{''.join(cards)}</ol>
        </div>""")

    return f"""
    <section class="fuel-box" aria-label="Prezzi benzina e diesel Nuoro">
      <div class="fuel-head">
        <p class="fuel-kicker">Prezzi carburante</p>
        <h2>{esc(fuel.get('title', 'Benzina e diesel a Nuoro'))}</h2>
        <p>{esc(fuel.get('summary', 'Prezzi benzina e diesel rilevati vicino a Nuoro.'))}</p>
        <small>Fonte: <a href="{esc(fuel.get('source_url', 'https://www.mimit.gov.it/images/exportCSV/'))}" target="_blank" rel="noopener">{esc(fuel.get('source', 'MIMIT Osservaprezzi carburanti'))}</a></small>
      </div>
      <div class="fuel-groups">{''.join(group_html)}</div>
    </section>"""


def main():
    data = load_data()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    updated = data.get("updated_at") or now
    fuel_html = render_fuel(data.get('fuel'))
    items = data.get("items", [])
    if not items:
        items = [{
            "section": "Setup",
            "time": now,
            "title": "Gazzettino Sardo è pronto",
            "summary": "La pagina è stata inizializzata. Il prossimo aggiornamento popolerà automaticamente la lista degli articoli della giornata.",
            "why": "Serve come base pubblica per il monitoraggio quotidiano delle notizie su Nuoro e provincia.",
            "tags": ["Nuoro", "setup"],
            "sources": DEFAULT_SOURCES,
        }]
    nav_sections = []
    seen = set()
    for item in items:
        sec = item.get('section', 'News')
        if sec not in seen:
            seen.add(sec)
            nav_sections.append(sec)
    nav = ''.join(f'<span>{esc(sec)}</span>' for sec in nav_sections[:8])
    rows = "\n".join(render_item(i, idx) for idx, i in enumerate(items))
    html_doc = f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Gazzettino Sardo</title>
  <meta name="description" content="Lista quotidiana delle notizie su Nuoro e provincia." />
  <style>
    :root {{
      --paper:#fffaf3;
      --ink:#171717;
      --muted:#76706a;
      --line:#e2d9cd;
      --accent:#b62424;
      --soft:#f5eee4;
    }}
    * {{ box-sizing:border-box; }}
    body {{
      margin:0;
      background:#efe6da;
      color:var(--ink);
      font-family: Georgia, "Times New Roman", serif;
    }}
    a {{ color:inherit; }}
    .page {{
      width:min(980px, calc(100vw - 28px));
      margin:28px auto;
      background:var(--paper);
      border:1px solid var(--line);
      box-shadow:0 20px 70px rgba(60,40,25,.12);
      padding:28px clamp(18px,4vw,46px) 42px;
    }}
    .masthead {{
      text-align:center;
      border-bottom:3px double var(--ink);
      padding-bottom:18px;
      margin-bottom:14px;
    }}
    .eyebrow {{
      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
      font-size:11px;
      letter-spacing:.18em;
      text-transform:uppercase;
      color:var(--muted);
      margin-bottom:8px;
    }}
    h1 {{
      margin:0;
      font-size:clamp(44px, 8vw, 86px);
      line-height:.88;
      letter-spacing:-.065em;
      font-weight:900;
    }}
    .subtitle {{
      max-width:700px;
      margin:14px auto 0;
      color:#4f4a45;
      font-size:17px;
      line-height:1.45;
    }}
    .info-bar {{
      display:flex;
      justify-content:space-between;
      gap:12px;
      border-top:1px solid var(--line);
      border-bottom:1px solid var(--line);
      padding:9px 0;
      margin:14px 0 26px;
      color:var(--muted);
      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
      font-size:12px;
      font-weight:650;
    }}
    .section-nav {{
      display:flex;
      gap:10px;
      flex-wrap:wrap;
      justify-content:center;
      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
      font-size:11px;
      text-transform:uppercase;
      letter-spacing:.08em;
      color:#6d6760;
      margin-top:14px;
    }}
    .section-nav span {{
      border:1px solid var(--line);
      background:#fff6ea;
      padding:5px 8px;
      border-radius:999px;
    }}
    .article-list {{
      display:grid;
      gap:0;
    }}
    .fuel-box {{
      display:grid;
      gap:18px;
      margin:4px 0 28px;
      padding:18px 20px;
      border:1px solid var(--line);
      background:#fff6ea;
    }}
    .fuel-head {{
      display:grid;
      gap:6px;
      border-bottom:1px solid var(--line);
      padding-bottom:14px;
    }}
    .fuel-box h2 {{
      margin:2px 0 2px;
      font-size:clamp(24px, 3vw, 34px);
    }}
    .fuel-box h3 {{
      margin:0 0 7px;
      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
      font-size:15px;
      text-transform:uppercase;
      letter-spacing:.08em;
      color:#332f2b;
    }}
    .fuel-box p {{
      margin:0;
      color:#5d5650;
      line-height:1.45;
      font-size:14px;
    }}
    .fuel-box small {{
      color:#7d746c;
      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
      font-size:11px;
    }}
    .fuel-kicker {{
      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
      text-transform:uppercase;
      letter-spacing:.12em;
      color:var(--accent) !important;
      font-size:11px !important;
      font-weight:850;
      margin-bottom:0 !important;
    }}
    .fuel-groups {{
      display:grid;
      grid-template-columns:repeat(2, minmax(0, 1fr));
      gap:16px;
    }}
    .fuel-group {{
      background:#fffaf3;
      border:1px solid var(--line);
      padding:14px;
    }}
    .fuel-box ol {{
      margin:12px 0 0;
      padding-left:20px;
      display:grid;
      gap:9px;
      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
    }}
    .fuel-box li strong {{ color:var(--accent); font-size:14px; }}
    .fuel-box li span {{ display:block; font-weight:750; font-size:12px; color:#332f2b; }}
    .fuel-box li small {{ display:block; color:#7d746c; font-size:11px; line-height:1.35; }}
    .article-row {{
      display:grid;
      grid-template-columns:58px 1fr;
      gap:18px;
      padding:24px 0;
      border-bottom:1px solid var(--line);
    }}
    .article-row:first-child {{
      padding-top:4px;
    }}
    .article-number {{
      text-decoration:none;
      color:var(--accent);
      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
      font-size:22px;
      font-weight:850;
      line-height:1;
      padding-top:5px;
    }}
    .article-meta {{
      display:flex;
      gap:10px;
      flex-wrap:wrap;
      margin-bottom:7px;
      color:var(--muted);
      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
      font-size:11px;
      font-weight:750;
      text-transform:uppercase;
      letter-spacing:.08em;
    }}
    .article-meta span:not(:last-child)::after {{
      content:"·";
      margin-left:10px;
      color:#b7aca0;
    }}
    h2 {{
      margin:0;
      font-size:clamp(24px, 3.2vw, 38px);
      line-height:1.03;
      letter-spacing:-.035em;
      font-weight:850;
    }}
    h2 a {{ text-decoration:none; }}
    h2 a:hover {{ color:var(--accent); }}
    .summary {{
      margin:10px 0 0;
      color:#35312d;
      line-height:1.55;
      font-size:16px;
    }}
    .why {{
      margin:10px 0 0;
      color:#5d5650;
      line-height:1.5;
      font-size:14px;
    }}
    .article-bottom {{
      display:flex;
      justify-content:space-between;
      align-items:center;
      gap:14px;
      flex-wrap:wrap;
      margin-top:13px;
    }}
    .tags, .sources {{
      display:flex;
      gap:8px;
      flex-wrap:wrap;
      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
    }}
    .tag {{
      color:#6f655c;
      background:var(--soft);
      border:1px solid var(--line);
      border-radius:999px;
      padding:4px 8px;
      font-size:11px;
      font-weight:700;
    }}
    .grouped-badge {{
      color:var(--accent);
      background:#fff1ec;
      border:1px solid #efc7bc;
      border-radius:999px;
      padding:2px 7px;
      letter-spacing:.04em;
    }}
    .variants {{
      margin-top:12px;
      border-left:2px solid var(--line);
      padding-left:12px;
      color:#625b55;
      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
      font-size:12px;
    }}
    .variants summary {{
      cursor:pointer;
      color:var(--accent);
      font-weight:800;
      margin-bottom:7px;
    }}
    .variants ul {{
      margin:8px 0 0;
      padding-left:16px;
      display:grid;
      gap:7px;
    }}
    .variants li span {{
      display:block;
      color:#958b82;
      font-size:11px;
      margin-top:2px;
    }}
    .variants a {{ text-decoration:none; }}
    .variants a:hover {{ color:var(--accent); }}
    .source-link {{
      color:var(--accent);
      text-decoration:none;
      border-bottom:1px solid rgba(182,36,36,.35);
      font-size:12px;
      font-weight:750;
    }}
    footer {{
      margin-top:26px;
      color:var(--muted);
      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
      font-size:12px;
      line-height:1.5;
    }}
    @media (max-width:700px) {{
      .page {{ width:100%; margin:0; min-height:100vh; border:0; padding:22px 18px 34px; }}
      h1 {{ font-size:48px; }}
      .info-bar {{ flex-direction:column; align-items:center; text-align:center; }}
      .fuel-groups {{ grid-template-columns:1fr; }}
      .article-row {{ grid-template-columns:1fr; gap:8px; padding:22px 0; }}
      .article-number {{ font-size:13px; padding:0; }}
      .article-number::before {{ content:"Articolo "; color:var(--muted); }}
      .article-meta {{ gap:5px; }}
      .article-meta span:not(:last-child)::after {{ display:none; }}
      .summary {{ font-size:15px; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <header class="masthead">
      <div class="eyebrow">Rassegna quotidiana · Nuoro e provincia</div>
      <h1>Gazzettino Sardo</h1>
      <p class="subtitle">Le notizie principali della giornata, ordinate come una lista di articoli con sintesi, contesto e link alle fonti originali.</p>
      <nav class="section-nav" aria-label="Sezioni">{nav}</nav>
    </header>
    <div class="info-bar">
      <span>Aggiornato: {esc(updated)}</span>
      <span>Fonti: La Nuova Sardegna · L'Unione Sarda · Cronache Nuoresi · ANSA Sardegna</span>
    </div>
    {fuel_html}
    <main class="article-list">{rows}</main>
    <footer>Questa pagina cita e linka le fonti originali. Non aggira paywall e non sostituisce gli articoli completi.</footer>
  </div>
</body>
</html>"""
    OUT.write_text(html_doc, encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
