# ⬡ GitHub Explorer — Streamlit App

A sleek GitHub discovery dashboard with 4 modes:

| Tab | What it does |
|-----|-------------|
| 🔥 Trending Today | Scrapes github.com/trending (daily / weekly / monthly) |
| ⭐ Most Starred | Queries GitHub API for all-time top repos |
| 📋 Awesome Lists | Finds `awesome-*` curated list repos by topic |
| 🔎 Search Repos | Full keyword search with sort by stars / forks / updated |

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

App opens at → http://localhost:8501

## Deploy free (lifetime)

1. Push this folder to a GitHub repo
2. Go to → https://share.streamlit.io
3. Select your repo + `app.py` → Deploy

Your app will be live at:
```
https://yourname-github-explorer.streamlit.app
```

## Features
- ✅ No API key required (uses public GitHub API)
- ✅ CSV download on every tab
- ✅ Cached results (1 hour TTL)
- ✅ Responsive dark UI
- ✅ Language filter on trending
- ✅ Repo cards + data table views
