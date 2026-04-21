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
# LIVE METAL PRICES - Dual Source
# ─────────────────────────────────────────────
USD_TO_SAR = 3.75


def fetch_from_yahoo():
    try:
        copper = yf.Ticker("HG=F")
        alum = yf.Ticker("ALI=F")
        cu_data = copper.history(period="5d")
        al_data = alum.history(period="5d")
        if cu_data.empty or al_data.empty:
            return None
        cu_now = float(cu_data["Close"].iloc[-1]) * 2204.62
        cu_prev = float(cu_data["Close"].iloc[-2]) * 2204.62 if len(cu_data) > 1 else cu_now
        al_now = float(al_data["Close"].iloc[-1])
        al_prev = float(al_data["Close"].iloc[-2]) if len(al_data) > 1 else al_now
        return {
            "copper": {"price": cu_now, "change": ((cu_now - cu_prev) / cu_prev) * 100 if cu_prev else 0},
            "aluminium": {"price": al_now, "change": ((al_now - al_prev) / al_prev) * 100 if al_prev else 0},
            "source": "Yahoo Finance (COMEX/CME Futures)",
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    except Exception:
        return None


def fetch_from_lme_backup():
    try:
        url = "https://api.metals.dev/v1/latest?api_key=demo&currency=USD&unit=toz"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return None
        data = response.json()
        metals = data.get("metals", {})
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
    return {
        "copper": {"price": 9200, "change": 0},
        "aluminium": {"price": 2400, "change": 0},
        "source": "⚠ Offline estimates (LME average)",
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


@st.cache_data(ttl=600)
def get_metal_prices():
    prices = fetch_from_yahoo()
    if prices:
        return prices
    prices = fetch_from_lme_backup()
    if prices:
        return prices
    return get_fallback_prices()


def render_price_ticker():
    prices = get_metal_prices()
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
