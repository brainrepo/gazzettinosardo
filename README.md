# News Nuoro

Pagina statica per raccogliere e correlare le notizie del giorno su Nuoro e provincia.

## Pubblicazione GitHub Pages

1. Crea/pusha questo repository su GitHub.
2. Abilita Pages da **Settings → Pages → Deploy from branch → main / root**.
3. La pagina principale è `index.html`.

## Aggiornamento locale

```bash
python3 scripts/build_page.py
```

Il job Hermes orario può aggiornare `data/news.json`, rigenerare `index.html` e fare push su GitHub.
