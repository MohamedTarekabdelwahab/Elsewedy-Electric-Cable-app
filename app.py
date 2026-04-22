import streamlit as st
import google.generativeai as genai
import math
import os
import glob
import requests
from datetime import datetime
from dataclasses import dataclass

# ─────────────────────────────────────────────
# 1. Page config
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
# LIVE METAL PRICES - Stooq + Fallback
# ─────────────────────────────────────────────
USD_TO_SAR = 3.75


def fetch_from_stooq():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        cu_url = "https://stooq.com/q/l/?s=hg.f&f=sd2t2ohlcv&h&e=csv"
        cu_resp = requests.get(cu_url, headers=headers, timeout=10)
        al_url = "https://stooq.com/q/l/?s=ali.f&f=sd2t2ohlcv&h&e=csv"
        al_resp = requests.get(al_url, headers=headers, timeout=10)

        if cu_resp.status_code != 200 or al_resp.status_code != 200:
            return None

        cu_lines = cu_resp.text.strip().split('\n')
        al_lines = al_resp.text.strip().split('\n')

        if len(cu_lines) < 2 or len(al_lines) < 2:
            return None

        cu_fields = cu_lines[1].split(',')
        al_fields = al_lines[1].split(',')

        cu_close = float(cu_fields[6])
        al_close = float(al_fields[6])

        cu_ton = cu_close * 2204.62
        al_ton = al_close * 2204.62

        if cu_ton < 5000 or cu_ton > 20000:
            return None
        if al_ton < 1500 or al_ton > 6000:
            return None

        return {
            "copper": {"price": cu_ton, "change": 0},
            "aluminium": {"price": al_ton, "change": 0},
            "source": "Stooq.com (COMEX Futures)",
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    except Exception:
        return None


def get_fallback_prices():
    return {
        "copper": {"price": 12660, "change": 0},
        "aluminium": {"price": 3570, "change": 0},
        "source": "LME reference (April 2026 avg)",
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


@st.cache_data(ttl=1800)
def get_metal_prices():
    prices = fetch_from_stooq()
    if prices:
        return prices
    return get_fallback_prices()


def render_price_ticker():
    prices = get_metal_prices()
    st.markdown("""
        <style>
        .price-ticker { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 12px; padding: 20px; margin: 10px 0 20px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 5px solid #CC0000; }
        .price-title { color: #ffffff !important; font-size: 14px; font-weight: 600; letter-spacing: 2px; margin-bottom: 12px; opacity: 0.9; }
        .metal-card { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1); }
        .metal-name { color: #ffffff !important; font-size: 13px; font-weight: 600; opacity: 0.8; letter-spacing: 1px; }
        .metal-price { color: #ffffff !important; font-size: 26px; font-weight: 700; margin: 6px 0; }
        .metal-sar { color: #ffcc44 !important; font-size: 12px; margin-top: 4px; opacity: 0.85; }
        .ticker-footer { color: #ffffff !important; font-size: 11px; opacity: 0.6; margin-top: 10px; text-align: right; }
        </style>
    """, unsafe_allow_html=True)

    cu = prices["copper"]
    al = prices["aluminium"]
    cu_sar = cu["price"] * USD_TO_SAR
    al_sar = al["price"] * USD_TO_SAR

    ticker_html = f"""
    <div class="price-ticker">
        <div class="price-title">LIVE METAL PRICES &mdash; LME / COMEX</div>
        <table style="width:100%; border-collapse:collapse;">
            <tr>
                <td style="width:50%; padding:5px;">
                    <div class="metal-card">
                        <div class="metal-name">COPPER (Cu)</div>
                        <div class="metal-price">${cu['price']:,.0f}<span style="font-size:14px; opacity:0.7;"> /ton</span></div>
                        <div class="metal-sar">&asymp; {cu_sar:,.0f} SAR/ton</div>
                    </div>
                </td>
                <td style="width:50%; padding:5px;">
                    <div class="metal-card">
                        <div class="metal-name">ALUMINIUM (Al)</div>
                        <div class="metal-price">${al['price']:,.0f}<span style="font-size:14px; opacity:0.7;"> /ton</span></div>
                        <div class="metal-sar">&asymp; {al_sar:,.0f} SAR/ton</div>
                    </div>
                </td>
            </tr>
        </table>
        <div class="ticker-footer">{prices['source']} &bull; Updated: {prices['updated']}</div>
    </div>
    """
    st.markdown(ticker_html, unsafe_allow_html=True)


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


def display_logo(w):
    if os.path.exists("logo.png"):
        st.image("logo.png", width=w)
    else:
        st.markdown("### Elsewedy Electric")


# ─────────────────────────────────────────────
# 4. CATALOG
# ─────────────────────────────────────────────
CATALOG = {
    "cu": {
        "xlpe": {
            "air": [
                {"s": 1.5, "Iz": 23}, {"s": 2.5, "Iz": 34}, {"s": 4, "Iz": 44},
                {"s": 6, "Iz": 53}, {"s": 10, "Iz": 72}, {"s": 16, "Iz": 95},
                {"s": 25, "Iz": 126}, {"s": 35, "Iz": 156}, {"s": 50, "Iz": 186},
                {"s": 70, "Iz": 236}, {"s": 95, "Iz": 290}, {"s": 120, "Iz": 337},
                {"s": 150, "Iz": 383}, {"s": 185, "Iz": 441}, {"s": 240, "Iz": 524},
                {"s": 300, "Iz": 602},
            ],
            "ground": [
                {"s": 1.5, "Iz": 31}, {"s": 2.5, "Iz": 42}, {"s": 4, "Iz": 54},
                {"s": 6, "Iz": 68}, {"s": 10, "Iz": 89}, {"s": 16, "Iz": 116},
                {"s": 25, "Iz": 153}, {"s": 35, "Iz": 184}, {"s": 50, "Iz": 220},
                {"s": 70, "Iz": 270}, {"s": 95, "Iz": 324}, {"s": 120, "Iz": 368},
                {"s": 150, "Iz": 410}, {"s": 185, "Iz": 464}, {"s": 240, "Iz": 537},
                {"s": 300, "Iz": 605},
            ],
            "duct": [
                {"s": 1.5, "Iz": 25}, {"s": 2.5, "Iz": 33}, {"s": 4, "Iz": 39},
                {"s": 6, "Iz": 49}, {"s": 10, "Iz": 65}, {"s": 16, "Iz": 82},
                {"s": 25, "Iz": 110}, {"s": 35, "Iz": 132}, {"s": 50, "Iz": 157},
                {"s": 70, "Iz": 195}, {"s": 95, "Iz": 236}, {"s": 120, "Iz": 272},
                {"s": 150, "Iz": 307}, {"s": 185, "Iz": 351}, {"s": 240, "Iz": 414},
                {"s": 300, "Iz": 471},
            ],
        },
        "pvc": {
            "air": [
                {"s": 1.5, "Iz": 20}, {"s": 2.5, "Iz": 24}, {"s": 4, "Iz": 34},
                {"s": 6, "Iz": 43}, {"s": 10, "Iz": 59}, {"s": 16, "Iz": 80},
                {"s": 25, "Iz": 102}, {"s": 35, "Iz": 125}, {"s": 50, "Iz": 151},
                {"s": 70, "Iz": 191}, {"s": 95, "Iz": 235}, {"s": 120, "Iz": 270},
                {"s": 150, "Iz": 310}, {"s": 185, "Iz": 357}, {"s": 240, "Iz": 423},
                {"s": 300, "Iz": 486},
            ],
            "ground": [
                {"s": 1.5, "Iz": 27}, {"s": 2.5, "Iz": 35}, {"s": 4, "Iz": 46},
                {"s": 6, "Iz": 59}, {"s": 10, "Iz": 78}, {"s": 16, "Iz": 98},
                {"s": 25, "Iz": 130}, {"s": 35, "Iz": 156}, {"s": 50, "Iz": 189},
                {"s": 70, "Iz": 232}, {"s": 95, "Iz": 278}, {"s": 120, "Iz": 315},
                {"s": 150, "Iz": 354}, {"s": 185, "Iz": 399}, {"s": 240, "Iz": 462},
                {"s": 300, "Iz": 521},
            ],
            "duct": [
                {"s": 1.5, "Iz": 21}, {"s": 2.5, "Iz": 27}, {"s": 4, "Iz": 36},
                {"s": 6, "Iz": 43}, {"s": 10, "Iz": 57}, {"s": 16, "Iz": 71},
                {"s": 25, "Iz": 94}, {"s": 35, "Iz": 114}, {"s": 50, "Iz": 136},
                {"s": 70, "Iz": 169}, {"s": 95, "Iz": 205}, {"s": 120, "Iz": 234},
                {"s": 150, "Iz": 266}, {"s": 185, "Iz": 303}, {"s": 240, "Iz": 357},
                {"s": 300, "Iz": 406},
            ],
        },
    },
    "al": {
        "xlpe": {
            "air": [
                {"s": 16, "Iz": 73}, {"s": 25, "Iz": 98}, {"s": 35, "Iz": 121},
                {"s": 50, "Iz": 145}, {"s": 70, "Iz": 183}, {"s": 95, "Iz": 225},
                {"s": 120, "Iz": 262}, {"s": 150, "Iz": 297}, {"s": 185, "Iz": 344},
                {"s": 240, "Iz": 409}, {"s": 300, "Iz": 471},
            ],
            "ground": [
                {"s": 16, "Iz": 91}, {"s": 25, "Iz": 118}, {"s": 35, "Iz": 142},
                {"s": 50, "Iz": 171}, {"s": 70, "Iz": 209}, {"s": 95, "Iz": 251},
                {"s": 120, "Iz": 286}, {"s": 150, "Iz": 319}, {"s": 185, "Iz": 361},
                {"s": 240, "Iz": 420}, {"s": 300, "Iz": 474},
            ],
            "duct": [
                {"s": 16, "Iz": 65}, {"s": 25, "Iz": 86}, {"s": 35, "Iz": 103},
                {"s": 50, "Iz": 121}, {"s": 70, "Iz": 151}, {"s": 95, "Iz": 183},
                {"s": 120, "Iz": 211}, {"s": 150, "Iz": 239}, {"s": 185, "Iz": 274},
                {"s": 240, "Iz": 323}, {"s": 300, "Iz": 369},
            ],
        },
        "pvc": {
            "air": [
                {"s": 16, "Iz": 59}, {"s": 25, "Iz": 79}, {"s": 35, "Iz": 97},
                {"s": 50, "Iz": 117}, {"s": 70, "Iz": 148}, {"s": 95, "Iz": 182},
                {"s": 120, "Iz": 210}, {"s": 150, "Iz": 241}, {"s": 185, "Iz": 278},
                {"s": 240, "Iz": 331}, {"s": 300, "Iz": 381},
            ],
            "ground": [
                {"s": 16, "Iz": 78}, {"s": 25, "Iz": 101}, {"s": 35, "Iz": 121},
                {"s": 50, "Iz": 147}, {"s": 70, "Iz": 180}, {"s": 95, "Iz": 216},
                {"s": 120, "Iz": 245}, {"s": 150, "Iz": 275}, {"s": 185, "Iz": 311},
                {"s": 240, "Iz": 362}, {"s": 300, "Iz": 409},
            ],
            "duct": [
                {"s": 16, "Iz": 56}, {"s": 25, "Iz": 73}, {"s": 35, "Iz": 89},
                {"s": 50, "Iz": 106}, {"s": 70, "Iz": 131}, {"s": 95, "Iz": 159},
                {"s": 120, "Iz": 182}, {"s": 150, "Iz": 206}, {"s": 185, "Iz": 236},
                {"s": 240, "Iz": 279}, {"s": 300, "Iz": 318},
            ],
        },
    },
}

TEMP_DERATING_AIR = {
    "xlpe": {15: 1.15, 20: 1.10, 25: 1.05, 30: 1.00, 35: 0.95, 40: 0.90, 45: 0.84, 50: 0.78, 55: 0.72},
    "pvc": {15: 1.21, 20: 1.15, 25: 1.07, 30: 1.00, 35: 0.92, 40: 0.84, 45: 0.75, 50: 0.66, 55: 0.55},
}
TEMP_DERATING_GROUND = {
    "xlpe": {15: 1.04, 20: 1.00, 25: 0.96, 30: 0.93, 35: 0.89, 40: 0.85, 45: 0.80, 50: 0.76, 55: 0.71},
    "pvc": {15: 1.05, 20: 1.00, 25: 0.95, 30: 0.89, 35: 0.84, 40: 0.77, 45: 0.71, 50: 0.63, 55: 0.55},
}
SOIL_THERMAL_DIRECT = {0.8: 1.05, 0.9: 1.03, 1.0: 1.00, 1.2: 0.92, 1.5: 0.83, 2.0: 0.73, 2.5: 0.66, 3.0: 0.60}
SOIL_THERMAL_DUCT = {0.8: 1.03, 0.9: 1.02, 1.0: 1.00, 1.2: 0.95, 1.5: 0.89, 2.0: 0.81, 2.5: 0.75, 3.0: 0.70}
DEPTH_DIRECT_MAP = {0.5: 1.00, 0.6: 0.99, 0.8: 0.96, 1.0: 0.94, 1.25: 0.92, 1.5: 0.91}
DEPTH_DUCT_MAP = {0.5: 1.00, 0.6: 0.99, 0.8: 0.97, 1.0: 0.96, 1.25: 0.94, 1.5: 0.93}

RESISTANCE = {
    "cu": {1.5: 12.10, 2.5: 7.41, 4: 4.61, 6: 3.08, 10: 1.83, 16: 1.15,
           25: 0.727, 35: 0.524, 50: 0.387, 70: 0.268, 95: 0.193,
           120: 0.153, 150: 0.124, 185: 0.0991, 240: 0.0754, 300: 0.0601},
    "al": {16: 1.91, 25: 1.20, 35: 0.868, 50: 0.641, 70: 0.443, 95: 0.320,
           120: 0.253, 150: 0.206, 185: 0.164, 240: 0.125, 300: 0.100},
}
REACTANCE_DEFAULT = 0.08

SC_CATALOG = {
    "cu": {
        "xlpe": {
            "ground": [
                {"s": 4, "Iz": 60}, {"s": 6, "Iz": 77}, {"s": 10, "Iz": 105},
                {"s": 16, "Iz": 131}, {"s": 25, "Iz": 168}, {"s": 35, "Iz": 201},
                {"s": 50, "Iz": 239}, {"s": 70, "Iz": 292}, {"s": 95, "Iz": 349},
                {"s": 120, "Iz": 397}, {"s": 150, "Iz": 445}, {"s": 185, "Iz": 503},
                {"s": 240, "Iz": 583}, {"s": 300, "Iz": 658}, {"s": 400, "Iz": 744},
                {"s": 500, "Iz": 840}, {"s": 630, "Iz": 942}, {"s": 800, "Iz": 1042},
                {"s": 1000, "Iz": 1142},
            ],
            "duct": [
                {"s": 4, "Iz": 42}, {"s": 6, "Iz": 56}, {"s": 10, "Iz": 72},
                {"s": 16, "Iz": 92}, {"s": 25, "Iz": 118}, {"s": 35, "Iz": 143},
                {"s": 50, "Iz": 172}, {"s": 70, "Iz": 214}, {"s": 95, "Iz": 259},
                {"s": 120, "Iz": 298}, {"s": 150, "Iz": 339}, {"s": 185, "Iz": 390},
                {"s": 240, "Iz": 457}, {"s": 300, "Iz": 524}, {"s": 400, "Iz": 603},
                {"s": 500, "Iz": 695}, {"s": 630, "Iz": 794}, {"s": 800, "Iz": 894},
                {"s": 1000, "Iz": 999},
            ],
            "air": [
                {"s": 4, "Iz": 44}, {"s": 6, "Iz": 59}, {"s": 10, "Iz": 75},
                {"s": 16, "Iz": 105}, {"s": 25, "Iz": 138}, {"s": 35, "Iz": 166},
                {"s": 50, "Iz": 210}, {"s": 70, "Iz": 268}, {"s": 95, "Iz": 321},
                {"s": 120, "Iz": 375}, {"s": 150, "Iz": 446}, {"s": 185, "Iz": 519},
                {"s": 240, "Iz": 622}, {"s": 300, "Iz": 722}, {"s": 400, "Iz": 842},
                {"s": 500, "Iz": 981}, {"s": 630, "Iz": 1132}, {"s": 800, "Iz": 1291},
                {"s": 1000, "Iz": 1473},
            ],
        },
    },
    "al": {
        "xlpe": {
            "ground": [
                {"s": 16, "Iz": 103}, {"s": 25, "Iz": 132}, {"s": 35, "Iz": 158},
                {"s": 50, "Iz": 187}, {"s": 70, "Iz": 228}, {"s": 95, "Iz": 273},
                {"s": 120, "Iz": 310}, {"s": 150, "Iz": 347}, {"s": 185, "Iz": 394},
                {"s": 240, "Iz": 456}, {"s": 300, "Iz": 515}, {"s": 400, "Iz": 588},
                {"s": 500, "Iz": 670}, {"s": 630, "Iz": 759}, {"s": 800, "Iz": 852},
                {"s": 1000, "Iz": 944},
            ],
            "duct": [
                {"s": 16, "Iz": 76}, {"s": 25, "Iz": 98}, {"s": 35, "Iz": 117},
                {"s": 50, "Iz": 140}, {"s": 70, "Iz": 174}, {"s": 95, "Iz": 209},
                {"s": 120, "Iz": 240}, {"s": 150, "Iz": 273}, {"s": 185, "Iz": 313},
                {"s": 240, "Iz": 368}, {"s": 300, "Iz": 419}, {"s": 400, "Iz": 488},
                {"s": 500, "Iz": 563}, {"s": 630, "Iz": 648}, {"s": 800, "Iz": 743},
                {"s": 1000, "Iz": 838},
            ],
            "air": [
                {"s": 16, "Iz": 90}, {"s": 25, "Iz": 120}, {"s": 35, "Iz": 146},
                {"s": 50, "Iz": 177}, {"s": 70, "Iz": 223}, {"s": 95, "Iz": 272},
                {"s": 120, "Iz": 316}, {"s": 150, "Iz": 362}, {"s": 185, "Iz": 419},
                {"s": 240, "Iz": 498}, {"s": 300, "Iz": 577}, {"s": 400, "Iz": 675},
                {"s": 500, "Iz": 788}, {"s": 630, "Iz": 913}, {"s": 800, "Iz": 1052},
                {"s": 1000, "Iz": 1200},
            ],
        },
    },
}

RESISTANCE_SC = {
    "cu": {**{1.5: 12.10, 2.5: 7.41, 4: 4.61, 6: 3.08, 10: 1.83, 16: 1.15,
              25: 0.727, 35: 0.524, 50: 0.387, 70: 0.268, 95: 0.193, 120: 0.153,
              150: 0.124, 185: 0.0991, 240: 0.0754, 300: 0.0601},
           400: 0.0470, 500: 0.0366, 630: 0.0283, 800: 0.0221, 1000: 0.0176},
    "al": {**{16: 1.91, 25: 1.20, 35: 0.868, 50: 0.641, 70: 0.443, 95: 0.320,
              120: 0.253, 150: 0.206, 185: 0.164, 240: 0.125, 300: 0.100},
           400: 0.0778, 500: 0.0605, 630: 0.0469, 800: 0.0367, 1000: 0.0291},
}

SC_K = {"cu": {"xlpe": 143, "pvc": 115}, "al": {"xlpe": 94, "pvc": 76}}
ALPHA = {"cu": 0.00393, "al": 0.00403}
THETA_OP = {"xlpe": 90, "pvc": 70}

GROUP_AIR_DETAIL = {
    ("trefoil", "touching"): {1: 1.00, 2: 0.88, 3: 0.82, 4: 0.79, 5: 0.76, 6: 0.73},
    ("trefoil", "150mm"): {1: 1.00, 2: 0.90, 3: 0.85, 4: 0.82, 5: 0.80, 6: 0.79},
    ("trefoil", "300mm"): {1: 1.00, 2: 0.95, 3: 0.92, 4: 0.90, 5: 0.89, 6: 0.88},
    ("flat", "touching"): {1: 1.00, 2: 0.87, 3: 0.80, 4: 0.77, 5: 0.73, 6: 0.68},
    ("flat", "150mm"): {1: 1.00, 2: 0.89, 3: 0.83, 4: 0.80, 5: 0.78, 6: 0.76},
    ("flat", "300mm"): {1: 1.00, 2: 0.93, 3: 0.90, 4: 0.88, 5: 0.87, 6: 0.86},
}
GROUP_GROUND_DETAIL = {1: 1.00, 2: 0.81, 3: 0.69, 4: 0.62, 5: 0.58, 6: 0.54}


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
    tables = TEMP_DERATING_GROUND if installation in ["ground", "duct"] else TEMP_DERATING_AIR
    table = tables[insulation]
    if temp_c in table:
        return table[temp_c]
    temps = sorted(table.keys())
    for i in range(len(temps) - 1):
        t1, t2 = temps[i], temps[i + 1]
        if t1 <= temp_c <= t2:
            return table[t1] + (table[t2] - table[t1]) * (temp_c - t1) / (t2 - t1)
    return table[temps[-1]]


def ac_resistance(conductor, insulation, size_mm2):
    R_dc20 = RESISTANCE[conductor].get(size_mm2, 0.16)
    alpha = ALPHA[conductor]
    theta = THETA_OP[insulation]
    return R_dc20 * (1 + alpha * (theta - 20))


def select_cable(load_kw, voltage_v, phases, pf, length_m,
                 temp_c, conductor, insulation, installation,
                 max_vdrop_pct, num_cables, soil_thermal, burial_depth,
                 formation, spacing, isc_ka, trip_time_s):
    warnings = []
    sinpf = math.sqrt(max(0, 1 - pf ** 2))
    if phases == 3:
        IFL = (load_kw * 1000) / (math.sqrt(3) * voltage_v * pf)
    else:
        IFL = (load_kw * 1000) / (voltage_v * pf)

    t_derate = get_temp_derating(insulation, temp_c, installation)
    if installation in ["ground", "duct"]:
        g_derate = GROUP_GROUND_DETAIL.get(num_cables, 0.54)
    else:
        key = (formation, spacing)
        g_table = GROUP_AIR_DETAIL.get(key, GROUP_AIR_DETAIL[("trefoil", "touching")])
        g_derate = g_table.get(num_cables, 0.73)

    st_derate = 1.0
    d_derate = 1.0
    if installation in ["ground", "duct"]:
        soil_map = SOIL_THERMAL_DUCT if installation == "duct" else SOIL_THERMAL_DIRECT
        st_derate = soil_map.get(soil_thermal, 1.0)
        depth_map = DEPTH_DUCT_MAP if installation == "duct" else DEPTH_DIRECT_MAP
        d_derate = depth_map.get(burial_depth, 1.0)

    total_derate = t_derate * g_derate * st_derate * d_derate
    I_required = IFL / total_derate

    k = SC_K[conductor][insulation]
    sc_size_min = (isc_ka * 1000 * math.sqrt(trip_time_s)) / k
    std_sizes = [c["s"] for c in CATALOG[conductor][insulation][installation]]
    sc_size_mm2 = next((s for s in std_sizes if s >= sc_size_min), std_sizes[-1])

    table = CATALOG[conductor][insulation][installation]
    chosen = next((c for c in table if c["Iz"] >= I_required), None)
    if chosen is None:
        chosen = table[-1]
        warnings.append(f"Load ({I_required:.1f} A required) exceeds max catalog size.")

    def vdrop(size):
        R_ac = ac_resistance(conductor, insulation, size)
        L = length_m / 1000
        imp = R_ac * pf + REACTANCE_DEFAULT * sinpf
        vd = (math.sqrt(3) if phases == 3 else 2) * IFL * imp * L
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
            warnings.append(f"Voltage drop ({vd_pct:.2f}%) still exceeds {max_vdrop_pct}%.")

    sc_governed = False
    if sc_size_mm2 > chosen["s"]:
        sc_governed = True
        sc_cable = next((c for c in table if c["s"] >= sc_size_mm2), table[-1])
        warnings.append(f"Cable upsized from {chosen['s']} mm2 to {sc_cable['s']} mm2 due to SC.")
        chosen = sc_cable
        vd_v, vd_pct = vdrop(chosen["s"])

    eff_cap = chosen["Iz"] * total_derate
    util = (IFL / eff_cap * 100) if eff_cap > 0 else 0
    r_ac_fin = ac_resistance(conductor, insulation, chosen["s"])

    if util > 100:
        warnings.append(f"Cable utilisation {util:.1f}% exceeds rated capacity.")

    warnings.append(f"NOTE: This VD ({vd_pct:.2f}%) covers this cable only. Ensure total VD < 5%.")

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
    warnings = []
    sinpf = math.sqrt(max(0, 1 - pf ** 2))
    if phases == 3:
        IFL = (load_kw * 1000) / (math.sqrt(3) * voltage_v * pf)
    else:
        IFL = (load_kw * 1000) / (voltage_v * pf)

    t_derate = get_temp_derating(insulation, temp_c, installation)
    TABLE8_GROUND = {1: 1.00, 2: 0.87, 3: 0.76, 4: 0.72, 5: 0.67, 6: 0.64}
    TABLE10_AIR = {1: 1.00, 2: 0.88, 3: 0.82, 4: 0.79, 5: 0.76, 6: 0.73}
    g_table = TABLE10_AIR if installation == "air" else TABLE8_GROUND
    g_derate = g_table.get(num_cables, 0.60)

    st_derate = 1.0
    d_derate = 1.0
    if installation in ["ground", "duct"]:
        soil_map = SOIL_THERMAL_DUCT if installation == "duct" else SOIL_THERMAL_DIRECT
        st_derate = soil_map.get(soil_thermal, 1.0)
        depth_map = DEPTH_DUCT_MAP if installation == "duct" else DEPTH_DIRECT_MAP
        d_derate = depth_map.get(burial_depth, 1.0)

    total_derate = t_derate * g_derate * st_derate * d_derate
    I_required = IFL / total_derate

    table = SC_CATALOG[conductor]["xlpe"][installation]
    chosen = next((c for c in table if c["Iz"] >= I_required), None)
    if chosen is None:
        chosen = table[-1]
        warnings.append(f"Load ({I_required:.1f} A) exceeds max size.")

    R_dc = RESISTANCE_SC[conductor].get(chosen["s"], 0.05)
    alpha = ALPHA[conductor]
    theta = THETA_OP["xlpe"]
    R_ac = R_dc * (1 + alpha * (theta - 20))

    def vdrop(R):
        L = length_m / 1000
        imp = R * pf + REACTANCE_DEFAULT * sinpf
        vd = (math.sqrt(3) if phases == 3 else 2) * IFL * imp * L
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
                    R_ac = R2_ac
                    break
        vd_v, vd_pct = vdrop(R_ac)

    k = SC_K[conductor]["xlpe"]
    sc_size_min = (isc_ka * 1000 * math.sqrt(trip_time_s)) / k
    sc_governed = False
    if sc_size_min > chosen["s"]:
        sc_governed = True
        sc_cable = next((c for c in table if c["s"] >= sc_size_min), table[-1])
        chosen = sc_cable
        R_ac = RESISTANCE_SC[conductor].get(chosen["s"], 0.05) * (1 + alpha * (theta - 20))
        vd_v, vd_pct = vdrop(R_ac)

    eff_cap = chosen["Iz"] * total_derate
    util = (IFL / eff_cap * 100) if eff_cap > 0 else 0

    warnings.append(f"NOTE: This VD ({vd_pct:.2f}%) covers this cable only. Ensure total VD < 5%.")

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
    st.markdown("### Senior Prescription Engineer")
    st.markdown("**Eng. Mohamed Tarek**  \n+966570514091  \nMohamed.abdelwahab@elsewedy.com")
    st.markdown("---")
    st.subheader("Downloads")

    pdf_path = "EE KSA Brochure.pdf"
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            st.download_button(
                "EE KSA Brochure",
                f,
                file_name="Elsewedy_KSA_Brochure.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="main_brochure"
            )

    catalogs_folder = "catalogs"
    if os.path.exists(catalogs_folder):
        pdf_files = sorted(glob.glob(os.path.join(catalogs_folder, "*.pdf")))
        if pdf_files:
            st.markdown("---")
            st.markdown("**Product Catalogs**")
            for pdf_file in pdf_files:
                file_name = os.path.basename(pdf_file)
                display_name = file_name.replace(".pdf", "").replace("_", " ").replace("-", " ")
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        display_name,
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
st.title("Elsewedy Electric Smart Tool")

render_price_ticker()

st.markdown("---")

tab1, tab_vf, tab_conduit, tab2 = st.tabs([
    "Cable Size Calculator",
    "Price Variance (VF)",
    "Conduit Fill",
    "Technical Support"
])

with tab1:
    st.subheader("Cable Size Selection - Elsewedy Catalog (IEC 60502)")

    cable_type = st.radio(
        "Cable type",
        ["multicore", "single_core"],
        format_func=lambda x: "Multicore (3-core / 4-core)" if x == "multicore" else "Single Core (1xmm2)",
        horizontal=True,
    )
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Load Data**")
        load_kw = st.number_input("Load (kW)", min_value=0.1, value=50.0, step=0.5)
        voltage_v = st.selectbox("System Voltage", [220, 230, 380, 400], index=1)
        if cable_type == "multicore":
            neutral = st.radio("Neutral conductor required?", [True, False],
                               format_func=lambda x: "Yes - 4-core" if x else "No - 3-core",
                               horizontal=True)
        else:
            neutral = False
        phases = st.radio("System Type", [3, 1],
                          format_func=lambda x: "Three Phase (3Ph)" if x == 3 else "Single Phase (1Ph)")
        pf = st.slider("Power Factor (cos phi)", 0.5, 1.0, 0.85, 0.01)

    with col2:
        st.markdown("**Cable & Installation**")
        length_m = st.number_input("Cable Length (m)", min_value=1.0, value=100.0, step=5.0)
        temp_c = st.selectbox("Ambient Temperature (C)", [25, 30, 35, 40, 45, 50, 55], index=3)
        conductor = st.selectbox("Conductor Material", ["cu", "al"],
                                 format_func=lambda x: "Copper (Cu)" if x == "cu" else "Aluminium (Al)")
        if cable_type == "single_core":
            insulation = "xlpe"
            st.selectbox("Insulation Type", ["XLPE (90C)"], disabled=True)
        else:
            insulation = st.selectbox("Insulation Type", ["xlpe", "pvc"],
                                      format_func=lambda x: "XLPE (90C)" if x == "xlpe" else "PVC (70C)")
        installation = st.selectbox("Installation Method",
                                    ["air", "ground", "duct"],
                                    format_func=lambda x: {"air": "In air / Cable tray",
                                                           "ground": "Direct buried",
                                                           "duct": "In underground duct"}[x])

    soil_thermal = 1.2
    burial_depth = 0.8
    if installation in ["ground", "duct"]:
        st.markdown("---")
        st.markdown("**Soil & Burial Conditions**")
        sc1, sc2 = st.columns(2)
        with sc1:
            soil_thermal = st.selectbox("Soil Thermal Resistivity (K.m/W)",
                                        options=list(SOIL_THERMAL_DIRECT.keys()), index=2)
        with sc2:
            burial_depth = st.selectbox("Depth of Laying (m)",
                                        options=list(DEPTH_DIRECT_MAP.keys()), index=2)

    st.markdown("---")
    st.markdown("**Grouping & Protection**")
    gc1, gc2, gc3 = st.columns(3)
    with gc1:
        max_vdrop = st.selectbox("Max Voltage Drop (%)", [3.0, 5.0], index=1)
    with gc2:
        num_cables = st.selectbox("Number of cables (grouping)", [1, 2, 3, 4, 5, 6], index=0)
    with gc3:
        formation = st.selectbox("Cable formation", ["trefoil", "flat"],
                                 format_func=lambda x: "Trefoil" if x == "trefoil" else "Flat",
                                 disabled=(num_cables == 1))

    spacing = "touching"
    if num_cables > 1 and installation == "air":
        spacing = st.selectbox("Cable spacing", ["touching", "150mm", "300mm"],
                               format_func=lambda x: {"touching": "Touching",
                                                      "150mm": "Spaced 150 mm",
                                                      "300mm": "Spaced 300 mm"}[x])

    st.markdown("---")
    st.markdown("**Short Circuit Data**")
    scc1, scc2 = st.columns(2)
    with scc1:
        isc_ka = st.number_input("Fault level at cable origin (kA)",
                                 min_value=0.1, value=10.0, step=0.5)
    with scc2:
        trip_time_s = st.selectbox("Protection trip time (s)",
                                   [0.1, 0.2, 0.4, 0.5, 1.0, 2.0, 3.0], index=0)

    if st.button("Calculate Cable Size", use_container_width=True):
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
            ins_label = insulation.upper()

            col_a, col_b, col_c = st.columns(3)
            if cable_type == "single_core":
                cores_label = "single core"
                cable_desig = f"1x{res.size_mm2} mm2 {cond_label}/XLPE"
            else:
                cores_label = "4-core" if neutral else "3-core"
                cable_desig = f"{res.size_mm2} mm2 {cond_label}/{ins_label}/{cores_label}"

            col_a.metric("Recommended Size",
                         f"1x{res.size_mm2} mm2" if cable_type == "single_core" else f"{res.size_mm2} mm2",
                         cable_desig)
            col_b.metric("Full Load Current", f"{res.full_load_current} A",
                         f"Iz catalog = {res.catalog_iz} A")
            col_c.metric("Voltage Drop", f"{res.voltage_drop_pct}%",
                         f"Limit {max_vdrop}% - {'OK' if res.vdrop_ok else 'FAIL'}")

            show_soil = installation in ["ground", "duct"]
            sc_label = f"SC min = {res.sc_size_mm2} mm2"
            if res.sc_governed:
                st.error(f"Cable upsized by Short Circuit requirement - {sc_label}")
            else:
                st.info(f"Short circuit check passed - {sc_label}")

            st.markdown("**Calculation Details**")
            details = {
                "Full load current": f"{res.full_load_current} A",
                "AC resistance": f"{res.r_ac_ohm_km} ohm/km",
                "Temp derating factor": f"x {res.temp_derating}",
                "Group derating factor": f"x {res.group_derating}",
                "Soil thermal derating": f"x {res.soil_thermal_derating}" if show_soil else "N/A",
                "Burial depth derating": f"x {res.depth_derating}" if show_soil else "N/A",
                "Effective cable capacity": f"{res.effective_capacity} A",
                "Cable utilisation": f"{res.utilisation_pct}%",
                "Voltage drop": f"{res.voltage_drop_v} V ({res.voltage_drop_pct}%)",
                "Cable designation": cable_desig + " 0.6/1 kV",
            }
            for k, v in details.items():
                c1, c2 = st.columns([2, 3])
                c1.markdown(f"<span style='color:#666'>{k}</span>", unsafe_allow_html=True)
                c2.markdown(f"**{v}**")

            notes = [w for w in res.warnings if w.startswith("NOTE:")]
            warnings_only = [w for w in res.warnings if not w.startswith("NOTE:")]

            if warnings_only:
                for w in warnings_only:
                    st.warning(w)
            else:
                st.success("Cable selection is within all limits.")

            for n in notes:
                st.info(n)

        except Exception as e:
            st.error(f"Calculation error: {e}")


# ─────────────────────────────────────────────
# TAB: Price Variance Calculator (VF) - Copper, SAR, per meter
# ─────────────────────────────────────────────
with tab_vf:
    st.subheader("Price Variance Calculator (VF) - Copper / SAR")
    st.markdown(
        "Calculate cable sales price per meter based on copper LME price variance."
    )

    # Get current LME price (USD/ton) from the live ticker
    current_prices = get_metal_prices()
    current_lme_auto = current_prices["copper"]["price"]

    st.markdown("---")

    # ── VF Input Mode Toggle ──
    vf_mode = st.radio(
        "VF Input Mode",
        ["Calculate from cable specs", "Enter VF manually"],
        horizontal=True,
        help="Choose whether to calculate VF from cable specifications or enter it directly"
    )

    st.markdown("### Step 1: Cable Specifications")

    if vf_mode == "Calculate from cable specs":
        vf_col1, vf_col2 = st.columns(2)
        with vf_col1:
            vf_cores = st.number_input(
                "Number of cores",
                min_value=1, max_value=61, value=4, step=1,
                help="Total number of conductors in the cable"
            )
        with vf_col2:
            vf_cross_section = st.number_input(
                "Cross section area (mm2)",
                min_value=0.5, max_value=1000.0, value=50.0, step=0.5,
                help="Conductor cross-sectional area per core"
            )

        # ── Copper Weight per meter (g/m) ──
        # Formula: Cores x Cross Section (mm2) x Density (8.96 g/cm3)
        # Net result: Cores x mm2 x 8.96 = grams per meter
        copper_weight = vf_cores * vf_cross_section * 8.96  # g/m

        # ── Variance Factor ──
        # VF = Weight (g/m) x 3.75 / 1000
        variance_factor = copper_weight * 3.75 / 1000

        st.markdown("---")
        st.markdown("### Step 2: Calculated Values (per meter)")

        calc_col1, calc_col2 = st.columns(2)
        calc_col1.metric(
            "Copper Weight",
            f"{copper_weight:.2f} g/m",
            f"{copper_weight/1000:.4f} kg/m"
        )
        calc_col2.metric(
            "Variance Factor (VF)",
            f"{variance_factor:.4f}",
            "Weight x 3.75 / 1000"
        )
    else:
        # ── Manual VF Input ──
        st.info(
            "Enter the Variance Factor (VF) directly if you have it pre-calculated "
            "from your pricing sheet or customer agreement."
        )
        vf_cores = None  # not used
        vf_cross_section = None  # not used
        copper_weight = None  # not used

        vf_manual_col1, vf_manual_col2 = st.columns([1, 2])
        with vf_manual_col1:
            variance_factor = st.number_input(
                "Variance Factor (VF)",
                min_value=0.0, max_value=1000.0, value=6.72, step=0.01, format="%.4f",
                help="Enter VF value directly (typically between 0.1 and 100)"
            )
        with vf_manual_col2:
            st.markdown("")
            st.markdown("")
            st.metric("Variance Factor (VF)", f"{variance_factor:.4f}", "Manual entry")

    st.markdown("---")
    st.markdown("### Step 3: Price Calculation")

    # ── Formula display ──
    st.markdown("""
    <div style="background: #e3f2fd; border-left: 4px solid #1976d2; padding: 12px 16px; border-radius: 6px; margin-bottom: 15px;">
        <div style="color: #1565c0; font-weight: 600; font-size: 13px; margin-bottom: 4px;">FORMULA</div>
        <div style="color: #0d47a1; font-family: 'Courier New', monospace; font-size: 15px;">
            P<sub>2</sub> = P<sub>1</sub> + [ VF × (LME<sub>2</sub> − LME<sub>1</sub>) / 1000 ]
        </div>
        <div style="color: #555; font-size: 12px; margin-top: 6px;">
            If LME<sub>2</sub> &gt; LME<sub>1</sub> → price <b style="color:#d32f2f;">increases (+)</b>  |  
            If LME<sub>2</sub> &lt; LME<sub>1</sub> → price <b style="color:#2e7d32;">decreases (−)</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    price_col1, price_col2, price_col3 = st.columns(3)
    with price_col1:
        quoted_price = st.number_input(
            "Quoted Price (SAR/m)",
            min_value=0.0, value=100.0, step=1.0,
            help="Original price per meter given to customer"
        )
    with price_col2:
        old_lme = st.number_input(
            "Old LME Price (USD/ton)",
            min_value=0.0, value=9500.0, step=50.0,
            help="LME copper price at the time of quotation"
        )
    with price_col3:
        use_auto_lme = st.checkbox(
            "Use live LME price",
            value=True,
            help=f"Current live price: ${current_lme_auto:,.0f}/ton"
        )
        if use_auto_lme:
            current_lme = current_lme_auto
            st.info(f"Live: ${current_lme:,.0f}/ton")
        else:
            current_lme = st.number_input(
                "Current LME Price (USD/ton)",
                min_value=0.0, value=float(current_lme_auto), step=50.0
            )

    # ── Sales Price Formula ──
    # P2 = P1 + (VF x (LME2 - LME1) / 1000)
    lme_diff = current_lme - old_lme
    price_adjustment = variance_factor * lme_diff / 1000  # SAR/m
    sales_price = quoted_price + price_adjustment

    # Determine direction for visual feedback
    if price_adjustment > 0.01:
        direction = "INCREASE"
        direction_color = "#d32f2f"  # Red (customer pays more)
        direction_arrow = "▲"
        direction_sign = "+"
    elif price_adjustment < -0.01:
        direction = "DECREASE"
        direction_color = "#2e7d32"  # Green (customer pays less)
        direction_arrow = "▼"
        direction_sign = "−"
    else:
        direction = "NO CHANGE"
        direction_color = "#757575"  # Gray
        direction_arrow = "■"
        direction_sign = ""

    st.markdown("---")
    st.markdown("### Result (per meter)")

    # ── Big visual summary box ──
    summary_html = f"""
    <div style="background: linear-gradient(135deg, {direction_color}15 0%, {direction_color}25 100%);
                border-left: 6px solid {direction_color};
                border-radius: 10px;
                padding: 20px;
                margin: 15px 0;
                text-align: center;">
        <div style="color: {direction_color}; font-size: 13px; font-weight: 700; letter-spacing: 2px;">
            {direction_arrow} PRICE {direction}
        </div>
        <div style="color: {direction_color}; font-size: 36px; font-weight: 800; margin: 10px 0;">
            {direction_sign}{abs(price_adjustment):,.2f} SAR/m
        </div>
        <div style="color: #333; font-size: 14px;">
            Quoted: <b>{quoted_price:,.2f}</b> SAR/m  &nbsp;→&nbsp;
            Sales: <b>{sales_price:,.2f}</b> SAR/m
        </div>
    </div>
    """
    st.markdown(summary_html, unsafe_allow_html=True)

    # ── Metrics row ──
    result_col1, result_col2, result_col3 = st.columns(3)
    result_col1.metric(
        "LME Change",
        f"${lme_diff:+,.0f}/ton",
        f"{(lme_diff/old_lme*100):+.2f}%" if old_lme > 0 else "N/A"
    )
    result_col2.metric(
        "Price Adjustment",
        f"{price_adjustment:+,.2f} SAR/m",
        "VF x (LME diff) / 1000"
    )
    result_col3.metric(
        "Sales Price",
        f"{sales_price:,.2f} SAR/m",
        f"{((sales_price-quoted_price)/quoted_price*100):+.2f}%" if quoted_price > 0 else "N/A"
    )

    # ── Visual feedback message ──
    if price_adjustment > 0.01:
        st.warning(
            f"**LME increased by ${lme_diff:,.0f}/ton** since quotation. "
            f"New sales price must ADD {price_adjustment:,.2f} SAR/m to recover copper cost."
        )
    elif price_adjustment < -0.01:
        st.success(
            f"**LME decreased by ${abs(lme_diff):,.0f}/ton** since quotation. "
            f"Customer benefits: price reduced by {abs(price_adjustment):,.2f} SAR/m."
        )
    else:
        st.info("No significant change in LME price since quotation.")

    # ── Formula breakdown (expander) ──
    with st.expander("Show formula breakdown"):
        if vf_mode == "Calculate from cable specs":
            st.markdown(f"""
**Step 1 - Copper Weight per meter:**
```
Weight = Cores x Cross Section x Density
Weight = {vf_cores} x {vf_cross_section} x 8.96
Weight = {copper_weight:.2f} g/m
```

**Step 2 - Variance Factor (VF):**
```
VF = Copper Weight x 3.75 / 1000
VF = {copper_weight:.2f} x 3.75 / 1000
VF = {variance_factor:.4f}
```

**Step 3 - Sales Price (P2 = P1 + VF x (LME2 - LME1) / 1000):**
```
Sales = Quoted + VF x (Current LME - Old LME) / 1000
Sales = {quoted_price:,.2f} + {variance_factor:.4f} x ({current_lme:,.0f} - {old_lme:,.0f}) / 1000
Sales = {quoted_price:,.2f} + {price_adjustment:+,.4f}
Sales = {sales_price:,.2f} SAR/m
```
            """)
        else:
            st.markdown(f"""
**Step 1 - Variance Factor (VF):**
```
VF = {variance_factor:.4f}  (entered manually)
```

**Step 2 - Sales Price (P2 = P1 + VF x (LME2 - LME1) / 1000):**
```
Sales = Quoted + VF x (Current LME - Old LME) / 1000
Sales = {quoted_price:,.2f} + {variance_factor:.4f} x ({current_lme:,.0f} - {old_lme:,.0f}) / 1000
Sales = {quoted_price:,.2f} + {price_adjustment:+,.4f}
Sales = {sales_price:,.2f} SAR/m
```
            """)


with tab_conduit:
    st.subheader("Conduit Fill Calculator (IEC 61386 / NEC 344)")
    st.markdown(
        "Check if cables fit in the selected conduit size according to fill ratio standards."
    )

    # ── Standard Conduit Sizes (Internal Diameter in mm) ──
    # PVC conduits (common sizes in Saudi Arabia)
    CONDUIT_PVC = {
        "20 mm":   {"trade": "20 mm",   "id": 17.0, "od": 20.0},
        "25 mm":   {"trade": "25 mm",   "id": 21.4, "od": 25.0},
        "32 mm":   {"trade": "32 mm",   "id": 27.8, "od": 32.0},
        "40 mm":   {"trade": "40 mm",   "id": 35.4, "od": 40.0},
        "50 mm":   {"trade": "50 mm",   "id": 44.3, "od": 50.0},
        "63 mm":   {"trade": "63 mm",   "id": 57.0, "od": 63.0},
        "75 mm":   {"trade": "75 mm",   "id": 67.8, "od": 75.0},
        "90 mm":   {"trade": "90 mm",   "id": 81.4, "od": 90.0},
        "110 mm":  {"trade": "110 mm",  "id": 99.4, "od": 110.0},
        "125 mm":  {"trade": "125 mm",  "id": 113.0, "od": 125.0},
        "160 mm":  {"trade": "160 mm",  "id": 144.6, "od": 160.0},
        "200 mm":  {"trade": "200 mm",  "id": 180.8, "od": 200.0},
    }
    # GI (Galvanized Iron) conduits
    CONDUIT_GI = {
        "20 mm (3/4\")": {"trade": "20 mm",   "id": 17.0, "od": 20.0},
        "25 mm (1\")":   {"trade": "25 mm",   "id": 21.6, "od": 25.0},
        "32 mm (1.25\")": {"trade": "32 mm",  "id": 28.0, "od": 32.0},
        "40 mm (1.5\")": {"trade": "40 mm",   "id": 35.0, "od": 40.0},
        "50 mm (2\")":   {"trade": "50 mm",   "id": 44.0, "od": 50.0},
        "65 mm (2.5\")": {"trade": "65 mm",   "id": 57.0, "od": 65.0},
        "80 mm (3\")":   {"trade": "80 mm",   "id": 72.0, "od": 80.0},
        "100 mm (4\")":  {"trade": "100 mm",  "id": 98.0, "od": 100.0},
        "125 mm (5\")":  {"trade": "125 mm",  "id": 123.0, "od": 125.0},
        "150 mm (6\")":  {"trade": "150 mm",  "id": 148.0, "od": 150.0},
    }

    # ── Cable OD Estimation (approximate, based on Elsewedy catalog averages) ──
    def estimate_cable_od(cores, cross_section, armoured=False):
        """
        Estimate cable outer diameter in mm.
        Based on typical LV multicore cables (Cu/XLPE or Cu/PVC).
        """
        if cross_section <= 16:
            base_od = math.sqrt(cross_section) * 1.6 + 4
        elif cross_section <= 95:
            base_od = math.sqrt(cross_section) * 1.5 + 5
        else:
            base_od = math.sqrt(cross_section) * 1.4 + 8

        # Adjust for number of cores
        # 1 core uses base_od directly
        # 2+ cores: multiplier based on cable geometry
        if cores == 1:
            od = base_od
        elif cores == 2:
            od = base_od * 1.7
        elif cores == 3:
            od = base_od * 1.9
        elif cores == 4:
            od = base_od * 2.1
        elif cores == 5:
            od = base_od * 2.25
        else:
            od = base_od * (2.0 + cores * 0.05)

        # Armour adds ~3 mm
        if armoured:
            od += 3

        return round(od, 1)

    # ── IEC / NEC Fill Ratios ──
    FILL_RATIOS = {
        1: 0.53,   # 53% for single cable
        2: 0.31,   # 31% for two cables
        "3+": 0.40 # 40% for three or more cables
    }

    st.markdown("---")
    st.markdown("### Step 1: Cable Specifications")

    cf_mode = st.radio(
        "Cable OD Input",
        ["Calculate from cable specs", "Enter OD manually"],
        horizontal=True,
        help="Calculate automatically from cores + mm², or enter outer diameter directly"
    )

    if cf_mode == "Calculate from cable specs":
        cf_col1, cf_col2, cf_col3 = st.columns(3)
        with cf_col1:
            cf_num_cables = st.number_input(
                "Number of cables",
                min_value=1, max_value=100, value=3, step=1,
                help="How many cables will run in the same conduit"
            )
        with cf_col2:
            cf_cores = st.number_input(
                "Cores per cable",
                min_value=1, max_value=61, value=4, step=1
            )
        with cf_col3:
            cf_cross_section = st.number_input(
                "Cross section (mm2)",
                min_value=1.5, max_value=1000.0, value=25.0, step=0.5
            )

        cf_armoured = st.checkbox("Armoured cable (SWA/STA)", value=False,
                                   help="Adds ~3 mm to the outer diameter")

        cable_od = estimate_cable_od(cf_cores, cf_cross_section, cf_armoured)
        st.info(
            f"Estimated cable OD: **{cable_od} mm** "
            f"(for {cf_cores}x{cf_cross_section} mm² "
            f"{'armoured' if cf_armoured else 'unarmoured'} cable)"
        )
    else:
        cf_col1, cf_col2 = st.columns(2)
        with cf_col1:
            cf_num_cables = st.number_input(
                "Number of cables",
                min_value=1, max_value=100, value=3, step=1
            )
        with cf_col2:
            cable_od = st.number_input(
                "Cable outer diameter (mm)",
                min_value=1.0, max_value=200.0, value=20.0, step=0.5,
                help="Outer diameter from cable datasheet"
            )

    st.markdown("---")
    st.markdown("### Step 2: Conduit Selection")

    cond_col1, cond_col2 = st.columns(2)
    with cond_col1:
        conduit_type = st.selectbox(
            "Conduit material",
            ["PVC", "GI (Galvanized Iron)"],
            help="PVC is most common indoors; GI for mechanical protection"
        )
    with cond_col2:
        conduit_dict = CONDUIT_PVC if conduit_type == "PVC" else CONDUIT_GI
        conduit_size_key = st.selectbox(
            "Conduit trade size",
            list(conduit_dict.keys()),
            help="Standard trade sizes available in KSA market"
        )

    conduit = conduit_dict[conduit_size_key]
    conduit_id = conduit["id"]
    conduit_od = conduit["od"]

    # ── Calculations ──
    # Areas
    cable_area_each = math.pi * (cable_od / 2) ** 2
    total_cable_area = cable_area_each * cf_num_cables
    conduit_area = math.pi * (conduit_id / 2) ** 2

    # Fill ratio
    fill_pct = (total_cable_area / conduit_area) * 100

    # Allowed fill based on number of cables
    if cf_num_cables == 1:
        allowed_fill_pct = 53
        fill_rule = "Single cable (IEC 53%)"
    elif cf_num_cables == 2:
        allowed_fill_pct = 31
        fill_rule = "Two cables (IEC 31%)"
    else:
        allowed_fill_pct = 40
        fill_rule = "3+ cables (IEC/NEC 40%)"

    passed = fill_pct <= allowed_fill_pct
    margin = allowed_fill_pct - fill_pct

    st.markdown("---")
    st.markdown("### Step 3: Results")

    # ── Visual pass/fail box ──
    if passed:
        color = "#2e7d32"
        status = "PASS"
        arrow = "✓"
        bg = "#e8f5e9"
    else:
        color = "#d32f2f"
        status = "FAIL"
        arrow = "✗"
        bg = "#ffebee"

    result_html = f"""
    <div style="background: {bg};
                border-left: 6px solid {color};
                border-radius: 10px;
                padding: 20px;
                margin: 15px 0;
                text-align: center;">
        <div style="color: {color}; font-size: 13px; font-weight: 700; letter-spacing: 2px;">
            {arrow} CONDUIT FILL CHECK: {status}
        </div>
        <div style="color: {color}; font-size: 36px; font-weight: 800; margin: 10px 0;">
            {fill_pct:.1f}%
        </div>
        <div style="color: #333; font-size: 14px;">
            Allowed: <b>{allowed_fill_pct}%</b>  |  Margin: <b>{margin:+.1f}%</b>
        </div>
        <div style="color: #666; font-size: 12px; margin-top: 8px;">
            {fill_rule}
        </div>
    </div>
    """
    st.markdown(result_html, unsafe_allow_html=True)

    # ── Detailed metrics ──
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric(
        "Cable Area (each)",
        f"{cable_area_each:.1f} mm²",
        f"OD = {cable_od} mm"
    )
    m_col2.metric(
        "Total Cable Area",
        f"{total_cable_area:.1f} mm²",
        f"{cf_num_cables} cable(s)"
    )
    m_col3.metric(
        "Conduit Inner Area",
        f"{conduit_area:.1f} mm²",
        f"ID = {conduit_id} mm"
    )

    # ── Recommendations ──
    if not passed:
        # Find minimum required conduit size
        recommended = None
        for size_key, cond in conduit_dict.items():
            cond_area_check = math.pi * (cond["id"] / 2) ** 2
            fill_check = (total_cable_area / cond_area_check) * 100
            if fill_check <= allowed_fill_pct:
                recommended = (size_key, cond, fill_check)
                break

        if recommended:
            rec_key, rec_cond, rec_fill = recommended
            st.error(
                f"**FAIL — Conduit too small!**  "
                f"Fill ratio {fill_pct:.1f}% exceeds allowed {allowed_fill_pct}%."
            )
            st.success(
                f"**Recommended size:** {rec_key} {conduit_type} "
                f"(ID = {rec_cond['id']} mm, fill = {rec_fill:.1f}%)"
            )
        else:
            st.error(
                f"**FAIL** — Even the largest {conduit_type} conduit in the list is not enough. "
                f"Consider splitting cables into multiple conduits."
            )
    else:
        # Suggest smaller conduit if margin is large
        if margin > 15:
            smaller_sizes = list(conduit_dict.keys())
            current_index = smaller_sizes.index(conduit_size_key)
            if current_index > 0:
                smaller_key = smaller_sizes[current_index - 1]
                smaller_cond = conduit_dict[smaller_key]
                smaller_area = math.pi * (smaller_cond["id"] / 2) ** 2
                smaller_fill = (total_cable_area / smaller_area) * 100
                if smaller_fill <= allowed_fill_pct:
                    st.info(
                        f"**Cost saving tip:** A smaller {smaller_key} conduit would also work "
                        f"(fill = {smaller_fill:.1f}%, still ≤ {allowed_fill_pct}%)."
                    )
        st.success(
            f"**PASS** — Fill ratio {fill_pct:.1f}% is within allowed {allowed_fill_pct}% limit. "
            f"Safe margin: {margin:.1f}%."
        )

    # ── Formula breakdown ──
    with st.expander("Show formula breakdown"):
        st.markdown(f"""
**Step 1 - Cable Area (each):**
```
A_cable = π × (OD/2)²
A_cable = π × ({cable_od}/2)²
A_cable = {cable_area_each:.2f} mm²
```

**Step 2 - Total Cable Area:**
```
A_total = A_cable × Number of cables
A_total = {cable_area_each:.2f} × {cf_num_cables}
A_total = {total_cable_area:.2f} mm²
```

**Step 3 - Conduit Inner Area:**
```
A_conduit = π × (ID/2)²
A_conduit = π × ({conduit_id}/2)²
A_conduit = {conduit_area:.2f} mm²
```

**Step 4 - Fill Ratio:**
```
Fill % = (A_total / A_conduit) × 100
Fill % = ({total_cable_area:.2f} / {conduit_area:.2f}) × 100
Fill % = {fill_pct:.2f}%
```

**IEC / NEC Fill Limits:**
- 1 cable → 53% max
- 2 cables → 31% max
- 3+ cables → **40% max** (most common case)

**Current rule applied:** {fill_rule}
        """)


with tab2:
    st.subheader("AI Technical Support")
    query = st.text_input("Ask about cables, standards, or specifications:",
                          placeholder="e.g. What is the current rating of 4x16mm2 XLPE cable?")
    if query:
        if model is None:
            st.error("AI model not available.")
        else:
            with st.spinner("AI is thinking..."):
                try:
                    response = model.generate_content(query)
                    st.markdown("### Answer:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"AI Error: {e}")
        st.markdown("---")
        st.markdown("#### For more information, please contact:")
        st.success("**Eng. Mohamed Tarek**  \n+966570514091  \nMohamed.abdelwahab@elsewedy.com")

st.markdown("---")
st.caption("(c) 2026 Developed by Eng. Mohamed Tarek | Elsewedy Electric KSA")
