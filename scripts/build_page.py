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
      --pink:#f58abb;
      --ink:#05070d;
      --muted:#747782;
      --line:#e8e8ec;
      --panel:#ffffff;
      --soft:#f7f7f9;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin:0;
      min-height:100vh;
      background:var(--pink);
      color:var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing:-0.015em;
    }}
    .stage {{
      width:min(1180px, calc(100vw - 32px));
      margin: clamp(20px, 6vw, 74px) auto;
      min-height: calc(100vh - 120px);
      background:var(--panel);
      border:1px solid rgba(0,0,0,.08);
      box-shadow: 0 34px 90px rgba(83, 21, 51, .22);
      display:grid;
      grid-template-columns: 78px 1fr;
      overflow:hidden;
    }}
    .rail {{
      border-right:1px solid var(--line);
      display:flex;
      flex-direction:column;
      align-items:center;
      padding:24px 0;
      gap:32px;
      background:#fff;
    }}
    .logo {{
      width:28px; height:28px; border:2px solid #111; border-radius:999px;
      display:grid; place-items:center; font-weight:900; font-size:15px;
    }}
    .hamb {{ margin-top:auto; margin-bottom:auto; font-size:22px; transform:rotate(90deg); color:#222; }}
    .dot-stack {{ display:grid; gap:14px; margin-top:auto; }}
    .dot {{ width:22px; height:22px; border-radius:999px; border:1px solid #ddd; background:linear-gradient(135deg,#1787ff,#6ee7b7); }}
    .dot:nth-child(2) {{ background:linear-gradient(135deg,#ff8ec7,#ffd166); }}
    .dot:nth-child(3) {{ background:linear-gradient(135deg,#111,#777); }}
    .content {{ min-width:0; overflow:hidden; }}
    .topbar {{
      display:grid;
      grid-template-columns: 1fr minmax(190px, 320px);
      gap:24px;
      align-items:center;
      padding:30px 38px 12px;
    }}
    .nav {{ display:flex; gap:22px; white-space:nowrap; overflow:hidden; }}
    .nav-chip {{ color:#6c6f78; text-decoration:none; font-size:13px; font-weight:650; }}
    .nav-chip:first-child, .nav-chip:hover {{ color:#111; }}
    .search {{ border-bottom:2px solid #1e1e24; display:flex; align-items:center; gap:8px; padding:4px 0; }}
    .search input {{ border:0; outline:0; width:100%; font-size:12px; font-weight:700; }}
    .controls {{ padding:0 38px 24px; display:flex; align-items:center; gap:10px; flex-wrap:wrap; }}
    .control-pill {{ border:1px solid #151821; color:#151821; border-radius:999px; padding:8px 16px; font-size:12px; font-weight:800; background:#fff; }}
    .control-pill.primary {{ background:#10131b; color:#fff; }}
    .hero {{ padding:0 38px 14px; }}
    .brand-line {{ display:flex; align-items:center; gap:12px; margin-bottom:12px; }}
    .brand-dot {{ width:22px; height:22px; border-radius:999px; background:#1584ff; }}
    .brand-title {{ font-size:14px; font-weight:900; }}
    .brand-sub {{ font-size:10px; text-transform:uppercase; color:#8d9098; font-weight:800; margin-left:8px; }}
    h1 {{ margin:0; font-size:clamp(32px, 6vw, 76px); line-height:.94; letter-spacing:-0.065em; max-width:850px; }}
    .deck {{ max-width:760px; color:#666a73; line-height:1.5; margin:18px 0 0; font-size:15px; }}
    .updated {{ margin-top:14px; color:#9aa; font-size:12px; font-weight:750; }}
    .masonry {{
      padding: 8px 38px 46px;
      display:grid;
      grid-template-columns: repeat(3, minmax(240px, 1fr));
      gap:34px 42px;
      align-items:start;
    }}
    .story-card {{ min-width:0; break-inside:avoid; }}
    .story-card.feature {{ grid-row: span 2; }}
    .story-card.wide {{ grid-column: span 2; }}
    .story-top {{ display:grid; grid-template-columns:auto 1fr auto; gap:10px; align-items:center; margin-bottom:16px; }}
    .author-mark {{ width:26px; height:26px; border-radius:999px; background:var(--story-color); display:grid; place-items:center; font-size:12px; font-weight:900; color:#111; }}
    .story-kicker {{ font-size:12px; font-weight:900; }}
    .story-actions {{ display:flex; gap:6px; }}
    .mini-btn {{ border:1px solid #10131b; border-radius:999px; padding:4px 9px; font-size:10px; line-height:1; color:#111; text-decoration:none; background:#fff; font-weight:850; }}
    .mini-btn.dark {{ background:#10131b; color:#fff; }}
    .label-row {{ display:flex; gap:4px; flex-wrap:wrap; min-height:18px; }}
    .tag {{ background:var(--story-color); color:#24242a; border-radius:999px; padding:2px 6px; font-size:9px; text-transform:uppercase; font-weight:900; }}
    .story-card h2 {{ margin:10px 0 8px; font-size:clamp(21px, 2.3vw, 34px); line-height:1.04; letter-spacing:-.052em; }}
    .story-card:not(.feature) h2 {{ font-size:22px; line-height:1.08; }}
    .summary {{ margin:0; color:#5f626b; line-height:1.48; font-size:13px; }}
    .why {{ margin:12px 0 0; color:#1b1e25; line-height:1.45; font-size:12px; border-left:3px solid var(--story-color); padding-left:10px; }}
    .story-foot {{ margin-top:26px; display:flex; gap:16px; color:#8f939d; font-size:11px; align-items:center; }}
    .score {{ color:#262a34; font-weight:850; }}
    .sources {{ margin-top:12px; display:flex; gap:8px; flex-wrap:wrap; }}
    .source-link {{ color:#60636c; font-size:11px; text-decoration:none; border-bottom:1px solid #cfd1d6; }}
    footer {{ padding:0 38px 32px; color:#8e929d; font-size:12px; }}
    @media (max-width: 900px) {{
      .stage {{ grid-template-columns:1fr; margin:0; width:100%; min-height:100vh; }}
      .rail {{ display:none; }}
      .topbar {{ grid-template-columns:1fr; padding:22px 20px 10px; }}
      .nav {{ gap:14px; overflow:auto; padding-bottom:4px; }}
      .controls, .hero, .masonry, footer {{ padding-left:20px; padding-right:20px; }}
      .masonry {{ grid-template-columns:1fr; gap:32px; }}
      .story-card.feature, .story-card.wide {{ grid-column:auto; grid-row:auto; }}
      h1 {{ font-size:46px; }}
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
