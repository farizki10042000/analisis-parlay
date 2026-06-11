import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

st.set_page_config(
    page_title="⚽ Analisis Parlay Bola",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .main-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 2rem; border-radius: 16px; text-align: center; margin-bottom: 2rem;
    border: 1px solid #e94560;
  }
  .main-header h1 { color: #fff; font-size: 2.2rem; margin: 0; font-weight: 700; }
  .main-header p  { color: #a0aec0; margin: .5rem 0 0; font-size: 1rem; }

  .metric-card {
    background: #1a1a2e; border: 1px solid #2d3748;
    border-radius: 12px; padding: 1.2rem; text-align: center;
  }
  .metric-card .val { font-size: 2rem; font-weight: 700; color: #e94560; }
  .metric-card .lbl { font-size: .85rem; color: #718096; margin-top: .3rem; }

  .match-card {
    background: #1a1a2e; border: 1px solid #2d3748;
    border-radius: 12px; padding: 1.2rem; margin-bottom: .8rem;
    transition: border-color .2s;
  }
  .match-card:hover { border-color: #e94560; }

  .prob-high   { color: #48bb78; font-weight: 700; }
  .prob-medium { color: #ecc94b; font-weight: 700; }
  .prob-low    { color: #fc8181; font-weight: 700; }

  .badge-win  { background:#276749; color:#9ae6b4; padding:2px 10px; border-radius:20px; font-size:.75rem; }
  .badge-draw { background:#744210; color:#fbd38d; padding:2px 10px; border-radius:20px; font-size:.75rem; }
  .badge-lose { background:#742a2a; color:#feb2b2; padding:2px 10px; border-radius:20px; font-size:.75rem; }

  .disclaimer {
    background: #2d1b00; border: 1px solid #c05621;
    border-radius: 10px; padding: 1rem; margin-top: 1rem;
    color: #fbd38d; font-size: .85rem;
  }

  div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
  .stButton > button {
    background: linear-gradient(135deg, #e94560, #c0392b);
    color: white; border: none; border-radius: 8px;
    padding: .6rem 1.5rem; font-weight: 600; width: 100%;
  }
  .stButton > button:hover { opacity: .9; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>⚽ Analisis Statistik Parlay Bola</h1>
  <p>Data real-time • Probabilitas berbasis statistik • Bukan jaminan kemenangan</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Pengaturan")

    api_key = st.text_input(
        "API Key (football-data.org)",
        type="password",
        help="Daftar gratis di https://www.football-data.org/client/register"
    )

    st.markdown("---")
    st.markdown("### 🏆 Pilih Liga")
    leagues = {
        "Premier League (Inggris)": "PL",
        "La Liga (Spanyol)": "PD",
        "Bundesliga (Jerman)": "BL1",
        "Serie A (Italia)": "SA",
        "Ligue 1 (Prancis)": "FL1",
        "Champions League": "CL",
        "Eredivisie (Belanda)": "DED",
        "Primeira Liga (Portugal)": "PPL",
    }
    selected_leagues = st.multiselect(
        "Pilih liga",
        list(leagues.keys()),
        default=["Premier League (Inggris)", "La Liga (Spanyol)"]
    )

    st.markdown("---")
    st.markdown("### 📅 Rentang Waktu")
    days_ahead = st.slider("Hari ke depan", 1, 7, 3)

    st.markdown("---")
    st.markdown("### 🔽 Sortir & Filter")
    sort_by = st.selectbox(
        "Urutkan berdasarkan",
        ["Probabilitas Tertinggi", "Probabilitas Terendah",
         "Liga", "Tanggal Pertandingan"]
    )
    min_prob = st.slider("Probabilitas minimum (%)", 0, 100, 50)

    show_analysis = st.checkbox("Tampilkan analisis detail", value=True)

    st.markdown("---")
    st.markdown("""
    <div style="color:#718096; font-size:.75rem; line-height:1.6">
    📌 <b>Cara pakai:</b><br>
    1. Daftar gratis di football-data.org<br>
    2. Masukkan API key<br>
    3. Klik "Ambil & Analisis Data"<br><br>
    ⚠️ Tanpa API key, contoh data demo akan ditampilkan.
    </div>
    """, unsafe_allow_html=True)

# ── Fungsi API ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_matches(api_key: str, league_code: str, days: int):
    """Ambil pertandingan dari football-data.org"""
    date_from = datetime.now().strftime("%Y-%m-%d")
    date_to   = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    headers   = {"X-Auth-Token": api_key}
    url = (f"https://api.football-data.org/v4/competitions/{league_code}"
           f"/matches?dateFrom={date_from}&dateTo={date_to}&status=SCHEDULED")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json().get("matches", [])
        return []
    except Exception:
        return []

@st.cache_data(ttl=300)
def fetch_team_stats(api_key: str, league_code: str):
    """Ambil statistik/klasemen liga"""
    headers = {"X-Auth-Token": api_key}
    url = f"https://api.football-data.org/v4/competitions/{league_code}/standings"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            standings = data.get("standings", [])
            if standings:
                stats = {}
                for entry in standings[0].get("table", []):
                    t = entry["team"]["id"]
                    stats[t] = {
                        "name": entry["team"]["name"],
                        "position": entry["position"],
                        "played": entry["playedGames"],
                        "won": entry["won"],
                        "draw": entry["draw"],
                        "lost": entry["lost"],
                        "goals_for": entry["goalsFor"],
                        "goals_against": entry["goalsAgainst"],
                        "points": entry["points"],
                        "form": entry.get("form", ""),
                    }
                return stats
        return {}
    except Exception:
        return {}

# ── Kalkulasi Probabilitas ────────────────────────────────────────────────────
def calculate_probability(home_stats: dict, away_stats: dict):
    """
    Menghitung probabilitas berdasarkan:
    - Posisi klasemen
    - Rata-rata gol
    - Win rate
    - Form terkini (5 game terakhir)
    - Keuntungan kandang
    """
    if not home_stats or not away_stats:
        return 50.0, 25.0, 25.0, "Kurang data"

    played_h = max(home_stats["played"], 1)
    played_a = max(away_stats["played"], 1)

    # Win-rate
    wr_h = home_stats["won"] / played_h
    wr_a = away_stats["won"] / played_a

    # Rata-rata gol
    gf_h = home_stats["goals_for"]   / played_h
    ga_h = home_stats["goals_against"] / played_h
    gf_a = away_stats["goals_for"]   / played_a
    ga_a = away_stats["goals_against"] / played_a

    # Kekuatan serangan & pertahanan (relatif rata-rata liga 1.5 gol)
    attack_h  = gf_h / 1.5
    defense_h = 1 / max(ga_h, 0.1)
    attack_a  = gf_a / 1.5
    defense_a = 1 / max(ga_a, 0.1)

    # Expected goals
    xg_h = attack_h * defense_a * 1.35   # home advantage +35 %
    xg_a = attack_a * defense_h * 1.0

    # Poisson sederhana P(home win) = P(xg_h > xg_a)
    xg_h = min(xg_h, 5); xg_a = min(xg_a, 5)
    diff  = xg_h - xg_a
    p_home_raw = 1 / (1 + np.exp(-diff * 0.8))

    # Form terkini
    form_h = home_stats.get("form", "") or ""
    form_a = away_stats.get("form", "") or ""
    def form_score(f):
        pts = {"W": 3, "D": 1, "L": 0}
        vals = [pts.get(c, 1) for c in f[-5:]] if f else [1]
        return sum(vals) / (len(vals) * 3)
    fs_h = form_score(form_h)
    fs_a = form_score(form_a)
    form_adj = (fs_h - fs_a) * 0.15

    # Posisi klasemen
    pos_h = home_stats.get("position", 10)
    pos_a = away_stats.get("position", 10)
    max_pos = 20
    pos_adj = ((pos_a - pos_h) / max_pos) * 0.1

    p_home = np.clip(p_home_raw + form_adj + pos_adj, 0.05, 0.90)

    # Draw lebih mungkin bila kekuatan seimbang
    balance = 1 - abs(p_home - 0.5) * 2
    p_draw  = np.clip(0.22 * (1 + balance * 0.3), 0.05, 0.40)
    p_away  = np.clip(1 - p_home - p_draw, 0.05, 0.85)

    # Normalisasi
    total   = p_home + p_draw + p_away
    p_home /= total; p_draw /= total; p_away /= total

    # Rekomendasi
    max_p = max(p_home, p_draw, p_away)
    if max_p == p_home:
        rec = "🏠 Home Win"
    elif max_p == p_draw:
        rec = "🤝 Draw"
    else:
        rec = "✈️ Away Win"

    # Confidence
    if max_p >= 0.60:
        conf = "🟢 Tinggi"
    elif max_p >= 0.45:
        conf = "🟡 Sedang"
    else:
        conf = "🔴 Rendah"

    return round(p_home*100, 1), round(p_draw*100, 1), round(p_away*100, 1), rec, conf, max_p*100

def analyze_form(form_str: str):
    if not form_str:
        return "Tidak ada data"
    icons = {"W": "✅", "D": "🟡", "L": "❌"}
    return " ".join(icons.get(c, "⬜") for c in form_str[-5:])

# ── Data Demo ─────────────────────────────────────────────────────────────────
def get_demo_data():
    return [
        {"league":"Premier League","home":"Manchester City","away":"Arsenal",
         "date":"2025-06-12 20:00","home_pos":1,"away_pos":2,
         "home_won":22,"home_draw":5,"home_lost":5,"home_played":32,
         "home_gf":68,"home_ga":30,"home_form":"WWWDW",
         "away_won":20,"away_draw":6,"away_lost":6,"away_played":32,
         "away_gf":62,"away_ga":32,"away_form":"WWLDW"},
        {"league":"La Liga","home":"Real Madrid","away":"Barcelona",
         "date":"2025-06-13 21:00","home_pos":1,"away_pos":2,
         "home_won":24,"home_draw":4,"home_lost":4,"home_played":32,
         "home_gf":75,"home_ga":28,"home_form":"WWWWW",
         "away_won":22,"away_draw":5,"away_lost":5,"away_played":32,
         "away_gf":70,"away_ga":30,"away_form":"WWWDL"},
        {"league":"Bundesliga","home":"Bayern Munich","away":"Borussia Dortmund",
         "date":"2025-06-14 18:30","home_pos":1,"away_pos":3,
         "home_won":25,"home_draw":3,"home_lost":4,"home_played":32,
         "home_gf":82,"home_ga":32,"home_form":"WWWWL",
         "away_won":18,"away_draw":6,"away_lost":8,"away_played":32,
         "away_gf":58,"away_ga":45,"away_form":"WLDWW"},
        {"league":"Serie A","home":"Inter Milan","away":"AC Milan",
         "date":"2025-06-14 20:45","home_pos":2,"away_pos":4,
         "home_won":21,"home_draw":7,"home_lost":4,"home_played":32,
         "home_gf":65,"home_ga":28,"home_form":"DWWWW",
         "away_won":17,"away_draw":8,"away_lost":7,"away_played":32,
         "away_gf":55,"away_ga":38,"away_form":"WDWLD"},
        {"league":"Premier League","home":"Liverpool","away":"Chelsea",
         "date":"2025-06-15 17:00","home_pos":3,"away_pos":6,
         "home_won":19,"home_draw":7,"home_lost":6,"home_played":32,
         "home_gf":60,"home_ga":35,"home_form":"WDWWL",
         "away_won":15,"away_draw":8,"away_lost":9,"away_played":32,
         "away_gf":52,"away_ga":42,"away_form":"LDWWD"},
        {"league":"Ligue 1","home":"PSG","away":"Marseille",
         "date":"2025-06-15 20:00","home_pos":1,"away_pos":4,
         "home_won":26,"home_draw":3,"home_lost":3,"home_played":32,
         "home_gf":88,"home_ga":22,"home_form":"WWWWW",
         "away_won":16,"away_draw":7,"away_lost":9,"away_played":32,
         "away_gf":50,"away_ga":40,"away_form":"LWDWW"},
        {"league":"La Liga","home":"Atletico Madrid","away":"Sevilla",
         "date":"2025-06-16 19:00","home_pos":3,"away_pos":8,
         "home_won":18,"home_draw":9,"home_lost":5,"home_played":32,
         "home_gf":55,"home_ga":30,"home_form":"DWWDW",
         "away_won":13,"away_draw":8,"away_lost":11,"away_played":32,
         "away_gf":45,"away_ga":50,"away_form":"LWWLD"},
        {"league":"Bundesliga","home":"Bayer Leverkusen","away":"RB Leipzig",
         "date":"2025-06-16 20:30","home_pos":2,"away_pos":4,
         "home_won":20,"home_draw":8,"home_lost":4,"home_played":32,
         "home_gf":62,"home_ga":30,"home_form":"WDWWW",
         "away_won":17,"away_draw":7,"away_lost":8,"away_played":32,
         "away_gf":58,"away_ga":38,"away_form":"WWLDD"},
    ]

# ── Proses & Tampilkan ────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    fetch_btn = st.button("🔍 Ambil & Analisis Data Pertandingan", use_container_width=True)

st.markdown("---")

if fetch_btn or "matches_df" in st.session_state:

    results = []

    if api_key and selected_leagues:
        with st.spinner("⏳ Mengambil data dari football-data.org ..."):
            for league_name in selected_leagues:
                code  = leagues[league_name]
                matches = fetch_matches(api_key, code, days_ahead)
                stats   = fetch_team_stats(api_key, code)

                for m in matches:
                    h_id = m["homeTeam"]["id"]
                    a_id = m["awayTeam"]["id"]
                    hs   = stats.get(h_id, {})
                    as_  = stats.get(a_id, {})

                    if hs and as_:
                        res = calculate_probability(hs, as_)
                        p_h, p_d, p_a = res[0], res[1], res[2]
                        rec, conf, best_p = res[3], res[4], res[5]
                    else:
                        p_h, p_d, p_a = 45.0, 25.0, 30.0
                        rec = "🏠 Home Win"; conf = "🔴 Rendah"; best_p = 45.0

                    match_dt = m.get("utcDate", "")[:16].replace("T", " ")
                    results.append({
                        "Liga": league_name,
                        "Tuan Rumah": m["homeTeam"]["name"],
                        "Tamu": m["awayTeam"]["name"],
                        "Tanggal": match_dt,
                        "P(Home)%": p_h,
                        "P(Draw)%": p_d,
                        "P(Away)%": p_a,
                        "Rekomendasi": rec,
                        "Confidence": conf,
                        "Best Prob%": round(best_p, 1),
                        "Form H": analyze_form(hs.get("form","")),
                        "Form A": analyze_form(as_.get("form","")),
                        "Pos H": hs.get("position", "-"),
                        "Pos A": as_.get("position", "-"),
                    })

        if not results:
            st.warning("⚠️ Tidak ada data dari API (mungkin tidak ada jadwal dalam rentang ini). Menampilkan data demo.")

    if not results:
        st.info("ℹ️ Menggunakan data demo. Masukkan API Key untuk data real-time.")
        for d in get_demo_data():
            hs = {"position":d["home_pos"],"played":d["home_played"],
                  "won":d["home_won"],"draw":d["home_draw"],"lost":d["home_lost"],
                  "goals_for":d["home_gf"],"goals_against":d["home_ga"],"form":d["home_form"]}
            as_ = {"position":d["away_pos"],"played":d["away_played"],
                   "won":d["away_won"],"draw":d["away_draw"],"lost":d["away_lost"],
                   "goals_for":d["away_gf"],"goals_against":d["away_ga"],"form":d["away_form"]}
            res = calculate_probability(hs, as_)
            p_h, p_d, p_a = res[0], res[1], res[2]
            rec, conf, best_p = res[3], res[4], res[5]
            results.append({
                "Liga": d["league"],
                "Tuan Rumah": d["home"],
                "Tamu": d["away"],
                "Tanggal": d["date"],
                "P(Home)%": p_h,
                "P(Draw)%": p_d,
                "P(Away)%": p_a,
                "Rekomendasi": rec,
                "Confidence": conf,
                "Best Prob%": round(best_p, 1),
                "Form H": analyze_form(d["home_form"]),
                "Form A": analyze_form(d["away_form"]),
                "Pos H": d["home_pos"],
                "Pos A": d["away_pos"],
            })

    df = pd.DataFrame(results)

    # ── Filter probabilitas minimum
    df = df[df["Best Prob%"] >= min_prob]

    # ── Sort
    sort_map = {
        "Probabilitas Tertinggi": ("Best Prob%", False),
        "Probabilitas Terendah":  ("Best Prob%", True),
        "Liga":                   ("Liga", True),
        "Tanggal Pertandingan":   ("Tanggal", True),
    }
    col_s, asc_s = sort_map[sort_by]
    df = df.sort_values(col_s, ascending=asc_s).reset_index(drop=True)
    df.index += 1

    st.session_state["matches_df"] = df

    # ── Statistik ringkasan ───────────────────────────────────────────────────
    st.markdown("### 📊 Ringkasan")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class="metric-card">
          <div class="val">{len(df)}</div>
          <div class="lbl">Total Pertandingan</div></div>""", unsafe_allow_html=True)
    with m2:
        high = len(df[df["Best Prob%"] >= 60])
        st.markdown(f"""<div class="metric-card">
          <div class="val" style="color:#48bb78">{high}</div>
          <div class="lbl">Confidence Tinggi (≥60%)</div></div>""", unsafe_allow_html=True)
    with m3:
        med = len(df[(df["Best Prob%"] >= 45) & (df["Best Prob%"] < 60)])
        st.markdown(f"""<div class="metric-card">
          <div class="val" style="color:#ecc94b">{med}</div>
          <div class="lbl">Confidence Sedang (45-60%)</div></div>""", unsafe_allow_html=True)
    with m4:
        avg_p = df["Best Prob%"].mean() if len(df) > 0 else 0
        st.markdown(f"""<div class="metric-card">
          <div class="val">{avg_p:.1f}%</div>
          <div class="lbl">Rata-rata Probabilitas</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabel utama ───────────────────────────────────────────────────────────
    st.markdown("### 🗂️ Daftar Pertandingan (Diurutkan)")
    tab1, tab2 = st.tabs(["📋 Tabel Ringkas", "🔍 Analisis Detail"])

    with tab1:
        display_df = df[[
            "Liga","Tuan Rumah","Tamu","Tanggal",
            "P(Home)%","P(Draw)%","P(Away)%","Rekomendasi","Confidence","Best Prob%"
        ]].copy()

        def color_prob(val):
            if val >= 60: return "color:#48bb78; font-weight:700"
            elif val >= 45: return "color:#ecc94b; font-weight:700"
            else: return "color:#fc8181; font-weight:700"

        styled = display_df.style\
            .applymap(lambda v: color_prob(v) if isinstance(v, float) else "",
                      subset=["P(Home)%","P(Draw)%","P(Away)%","Best Prob%"])\
            .set_properties(**{"background-color":"#1a1a2e","color":"#e2e8f0"})\
            .set_table_styles([{
                "selector":"th",
                "props":[("background-color","#0f3460"),
                         ("color","#fff"),("font-weight","700")]
            }])
        st.dataframe(styled, use_container_width=True, height=420)

        # Download
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download CSV",
            data=csv,
            file_name=f"analisis_parlay_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

    with tab2:
        if show_analysis:
            for _, row in df.iterrows():
                p_h = row["P(Home)%"]; p_d = row["P(Draw)%"]; p_a = row["P(Away)%"]
                best = row["Best Prob%"]
                cls  = "prob-high" if best>=60 else ("prob-medium" if best>=45 else "prob-low")
                bar_h = int(p_h); bar_d = int(p_d); bar_a = int(p_a)
                h_bar = f'<div style="background:#48bb78;height:8px;border-radius:4px;width:{bar_h}%"></div>'
                d_bar = f'<div style="background:#ecc94b;height:8px;border-radius:4px;width:{bar_d}%"></div>'
                a_bar = f'<div style="background:#fc8181;height:8px;border-radius:4px;width:{bar_a}%"></div>'

                st.markdown(f"""
                <div class="match-card">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.8rem">
                    <span style="color:#718096;font-size:.85rem">🏆 {row['Liga']} &nbsp;|&nbsp; 📅 {row['Tanggal']}</span>
                    <span class="{cls}">{row['Rekomendasi']} &nbsp; {best}%</span>
                  </div>
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem">
                    <div style="text-align:center;flex:1">
                      <div style="font-size:1.1rem;font-weight:700;color:#e2e8f0">{row['Tuan Rumah']}</div>
                      <div style="color:#718096;font-size:.8rem">🏠 Kandang | Pos #{row['Pos H']}</div>
                      <div style="margin-top:.3rem">{row['Form H']}</div>
                    </div>
                    <div style="text-align:center;padding:0 1.5rem">
                      <div style="font-size:1.3rem;color:#e94560;font-weight:700">VS</div>
                    </div>
                    <div style="text-align:center;flex:1">
                      <div style="font-size:1.1rem;font-weight:700;color:#e2e8f0">{row['Tamu']}</div>
                      <div style="color:#718096;font-size:.8rem">✈️ Tandang | Pos #{row['Pos A']}</div>
                      <div style="margin-top:.3rem">{row['Form A']}</div>
                    </div>
                  </div>
                  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem">
                    <div>
                      <div style="display:flex;justify-content:space-between;margin-bottom:3px">
                        <span style="color:#718096;font-size:.8rem">🏠 Home Win</span>
                        <span style="color:#48bb78;font-weight:700">{p_h}%</span>
                      </div>{h_bar}
                    </div>
                    <div>
                      <div style="display:flex;justify-content:space-between;margin-bottom:3px">
                        <span style="color:#718096;font-size:.8rem">🤝 Draw</span>
                        <span style="color:#ecc94b;font-weight:700">{p_d}%</span>
                      </div>{d_bar}
                    </div>
                    <div>
                      <div style="display:flex;justify-content:space-between;margin-bottom:3px">
                        <span style="color:#718096;font-size:.8rem">✈️ Away Win</span>
                        <span style="color:#fc8181;font-weight:700">{p_a}%</span>
                      </div>{a_bar}
                    </div>
                  </div>
                  <div style="margin-top:.8rem;text-align:right">
                    <span style="color:#718096;font-size:.8rem">Confidence: </span>
                    <span style="font-size:.85rem">{row['Confidence']}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aktifkan 'Tampilkan analisis detail' di sidebar untuk melihat kartu analisis.")

    # ── Disclaimer ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="disclaimer">
    ⚠️ <b>DISCLAIMER PENTING:</b>
    Analisis ini hanya berdasarkan statistik historis dan bukan jaminan hasil pertandingan.
    Probabilitas dihitung dari data klasemen, form, dan rata-rata gol — bukan prediksi pasti.
    Sepak bola mengandung banyak faktor tak terduga. Gunakan analisis ini sebagai <i>referensi tambahan</i>,
    bukan satu-satunya acuan. Bertaruhlah secara bertanggung jawab.
    </div>
    """, unsafe_allow_html=True)

else:
    # Landing state
    st.markdown("""
    <div style="text-align:center;padding:3rem;color:#718096">
      <div style="font-size:5rem">⚽</div>
      <h3 style="color:#a0aec0">Siap untuk Menganalisis Pertandingan</h3>
      <p>Klik tombol <b>"Ambil & Analisis Data"</b> di atas untuk memulai</p>
      <p style="font-size:.85rem">Tanpa API Key, data demo akan digunakan secara otomatis</p>
    </div>
    """, unsafe_allow_html=True)
