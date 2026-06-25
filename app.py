import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(
    page_title="GitHub Explorer",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("GitHub limits unauthenticated API requests to 60/hour. To browse without limits (5,000/hour), paste a Personal Access Token below.")
    gh_token = st.text_input("GitHub PAT (Optional)", type="password", help="Your token is only used locally and never stored.")
    if gh_token:
        st.success("Token active!")

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #0d0f14;
    color: #e8eaf0;
    font-family: 'DM Sans', sans-serif;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem; max-width: 1400px; }

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
    background: linear-gradient(135deg, #0d0f14 0%, #131720 100%);
    border-bottom: 1px solid #1e2330;
    margin-bottom: 2rem;
}
.hero h1 {
    font-family: 'Space Mono', monospace;
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(90deg, #58e06e, #00c9a7, #4f8ef7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.5rem;
    letter-spacing: -1px;
}
.hero p {
    color: #6b7280;
    font-size: 1rem;
    font-weight: 300;
    margin: 0;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
}

/* ── Tab nav ── */
.stTabs [data-baseweb="tab-list"] {
    background: #131720;
    border-radius: 12px;
    border: 1px solid #1e2330;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #6b7280 !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.78rem !important;
    padding: 8px 18px !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: #1e2330 !important;
    color: #58e06e !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #58e06e, #00c9a7) !important;
    color: #0d0f14 !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.78rem !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    transition: opacity 0.2s !important;
    letter-spacing: 0.5px;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── Inputs ── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stSlider > div {
    background: #131720 !important;
    border: 1px solid #1e2330 !important;
    border-radius: 8px !important;
    color: #e8eaf0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput label, .stSelectbox label, .stSlider label {
    color: #6b7280 !important;
    font-size: 0.78rem !important;
    font-family: 'Space Mono', monospace !important;
}

/* ── Dataframe ── */
.stDataFrame {
    border: 1px solid #1e2330 !important;
    border-radius: 12px !important;
    overflow: hidden;
}
.stDataFrame iframe { border-radius: 12px !important; }

/* ── Metric cards ── */
.metric-card {
    background: #131720;
    border: 1px solid #1e2330;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    text-align: center;
}
.metric-card .val {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #58e06e;
    display: block;
}
.metric-card .lbl {
    font-size: 0.72rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'Space Mono', monospace;
}

/* ── Repo cards ── */
.repo-card {
    background: #131720;
    border: 1px solid #1e2330;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.2s;
}
.repo-card:hover { border-color: #58e06e44; }
.repo-card .rank {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #58e06e;
    font-weight: 700;
}
.repo-card .name {
    font-size: 1rem;
    font-weight: 600;
    color: #e8eaf0;
    text-decoration: none;
}
.repo-card .desc { font-size: 0.85rem; color: #6b7280; margin: 0.3rem 0; }
.tag {
    display: inline-block;
    background: #1e2330;
    color: #4f8ef7;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.7rem;
    font-family: 'Space Mono', monospace;
    margin-right: 6px;
}
.stars { color: #f4c542; font-size: 0.78rem; font-family: 'Space Mono', monospace; }
.forks { color: #4f8ef7; font-size: 0.78rem; font-family: 'Space Mono', monospace; margin-left: 8px; }

.topic-pill {
    display: inline-block;
    background: #1e233088;
    border: 1px solid #2a3145;
    color: #a0aec0;
    border-radius: 12px;
    padding: 2px 8px;
    font-size: 0.65rem;
    margin-right: 6px;
    margin-bottom: 4px;
}

.badge {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    margin-left: 12px;
    color: #6b7280;
}
.badge-lic { color: #a78bfa; }
.badge-upd { color: #34d399; }

/* ── Alert / info ── */
.stAlert { border-radius: 10px !important; }

/* ── Download btn ── */
.stDownloadButton > button {
    background: #1e2330 !important;
    color: #58e06e !important;
    border: 1px solid #2a3145 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.72rem !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


# ── Hero ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>⬡ GitHub Explorer</h1>
  <p>// trending · starred · awesome lists · search · all in one place</p>
</div>
""", unsafe_allow_html=True)


# ── Helpers ─────────────────────────────────────────────────────────────────
def get_headers(token=None):
    h = {"User-Agent": "Mozilla/5.0 GitHubExplorer/1.0"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

GH_API = "https://api.github.com/search/repositories"


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_trending(period="daily", language="", token=""):
    url = f"https://github.com/trending"
    params = {"since": period}
    if language:
        params["l"] = language
    try:
        r = requests.get(url, headers=get_headers(token), params=params, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        articles = soup.find_all("article", class_="Box-row")
        rows = []
        for a in articles:
            name_tag = a.find("h2")
            if not name_tag:
                continue
            href = name_tag.find("a")["href"]
            full_name = href.strip("/").replace("\n", "").replace(" ", "")
            desc_tag = a.find("p")
            desc = desc_tag.text.strip() if desc_tag else "—"
            lang_tag = a.find(attrs={"itemprop": "programmingLanguage"})
            lang = lang_tag.text.strip() if lang_tag else "—"
            stars_tag = a.find("span", class_="d-inline-block float-sm-right")
            stars = stars_tag.text.strip() if stars_tag else "—"
            rows.append({
                "Repository": full_name,
                "Description": desc,
                "Language": lang,
                "Stars Today": stars,
                "URL": f"https://github.com{href}"
            })
        return rows, None
    except Exception as e:
        return [], str(e)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_most_forked(query="forks:>1", limit=25, token=""):
    params = {"q": query, "sort": "forks", "order": "desc", "per_page": limit}
    try:
        r = requests.get(GH_API, headers=get_headers(token), params=params, timeout=10)
        data = r.json()
        if "items" not in data:
            return [], data.get("message", "Unknown error")
        rows = []
        for repo in data["items"]:
            topics = repo.get("topics", [])
            lic = repo.get("license")
            rows.append({
                "Repository": repo["full_name"],
                "Stars": f"{repo['stargazers_count']:,}",
                "Forks": f"{repo['forks_count']:,}",
                "Language": repo["language"] or "—",
                "Description": repo["description"] or "—",
                "URL": repo["html_url"],
                "Topics": topics[:4],
                "License": lic.get("spdx_id") if lic else None,
                "Updated": repo["updated_at"][:10] if repo.get("updated_at") else "—"
            })
        return rows, None
    except Exception as e:
        return [], str(e)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_org_repos(org_handle, limit=30, sort_by="stars", token=""):
    if sort_by == "created":
        url = f"https://api.github.com/users/{org_handle}/repos"
        params = {"sort": "created", "direction": "desc", "per_page": limit}
    else:
        url = GH_API
        params = {"q": f"user:{org_handle}", "sort": sort_by, "order": "desc", "per_page": limit}
        
    try:
        r = requests.get(url, headers=get_headers(token), params=params, timeout=10)
        data = r.json()
        
        if sort_by == "created":
            if isinstance(data, dict) and "message" in data:
                return [], data.get("message", "Unknown error")
            items = data
        else:
            if "items" not in data:
                return [], data.get("message", "Unknown error")
            items = data["items"]
            
        rows = []
        for repo in items:
            topics = repo.get("topics", [])
            lic = repo.get("license")
            rows.append({
                "Repository": repo["full_name"],
                "Stars": f"{repo['stargazers_count']:,}",
                "Forks": f"{repo['forks_count']:,}",
                "Language": repo["language"] or "—",
                "Description": repo["description"] or "—",
                "URL": repo["html_url"],
                "Topics": topics[:4],
                "License": lic.get("spdx_id") if lic else None,
                "Updated": repo["updated_at"][:10] if repo.get("updated_at") else "—"
            })
        return rows, None
    except Exception as e:
        return [], str(e)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_most_starred(query="stars:>1", limit=25, token=""):
    params = {"q": query, "sort": "stars", "order": "desc", "per_page": limit}
    try:
        r = requests.get(GH_API, headers=get_headers(token), params=params, timeout=10)
        data = r.json()
        if "items" not in data:
            return [], data.get("message", "Unknown error")
        rows = []
        for repo in data["items"]:
            topics = repo.get("topics", [])
            lic = repo.get("license")
            rows.append({
                "Repository": repo["full_name"],
                "Stars": f"{repo['stargazers_count']:,}",
                "Forks": f"{repo['forks_count']:,}",
                "Language": repo["language"] or "—",
                "Description": repo["description"] or "—",
                "URL": repo["html_url"],
                "Topics": topics[:4],
                "License": lic.get("spdx_id") if lic else None,
                "Updated": repo["updated_at"][:10] if repo.get("updated_at") else "—"
            })
        return rows, None
    except Exception as e:
        return [], str(e)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_search(keyword, limit=30, sort_by="stars", token=""):
    params = {"q": f"{keyword} in:name", "sort": sort_by, "order": "desc", "per_page": limit}
    try:
        r = requests.get(GH_API, headers=get_headers(token), params=params, timeout=10)
        data = r.json()
        if "items" not in data:
            return [], data.get("message", "Unknown error")
        rows = []
        for repo in data["items"]:
            topics = repo.get("topics", [])
            lic = repo.get("license")
            rows.append({
                "Repository": repo["full_name"],
                "Stars": f"{repo['stargazers_count']:,}",
                "Forks": f"{repo['forks_count']:,}",
                "Language": repo["language"] or "—",
                "Description": repo["description"] or "—",
                "URL": repo["html_url"],
                "Topics": topics[:4],
                "License": lic.get("spdx_id") if lic else None,
                "Updated": repo["updated_at"][:10] if repo.get("updated_at") else "—"
            })
        return rows, None
    except Exception as e:
        return [], str(e)


def render_repo_cards(rows, rank=True):
    for i, r in enumerate(rows[:30], 1):
        url = r.get("URL", "#")
        name = r.get("Repository", "unknown")
        desc = r.get("Description", "")
        lang = r.get("Language", "—")
        stars = r.get("Stars Today") or r.get("Stars", "")
        forks = r.get("Forks", "")
        updated = r.get("Updated", "")
        lic = r.get("License")
        topics = r.get("Topics", [])
        
        forks_html = f'<span class="forks">🍴 {forks}</span>' if forks else ""
        rank_html = f'<span class="rank">#{i}</span>' if rank else ""
        
        # Build extra metadata badges
        meta_html = ""
        if lic:
            meta_html += f'<span class="badge badge-lic">⚖️ {lic}</span>'
        if updated and updated != "—":
            meta_html += f'<span class="badge badge-upd">📅 {updated}</span>'
            
        # Build topics HTML
        topics_html = ""
        if topics:
            topics_html = '<div style="margin: 8px 0;">' + "".join([f'<span class="topic-pill">{t}</span>' for t in topics]) + '</div>'
            
        st.markdown(f"""
        <div class="repo-card">
          {rank_html}
          <div><a class="name" href="{url}" target="_blank">⬡ {name}</a></div>
          <p class="desc">{desc}</p>
          {topics_html}
          <div style="margin-top: 10px;">
              <span class="tag">{lang}</span>
              <span class="stars">⭐ {stars}</span>{forks_html}
              {meta_html}
          </div>
        </div>
        """, unsafe_allow_html=True)


def df_to_csv(rows):
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8")


# ── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab_forked, tab_orgs, tab3, tab4 = st.tabs([
    "🔥  Trending Today",
    "⭐  Most Starred",
    "🍴  Most Forked",
    "🏢  AI Organizations",
    "📋  Awesome Lists",
    "🔎  Search Repos",
])


# ── TAB 1: TRENDING ─────────────────────────────────────────────────────────
with tab1:
    st.markdown("### Today's Top Trending Repositories")
    c1, c2 = st.columns([1, 1])
    with c1:
        period = st.selectbox("Time range", ["daily", "weekly", "monthly"],
                              format_func=lambda x: {"daily": "Today", "weekly": "This Week", "monthly": "This Month"}[x])
    with c2:
        lang_filter = st.text_input("Filter by language (optional)", placeholder="python, javascript, rust…")

    if st.button("Fetch Trending Repos", key="btn_trend"):
        with st.spinner("Scraping GitHub Trending…"):
            rows, err = fetch_trending(period, lang_filter.lower().strip(), gh_token)
        if err:
            st.error(f"Error: {err}")
        elif not rows:
            st.warning("No trending repos found. GitHub may have rate-limited the request.")
        else:
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.markdown(f'<div class="metric-card"><span class="val">{len(rows)}</span><span class="lbl">Repos Found</span></div>', unsafe_allow_html=True)
            with mc2:
                langs = [r["Language"] for r in rows if r["Language"] != "—"]
                top_lang = max(set(langs), key=langs.count) if langs else "—"
                st.markdown(f'<div class="metric-card"><span class="val">{top_lang}</span><span class="lbl">Top Language</span></div>', unsafe_allow_html=True)
            with mc3:
                st.markdown(f'<div class="metric-card"><span class="val">{datetime.now().strftime("%b %d")}</span><span class="lbl">Fetched On</span></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            col_cards, col_table = st.columns([1, 1])
            with col_cards:
                st.markdown("**Top 10 Cards**")
                render_repo_cards(rows[:10])
            with col_table:
                st.markdown("**Full List**")
                df = pd.DataFrame(rows)
                st.dataframe(df[["Repository", "Language", "Stars Today"]].head(30),
                             use_container_width=True, hide_index=True)
                st.download_button("⬇ Download CSV", df_to_csv(rows), "trending_repos.csv", "text/csv")


# ── TAB 2: MOST STARRED ─────────────────────────────────────────────────────
with tab2:
    st.markdown("### All-Time Most Starred GitHub Repos")
    c1, c2 = st.columns([2, 1])
    with c1:
        star_query = st.text_input("GitHub search query", value="stars:>50000",
                                   help='e.g. "machine-learning stars:>1000" or "llm language:python"')
    with c2:
        star_limit = st.slider("Results", 10, 100, 25)

    if st.button("Fetch Most Starred", key="btn_star"):
        with st.spinner("Querying GitHub API…"):
            rows, err = fetch_most_starred(star_query, star_limit, gh_token)
        if err:
            st.error(f"API Error: {err}")
        elif not rows:
            st.warning("No results found.")
        else:
            mc1, mc2 = st.columns(2)
            with mc1:
                top_stars = rows[0]["Stars"] if rows else "—"
                st.markdown(f'<div class="metric-card"><span class="val">{top_stars}</span><span class="lbl">Most Stars (#1)</span></div>', unsafe_allow_html=True)
            with mc2:
                st.markdown(f'<div class="metric-card"><span class="val">{len(rows)}</span><span class="lbl">Repos Fetched</span></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            render_repo_cards(rows[:5], rank=True)
            st.markdown("**Full table**")
            df = pd.DataFrame(rows)
            st.dataframe(df[["Repository", "Stars", "Forks", "Language", "Description"]],
                         use_container_width=True, hide_index=True)
            st.download_button("⬇ Download CSV", df_to_csv(rows), "most_starred.csv", "text/csv")


# ── TAB FORKED: MOST FORKED ─────────────────────────────────────────────────
with tab_forked:
    st.markdown("### All-Time Most Forked GitHub Repos")
    c1, c2 = st.columns([2, 1])
    with c1:
        fork_query = st.text_input("GitHub search query", value="forks:>10000",
                                   help='e.g. "machine-learning forks:>100" or "llm language:python"', key="fork_q")
    with c2:
        fork_limit = st.slider("Results", 10, 100, 25, key="fork_l")

    if st.button("Fetch Most Forked", key="btn_fork"):
        with st.spinner("Querying GitHub API…"):
            rows, err = fetch_most_forked(fork_query, fork_limit, gh_token)
        if err:
            st.error(f"API Error: {err}")
        elif not rows:
            st.warning("No results found.")
        else:
            mc1, mc2 = st.columns(2)
            with mc1:
                top_forks = rows[0]["Forks"] if rows else "—"
                st.markdown(f'<div class="metric-card"><span class="val">{top_forks}</span><span class="lbl">Most Forks (#1)</span></div>', unsafe_allow_html=True)
            with mc2:
                st.markdown(f'<div class="metric-card"><span class="val">{len(rows)}</span><span class="lbl">Repos Fetched</span></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            render_repo_cards(rows[:5], rank=True)
            st.markdown("**Full table**")
            df = pd.DataFrame(rows)
            st.dataframe(df[["Repository", "Stars", "Forks", "Language", "Description"]],
                         use_container_width=True, hide_index=True)
            st.download_button("⬇ Download CSV", df_to_csv(rows), "most_forked.csv", "text/csv")


# ── TAB ORGS: AI ORGANIZATIONS ─────────────────────────────────────────────
with tab_orgs:
    st.markdown("### Top AI Organizations & Collectives")
    st.caption("Explore top repositories from frontier labs, cloud providers, and open research collectives.")
    
    AI_ORGS = {
        "1. Frontier Model Labs": {
            "OpenAI": "openai",
            "Anthropic": "anthropics",
            "Google DeepMind": "google-deepmind",
            "Meta AI / FAIR": "facebookresearch",
            "Meta Llama": "meta-llama",
            "xAI": "xai-org",
            "Mistral AI": "mistralai",
            "Cohere": "cohere-ai",
            "AI21 Labs": "AI21Labs",
            "Alibaba (Qwen)": "QwenLM",
            "ByteDance": "bytedance",
            "DeepSeek": "deepseek-ai",
            "Microsoft AI / Research": "microsoft",
            "Apple": "apple"
        },
        "2. Cloud & Enterprise": {
            "Microsoft Azure": "Azure",
            "Google Cloud": "GoogleCloudPlatform",
            "Amazon AWS": "aws",
            "Oracle Cloud": "oracle",
            "IBM": "IBM",
            "Snowflake": "snowflakedb",
            "Databricks": "databricks",
            "Salesforce": "salesforce",
            "Alibaba Cloud": "aliyun",
            "Tencent": "Tencent",
            "Supabase": "supabase",
            "Vercel": "vercel"
        },
        "3. Research-based Organizations": {
            "Stability AI": "Stability-AI",
            "Allen Institute for AI (AI2)": "allenai",
            "Hugging Face": "huggingface",
            "NVIDIA": "NVIDIA",
            "NVIDIA Labs": "NVlabs",
            "Tsinghua/Zhipu (GLM)": "THUDM",
            "BAAI": "baai-ac",
            "PyTorch": "pytorch",
            "TensorFlow": "tensorflow",
            "Scikit-learn": "scikit-learn"
        },
        "4. Independent Open Research Collectives": {
            "Nous Research": "NousResearch",
            "EleutherAI": "EleutherAI",
            "LAION": "LAION-AI",
            "Together AI": "togethercomputer",
            "OpenBMB": "OpenBMB",
            "OpenRouter": "OpenRouter-ai",
            "Unsloth AI": "unslothai",
            "Axolotl (OpenAccess AI)": "OpenAccess-AI-Collective",
            "RWKV Foundation": "BlinkDL",
            "BigScience": "bigscience-workshop",
            "vLLM Project": "vllm-project"
        },
        "5. AI Tools, Frameworks & Breakout Projects": {
            "LangChain": "langchain-ai",
            "LlamaIndex": "run-llama",
            "n8n": "n8n-io",
            "Ollama": "ollama",
            "Open WebUI": "open-webui",
            "AutoGPT": "Significant-Gravitas",
            "Weaviate": "weaviate",
            "Qdrant": "qdrant",
            "Milvus": "milvus-io",
            "Chroma": "chroma-core",
            "Weights & Biases": "wandb",
            "Ray (Anyscale)": "ray-project",
            "TauricResearch": "TauricResearch"
        }
    }
    
    c1, c2 = st.columns([2, 1])
    with c1:
        org_category = st.selectbox("Organization Category", list(AI_ORGS.keys()))
        selected_org_name = st.selectbox("Organization", list(AI_ORGS[org_category].keys()))
        org_handle = AI_ORGS[org_category][selected_org_name]
        
        custom_org = st.text_input("Or enter a custom GitHub handle/org:", placeholder="e.g. vllm-project", help="Overrides the dropdown selection if provided.")
        
    with c2:
        org_sort_options = {
            "stars": "Most Stars",
            "forks": "Most Forks",
            "updated": "Recently Updated",
            "created": "Newest Added",
            "help-wanted-issues": "Help Wanted Issues"
        }
        org_sort_by = st.selectbox("Sort by", list(org_sort_options.keys()), format_func=lambda x: org_sort_options[x], key="org_sort")
        org_limit = st.slider("Results", 5, 50, 15, key="org_limit")

    target_org = custom_org.strip() if custom_org.strip() else org_handle

    if st.button("Fetch Org Repos", key="btn_orgs"):
        with st.spinner(f"Fetching repos for @{target_org}…"):
            rows, err = fetch_org_repos(target_org, org_limit, org_sort_by, gh_token)
        if err:
            st.error(f"API Error: {err}")
        elif not rows:
            st.warning(f"No repositories found for {target_org}.")
        else:
            st.success(f"Found top repositories for `{target_org}`")
            render_repo_cards(rows, rank=True)
            df = pd.DataFrame(rows)
            st.dataframe(df[["Repository", "Stars", "Forks", "Language", "Description"]],
                         use_container_width=True, hide_index=True)
            st.download_button("⬇ Download CSV", df_to_csv(rows), f"{target_org}_repos.csv", "text/csv")


# ── TAB 3: AWESOME LISTS ────────────────────────────────────────────────────
with tab3:
    st.markdown("### Explore `awesome-*` Curated Lists")
    st.caption("These are community-curated lists of resources on every topic imaginable.")

    c1, c2 = st.columns([2, 1])
    with c1:
        awesome_topic = st.text_input("Topic (appended to 'awesome')", value="python",
                                      placeholder="llm, react, rust, selfhosted…")
    with c2:
        awesome_limit = st.slider("Results", 5, 50, 15, key="aw_limit")

    if st.button("Find Awesome Lists", key="btn_awesome"):
        kw = f"awesome-{awesome_topic.strip()}" if awesome_topic.strip() else "awesome"
        with st.spinner(f"Searching for {kw}…"):
            rows, err = fetch_search(kw, awesome_limit, "stars", gh_token)
        if err:
            st.error(f"API Error: {err}")
        elif not rows:
            st.warning("No awesome lists found for that topic.")
        else:
            # filter to only repos whose name starts with "awesome"
            filtered = [r for r in rows if r["Repository"].split("/")[-1].lower().startswith("awesome")]
            if not filtered:
                filtered = rows  # fallback
            st.success(f"Found {len(filtered)} awesome lists for `{awesome_topic}`")
            render_repo_cards(filtered, rank=False)
            st.download_button("⬇ Download CSV", df_to_csv(filtered), f"awesome_{awesome_topic}.csv", "text/csv")

    with st.expander("📚 Popular Awesome Topics"):
        topics = ["python", "llm", "machine-learning", "react", "rust", "selfhosted",
                  "kubernetes", "security", "go", "typescript", "devops", "ai-agents",
                  "system-design", "interview-questions", "data-engineering"]
        cols = st.columns(5)
        for i, t in enumerate(topics):
            cols[i % 5].code(f"awesome-{t}")


# ── TAB 4: SEARCH ────────────────────────────────────────────────────────────
with tab4:
    st.markdown("### Search Any Repository")
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        search_kw = st.text_input("Keyword", placeholder="e.g.  langchain, stable-diffusion, rag, transformer…")
    with c2:
        sort_by = st.selectbox("Sort by", ["stars", "forks", "updated"])
    with c3:
        search_limit = st.slider("Results", 10, 100, 30, key="s_limit")

    if st.button("Search GitHub", key="btn_search"):
        if not search_kw.strip():
            st.warning("Please enter a keyword.")
        else:
            with st.spinner(f"Searching for '{search_kw}'…"):
                rows, err = fetch_search(search_kw, search_limit, sort_by, gh_token)
            if err:
                st.error(f"API Error: {err}")
            elif not rows:
                st.warning("No repositories found.")
            else:
                mc1, mc2, mc3 = st.columns(3)
                with mc1:
                    st.markdown(f'<div class="metric-card"><span class="val">{len(rows)}</span><span class="lbl">Results</span></div>', unsafe_allow_html=True)
                with mc2:
                    top = rows[0]["Repository"].split("/")[-1] if rows else "—"
                    st.markdown(f'<div class="metric-card"><span class="val" style="font-size:1.1rem">{top}</span><span class="lbl">Top Match</span></div>', unsafe_allow_html=True)
                with mc3:
                    stars = rows[0]["Stars"] if rows else "—"
                    st.markdown(f'<div class="metric-card"><span class="val">{stars}</span><span class="lbl">Top Repo Stars</span></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                df = pd.DataFrame(rows)
                st.dataframe(df[["Repository", "Stars", "Language", "Description", "Updated"]],
                             use_container_width=True, hide_index=True)
                st.download_button("⬇ Download CSV", df_to_csv(rows),
                                   f"search_{search_kw.replace(' ','_')}.csv", "text/csv")


# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<br><hr style="border-color:#1e2330">
<p style="text-align:center; color:#2a3145; font-family:'Space Mono',monospace; font-size:0.7rem;">
  GitHub Explorer · data via github.com/trending & api.github.com · deploy free on share.streamlit.io
</p>
""", unsafe_allow_html=True)
