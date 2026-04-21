# ─────────────────────────────────────────────
# LIVE METAL PRICES - Dual Source
# Primary: Yahoo Finance (free, no API key)
# Fallback: Metals-API / LME via public endpoint
# ─────────────────────────────────────────────

USD_TO_SAR = 3.75  # ثابت (الريال مربوط بالدولار)


def fetch_from_yahoo():
    """Primary source: Yahoo Finance Futures."""
    try:
        copper = yf.Ticker("HG=F")       # COMEX Copper Futures (USD/lb)
        alum = yf.Ticker("ALI=F")        # CME Aluminium Futures (USD/ton)

        cu_data = copper.history(period="5d")
        al_data = alum.history(period="5d")

        if cu_data.empty or al_data.empty:
            return None

        # Copper: USD/lb → USD/ton (1 ton = 2204.62 lb)
        cu_now = float(cu_data["Close"].iloc[-1]) * 2204.62
        cu_prev = float(cu_data["Close"].iloc[-2]) * 2204.62 if len(cu_data) > 1 else cu_now

        # Aluminium: already USD/ton
        al_now = float(al_data["Close"].iloc[-1])
        al_prev = float(al_data["Close"].iloc[-2]) if len(al_data) > 1 else al_now

        return {
            "copper": {
                "price": cu_now,
                "change": ((cu_now - cu_prev) / cu_prev) * 100 if cu_prev else 0
            },
            "aluminium": {
                "price": al_now,
                "change": ((al_now - al_prev) / al_prev) * 100 if al_prev else 0
            },
            "source": "Yahoo Finance (COMEX/CME Futures)",
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    except Exception:
        return None


def fetch_from_lme_backup():
    """Fallback source: public metal prices API."""
    try:
        # Using a free public API (no key required)
        url = "https://api.metals.dev/v1/latest?api_key=demo&currency=USD&unit=toz"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return None

        data = response.json()
        metals = data.get("metals", {})

        # Prices in USD per troy ounce → convert to USD per ton
        # 1 metric ton = 32,150.7 troy ounces
        cu_toz = metals.get("copper", 0)
        al_toz = metals.get("aluminum", 0)

        if not cu_toz or not al_toz:
            return None

        cu_ton = cu_toz * 32150.7
        al_ton = al_toz * 32150.7

        return {
            "copper": {"price": cu_ton, "change": 0},
            "aluminium": {"price": al_ton, "change": 0},
            "source": "Metals-API (LME spot)",
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    except Exception:
        return None


def get_fallback_prices():
    """Last-resort static prices (approximate LME averages)."""
    return {
        "copper": {"price": 9200, "change": 0},
        "aluminium": {"price": 2400, "change": 0},
        "source": "⚠ Offline estimates (LME average)",
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_metal_prices():
    """Try Yahoo first, then LME, then static fallback."""
    prices = fetch_from_yahoo()
    if prices:
        return prices

    prices = fetch_from_lme_backup()
    if prices:
        return prices

    return get_fallback_prices()


def render_price_ticker():
    """Renders the live metal prices panel at the top of the app."""
    prices = get_metal_prices()

    # Custom CSS for the ticker
    st.markdown("""
        <style>
        .price-ticker {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0 20px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-left: 5px solid #CC0000;
        }
        .price-title {
            color: #ffffff !important;
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 2px;
            margin-bottom: 12px;
            opacity: 0.9;
        }
        .metal-card {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .metal-name {
            color: #ffffff !important;
            font-size: 13px;
            font-weight: 600;
            opacity: 0.8;
            letter-spacing: 1px;
        }
        .metal-price {
            color: #ffffff !important;
            font-size: 26px;
            font-weight: 700;
            margin: 6px 0;
        }
        .metal-change-up {
            color: #00ff88 !important;
            font-size: 14px;
            font-weight: 600;
        }
        .metal-change-down {
            color: #ff4466 !important;
            font-size: 14px;
            font-weight: 600;
        }
        .metal-sar {
            color: #ffcc44 !important;
            font-size: 12px;
            margin-top: 4px;
            opacity: 0.85;
        }
        .ticker-footer {
            color: #ffffff !important;
            font-size: 11px;
            opacity: 0.6;
            margin-top: 10px;
            text-align: right;
        }
        </style>
    """, unsafe_allow_html=True)

    cu = prices["copper"]
    al = prices["aluminium"]

    # Arrow + color based on change
    def arrow(change):
        if change > 0:
            return f'<span class="metal-change-up">▲ +{change:.2f}%</span>'
        elif change < 0:
            return f'<span class="metal-change-down">▼ {change:.2f}%</span>'
        else:
            return '<span class="metal-sar">— stable</span>'

    cu_sar = cu["price"] * USD_TO_SAR
    al_sar = al["price"] * USD_TO_SAR

    ticker_html = f"""
    <div class="price-ticker">
        <div class="price-title">💰 LIVE METAL PRICES — LME / COMEX</div>
        <table style="width:100%; border-collapse:collapse;">
            <tr>
                <td style="width:50%; padding:5px;">
                    <div class="metal-card">
                        <div class="metal-name">🟠 COPPER (Cu)</div>
                        <div class="metal-price">${cu['price']:,.0f}<span style="font-size:14px; opacity:0.7;"> /ton</span></div>
                        {arrow(cu['change'])}
                        <div class="metal-sar">≈ {cu_sar:,.0f} SAR/ton</div>
                    </div>
                </td>
                <td style="width:50%; padding:5px;">
                    <div class="metal-card">
                        <div class="metal-name">⚪ ALUMINIUM (Al)</div>
                        <div class="metal-price">${al['price']:,.0f}<span style="font-size:14px; opacity:0.7;"> /ton</span></div>
                        {arrow(al['change'])}
                        <div class="metal-sar">≈ {al_sar:,.0f} SAR/ton</div>
                    </div>
                </td>
            </tr>
        </table>
        <div class="ticker-footer">📡 {prices['source']} &nbsp;•&nbsp; 🕐 Updated: {prices['updated']}</div>
    </div>
    """

    st.markdown(ticker_html, unsafe_allow_html=True)


import streamlit as st
import google.generativeai as genai
import math
import os
import glob
import yfinance as yf
import requests
from datetime import datetime
from dataclasses import dataclass

# ─────────────────────────────────────────────
# 1. Page config — MUST be first Streamlit call
# ─────────────────────────────────────────────
st.set_page_config(page_title="Elsewedy Smart Tool", layout="wide")

st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .stApp [data-testid="stHeader"] { display: none; }
    .stApp { background-color: #F5F5F5; }
    .stApp, p, span, h1, h2, h3, h4, label, .stMarkdown, .stTextInput {
        color: #000000 !important;
    }
    * { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stDownloadButton button {
        background-color: #CC0000;
        color: white !important;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. API Key setup
# ─────────────────────────────────────────────
part1 = "AIzaSyD2J9a9RXLKjkC-"
part2 = "cw12JR7zxz3t7oVSA-Q"

model = None
try:
    genai.configure(api_key=part1 + part2)
    available_models = [
        m.name for m in genai.list_models()
        if "generateContent" in m.supported_generation_methods
    ]
    if available_models:
        model = genai.GenerativeModel(available_models[0])
except Exception as e:
    st.error(f"AI Configuration Error: {e}")

# ─────────────────────────────────────────────
# 3. Logo helper
# ─────────────────────────────────────────────
def display_logo(w):
    if os.path.exists("logo.png"):
        st.image("logo.png", width=w)
    else:
        st.markdown("###  Elsewedy Electric")

# ─────────────────────────────────────────────
# 4. CATALOG — Verified from Elsewedy PDF
#
#    Cu / XLPE / 3-core unarmoured  → page 88
#    Al / XLPE / 3-core unarmoured  → page 90
#    Cu / PVC  / 3-core SWA         → page 78
#    Al / PVC  / 3-core STA/SWA     → page 76 & 98
#
#    Columns used: ground (A) | duct (A) | air shaded (A)
# ─────────────────────────────────────────────

CATALOG = {
    "cu": {
        "xlpe": {
            # page 88 — 3-core Cu/XLPE/PVC unarmoured
            "air": [
                {"s": 1.5,  "Iz": 23},
                {"s": 2.5,  "Iz": 34},
                {"s": 4,    "Iz": 44},
                {"s": 6,    "Iz": 53},
                {"s": 10,   "Iz": 72},
                {"s": 16,   "Iz": 95},
                {"s": 25,   "Iz": 126},
                {"s": 35,   "Iz": 156},
                {"s": 50,   "Iz": 186},
                {"s": 70,   "Iz": 236},
                {"s": 95,   "Iz": 290},
                {"s": 120,  "Iz": 337},
                {"s": 150,  "Iz": 383},
                {"s": 185,  "Iz": 441},
                {"s": 240,  "Iz": 524},
                {"s": 300,  "Iz": 602},
            ],
            "ground": [
                {"s": 1.5,  "Iz": 31},
                {"s": 2.5,  "Iz": 42},
                {"s": 4,    "Iz": 54},
                {"s": 6,    "Iz": 68},
                {"s": 10,   "Iz": 89},
                {"s": 16,   "Iz": 116},
                {"s": 25,   "Iz": 153},
                {"s": 35,   "Iz": 184},
                {"s": 50,   "Iz": 220},
                {"s": 70,   "Iz": 270},
                {"s": 95,   "Iz": 324},
                {"s": 120,  "Iz": 368},
                {"s": 150,  "Iz": 410},
                {"s": 185,  "Iz": 464},
                {"s": 240,  "Iz": 537},
                {"s": 300,  "Iz": 605},
            ],
            "duct": [
                {"s": 1.5,  "Iz": 25},
                {"s": 2.5,  "Iz": 33},
                {"s": 4,    "Iz": 39},
                {"s": 6,    "Iz": 49},
                {"s": 10,   "Iz": 65},
                {"s": 16,   "Iz": 82},
                {"s": 25,   "Iz": 110},
                {"s": 35,   "Iz": 132},
                {"s": 50,   "Iz": 157},
                {"s": 70,   "Iz": 195},
                {"s": 95,   "Iz": 236},
                {"s": 120,  "Iz": 272},
                {"s": 150,  "Iz": 307},
                {"s": 185,  "Iz": 351},
                {"s": 240,  "Iz": 414},
                {"s": 300,  "Iz": 471},
            ],
        },
        "pvc": {
            # page 70 — 3-core Cu/PVC unarmoured (CORRECT SOURCE)
            "air": [
                {"s": 1.5,  "Iz": 20},
                {"s": 2.5,  "Iz": 24},
                {"s": 4,    "Iz": 34},
                {"s": 6,    "Iz": 43},
                {"s": 10,   "Iz": 59},
                {"s": 16,   "Iz": 80},
                {"s": 25,   "Iz": 102},
                {"s": 35,   "Iz": 125},
                {"s": 50,   "Iz": 151},
                {"s": 70,   "Iz": 191},
                {"s": 95,   "Iz": 235},
                {"s": 120,  "Iz": 270},
                {"s": 150,  "Iz": 310},
                {"s": 185,  "Iz": 357},
                {"s": 240,  "Iz": 423},
                {"s": 300,  "Iz": 486},
            ],
            "ground": [
                {"s": 1.5,  "Iz": 27},
                {"s": 2.5,  "Iz": 35},
                {"s": 4,    "Iz": 46},
                {"s": 6,    "Iz": 59},
                {"s": 10,   "Iz": 78},
                {"s": 16,   "Iz": 98},
                {"s": 25,   "Iz": 130},
                {"s": 35,   "Iz": 156},
                {"s": 50,   "Iz": 189},
                {"s": 70,   "Iz": 232},
                {"s": 95,   "Iz": 278},
                {"s": 120,  "Iz": 315},
                {"s": 150,  "Iz": 354},
                {"s": 185,  "Iz": 399},
                {"s": 240,  "Iz": 462},
                {"s": 300,  "Iz": 521},
            ],
            "duct": [
                {"s": 1.5,  "Iz": 21},
                {"s": 2.5,  "Iz": 27},
                {"s": 4,    "Iz": 36},
                {"s": 6,    "Iz": 43},
                {"s": 10,   "Iz": 57},
                {"s": 16,   "Iz": 71},
                {"s": 25,   "Iz": 94},
                {"s": 35,   "Iz": 114},
                {"s": 50,   "Iz": 136},
                {"s": 70,   "Iz": 169},
                {"s": 95,   "Iz": 205},
                {"s": 120,  "Iz": 234},
                {"s": 150,  "Iz": 266},
                {"s": 185,  "Iz": 303},
                {"s": 240,  "Iz": 357},
                {"s": 300,  "Iz": 406},
            ],
        },
    },
    "al": {
        "xlpe": {
            # page 90 — 3-core Al/XLPE/PVC unarmoured
            "air": [
                {"s": 16,  "Iz": 73},
                {"s": 25,  "Iz": 98},
                {"s": 35,  "Iz": 121},
                {"s": 50,  "Iz": 145},
                {"s": 70,  "Iz": 183},
                {"s": 95,  "Iz": 225},
                {"s": 120, "Iz": 262},
                {"s": 150, "Iz": 297},
                {"s": 185, "Iz": 344},
                {"s": 240, "Iz": 409},
                {"s": 300, "Iz": 471},
            ],
            "ground": [
                {"s": 16,  "Iz": 91},
                {"s": 25,  "Iz": 118},
                {"s": 35,  "Iz": 142},
                {"s": 50,  "Iz": 171},
                {"s": 70,  "Iz": 209},
                {"s": 95,  "Iz": 251},
                {"s": 120, "Iz": 286},
                {"s": 150, "Iz": 319},
                {"s": 185, "Iz": 361},
                {"s": 240, "Iz": 420},
                {"s": 300, "Iz": 474},
            ],
            "duct": [
                {"s": 16,  "Iz": 65},
                {"s": 25,  "Iz": 86},
                {"s": 35,  "Iz": 103},
                {"s": 50,  "Iz": 121},
                {"s": 70,  "Iz": 151},
                {"s": 95,  "Iz": 183},
                {"s": 120, "Iz": 211},
                {"s": 150, "Iz": 239},
                {"s": 185, "Iz": 274},
                {"s": 240, "Iz": 323},
                {"s": 300, "Iz": 369},
            ],
        },
        "pvc": {
            # page 72 — 3-core Al/PVC unarmoured (CORRECT SOURCE)
            "air": [
                {"s": 16,  "Iz": 59},
                {"s": 25,  "Iz": 79},
                {"s": 35,  "Iz": 97},
                {"s": 50,  "Iz": 117},
                {"s": 70,  "Iz": 148},
                {"s": 95,  "Iz": 182},
                {"s": 120, "Iz": 210},
                {"s": 150, "Iz": 241},
                {"s": 185, "Iz": 278},
                {"s": 240, "Iz": 331},
                {"s": 300, "Iz": 381},
            ],
            "ground": [
                {"s": 16,  "Iz": 78},
                {"s": 25,  "Iz": 101},
                {"s": 35,  "Iz": 121},
                {"s": 50,  "Iz": 147},
                {"s": 70,  "Iz": 180},
                {"s": 95,  "Iz": 216},
                {"s": 120, "Iz": 245},
                {"s": 150, "Iz": 275},
                {"s": 185, "Iz": 311},
                {"s": 240, "Iz": 362},
                {"s": 300, "Iz": 409},
            ],
            "duct": [
                {"s": 16,  "Iz": 56},
                {"s": 25,  "Iz": 73},
                {"s": 35,  "Iz": 89},
                {"s": 50,  "Iz": 106},
                {"s": 70,  "Iz": 131},
                {"s": 95,  "Iz": 159},
                {"s": 120, "Iz": 182},
                {"s": 150, "Iz": 206},
                {"s": 185, "Iz": 236},
                {"s": 240, "Iz": 279},
                {"s": 300, "Iz": 318},
            ],
        },
    },
}

# ─────────────────────────────────────────────
# 5. Derating Tables — Elsewedy Catalog
# ─────────────────────────────────────────────

# ── Table 3 — Air temp derating (base 30°C) — page 19
TEMP_DERATING_AIR = {
    "xlpe": {15:1.15, 20:1.10, 25:1.05, 30:1.00,
              35:0.95, 40:0.90, 45:0.84, 50:0.78, 55:0.72},
    "pvc":  {15:1.21, 20:1.15, 25:1.07, 30:1.00,
              35:0.92, 40:0.84, 45:0.75, 50:0.66, 55:0.55},
}
# ── Table 4 — Ground temp derating (base 20°C) — page 19
TEMP_DERATING_GROUND = {
    "xlpe": {15:1.04, 20:1.00, 25:0.96, 30:0.93,
              35:0.89, 40:0.85, 45:0.80, 50:0.76, 55:0.71},
    "pvc":  {15:1.05, 20:1.00, 25:0.95, 30:0.89,
              35:0.84, 40:0.77, 45:0.71, 50:0.63, 55:0.55},
}
# ── Table 9 — Grouping multicore in ground (trefoil touching) — page 21
GROUP_DERATING_GROUND = {1:1.00, 2:0.81, 3:0.69, 4:0.62, 5:0.58, 6:0.54}
# ── Table 10 — Grouping multicore in air (1 tray, touching) — page 21
GROUP_DERATING_AIR    = {1:1.00, 2:0.88, 3:0.82, 4:0.79, 5:0.76, 6:0.73}
# ── Table 6 — Soil thermal resistivity — page 20
SOIL_THERMAL_DIRECT = {0.8:1.05, 0.9:1.03, 1.0:1.00, 1.2:0.92, 1.5:0.83, 2.0:0.73, 2.5:0.66, 3.0:0.60}
SOIL_THERMAL_DUCT   = {0.8:1.03, 0.9:1.02, 1.0:1.00, 1.2:0.95, 1.5:0.89, 2.0:0.81, 2.5:0.75, 3.0:0.70}
# ── Table 5 — Burial depth derating (3-core) — page 20
DEPTH_DIRECT_MAP  = {0.5:1.00, 0.6:0.99, 0.8:0.96, 1.0:0.94, 1.25:0.92, 1.5:0.91}
DEPTH_DUCT_MAP    = {0.5:1.00, 0.6:0.99, 0.8:0.97, 1.0:0.96, 1.25:0.94, 1.5:0.93}

RESISTANCE = {
    "cu": {1.5:12.10, 2.5:7.41, 4:4.61, 6:3.08, 10:1.83, 16:1.15,
           25:0.727, 35:0.524, 50:0.387, 70:0.268, 95:0.193,
           120:0.153, 150:0.124, 185:0.0991, 240:0.0754, 300:0.0601},
    "al": {16:1.91, 25:1.20, 35:0.868, 50:0.641, 70:0.443, 95:0.320,
           120:0.253, 150:0.206, 185:0.164, 240:0.125, 300:0.100},
}
REACTANCE_DEFAULT = 0.08

# ─────────────────────────────────────────────
# SINGLE CORE CATALOG — Elsewedy LV 0.6/1 kV
# Cu/XLPE unarmoured → page 82
# Al/XLPE ATA armoured → page 85
# Columns: ground (Trefoil) | duct | air (Trefoil Touched)
# ─────────────────────────────────────────────
SC_CATALOG = {
    "cu": {
        "xlpe": {
            "ground": [
                {"s":4,"Iz":60},{"s":6,"Iz":77},{"s":10,"Iz":105},
                {"s":16,"Iz":131},{"s":25,"Iz":168},{"s":35,"Iz":201},
                {"s":50,"Iz":239},{"s":70,"Iz":292},{"s":95,"Iz":349},
                {"s":120,"Iz":397},{"s":150,"Iz":445},{"s":185,"Iz":503},
                {"s":240,"Iz":583},{"s":300,"Iz":658},{"s":400,"Iz":744},
                {"s":500,"Iz":840},{"s":630,"Iz":942},{"s":800,"Iz":1042},
                {"s":1000,"Iz":1142},
            ],
            "duct": [
                {"s":4,"Iz":42},{"s":6,"Iz":56},{"s":10,"Iz":72},
                {"s":16,"Iz":92},{"s":25,"Iz":118},{"s":35,"Iz":143},
                {"s":50,"Iz":172},{"s":70,"Iz":214},{"s":95,"Iz":259},
                {"s":120,"Iz":298},{"s":150,"Iz":339},{"s":185,"Iz":390},
                {"s":240,"Iz":457},{"s":300,"Iz":524},{"s":400,"Iz":603},
                {"s":500,"Iz":695},{"s":630,"Iz":794},{"s":800,"Iz":894},
                {"s":1000,"Iz":999},
            ],
            "air": [
                {"s":4,"Iz":44},{"s":6,"Iz":59},{"s":10,"Iz":75},
                {"s":16,"Iz":105},{"s":25,"Iz":138},{"s":35,"Iz":166},
                {"s":50,"Iz":210},{"s":70,"Iz":268},{"s":95,"Iz":321},
                {"s":120,"Iz":375},{"s":150,"Iz":446},{"s":185,"Iz":519},
                {"s":240,"Iz":622},{"s":300,"Iz":722},{"s":400,"Iz":842},
                {"s":500,"Iz":981},{"s":630,"Iz":1132},{"s":800,"Iz":1291},
                {"s":1000,"Iz":1473},
            ],
        },
    },
    "al": {
        "xlpe": {
            "ground": [
                {"s":16,"Iz":103},{"s":25,"Iz":132},{"s":35,"Iz":158},
                {"s":50,"Iz":187},{"s":70,"Iz":228},{"s":95,"Iz":273},
                {"s":120,"Iz":310},{"s":150,"Iz":347},{"s":185,"Iz":394},
                {"s":240,"Iz":456},{"s":300,"Iz":515},{"s":400,"Iz":588},
                {"s":500,"Iz":670},{"s":630,"Iz":759},{"s":800,"Iz":852},
                {"s":1000,"Iz":944},
            ],
            "duct": [
                {"s":16,"Iz":76},{"s":25,"Iz":98},{"s":35,"Iz":117},
                {"s":50,"Iz":140},{"s":70,"Iz":174},{"s":95,"Iz":209},
                {"s":120,"Iz":240},{"s":150,"Iz":273},{"s":185,"Iz":313},
                {"s":240,"Iz":368},{"s":300,"Iz":419},{"s":400,"Iz":488},
                {"s":500,"Iz":563},{"s":630,"Iz":648},{"s":800,"Iz":743},
                {"s":1000,"Iz":838},
            ],
            "air": [
                {"s":16,"Iz":90},{"s":25,"Iz":120},{"s":35,"Iz":146},
                {"s":50,"Iz":177},{"s":70,"Iz":223},{"s":95,"Iz":272},
                {"s":120,"Iz":316},{"s":150,"Iz":362},{"s":185,"Iz":419},
                {"s":240,"Iz":498},{"s":300,"Iz":577},{"s":400,"Iz":675},
                {"s":500,"Iz":788},{"s":630,"Iz":913},{"s":800,"Iz":1052},
                {"s":1000,"Iz":1200},
            ],
        },
    },
}

# Extended resistance for large single core sizes (IEC 60228)
RESISTANCE_SC = {
    "cu": {**{1.5:12.10,2.5:7.41,4:4.61,6:3.08,10:1.83,16:1.15,
              25:0.727,35:0.524,50:0.387,70:0.268,95:0.193,120:0.153,
              150:0.124,185:0.0991,240:0.0754,300:0.0601},
           400:0.0470,500:0.0366,630:0.0283,800:0.0221,1000:0.0176},
    "al": {**{16:1.91,25:1.20,35:0.868,50:0.641,70:0.443,95:0.320,
              120:0.253,150:0.206,185:0.164,240:0.125,300:0.100},
           400:0.0778,500:0.0605,630:0.0469,800:0.0367,1000:0.0291},
}

# ── Short Circuit k-factors — IEC 60364-5-54 / Elsewedy Table 13
SC_K = {"cu": {"xlpe": 143, "pvc": 115}, "al": {"xlpe": 94, "pvc": 76}}

# ── Temperature coefficient — IEC 60228
ALPHA = {"cu": 0.00393, "al": 0.00403}

# ── Insulation max operating temperature
THETA_OP = {"xlpe": 90, "pvc": 70}

# ── Grouping derating — Table 10 air, by (formation, spacing, num_cables)
# formation: "trefoil" or "flat" | spacing: "touching","150mm","300mm"
GROUP_AIR_DETAIL = {
    ("trefoil", "touching"): {1:1.00,2:0.88,3:0.82,4:0.79,5:0.76,6:0.73},
    ("trefoil", "150mm"):    {1:1.00,2:0.90,3:0.85,4:0.82,5:0.80,6:0.79},
    ("trefoil", "300mm"):    {1:1.00,2:0.95,3:0.92,4:0.90,5:0.89,6:0.88},
    ("flat",    "touching"): {1:1.00,2:0.87,3:0.80,4:0.77,5:0.73,6:0.68},
    ("flat",    "150mm"):    {1:1.00,2:0.89,3:0.83,4:0.80,5:0.78,6:0.76},
    ("flat",    "300mm"):    {1:1.00,2:0.93,3:0.90,4:0.88,5:0.87,6:0.86},
}
# Table 9 ground — trefoil touching (conservative, standard for buried)
GROUP_GROUND_DETAIL = {1:1.00,2:0.81,3:0.69,4:0.62,5:0.58,6:0.54}


# ─────────────────────────────────────────────
# 6. Dataclass & Calculation
# ─────────────────────────────────────────────

@dataclass
class CableResult:
    size_mm2: float
    catalog_iz: float
    full_load_current: float
    temp_derating: float
    group_derating: float
    soil_thermal_derating: float
    depth_derating: float
    effective_capacity: float
    utilisation_pct: float
    voltage_drop_v: float
    voltage_drop_pct: float
    r_ac_ohm_km: float
    vdrop_ok: bool
    sc_size_mm2: float
    sc_governed: bool
    warnings: list


def get_temp_derating(insulation, temp_c, installation):
    """Use Table 3 (air) or Table 4 (ground/duct) per Elsewedy catalog page 19."""
    tables = TEMP_DERATING_GROUND if installation in ["ground", "duct"] else TEMP_DERATING_AIR
    table  = tables[insulation]
    if temp_c in table:
        return table[temp_c]
    temps = sorted(table.keys())
    for i in range(len(temps) - 1):
        t1, t2 = temps[i], temps[i + 1]
        if t1 <= temp_c <= t2:
            return table[t1] + (table[t2] - table[t1]) * (temp_c - t1) / (t2 - t1)
    return table[temps[-1]]


def ac_resistance(conductor, insulation, size_mm2):
    """
    AC resistance at operating temperature — IEC 60228 + temperature correction.
    R_ac = R_dc20 × [1 + α × (θ_op − 20)]
    Skin & proximity effects negligible for LV multicore.
    """
    R_dc20 = RESISTANCE[conductor].get(size_mm2, 0.16)
    alpha  = ALPHA[conductor]
    theta  = THETA_OP[insulation]
    return R_dc20 * (1 + alpha * (theta - 20))


def select_cable(load_kw, voltage_v, phases, pf, length_m,
                 temp_c, conductor, insulation, installation,
                 max_vdrop_pct, num_cables, soil_thermal, burial_depth,
                 formation, spacing, isc_ka, trip_time_s):

    warnings = []
    sinpf = math.sqrt(max(0, 1 - pf ** 2))

    # ── Full load current ──────────────────────────────────────
    if phases == 3:
        IFL = (load_kw * 1000) / (math.sqrt(3) * voltage_v * pf)
    else:
        IFL = (load_kw * 1000) / (voltage_v * pf)

    # ── Derating factors ───────────────────────────────────────
    t_derate  = get_temp_derating(insulation, temp_c, installation)

    # Point 4 — formation-aware grouping derating
    if installation in ["ground", "duct"]:
        g_derate = GROUP_GROUND_DETAIL.get(num_cables, 0.54)
    else:
        key      = (formation, spacing)
        g_table  = GROUP_AIR_DETAIL.get(key, GROUP_AIR_DETAIL[("trefoil","touching")])
        g_derate = g_table.get(num_cables, 0.73)

    st_derate = 1.0
    d_derate  = 1.0
    if installation in ["ground", "duct"]:
        soil_map  = SOIL_THERMAL_DUCT if installation == "duct" else SOIL_THERMAL_DIRECT
        st_derate = soil_map.get(soil_thermal, 1.0)
        depth_map = DEPTH_DUCT_MAP if installation == "duct" else DEPTH_DIRECT_MAP
        d_derate  = depth_map.get(burial_depth, 1.0)

    total_derate = t_derate * g_derate * st_derate * d_derate
    I_required   = IFL / total_derate

    # ── Short circuit minimum size — IEC 60364-5-54 ───────────
    # Point 5: S_min = (Isc × √t) / k
    k          = SC_K[conductor][insulation]
    sc_size_min = (isc_ka * 1000 * math.sqrt(trip_time_s)) / k
    # round up to next standard size
    std_sizes  = [c["s"] for c in CATALOG[conductor][insulation][installation]]
    sc_size_mm2 = next((s for s in std_sizes if s >= sc_size_min), std_sizes[-1])

    # ── Select from catalog by ampacity ───────────────────────
    table  = CATALOG[conductor][insulation][installation]
    chosen = next((c for c in table if c["Iz"] >= I_required), None)
    if chosen is None:
        chosen = table[-1]
        warnings.append(
            f"Load ({I_required:.1f} A required) exceeds max catalog size "
            f"({table[-1]['Iz']} A). Consider parallel cables."
        )

    # ── Voltage drop using AC resistance at operating temp ────
    # Point 1: use R_ac not R_dc20
    def vdrop(size):
        R_ac = ac_resistance(conductor, insulation, size)
        L    = length_m / 1000
        imp  = R_ac * pf + REACTANCE_DEFAULT * sinpf
        vd   = (math.sqrt(3) if phases == 3 else 2) * IFL * imp * L
        return vd, (vd / voltage_v) * 100

    vd_v, vd_pct = vdrop(chosen["s"])

    if vd_pct > max_vdrop_pct:
        for cable in table:
            if cable["Iz"] >= I_required:
                _, cand_pct = vdrop(cable["s"])
                if cand_pct <= max_vdrop_pct:
                    chosen = cable
                    break
        vd_v, vd_pct = vdrop(chosen["s"])
        if vd_pct > max_vdrop_pct:
            warnings.append(
                f"Voltage drop ({vd_pct:.2f}%) still exceeds {max_vdrop_pct}%. "
                "Consider splitting the circuit or reducing cable length."
            )

    # ── Apply SC minimum — upsize if needed ───────────────────
    sc_governed = False
    if sc_size_mm2 > chosen["s"]:
        sc_governed = True
        sc_cable = next((c for c in table if c["s"] >= sc_size_mm2), table[-1])
        warnings.append(
            f"Cable upsized from {chosen['s']} mm² to {sc_cable['s']} mm² "
            f"due to short circuit requirement "
            f"(Isc={isc_ka} kA, t={trip_time_s}s → min {sc_size_min:.1f} mm²)."
        )
        chosen = sc_cable
        vd_v, vd_pct = vdrop(chosen["s"])

    # ── Final values ───────────────────────────────────────────
    eff_cap  = chosen["Iz"] * total_derate
    util     = (IFL / eff_cap * 100) if eff_cap > 0 else 0
    r_ac_fin = ac_resistance(conductor, insulation, chosen["s"])

    if util > 100:
        warnings.append(f"Cable utilisation {util:.1f}% exceeds rated capacity.")

    # Point 2 — cumulative VD note (always shown in results)
    warnings.append(
        f"NOTE: This VD ({vd_pct:.2f}%) covers this cable only. "
        "Ensure total VD from source to load does not exceed 5% (IEC 60364)."
    )

    return CableResult(
        size_mm2=chosen["s"],
        catalog_iz=chosen["Iz"],
        full_load_current=round(IFL, 2),
        temp_derating=round(t_derate, 3),
        group_derating=round(g_derate, 3),
        soil_thermal_derating=round(st_derate, 3),
        depth_derating=round(d_derate, 3),
        effective_capacity=round(eff_cap, 2),
        utilisation_pct=round(util, 1),
        voltage_drop_v=round(vd_v, 3),
        voltage_drop_pct=round(vd_pct, 3),
        r_ac_ohm_km=round(r_ac_fin, 4),
        vdrop_ok=vd_pct <= max_vdrop_pct,
        sc_size_mm2=round(sc_size_min, 1),
        sc_governed=sc_governed,
        warnings=warnings,
    )



def select_single_core(load_kw, voltage_v, phases, pf, length_m,
                       temp_c, conductor, insulation, installation,
                       max_vdrop_pct, num_cables,
                       soil_thermal, burial_depth,
                       isc_ka, trip_time_s):
    """
    Single core cable selection.
    Iz values: ground=trefoil, duct=duct, air=trefoil touched.
    Grouping derating: Table 8 (single core in ground) or Table 10 (air).
    """
    warnings = []
    sinpf = math.sqrt(max(0, 1 - pf**2))

    # Full load current
    if phases == 3:
        IFL = (load_kw * 1000) / (math.sqrt(3) * voltage_v * pf)
    else:
        IFL = (load_kw * 1000) / (voltage_v * pf)

    # Temperature derating — same tables as multicore
    t_derate = get_temp_derating(insulation, temp_c, installation)

    # Grouping — Table 8 for single core in ground (trefoil touching)
    # Table 10 for single core in air (same as multicore touching)
    TABLE8_GROUND = {1:1.00,2:0.87,3:0.76,4:0.72,5:0.67,6:0.64}
    TABLE10_AIR   = {1:1.00,2:0.88,3:0.82,4:0.79,5:0.76,6:0.73}
    g_table = TABLE10_AIR if installation == "air" else TABLE8_GROUND
    g_derate = g_table.get(num_cables, 0.60)

    # Soil & depth derating — same as multicore
    st_derate = 1.0
    d_derate  = 1.0
    if installation in ["ground", "duct"]:
        soil_map  = SOIL_THERMAL_DUCT if installation == "duct" else SOIL_THERMAL_DIRECT
        st_derate = soil_map.get(soil_thermal, 1.0)
        depth_map = DEPTH_DUCT_MAP if installation == "duct" else DEPTH_DIRECT_MAP
        d_derate  = depth_map.get(burial_depth, 1.0)

    total_derate = t_derate * g_derate * st_derate * d_derate
    I_required   = IFL / total_derate

    # Catalog: single core is always XLPE (insulation locked in UI)

    table  = SC_CATALOG[conductor]["xlpe"][installation]
    chosen = next((c for c in table if c["Iz"] >= I_required), None)
    if chosen is None:
        chosen = table[-1]
        warnings.append(
            f"Load ({I_required:.1f} A) exceeds max catalog size "
            f"({table[-1]['s']} mm² = {table[-1]['Iz']} A). Consider parallel single cores."
        )

    # AC resistance at operating temp
    R_dc = RESISTANCE_SC[conductor].get(chosen["s"], 0.05)
    alpha = ALPHA[conductor]
    theta = THETA_OP["xlpe"]  # single core in catalog is always XLPE
    R_ac  = R_dc * (1 + alpha * (theta - 20))

    # Voltage drop
    def vdrop(R):
        L   = length_m / 1000
        imp = R * pf + REACTANCE_DEFAULT * sinpf
        vd  = (math.sqrt(3) if phases == 3 else 2) * IFL * imp * L
        return vd, (vd / voltage_v) * 100

    vd_v, vd_pct = vdrop(R_ac)

    if vd_pct > max_vdrop_pct:
        for cable in table:
            if cable["Iz"] >= I_required:
                R2 = RESISTANCE_SC[conductor].get(cable["s"], 0.05)
                R2_ac = R2 * (1 + alpha * (theta - 20))
                _, cand_pct = vdrop(R2_ac)
                if cand_pct <= max_vdrop_pct:
                    chosen = cable
                    R_ac   = R2_ac
                    break
        vd_v, vd_pct = vdrop(R_ac)
        if vd_pct > max_vdrop_pct:
            warnings.append(
                f"Voltage drop ({vd_pct:.2f}%) still exceeds {max_vdrop_pct}%. "
                "Consider parallel cables or reducing length."
            )

    # Short circuit check
    k = SC_K[conductor]["xlpe"]
    sc_size_min = (isc_ka * 1000 * math.sqrt(trip_time_s)) / k
    sc_governed = False
    if sc_size_min > chosen["s"]:
        sc_governed = True
        sc_cable = next((c for c in table if c["s"] >= sc_size_min), table[-1])
        warnings.append(
            f"Cable upsized from {chosen['s']} mm² to {sc_cable['s']} mm² "
            f"due to SC requirement (min {sc_size_min:.1f} mm²)."
        )
        chosen = sc_cable
        R_ac   = RESISTANCE_SC[conductor].get(chosen["s"], 0.05) * (1 + alpha * (theta - 20))
        vd_v, vd_pct = vdrop(R_ac)

    eff_cap = chosen["Iz"] * total_derate
    util    = (IFL / eff_cap * 100) if eff_cap > 0 else 0

    warnings.append(
        f"NOTE: This VD ({vd_pct:.2f}%) covers this cable only. "
        "Ensure total VD from source to load does not exceed 5% (IEC 60364)."
    )

    return CableResult(
        size_mm2=chosen["s"],
        catalog_iz=chosen["Iz"],
        full_load_current=round(IFL, 2),
        temp_derating=round(t_derate, 3),
        group_derating=round(g_derate, 3),
        soil_thermal_derating=round(st_derate, 3),
        depth_derating=round(d_derate, 3),
        effective_capacity=round(eff_cap, 2),
        utilisation_pct=round(util, 1),
        voltage_drop_v=round(vd_v, 3),
        voltage_drop_pct=round(vd_pct, 3),
        r_ac_ohm_km=round(R_ac, 4),
        vdrop_ok=vd_pct <= max_vdrop_pct,
        sc_size_mm2=round(sc_size_min, 1),
        sc_governed=sc_governed,
        warnings=warnings,
    )


# ─────────────────────────────────────────────
# 7. Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    display_logo(150)
    st.markdown("### 👤 Senior Prescription Engineer")
    st.markdown("**Eng. Mohamed Tarek**  \n📞 +966570514091  \n📧 Mohamed.abdelwahab@elsewedy.com")
    st.markdown("---")
    st.subheader("📥 Downloads")

    # الكتالوج الرئيسي
    pdf_path = "EE KSA Brochure.pdf"
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            st.download_button(
                "📄 EE KSA Brochure",
                f,
                file_name="Elsewedy_KSA_Brochure.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="main_brochure"
            )

    # الكتالوجات الإضافية (قراءة تلقائية)
    catalogs_folder = "catalogs"
    if os.path.exists(catalogs_folder):
        pdf_files = sorted(glob.glob(os.path.join(catalogs_folder, "*.pdf")))
        if pdf_files:
            st.markdown("---")
            st.markdown("**📚 Product Catalogs**")
            for pdf_file in pdf_files:
                file_name = os.path.basename(pdf_file)
                display_name = file_name.replace(".pdf", "").replace("_", " ").replace("-", " ")
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        f"📑 {display_name}",
                        f,
                        file_name=file_name,
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"cat_{file_name}"
                    )

# ─────────────────────────────────────────────
# 8. Main UI
# ─────────────────────────────────────────────
display_logo(200)
st.title(" Elsewedy Electric Smart Tool")

# ─── Live Metal Prices Ticker ───
render_price_ticker()

st.markdown("---")

tab1, tab2 = st.tabs(["🔌 Cable Size Calculator", "🤖 Technical Support"])

    # ── Cable type selector ───────────────────────────────────────────────
    cable_type = st.radio(
        "Cable type",
        ["multicore", "single_core"],
        format_func=lambda x: "Multicore (3-core / 4-core)" if x=="multicore" else "Single Core (1×mm²)",
        horizontal=True,
    )
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Load Data**")
        load_kw   = st.number_input("Load (kW)", min_value=0.1, value=50.0, step=0.5)
        voltage_v = st.selectbox("System Voltage", [220, 230, 380, 400], index=1)
        if cable_type == "multicore":
            neutral = st.radio("Neutral conductor required?", [True, False],
                               format_func=lambda x: "Yes — 4-core" if x else "No — 3-core",
                               horizontal=True,
                               help="4-core = same Iz as 3-core. Selection only affects the cable label.")
        else:
            neutral = False  # single core — neutral is a separate cable if needed
        phases    = st.radio("System Type", [3, 1],
                             format_func=lambda x: "Three Phase (3Ø)" if x == 3 else "Single Phase (1Ø)")
        pf        = st.slider("Power Factor (cosφ)", 0.5, 1.0, 0.85, 0.01)

    with col2:
        st.markdown("**Cable & Installation**")
        length_m     = st.number_input("Cable Length (m)", min_value=1.0, value=100.0, step=5.0)
        temp_c       = st.selectbox("Ambient Temperature (°C)",
                                     [25, 30, 35, 40, 45, 50, 55], index=3,
                                     help="Saudi default: 40°C")
        conductor    = st.selectbox("Conductor Material", ["cu", "al"],
                                     format_func=lambda x: "Copper (Cu)" if x == "cu" else "Aluminium (Al)")
        if cable_type == "single_core":
            insulation = "xlpe"
            st.selectbox("Insulation Type", ["XLPE (90°C)"],
                         disabled=True,
                         help="Single core LV cables are XLPE only in the Elsewedy catalog.")
        else:
            insulation = st.selectbox("Insulation Type", ["xlpe", "pvc"],
                                      format_func=lambda x: "XLPE (90°C)" if x == "xlpe" else "PVC (70°C)")
        installation = st.selectbox("Installation Method",
                                     ["air", "ground", "duct"],
                                     format_func=lambda x: {
                                         "air":    "In air / Cable tray",
                                         "ground": "Direct buried",
                                         "duct":   "In underground duct"}[x])

    soil_thermal = 1.2
    burial_depth = 0.8
    if installation in ["ground", "duct"]:
        st.markdown("---")
        st.markdown("**Soil & Burial Conditions**")
        sc1, sc2 = st.columns(2)
        with sc1:
            soil_thermal = st.selectbox(
                "Soil Thermal Resistivity (K.m/W)",
                options=list(SOIL_THERMAL_DIRECT.keys()), index=2,
                help="Wet soil ≈ 0.8 | Normal ≈ 1.2 | Dry sandy ≈ 2.5")
        with sc2:
            burial_depth = st.selectbox(
                "Depth of Laying (m)",
                options=list(DEPTH_DIRECT_MAP.keys()), index=2)

    st.markdown("---")
    st.markdown("**Grouping & Protection**")
    gc1, gc2, gc3 = st.columns(3)
    with gc1:
        max_vdrop  = st.selectbox("Max Voltage Drop (%)", [3.0, 5.0], index=1)
    with gc2:
        num_cables = st.selectbox("Number of cables (grouping)", [1,2,3,4,5,6], index=0)
    with gc3:
        formation  = st.selectbox("Cable formation",
                                   ["trefoil", "flat"],
                                   format_func=lambda x: "Trefoil" if x=="trefoil" else "Flat",
                                   disabled=(num_cables == 1))

    spacing = "touching"
    if num_cables > 1 and installation == "air":
        spacing = st.selectbox("Cable spacing",
                                ["touching", "150mm", "300mm"],
                                format_func=lambda x: {"touching":"Touching","150mm":"Spaced 150 mm","300mm":"Spaced 300 mm"}[x])

    st.markdown("---")
    st.markdown("**Short Circuit Data**")
    sc1, sc2 = st.columns(2)
    with sc1:
        isc_ka      = st.number_input("Fault level at cable origin (kA)",
                                       min_value=0.1, value=10.0, step=0.5,
                                       help="Short circuit current at the source end of this cable")
    with sc2:
        trip_time_s = st.selectbox("Protection trip time (s)",
                                    [0.1, 0.2, 0.4, 0.5, 1.0, 2.0, 3.0],
                                    index=0,
                                    help="Clearing time of upstream breaker or fuse")

    if st.button(" Calculate Cable Size", use_container_width=True):
        try:
            if cable_type == "single_core":
                res = select_single_core(
                    load_kw, voltage_v, phases, pf, length_m,
                    temp_c, conductor, insulation, installation,
                    max_vdrop, num_cables, soil_thermal, burial_depth,
                    isc_ka, trip_time_s
                )
            else:
                res = select_cable(
                    load_kw, voltage_v, phases, pf, length_m,
                    temp_c, conductor, insulation, installation,
                    max_vdrop, num_cables, soil_thermal, burial_depth,
                    formation, spacing, isc_ka, trip_time_s
                )

            st.markdown("---")
            st.markdown("### Results")

            cond_label = "Cu" if conductor == "cu" else "Al"
            ins_label  = insulation.upper()

            col_a, col_b, col_c = st.columns(3)
            if cable_type == "single_core":
                cores_label = "single core"
                cable_desig = f"1×{res.size_mm2} mm²  {cond_label}/XLPE"
            else:
                cores_label = "4-core" if neutral else "3-core"
                cable_desig = f"{res.size_mm2} mm²  {cond_label}/{ins_label}/{cores_label}"
            col_a.metric("Recommended Size",
                         f"1×{res.size_mm2} mm²" if cable_type=="single_core" else f"{res.size_mm2} mm²",
                         cable_desig)
            col_b.metric("Full Load Current", f"{res.full_load_current} A",
                         f"Iz catalog = {res.catalog_iz} A")
            col_c.metric("Voltage Drop",      f"{res.voltage_drop_pct}%",
                         f"Limit {max_vdrop}% — {'✓ OK' if res.vdrop_ok else '✗ FAIL'}")

            show_soil = installation in ["ground", "duct"]

            # ── SC badge
            sc_label = f"SC min = {res.sc_size_mm2} mm²"
            if res.sc_governed:
                st.error(f" Cable upsized by Short Circuit requirement — {sc_label}")
            else:
                st.info(f"✓ Short circuit check passed — {sc_label}  (selected {res.size_mm2} mm² ≥ required)")

            st.markdown("**Calculation Details**")
            details = {
                "Full load current":        f"{res.full_load_current} A",
                "AC resistance at op. temp":f"{res.r_ac_ohm_km} Ω/km  (used for VD calc — IEC 60228)",
                "Temp derating factor":     f"× {res.temp_derating}  (at {temp_c}°C — Table {'4' if show_soil else '3'})",
                "Group derating factor":    f"× {res.group_derating}  ({num_cables} cable(s), {formation}, {spacing})",
                "Soil thermal derating":    f"× {res.soil_thermal_derating}  (Table 6)" if show_soil else "N/A",
                "Burial depth derating":    f"× {res.depth_derating}  (Table 5)" if show_soil else "N/A",
                "Effective cable capacity": f"{res.effective_capacity} A",
                "Cable utilisation":        f"{res.utilisation_pct}%",
                "Voltage drop":             f"{res.voltage_drop_v} V  ({res.voltage_drop_pct}%)",
                "SC withstand (min size)":  f"{res.sc_size_mm2} mm²  (Isc={isc_ka} kA, t={trip_time_s}s, k={SC_K[conductor][insulation]})",
                "Cable designation":         cable_desig + "  0.6/1 kV",
                "Catalog reference":         ("Single core — IEC 60502 p.82/85" if cable_type=="single_core" else f"{cores_label} multicore — IEC 60502 / IEC 60287"),
            }
            for k, v in details.items():
                c1, c2 = st.columns([2, 3])
                c1.markdown(f"<span style='color:#666'>{k}</span>", unsafe_allow_html=True)
                c2.markdown(f"**{v}**")

            # ── Separate notes from real warnings ─────────────────────────
            notes         = [w for w in res.warnings if w.startswith("NOTE:")]
            warnings_only = [w for w in res.warnings if not w.startswith("NOTE:")]

            if warnings_only:
                for w in warnings_only:
                    st.warning(f"⚠ {w}")
            else:
                st.success("✓ Cable selection is within all limits.")

            for n in notes:
                st.info(f"ℹ {n}")

            # ── Smart warnings for large sections ─────────────────────────
            if res.size_mm2 >= 185:
                st.warning(
                    f"⚠ Large section selected ({res.size_mm2} mm²). Consider the following:\n\n"
                    f"**Option A — Parallel multicore:** Run 2× {int(res.size_mm2/2)} mm² cables "
                    f"(easier to handle, terminate and replace).\n\n"
                    f"**Option B — Single core:** Higher Iz per cable but requires careful "
                    f"formation control (trefoil mandatory above 95 mm²). "
                    f"Verify against Elsewedy single-core tables — "
                    f"{'page 82–83' if insulation=='xlpe' else 'page 78–79'} in the catalog."
                )
            elif res.size_mm2 >= 95:
                st.info(
                    f"ℹ Section {res.size_mm2} mm² — single-core cables are available as an "
                    f"alternative if installation space is a constraint. "
                    f"Iz for single-core {res.size_mm2} mm² {ins_label} in air (trefoil) is higher "
                    f"than multicore — see Elsewedy catalog for comparison."
                )

        except Exception as e:
            st.error(f"Calculation error: {e}")

with tab2:
    st.subheader("🤖 AI Technical Support")
    query = st.text_input("Ask about cables, standards, or specifications:",
                          placeholder="e.g. What is the current rating of 4×16mm² XLPE cable?")
    if query:
        if model is None:
            st.error("AI model not available. Check your API key.")
        else:
            with st.spinner("AI is thinking..."):
                try:
                    response = model.generate_content(query)
                    st.markdown("### 🤖 Answer:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"AI Error: {e}")
        st.markdown("---")
        st.markdown("#### For more information, please contact:")
        st.success("**Eng. Mohamed Tarek**  \n📞 +966570514091  \n📧 Mohamed.abdelwahab@elsewedy.com")

# ─────────────────────────────────────────────
# 9. Footer
# ─────────────────────────────────────────────
st.markdown("---")
st.caption("© 2026 Developed by Eng. Mohamed Tarek | Elsewedy Electric KSA")
