import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(
    page_title="⚽ Analisis Parlay Bola",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .main-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 2rem; border-radius: 16px; text-align: center; margin-bottom: 1.5rem;
    border: 1px solid #e94560;
  }
  .main-header h1 { color: #fff; font-size: 2rem; margin: 0; font-weight: 700; }
  .main-header p  { color: #a0aec0; margin: .4rem 0 0; font-size: .95rem; }

  .search-box {
    background: #1a1a2e; border: 2px solid #e94560;
    border-radius: 12px; padding: 1.2rem 1.5rem; margin-bottom: 1.5rem;
  }
  .search-box h3 { color: #e94560; margin: 0 0 .5rem; font-size: 1rem; }

  .club-result {
    background: linear-gradient(135deg, #1a1a2e, #0f3460);
    border: 2px solid #e94560; border-radius: 14px;
    padding: 1.5rem; margin-bottom: 1rem;
  }
  .club-result .club-name { font-size: 1.4rem; font-weight: 700; color: #fff; }
  .club-result .club-sub  { color: #a0aec0; font-size: .85rem; margin-top: .2rem; }

  .metric-card {
    background: #1a1a2e; border: 1px solid #2d3748;
    border-radius: 12px; padding: 1.1rem; text-align: center;
  }
  .metric-card .val { font-size: 1.8rem; font-weight: 700; color: #e94560; }
  .metric-card .lbl { font-size: .8rem; color: #718096; margin-top: .3rem; }

  .match-card {
    background: #1a1a2e; border: 1px solid #2d3748;
    border-radius: 12px; padding: 1.2rem; margin-bottom: .7rem;
    transition: border-color .2s;
  }
  .match-card:hover { border-color: #e94560; }
  .match-card.highlight { border-color: #e94560; background: #1f1535; }

  .prob-high   { color: #48bb78; font-weight: 700; }
  .prob-medium { color: #ecc94b; font-weight: 700; }
  .prob-low    { color: #fc8181; font-weight: 700; }

  .tag-league {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: .72rem; font-weight: 600; margin-right: 4px;
  }
  .tag-euro   { background:#1a365d; color:#90cdf4; }
  .tag-asia   { background:#1a3a1a; color:#9ae6b4; }
  .tag-world  { background:#3d1a1a; color:#feb2b2; }
  .tag-other  { background:#2d2d2d; color:#e2e8f0; }

  .disclaimer {
    background: #2d1b00; border: 1px solid #c05621;
    border-radius: 10px; padding: 1rem; margin-top: 1rem;
    color: #fbd38d; font-size: .82rem;
  }

  div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
  .stButton > button {
    background: linear-gradient(135deg, #e94560, #c0392b);
    color: white; border: none; border-radius: 8px;
    padding: .55rem 1.2rem; font-weight: 600; width: 100%;
  }
  .stButton > button:hover { opacity: .88; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>⚽ Analisis Statistik Parlay Bola</h1>
  <p>30+ Liga Dunia • Piala Dunia • Liga Asia & Indonesia • Cari Klub Favorit • Real-time Data</p>
</div>
""", unsafe_allow_html=True)

# ── Definisi Liga ─────────────────────────────────────────────────────────────
# (nama tampil → {code, region, flag})
ALL_LEAGUES = {
    # ── EROPA ──
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inggris)":      {"code":"PL",   "region":"Eropa",  "tag":"tag-euro"},
    "🇪🇸 La Liga (Spanyol)":                  {"code":"PD",   "region":"Eropa",  "tag":"tag-euro"},
    "🇩🇪 Bundesliga (Jerman)":                {"code":"BL1",  "region":"Eropa",  "tag":"tag-euro"},
    "🇮🇹 Serie A (Italia)":                   {"code":"SA",   "region":"Eropa",  "tag":"tag-euro"},
    "🇫🇷 Ligue 1 (Prancis)":                  {"code":"FL1",  "region":"Eropa",  "tag":"tag-euro"},
    "🇳🇱 Eredivisie (Belanda)":               {"code":"DED",  "region":"Eropa",  "tag":"tag-euro"},
    "🇵🇹 Primeira Liga (Portugal)":           {"code":"PPL",  "region":"Eropa",  "tag":"tag-euro"},
    "🇧🇪 Pro League (Belgia)":                {"code":"BSA",  "region":"Eropa",  "tag":"tag-euro"},
    "🇹🇷 Süper Lig (Turki)":                  {"code":"TL",   "region":"Eropa",  "tag":"tag-euro"},
    "🇬🇷 Super League (Yunani)":              {"code":"GSL",  "region":"Eropa",  "tag":"tag-euro"},
    "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Premiership (Skotlandia)":          {"code":"PPL",  "region":"Eropa",  "tag":"tag-euro"},
    # ── UEFA ──
    "🏆 UEFA Champions League":               {"code":"CL",   "region":"UEFA",   "tag":"tag-euro"},
    "🥈 UEFA Europa League":                  {"code":"EL",   "region":"UEFA",   "tag":"tag-euro"},
    "🥉 UEFA Conference League":              {"code":"ECLL", "region":"UEFA",   "tag":"tag-euro"},
    # ── DUNIA ──
    "🌍 FIFA World Cup":                      {"code":"WC",   "region":"Dunia",  "tag":"tag-world"},
    "🌎 Copa America":                        {"code":"CA",   "region":"Dunia",  "tag":"tag-world"},
    "🌍 Africa Cup of Nations":               {"code":"CAN",  "region":"Dunia",  "tag":"tag-world"},
    # ── ASIA ──
    "🏆 AFC Champions League":               {"code":"ACL",  "region":"Asia",   "tag":"tag-asia"},
    "🇯🇵 J1 League (Jepang)":                 {"code":"JPL",  "region":"Asia",   "tag":"tag-asia"},
    "🇰🇷 K League 1 (Korea Selatan)":         {"code":"KL",   "region":"Asia",   "tag":"tag-asia"},
    "🇨🇳 Chinese Super League":               {"code":"CSL",  "region":"Asia",   "tag":"tag-asia"},
    "🇸🇦 Saudi Pro League":                   {"code":"SPL",  "region":"Asia",   "tag":"tag-asia"},
    "🇦🇪 UAE Pro League":                     {"code":"UAE",  "region":"Asia",   "tag":"tag-asia"},
    "🇦🇺 A-League (Australia)":               {"code":"ASL",  "region":"Asia",   "tag":"tag-asia"},
    "🇮🇳 Indian Super League":                {"code":"ISL",  "region":"Asia",   "tag":"tag-asia"},
    "🇹🇭 Thai League 1":                      {"code":"THL",  "region":"Asia",   "tag":"tag-asia"},
    "🇲🇾 Malaysia Super League":              {"code":"MSL",  "region":"Asia",   "tag":"tag-asia"},
    # ── INDONESIA ──
    "🇮🇩 BRI Liga 1 Indonesia":               {"code":"LIGA1","region":"Indonesia","tag":"tag-asia"},
    # ── AMERICAS ──
    "🇧🇷 Brasileirão Série A":                {"code":"BSB",  "region":"Amerika","tag":"tag-other"},
    "🇦🇷 Liga Profesional (Argentina)":       {"code":"ARG",  "region":"Amerika","tag":"tag-other"},
    "🇲🇽 Liga MX (Meksiko)":                  {"code":"MX",   "region":"Amerika","tag":"tag-other"},
    "🇺🇸 MLS (Amerika Serikat)":              {"code":"MLS",  "region":"Amerika","tag":"tag-other"},
}

# Kode yang benar-benar didukung football-data.org (free tier)
SUPPORTED_CODES = {"PL","PD","BL1","SA","FL1","DED","PPL","CL","EL","WC","BSB","MLS","EC"}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Pengaturan")
    api_key = st.text_input(
        "🔑 API Key (football-data.org)",
        type="password",
        help="Daftar gratis di https://www.football-data.org/client/register"
    )

    st.markdown("---")
    st.markdown("### 🌍 Filter Region")
    regions = ["Semua"] + sorted(set(v["region"] for v in ALL_LEAGUES.values()))
    selected_region = st.selectbox("Region", regions, index=0)

    if selected_region == "Semua":
        filtered_leagues = list(ALL_LEAGUES.keys())
    else:
        filtered_leagues = [k for k, v in ALL_LEAGUES.items() if v["region"] == selected_region]

    st.markdown("### 🏆 Pilih Liga")
    selected_leagues = st.multiselect(
        "Liga",
        filtered_leagues,
        default=[k for k in filtered_leagues if "Premier League" in k or "Liga 1 Indonesia" in k][:3]
    )

    st.markdown("---")
    st.markdown("### 📅 Rentang Waktu")
    days_ahead = st.slider("Hari ke depan", 1, 14, 5)

    st.markdown("---")
    st.markdown("### 🔽 Sortir & Filter")
    sort_by = st.selectbox(
        "Urutkan berdasarkan",
        ["Probabilitas Tertinggi","Probabilitas Terendah","Liga","Tanggal Pertandingan"]
    )
    min_prob = st.slider("Probabilitas minimum (%)", 0, 100, 45)
    show_analysis = st.checkbox("Tampilkan kartu analisis detail", value=True)

    st.markdown("---")
    st.markdown("""
    <div style="color:#718096;font-size:.75rem;line-height:1.7">
    📌 <b>Cara pakai:</b><br>
    1. Daftar gratis di football-data.org<br>
    2. Masukkan API key di atas<br>
    3. Pilih liga & klik Analisis<br>
    4. Cari klub di kotak pencarian<br><br>
    ℹ️ Tanpa API key → data demo otomatis
    </div>
    """, unsafe_allow_html=True)

# ── Fungsi API ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_matches(api_key: str, league_code: str, days: int):
    date_from = datetime.now().strftime("%Y-%m-%d")
    date_to   = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    headers   = {"X-Auth-Token": api_key}
    url = (f"https://api.football-data.org/v4/competitions/{league_code}"
           f"/matches?dateFrom={date_from}&dateTo={date_to}&status=SCHEDULED")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json().get("matches", [])
    except Exception:
        pass
    return []

@st.cache_data(ttl=300)
def fetch_team_stats(api_key: str, league_code: str):
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
                        "name":           entry["team"]["name"],
                        "position":       entry["position"],
                        "played":         entry["playedGames"],
                        "won":            entry["won"],
                        "draw":           entry["draw"],
                        "lost":           entry["lost"],
                        "goals_for":      entry["goalsFor"],
                        "goals_against":  entry["goalsAgainst"],
                        "points":         entry["points"],
                        "form":           entry.get("form", ""),
                    }
                return stats
    except Exception:
        pass
    return {}

# ── Probabilitas ──────────────────────────────────────────────────────────────
def calculate_probability(hs: dict, as_: dict):
    if not hs or not as_:
        return 50.0, 25.0, 25.0, "🏠 Home Win", "🔴 Rendah", 50.0

    ph = max(hs["played"], 1); pa = max(as_["played"], 1)

    wr_h = hs["won"] / ph;  wr_a = as_["won"] / pa
    gf_h = hs["goals_for"] / ph;   ga_h = hs["goals_against"] / ph
    gf_a = as_["goals_for"] / pa;  ga_a = as_["goals_against"] / pa

    att_h = gf_h / 1.5;  def_h = 1 / max(ga_h, 0.1)
    att_a = gf_a / 1.5;  def_a = 1 / max(ga_a, 0.1)

    xg_h = min(att_h * def_a * 1.35, 5)
    xg_a = min(att_a * def_h * 1.00, 5)
    diff = xg_h - xg_a
    p_home_raw = 1 / (1 + np.exp(-diff * 0.8))

    def form_score(f):
        pts = {"W": 3, "D": 1, "L": 0}
        v = [pts.get(c, 1) for c in (f or "")[-5:]] or [1]
        return sum(v) / (len(v) * 3)

    form_adj = (form_score(hs.get("form","")) - form_score(as_.get("form",""))) * 0.15
    pos_adj  = ((as_.get("position",10) - hs.get("position",10)) / 20) * 0.10
    wr_adj   = (wr_h - wr_a) * 0.10

    p_home = float(np.clip(p_home_raw + form_adj + pos_adj + wr_adj, 0.05, 0.90))
    balance = 1 - abs(p_home - 0.5) * 2
    p_draw  = float(np.clip(0.22 * (1 + balance * 0.3), 0.05, 0.38))
    p_away  = float(np.clip(1 - p_home - p_draw, 0.05, 0.85))

    total = p_home + p_draw + p_away
    p_home /= total; p_draw /= total; p_away /= total

    best_p = max(p_home, p_draw, p_away)
    if best_p == p_home:   rec = "🏠 Home Win"
    elif best_p == p_draw: rec = "🤝 Draw"
    else:                  rec = "✈️ Away Win"

    if best_p >= 0.62:   conf = "🟢 Tinggi"
    elif best_p >= 0.48: conf = "🟡 Sedang"
    else:                conf = "🔴 Rendah"

    return round(p_home*100,1), round(p_draw*100,1), round(p_away*100,1), rec, conf, round(best_p*100,1)

def form_icons(f):
    if not f: return "–"
    icons = {"W":"✅","D":"🟡","L":"❌"}
    return " ".join(icons.get(c,"⬜") for c in (f or "")[-5:])

# ── Data Demo ─────────────────────────────────────────────────────────────────
def get_demo_data():
    raw = [
        # Premier League
        ("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inggris)","Manchester City","Arsenal","2025-06-14 20:00",
         1,22,5,5,32,68,30,"WWWDW", 2,20,6,6,32,62,32,"WWLDW"),
        ("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inggris)","Liverpool","Chelsea","2025-06-15 17:00",
         3,19,7,6,32,60,35,"WDWWL", 6,15,8,9,32,52,42,"LDWWD"),
        ("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inggris)","Tottenham","Newcastle","2025-06-16 15:00",
         5,16,7,9,32,55,45,"WDLWW", 7,14,9,9,32,50,48,"WLDWL"),
        # La Liga
        ("🇪🇸 La Liga (Spanyol)","Real Madrid","Barcelona","2025-06-13 21:00",
         1,24,4,4,32,75,28,"WWWWW", 2,22,5,5,32,70,30,"WWWDL"),
        ("🇪🇸 La Liga (Spanyol)","Atletico Madrid","Sevilla","2025-06-16 19:00",
         3,18,9,5,32,55,30,"DWWDW", 8,13,8,11,32,45,50,"LWWLD"),
        # Bundesliga
        ("🇩🇪 Bundesliga (Jerman)","Bayern Munich","Borussia Dortmund","2025-06-14 18:30",
         1,25,3,4,32,82,32,"WWWWL", 3,18,6,8,32,58,45,"WLDWW"),
        ("🇩🇪 Bundesliga (Jerman)","Bayer Leverkusen","RB Leipzig","2025-06-16 20:30",
         2,20,8,4,32,62,30,"WDWWW", 4,17,7,8,32,58,38,"WWLDD"),
        # Serie A
        ("🇮🇹 Serie A (Italia)","Inter Milan","AC Milan","2025-06-14 20:45",
         2,21,7,4,32,65,28,"DWWWW", 4,17,8,7,32,55,38,"WDWLD"),
        ("🇮🇹 Serie A (Italia)","Juventus","Napoli","2025-06-15 20:45",
         3,19,8,5,32,60,32,"WWDWL", 5,16,7,9,32,55,42,"DWLWW"),
        # Ligue 1
        ("🇫🇷 Ligue 1 (Prancis)","PSG","Marseille","2025-06-15 20:00",
         1,26,3,3,32,88,22,"WWWWW", 4,16,7,9,32,50,40,"LWDWW"),
        # Champions League
        ("🏆 UEFA Champions League","Real Madrid","Manchester City","2025-06-18 20:00",
         1,6,1,1,8,18,7,"WWWWW", 2,5,2,1,8,16,9,"WWWDW"),
        ("🏆 UEFA Champions League","Bayern Munich","Arsenal","2025-06-19 20:00",
         3,5,1,2,8,14,10,"WWLWW", 4,4,2,2,8,12,11,"WDWLW"),
        # FIFA World Cup (demo kualifikasi)
        ("🌍 FIFA World Cup","Brazil","Argentina","2025-06-20 02:00",
         1,8,1,1,10,22,6,"WWWWW", 2,7,2,1,10,20,7,"WWWDW"),
        ("🌍 FIFA World Cup","France","Germany","2025-06-21 02:00",
         3,6,2,2,10,16,8,"WWDWL", 4,6,1,3,10,15,10,"WDWWL"),
        # Liga Asia - Jepang
        ("🇯🇵 J1 League (Jepang)","Gamba Osaka","Kashima Antlers","2025-06-14 14:00",
         2,12,5,5,22,38,22,"WWDLW", 4,10,6,6,22,32,25,"WLWDW"),
        ("🇯🇵 J1 League (Jepang)","Vissel Kobe","Urawa Red","2025-06-15 12:00",
         1,14,4,4,22,42,18,"WWWWL", 5,9,6,7,22,28,28,"LDWWW"),
        # K League Korea
        ("🇰🇷 K League 1 (Korea Selatan)","Jeonbuk Motors","Ulsan Hyundai","2025-06-14 14:00",
         2,11,5,6,22,34,24,"WWLWW", 1,13,4,5,22,38,20,"WWWDW"),
        # Saudi Pro League
        ("🇸🇦 Saudi Pro League","Al-Hilal","Al-Nassr","2025-06-15 19:00",
         1,18,3,3,24,55,20,"WWWWW", 2,16,4,4,24,50,22,"WWWDL"),
        # Indian Super League
        ("🇮🇳 Indian Super League","Mumbai City","Bengaluru FC","2025-06-14 19:30",
         1,12,4,6,22,36,24,"WWDWL", 3,10,5,7,22,30,28,"WLWDW"),
        # ── INDONESIA ──
        ("🇮🇩 BRI Liga 1 Indonesia","Persija Jakarta","Persib Bandung","2025-06-14 19:00",
         3,14,5,9,28,42,32,"WDWLW", 1,18,5,5,28,52,24,"WWWWL"),
        ("🇮🇩 BRI Liga 1 Indonesia","Arema FC","PSM Makassar","2025-06-15 15:30",
         6,11,7,10,28,35,36,"LWDWW", 2,16,6,6,28,48,28,"WWDWW"),
        ("🇮🇩 BRI Liga 1 Indonesia","Bali United","Borneo FC","2025-06-16 15:30",
         4,13,6,9,28,40,30,"WDWWL", 5,12,7,9,28,38,32,"DWWLW"),
        ("🇮🇩 BRI Liga 1 Indonesia","PSIS Semarang","Persebaya Surabaya","2025-06-17 18:30",
         8,10,6,12,28,32,40,"LWLWW", 7,11,6,11,28,35,38,"WDLWW"),
        ("🇮🇩 BRI Liga 1 Indonesia","Dewa United","Madura United","2025-06-18 15:30",
         10,9,5,14,28,28,44,"LLWWL", 9,10,5,13,28,30,42,"WLLDW"),
        ("🇮🇩 BRI Liga 1 Indonesia","Persija Jakarta","PSM Makassar","2025-06-21 19:00",
         3,14,5,9,28,42,32,"WDWLW", 2,16,6,6,28,48,28,"WWDWW"),
        # AFC Champions League
        ("🏆 AFC Champions League","Persib Bandung","Al-Hilal","2025-06-19 19:00",
         1,4,1,3,8,12,10,"WWLLD", 1,6,1,1,8,18,5,"WWWWL"),
        ("🏆 AFC Champions League","Urawa Red","Jeonbuk Motors","2025-06-20 17:00",
         2,4,2,2,8,13,9,"WWDLW", 3,3,2,3,8,10,11,"WLWDD"),
        # Malaysia
        ("🇲🇾 Malaysia Super League","Johor Darul Ta'zim","Selangor FC","2025-06-14 20:45",
         1,14,3,5,22,42,20,"WWWWL", 3,10,5,7,22,30,28,"WDWLW"),
        # Thai League
        ("🇹🇭 Thai League 1","Buriram United","Muangthong United","2025-06-15 18:00",
         1,15,4,3,22,45,18,"WWWWW", 2,13,5,4,22,38,22,"WWWDL"),
        # MLS
        ("🇺🇸 MLS (Amerika Serikat)","LA Galaxy","Inter Miami","2025-06-15 09:30",
         3,10,5,7,22,32,28,"WDWLW", 1,13,5,4,22,40,22,"WWWWL"),
        # Brasileirao
        ("🇧🇷 Brasileirão Série A","Flamengo","Palmeiras","2025-06-15 04:00",
         2,14,5,5,24,42,22,"WWDWW", 1,16,4,4,24,48,20,"WWWWL"),
    ]
    results = []
    for r in raw:
        (league, home, away, date,
         h_pos, h_w, h_d, h_l, h_p, h_gf, h_ga, h_form,
         a_pos, a_w, a_d, a_l, a_p, a_gf, a_ga, a_form) = r
        hs  = {"position":h_pos,"played":h_p,"won":h_w,"draw":h_d,"lost":h_l,
               "goals_for":h_gf,"goals_against":h_ga,"form":h_form}
        as_ = {"position":a_pos,"played":a_p,"won":a_w,"draw":a_d,"lost":a_l,
               "goals_for":a_gf,"goals_against":a_ga,"form":a_form}
        p_h, p_d, p_a, rec, conf, best_p = calculate_probability(hs, as_)
        tag = ALL_LEAGUES.get(league, {}).get("tag","tag-other")
        region = ALL_LEAGUES.get(league, {}).get("region","Lainnya")
        results.append({
            "Liga": league, "Region": region, "Tag": tag,
            "Tuan Rumah": home, "Tamu": away, "Tanggal": date,
            "P(Home)%": p_h, "P(Draw)%": p_d, "P(Away)%": p_a,
            "Rekomendasi": rec, "Confidence": conf, "Best Prob%": best_p,
            "Form H": form_icons(h_form), "Form A": form_icons(a_form),
            "Pos H": h_pos, "Pos A": a_pos,
        })
    return results

# ── Render Match Card ─────────────────────────────────────────────────────────
def render_match_card(row, highlight=False):
    p_h = row["P(Home)%"]; p_d = row["P(Draw)%"]; p_a = row["P(Away)%"]
    best = row["Best Prob%"]
    cls  = "prob-high" if best>=62 else ("prob-medium" if best>=48 else "prob-low")
    card_cls = "match-card highlight" if highlight else "match-card"
    tag  = row.get("Tag","tag-other")
    region = row.get("Region","")

    def bar(pct, color):
        return f'<div style="background:{color};height:8px;border-radius:4px;width:{int(pct)}%"></div>'

    st.markdown(f"""
    <div class="{card_cls}">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.7rem;flex-wrap:wrap;gap:.3rem">
        <span>
          <span class="tag-league {tag}">{region}</span>
          <span style="color:#718096;font-size:.82rem">🏆 {row['Liga']} &nbsp;|&nbsp; 📅 {row['Tanggal']}</span>
        </span>
        <span class="{cls}">{row['Rekomendasi']} &nbsp;{best}%</span>
      </div>
      <div style="display:grid;grid-template-columns:1fr auto 1fr;align-items:center;margin-bottom:1rem;gap:.5rem">
        <div style="text-align:center">
          <div style="font-size:1.05rem;font-weight:700;color:#e2e8f0">{row['Tuan Rumah']}</div>
          <div style="color:#718096;font-size:.75rem">🏠 Kandang &nbsp;#{row['Pos H']}</div>
          <div style="margin-top:.25rem;font-size:.85rem">{row['Form H']}</div>
        </div>
        <div style="text-align:center;padding:0 1rem">
          <div style="font-size:1.2rem;color:#e94560;font-weight:700">VS</div>
        </div>
        <div style="text-align:center">
          <div style="font-size:1.05rem;font-weight:700;color:#e2e8f0">{row['Tamu']}</div>
          <div style="color:#718096;font-size:.75rem">✈️ Tandang &nbsp;#{row['Pos A']}</div>
          <div style="margin-top:.25rem;font-size:.85rem">{row['Form A']}</div>
        </div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:.8rem">
        <div>
          <div style="display:flex;justify-content:space-between;margin-bottom:3px">
            <span style="color:#718096;font-size:.78rem">🏠 Home</span>
            <span style="color:#48bb78;font-weight:700;font-size:.85rem">{p_h}%</span>
          </div>{bar(p_h,"#48bb78")}
        </div>
        <div>
          <div style="display:flex;justify-content:space-between;margin-bottom:3px">
            <span style="color:#718096;font-size:.78rem">🤝 Draw</span>
            <span style="color:#ecc94b;font-weight:700;font-size:.85rem">{p_d}%</span>
          </div>{bar(p_d,"#ecc94b")}
        </div>
        <div>
          <div style="display:flex;justify-content:space-between;margin-bottom:3px">
            <span style="color:#718096;font-size:.78rem">✈️ Away</span>
            <span style="color:#fc8181;font-weight:700;font-size:.85rem">{p_a}%</span>
          </div>{bar(p_a,"#fc8181")}
        </div>
      </div>
      <div style="margin-top:.6rem;text-align:right;font-size:.78rem">
        <span style="color:#718096">Confidence: </span><span>{row['Confidence']}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT UTAMA
# ══════════════════════════════════════════════════════════════════════════════

# ── Baris tombol ──────────────────────────────────────────────────────────────
b1, b2, b3 = st.columns([1, 2, 1])
with b2:
    fetch_btn = st.button("🔍 Ambil & Analisis Semua Pertandingan", use_container_width=True)

st.markdown("---")

# ── Kotak Pencarian Klub ──────────────────────────────────────────────────────
st.markdown("""
<div class="search-box">
  <h3>🔎 Cari Klub Favorit</h3>
</div>
""", unsafe_allow_html=True)

search_col1, search_col2 = st.columns([3, 1])
with search_col1:
    club_search = st.text_input(
        "Nama klub",
        placeholder="Contoh: Persija, Real Madrid, Liverpool, Bayern...",
        label_visibility="collapsed"
    )
with search_col2:
    search_btn = st.button("🔍 Cari Klub", use_container_width=True)

# ── Proses Data ───────────────────────────────────────────────────────────────
def build_dataframe(api_key, selected_leagues, days_ahead):
    results = []
    if api_key and selected_leagues:
        for league_name in selected_leagues:
            info = ALL_LEAGUES.get(league_name, {})
            code = info.get("code","")
            if code not in SUPPORTED_CODES:
                continue
            matches = fetch_matches(api_key, code, days_ahead)
            stats   = fetch_team_stats(api_key, code)
            for m in matches:
                h_id = m["homeTeam"]["id"]; a_id = m["awayTeam"]["id"]
                hs = stats.get(h_id, {}); as_ = stats.get(a_id, {})
                p_h, p_d, p_a, rec, conf, best_p = calculate_probability(hs, as_)
                match_dt = m.get("utcDate","")[:16].replace("T"," ")
                tag = info.get("tag","tag-other"); region = info.get("region","")
                results.append({
                    "Liga": league_name, "Region": region, "Tag": tag,
                    "Tuan Rumah": m["homeTeam"]["name"],
                    "Tamu":       m["awayTeam"]["name"],
                    "Tanggal":    match_dt,
                    "P(Home)%": p_h, "P(Draw)%": p_d, "P(Away)%": p_a,
                    "Rekomendasi": rec, "Confidence": conf, "Best Prob%": best_p,
                    "Form H": form_icons(hs.get("form","")),
                    "Form A": form_icons(as_.get("form","")),
                    "Pos H": hs.get("position","-"), "Pos A": as_.get("position","-"),
                })
    if not results:
        results = get_demo_data()
    return pd.DataFrame(results)

# ── Trigger build ─────────────────────────────────────────────────────────────
if fetch_btn or "main_df" not in st.session_state:
    with st.spinner("⏳ Mengambil & menganalisis data pertandingan..."):
        df_all = build_dataframe(api_key, selected_leagues, days_ahead)
        st.session_state["main_df"] = df_all
        if not api_key or not selected_leagues:
            st.info("ℹ️ Menggunakan data demo. Masukkan API Key + pilih liga untuk data real-time.")
else:
    df_all = st.session_state["main_df"]

# ── Tampilkan hasil pencarian klub ────────────────────────────────────────────
if club_search or search_btn:
    query = club_search.strip().lower()
    if query:
        mask = (
            df_all["Tuan Rumah"].str.lower().str.contains(query, na=False) |
            df_all["Tamu"].str.lower().str.contains(query, na=False)
        )
        df_search = df_all[mask].copy()

        st.markdown(f"### 🔎 Hasil Pencarian: **{club_search}**")

        if df_search.empty:
            st.warning(f"❌ Klub '{club_search}' tidak ditemukan. Coba nama lain (misal: Persija, Real, Liverpool).")
        else:
            # Ringkasan klub
            for _, row in df_search.iterrows():
                is_home = query in row["Tuan Rumah"].lower()
                club_name = row["Tuan Rumah"] if is_home else row["Tamu"]
                lawan     = row["Tamu"] if is_home else row["Tuan Rumah"]
                posisi    = "Tuan Rumah 🏠" if is_home else "Tamu ✈️"
                prob_klub = row["P(Home)%"] if is_home else row["P(Away)%"]
                cls       = "prob-high" if prob_klub>=62 else ("prob-medium" if prob_klub>=48 else "prob-low")

                st.markdown(f"""
                <div class="club-result">
                  <div class="club-name">⚽ {club_name}</div>
                  <div class="club-sub">🏆 {row['Liga']} &nbsp;|&nbsp; 📅 {row['Tanggal']} &nbsp;|&nbsp; {posisi}</div>
                  <div style="margin-top:.8rem;display:flex;gap:2rem;flex-wrap:wrap">
                    <div>
                      <div style="color:#718096;font-size:.78rem">MELAWAN</div>
                      <div style="font-size:1rem;font-weight:600;color:#e2e8f0">{lawan}</div>
                    </div>
                    <div>
                      <div style="color:#718096;font-size:.78rem">PROBABILITAS MENANG</div>
                      <div class="{cls}" style="font-size:1.8rem">{prob_klub}%</div>
                    </div>
                    <div>
                      <div style="color:#718096;font-size:.78rem">REKOMENDASI</div>
                      <div style="font-size:1rem;font-weight:600;color:#e2e8f0">{row['Rekomendasi']}</div>
                    </div>
                    <div>
                      <div style="color:#718096;font-size:.78rem">CONFIDENCE</div>
                      <div style="font-size:1rem">{row['Confidence']}</div>
                    </div>
                    <div>
                      <div style="color:#718096;font-size:.78rem">FORM TERKINI</div>
                      <div style="font-size:.95rem">{row['Form H'] if is_home else row['Form A']}</div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("**Detail Pertandingan:**")
            for _, row in df_search.iterrows():
                render_match_card(row, highlight=True)

        st.markdown("---")

# ── Filter & Sort ─────────────────────────────────────────────────────────────
df_filtered = df_all[df_all["Best Prob%"] >= min_prob].copy()
sort_map = {
    "Probabilitas Tertinggi": ("Best Prob%", False),
    "Probabilitas Terendah":  ("Best Prob%", True),
    "Liga":                   ("Liga",       True),
    "Tanggal Pertandingan":   ("Tanggal",    True),
}
cs, asc = sort_map[sort_by]
df_filtered = df_filtered.sort_values(cs, ascending=asc).reset_index(drop=True)
df_filtered.index += 1

# ── Ringkasan Metrik ──────────────────────────────────────────────────────────
st.markdown("### 📊 Ringkasan")
m1, m2, m3, m4, m5 = st.columns(5)
cols_m = [m1, m2, m3, m4, m5]
vals = [
    (len(df_filtered), "Total Pertandingan", "#e94560"),
    (len(df_filtered[df_filtered["Best Prob%"]>=62]), "Confidence Tinggi (≥62%)", "#48bb78"),
    (len(df_filtered[(df_filtered["Best Prob%"]>=48)&(df_filtered["Best Prob%"]<62)]), "Confidence Sedang", "#ecc94b"),
    (len(df_filtered[df_filtered["Best Prob%"]<48]), "Confidence Rendah", "#fc8181"),
    (round(df_filtered["Best Prob%"].mean(),1) if len(df_filtered)>0 else 0, "Rata-rata Prob%", "#a78bfa"),
]
for col, (v, lbl, color) in zip(cols_m, vals):
    with col:
        st.markdown(f"""<div class="metric-card">
          <div class="val" style="color:{color}">{v}</div>
          <div class="lbl">{lbl}</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs utama ────────────────────────────────────────────────────────────────
st.markdown("### 🗂️ Daftar Pertandingan (Diurutkan)")
tab1, tab2, tab3 = st.tabs(["📋 Tabel Ringkas", "🔍 Analisis Detail", "🌏 Per Region"])

with tab1:
    display_df = df_filtered[[
        "Liga","Tuan Rumah","Tamu","Tanggal",
        "P(Home)%","P(Draw)%","P(Away)%","Rekomendasi","Confidence","Best Prob%"
    ]].copy()

    def color_prob(val):
        if val >= 62: return "color:#48bb78;font-weight:700"
        elif val >= 48: return "color:#ecc94b;font-weight:700"
        else: return "color:#fc8181;font-weight:700"

    def style_prob_cols(val):
        try: return color_prob(float(val))
        except: return ""

    try:
        styled = display_df.style\
            .map(style_prob_cols, subset=["P(Home)%","P(Draw)%","P(Away)%","Best Prob%"])\
            .set_properties(**{"background-color":"#1a1a2e","color":"#e2e8f0"})\
            .set_table_styles([{"selector":"th",
                "props":[("background-color","#0f3460"),("color","#fff"),("font-weight","700")]}])
    except AttributeError:
        styled = display_df.style\
            .applymap(style_prob_cols, subset=["P(Home)%","P(Draw)%","P(Away)%","Best Prob%"])\
            .set_properties(**{"background-color":"#1a1a2e","color":"#e2e8f0"})\
            .set_table_styles([{"selector":"th",
                "props":[("background-color","#0f3460"),("color","#fff"),("font-weight","700")]}])

    st.dataframe(styled, use_container_width=True, height=450)
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV",data=csv,
        file_name=f"parlay_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")

with tab2:
    if show_analysis:
        if df_filtered.empty:
            st.warning("Tidak ada data untuk filter saat ini.")
        else:
            for _, row in df_filtered.iterrows():
                render_match_card(row)
    else:
        st.info("Aktifkan 'Tampilkan kartu analisis detail' di sidebar.")

with tab3:
    regions_in_data = df_filtered["Region"].unique() if "Region" in df_filtered.columns else []
    for region in sorted(regions_in_data):
        df_reg = df_filtered[df_filtered["Region"]==region]
        if df_reg.empty: continue
        with st.expander(f"🌍 {region} — {len(df_reg)} pertandingan", expanded=(region=="Indonesia")):
            for _, row in df_reg.iterrows():
                render_match_card(row)

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer">
⚠️ <b>DISCLAIMER PENTING:</b>
Semua analisis berdasarkan statistik historis (klasemen, form, rata-rata gol) — bukan jaminan hasil.
Sepak bola mengandung banyak faktor tak terduga: cedera, kartu merah, cuaca, dan lainnya.
Gunakan sebagai <i>referensi tambahan saja</i>. Bertaruhlah secara bertanggung jawab dan sesuai kemampuan.
</div>
""", unsafe_allow_html=True)
