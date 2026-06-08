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

SECTION_COLORS = {
    "Sanità": "#74d7ff",
    "Comune / Tributi": "#f68bff",
    "Agricoltura / Europa": "#9df7c8",
    "Elezioni comunali": "#ffd166",
    "Cultura / Società": "#c4a7ff",
    "Cronaca": "#ff8a8a",
    "Setup": "#74d7ff",
}

def load_data():
    if DATA.exists():
        return json.loads(DATA.read_text(encoding="utf-8"))
    return {"updated_at": "", "items": []}

def esc(x):
    return html.escape(str(x or ""), quote=True)

def section_class(section):
    safe = ''.join(ch.lower() if ch.isalnum() else '-' for ch in str(section or 'news'))
    return 'section-' + '-'.join(part for part in safe.split('-') if part)

def render_item(item, index):
    section = item.get('section', 'News')
    color = SECTION_COLORS.get(section, '#74d7ff')
    tags = "".join(f'<span class="tag">#{esc(t)}</span>' for t in item.get("tags", [])[:4])
    sources = item.get("sources", [])
    links = "".join(
        f'<a class="source-link" href="{esc(src.get("url"))}" target="_blank" rel="noopener">{esc(src.get("name", "fonte"))}</a>'
        for src in sources[:3]
    )
    primary = esc(sources[0].get('url')) if sources else '#'
    kicker = esc(section).upper()
    card_size = 'feature' if index == 0 else ('wide' if index in (3, 6) else '')
    return f"""
<article class="story-card {card_size}" style="--story-color:{color}">
  <div class="story-top">
    <div class="author-mark"><span>{esc(section[:1] or 'N')}</span></div>
    <div class="story-kicker">{kicker}</div>
    <div class="story-actions">
      <a href="{primary}" target="_blank" rel="noopener" class="mini-btn">↗ Fonte</a>
      <button class="mini-btn dark" type="button">Nuoro</button>
    </div>
  </div>
  <div class="label-row">{tags}</div>
  <h2>{esc(item.get('title', 'Senza titolo'))}</h2>
  <p class="summary">{esc(item.get('summary', ''))}</p>
  <p class="why"><strong>Perché conta:</strong> {esc(item.get('why', 'Da monitorare.'))}</p>
  <div class="story-foot">
    <span class="score">◎ {index + 1}</span>
    <span>{esc(item.get('time', ''))}</span>
    <span>{len(sources)} fonti</span>
  </div>
  <div class="sources">{links}</div>
</article>"""

def main():
    data = load_data()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    updated = data.get("updated_at") or now
    items = data.get("items", [])
    if not items:
        items = [{
            "section": "Setup",
            "time": now,
            "title": "News Nuoro è pronto",
            "summary": "La pagina è stata inizializzata. Il prossimo passo è collegare il job Hermes orario che raccoglie le fonti locali e aggiorna automaticamente questa pagina.",
            "why": "Serve come base pubblica per il monitoraggio quotidiano delle notizie su Nuoro e provincia.",
            "tags": ["Nuoro", "setup", "Hermes"],
            "sources": DEFAULT_SOURCES,
        }]
    sections = []
    seen = set()
    for item in items:
        sec = item.get('section', 'News')
        if sec not in seen:
            seen.add(sec)
            sections.append(sec)
    nav = ''.join(f'<a href="#" class="nav-chip"># {esc(sec)}</a>' for sec in sections[:10])
    cards = "\n".join(render_item(i, idx) for idx, i in enumerate(items))
    html_doc = f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Gazzettino Sardo — News Nuoro</title>
  <meta name="description" content="Rassegna quotidiana correlata delle notizie su Nuoro e provincia." />
  <style>
    :root {{
      --pink:#f6a0c7;
      --ink:#101116;
      --muted:#6f727b;
      --soft:#f7f7f8;
      --line:#e7e7ea;
      --panel:#ffffff;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin:0;
      min-height:100vh;
      background:var(--pink);
      color:var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing:-0.012em;
    }}
    .stage {{
      width:min(1120px, calc(100vw - 40px));
      margin: clamp(18px, 5vw, 56px) auto;
      min-height: calc(100vh - 112px);
      background:var(--panel);
      border-radius:0;
      box-shadow: 0 28px 70px rgba(80, 24, 52, .16);
      display:grid;
      grid-template-columns: 64px 1fr;
      overflow:hidden;
    }}
    .rail {{
      border-right:1px solid var(--line);
      display:flex;
      flex-direction:column;
      align-items:center;
      padding:22px 0;
      background:#fff;
    }}
    .logo {{
      width:28px; height:28px; border:1.5px solid #15161c; border-radius:999px;
      display:grid; place-items:center; font-weight:900; font-size:14px;
    }}
    .hamb {{ margin:auto 0; font-size:18px; transform:rotate(90deg); color:#2d2f36; opacity:.78; }}
    .dot-stack {{ display:grid; gap:12px; margin-top:auto; }}
    .dot {{ width:18px; height:18px; border-radius:999px; border:1px solid #e2e2e6; background:#f2f3f5; }}
    .dot:first-child {{ background:#1683ff; }}
    .content {{ min-width:0; overflow:hidden; }}
    .topbar {{
      display:grid;
      grid-template-columns: 1fr minmax(180px, 280px);
      gap:22px;
      align-items:center;
      padding:28px 34px 10px;
    }}
    .nav {{ display:flex; gap:18px; white-space:nowrap; overflow:hidden; }}
    .nav-chip {{ color:#858891; text-decoration:none; font-size:12px; font-weight:700; }}
    .nav-chip:first-child, .nav-chip:hover {{ color:#16171d; }}
    .search {{ border-bottom:1.5px solid #20222a; display:flex; align-items:center; gap:8px; padding:5px 0; }}
    .search input {{ border:0; outline:0; width:100%; font-size:12px; font-weight:700; background:transparent; }}
    .controls {{ padding:0 34px 20px; display:flex; align-items:center; gap:8px; flex-wrap:wrap; }}
    .control-pill {{ border:1px solid #d9dbe0; color:#393b43; border-radius:999px; padding:7px 13px; font-size:11px; font-weight:800; background:#fff; }}
    .control-pill.primary {{ background:#11131a; color:#fff; border-color:#11131a; }}
    .hero {{ padding:0 34px 18px; }}
    .brand-line {{ display:flex; align-items:center; gap:10px; margin-bottom:12px; }}
    .brand-dot {{ width:18px; height:18px; border-radius:999px; background:#1683ff; }}
    .brand-title {{ font-size:13px; font-weight:900; }}
    .brand-sub {{ font-size:10px; text-transform:uppercase; color:#979aa3; font-weight:800; margin-left:6px; }}
    h1 {{ margin:0; font-size:clamp(34px, 5.7vw, 68px); line-height:.96; letter-spacing:-0.06em; max-width:820px; }}
    .deck {{ max-width:720px; color:#666a73; line-height:1.52; margin:16px 0 0; font-size:14px; }}
    .updated {{ margin-top:12px; color:#9a9da5; font-size:11px; font-weight:750; }}
    .masonry {{
      padding: 10px 34px 42px;
      display:grid;
      grid-template-columns: repeat(3, minmax(220px, 1fr));
      gap:30px 34px;
      align-items:start;
    }}
    .story-card {{ min-width:0; padding-top:2px; border-top:1px solid var(--line); }}
    .story-card.feature {{ grid-row: span 2; }}
    .story-card.wide {{ grid-column: span 2; }}
    .story-top {{ display:grid; grid-template-columns:auto 1fr auto; gap:9px; align-items:center; margin:14px 0 12px; }}
    .author-mark {{ width:22px; height:22px; border-radius:999px; background:var(--story-color); display:grid; place-items:center; font-size:11px; font-weight:900; color:#111; }}
    .story-kicker {{ font-size:11px; font-weight:900; color:#25272e; }}
    .story-actions {{ display:flex; gap:5px; }}
    .mini-btn {{ border:1px solid #dbdde2; border-radius:999px; padding:4px 8px; font-size:10px; line-height:1; color:#2f323a; text-decoration:none; background:#fff; font-weight:800; }}
    .mini-btn.dark {{ display:none; }}
    .label-row {{ display:flex; gap:5px; flex-wrap:wrap; min-height:18px; }}
    .tag {{ background:#f3f4f6; color:#676a73; border-radius:999px; padding:3px 7px; font-size:9px; text-transform:uppercase; font-weight:850; }}
    .story-card h2 {{ margin:10px 0 9px; font-size:clamp(22px, 2.2vw, 32px); line-height:1.06; letter-spacing:-.048em; }}
    .story-card:not(.feature) h2 {{ font-size:21px; line-height:1.12; }}
    .summary {{ margin:0; color:#5e626b; line-height:1.5; font-size:13px; }}
    .why {{ margin:12px 0 0; color:#2a2d34; line-height:1.45; font-size:12px; border-left:2px solid var(--story-color); padding-left:10px; }}
    .story-foot {{ margin-top:20px; display:flex; gap:12px; color:#9a9da5; font-size:11px; align-items:center; flex-wrap:wrap; }}
    .score {{ color:#252830; font-weight:850; }}
    .sources {{ margin-top:10px; display:flex; gap:8px; flex-wrap:wrap; }}
    .source-link {{ color:#61646d; font-size:11px; text-decoration:none; border-bottom:1px solid #d6d8dd; }}
    footer {{ padding:0 34px 30px; color:#9498a1; font-size:12px; }}
    @media (max-width: 900px) {{
      .stage {{ grid-template-columns:1fr; margin:0; width:100%; min-height:100vh; }}
      .rail {{ display:none; }}
      .topbar {{ grid-template-columns:1fr; padding:22px 20px 10px; }}
      .nav {{ gap:14px; overflow:auto; padding-bottom:4px; }}
      .controls, .hero, .masonry, footer {{ padding-left:20px; padding-right:20px; }}
      .masonry {{ grid-template-columns:1fr; gap:28px; }}
      .story-card.feature, .story-card.wide {{ grid-column:auto; grid-row:auto; }}
      h1 {{ font-size:44px; }}
    }}
  </style>
</head>
<body>
  <div class="stage">
    <aside class="rail" aria-label="Navigazione laterale">
      <div class="logo">G</div>
      <div class="hamb">≡</div>
      <div class="dot-stack"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
    </aside>
    <div class="content">
      <header class="topbar">
        <nav class="nav" aria-label="Categorie">{nav}</nav>
        <div class="search"><input aria-label="Cerca" placeholder="Search" /><span>⌕</span></div>
      </header>
      <div class="controls">
        <span class="control-pill primary">+ daily brief</span>
        <span class="control-pill">news</span>
        <span class="control-pill">nuoro</span>
        <span class="control-pill">today</span>
      </div>
      <section class="hero">
        <div class="brand-line"><span class="brand-dot"></span><span class="brand-title">Gazzettino Sardo</span><span class="brand-sub">Hermes news desk</span></div>
        <h1>News Nuoro — oggi</h1>
        <p class="deck">Rassegna correlata delle notizie della giornata su Nuoro e provincia. Le schede raggruppano fonti diverse e mettono in evidenza rilevanza, contesto e link originali.</p>
        <div class="updated">Aggiornato: {esc(updated)} · Fonti monitorate: La Nuova Sardegna, L'Unione Sarda, Cronache Nuoresi, ANSA Sardegna</div>
      </section>
      <main class="masonry">{cards}</main>
      <footer>Nota: questa pagina cita e linka le fonti originali. Non aggira paywall e non sostituisce gli articoli completi.</footer>
    </div>
  </div>
</body>
</html>"""
    OUT.write_text(html_doc, encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
