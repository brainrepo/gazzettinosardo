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

def render_item(item):
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in item.get("tags", []))
    links = "".join(
        f'<li><a href="{esc(src.get("url"))}" target="_blank" rel="noopener">{esc(src.get("name", "fonte"))}</a></li>'
        for src in item.get("sources", [])
    )
    return f"""
<article class="card">
  <div class="meta">{esc(item.get('section', 'News'))} · {esc(item.get('time', ''))}</div>
  <h2>{esc(item.get('title', 'Senza titolo'))}</h2>
  <p>{esc(item.get('summary', ''))}</p>
  <p class="why"><strong>Perché conta:</strong> {esc(item.get('why', 'Da monitorare.'))}</p>
  <div class="tags">{tags}</div>
  <details><summary>Fonti</summary><ul>{links}</ul></details>
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
    cards = "\n".join(render_item(i) for i in items)
    html_doc = f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>News Nuoro — oggi</title>
  <meta name="description" content="Rassegna quotidiana correlata delle notizie su Nuoro e provincia." />
  <style>
    :root {{ color-scheme: dark; --bg:#0b1020; --panel:#121a2f; --text:#eef3ff; --muted:#9fb0d0; --accent:#6ee7b7; --line:#263350; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; background: radial-gradient(circle at top left,#1b2a4a,var(--bg) 42%); color:var(--text); }}
    header {{ padding:48px 20px 24px; max-width:980px; margin:auto; }}
    h1 {{ font-size: clamp(34px, 6vw, 64px); margin:0 0 10px; letter-spacing:-0.04em; }}
    .subtitle {{ color:var(--muted); font-size:18px; line-height:1.5; max-width:760px; }}
    .bar {{ display:flex; gap:12px; flex-wrap:wrap; margin-top:22px; }}
    .pill {{ border:1px solid var(--line); background:rgba(18,26,47,.72); padding:9px 12px; border-radius:999px; color:var(--muted); }}
    main {{ max-width:980px; margin:auto; padding:10px 20px 60px; display:grid; gap:18px; }}
    .card {{ background:rgba(18,26,47,.82); border:1px solid var(--line); border-radius:24px; padding:22px; box-shadow:0 20px 60px rgba(0,0,0,.25); }}
    .card h2 {{ margin:6px 0 10px; font-size:24px; letter-spacing:-.02em; }}
    .card p {{ color:#dbe7ff; line-height:1.6; }}
    .meta {{ color:var(--accent); font-size:13px; text-transform:uppercase; letter-spacing:.08em; }}
    .why {{ border-left:3px solid var(--accent); padding-left:12px; }}
    .tags {{ display:flex; gap:8px; flex-wrap:wrap; margin:14px 0; }}
    .tag {{ font-size:12px; border:1px solid #2f456a; color:#b9cdf0; padding:5px 8px; border-radius:999px; }}
    a {{ color:var(--accent); }}
    details {{ color:var(--muted); }}
    footer {{ max-width:980px; margin:auto; padding:0 20px 40px; color:var(--muted); }}
  </style>
</head>
<body>
  <header>
    <h1>News Nuoro — oggi</h1>
    <p class="subtitle">Rassegna correlata delle notizie della giornata su Nuoro e provincia. Le schede raggruppano fonti diverse e mettono in evidenza rilevanza, contesto e link originali.</p>
    <div class="bar">
      <div class="pill">Aggiornato: {esc(updated)}</div>
      <div class="pill">Fonti: La Nuova Sardegna · L'Unione Sarda · Cronache Nuoresi</div>
      <div class="pill">Curato da Hermes</div>
    </div>
  </header>
  <main>{cards}</main>
  <footer>Nota: questa pagina cita e linka le fonti originali. Non aggira paywall e non sostituisce gli articoli completi.</footer>
</body>
</html>"""
    OUT.write_text(html_doc, encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
