import streamlit as st
import google.generativeai as genai
import math
import os
from dataclasses import dataclass

# ─────────────────────────────────────────────
# 1. Page config — MUST be first Streamlit call
# ─────────────────────────────────────────────
st.set_page_config(page_title="Elsewedy Smart Tool", layout="wide")

# --- تنسيق الألوان وإخفاء هوية Streamlit ---
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
    .result-box {
        background: #ffffff;
        border-left: 4px solid #CC0000;
        border-radius: 6px;
        padding: 1rem 1.25rem;
        margin-top: 1rem;
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
        st.markdown(f"### Elsewedy Electric")

# ─────────────────────────────────────────────
# 4. Cable Selection — Catalog & Logic
# ─────────────────────────────────────────────

CATALOG = {
    "cu": {
        "xlpe": {
            "air": [
                {"s": 1.5, "Iz": 26}, {"s": 2.5, "Iz": 36}, {"s": 4, "Iz": 49},
                {"s": 6, "Iz": 63}, {"s": 10, "Iz": 86}, {"s": 16, "Iz": 115},
                {"s": 25, "Iz": 149}, {"s": 35, "Iz": 185}, {"s": 50, "Iz": 225},
                {"s": 70, "Iz": 289}, {"s": 95, "Iz": 352}, {"s": 120, "Iz": 410},
                {"s": 150, "Iz": 473}, {"s": 185, "Iz": 542}, {"s": 240, "Iz": 641},
                {"s": 300, "Iz": 741},
            ],
            "ground": [
                {"s": 1.5, "Iz": 25}, {"s": 2.5, "Iz": 33}, {"s": 4, "Iz": 44},
                {"s": 6, "Iz": 56}, {"s": 10, "Iz": 75}, {"s": 16, "Iz": 100},
                {"s": 25, "Iz": 127}, {"s": 35, "Iz": 158}, {"s": 50, "Iz": 192},
                {"s": 70, "Iz": 241}, {"s": 95, "Iz": 292}, {"s": 120, "Iz": 339},
                {"s": 150, "Iz": 388}, {"s": 185, "Iz": 443}, {"s": 240, "Iz": 520},
                {"s": 300, "Iz": 598},
            ],
            "duct": [
                {"s": 1.5, "Iz": 22}, {"s": 2.5, "Iz": 29}, {"s": 4, "Iz": 38},
                {"s": 6, "Iz": 49}, {"s": 10, "Iz": 66}, {"s": 16, "Iz": 88},
                {"s": 25, "Iz": 111}, {"s": 35, "Iz": 138}, {"s": 50, "Iz": 168},
                {"s": 70, "Iz": 210}, {"s": 95, "Iz": 255}, {"s": 120, "Iz": 296},
                {"s": 150, "Iz": 339}, {"s": 185, "Iz": 387}, {"s": 240, "Iz": 455},
                {"s": 300, "Iz": 523},
            ],
        },
        "pvc": {
            "air": [
                {"s": 1.5, "Iz": 19.5}, {"s": 2.5, "Iz": 27}, {"s": 4, "Iz": 36},
                {"s": 6, "Iz": 46}, {"s": 10, "Iz": 63}, {"s": 16, "Iz": 85},
                {"s": 25, "Iz": 110}, {"s": 35, "Iz": 137}, {"s": 50, "Iz": 167},
                {"s": 70, "Iz": 214}, {"s": 95, "Iz": 261}, {"s": 120, "Iz": 303},
                {"s": 150, "Iz": 349}, {"s": 185, "Iz": 400}, {"s": 240, "Iz": 470},
                {"s": 300, "Iz": 545},
            ],
            "ground": [
                {"s": 1.5, "Iz": 18}, {"s": 2.5, "Iz": 24}, {"s": 4, "Iz": 31},
                {"s": 6, "Iz": 39}, {"s": 10, "Iz": 52}, {"s": 16, "Iz": 67},
                {"s": 25, "Iz": 86}, {"s": 35, "Iz": 107}, {"s": 50, "Iz": 130},
                {"s": 70, "Iz": 163}, {"s": 95, "Iz": 197}, {"s": 120, "Iz": 227},
                {"s": 150, "Iz": 259}, {"s": 185, "Iz": 295}, {"s": 240, "Iz": 346},
                {"s": 300, "Iz": 396},
            ],
            "duct": [
                {"s": 1.5, "Iz": 16}, {"s": 2.5, "Iz": 21}, {"s": 4, "Iz": 27},
                {"s": 6, "Iz": 34}, {"s": 10, "Iz": 46}, {"s": 16, "Iz": 62},
                {"s": 25, "Iz": 78}, {"s": 35, "Iz": 97}, {"s": 50, "Iz": 118},
                {"s": 70, "Iz": 148}, {"s": 95, "Iz": 179}, {"s": 120, "Iz": 207},
                {"s": 150, "Iz": 236}, {"s": 185, "Iz": 270}, {"s": 240, "Iz": 317},
                {"s": 300, "Iz": 364},
            ],
        },
    },
    "al": {
        "xlpe": {
            "air": [
                {"s": 16, "Iz": 87}, {"s": 25, "Iz": 114}, {"s": 35, "Iz": 141},
                {"s": 50, "Iz": 172}, {"s": 70, "Iz": 220}, {"s": 95, "Iz": 269},
                {"s": 120, "Iz": 312}, {"s": 150, "Iz": 361}, {"s": 185, "Iz": 412},
                {"s": 240, "Iz": 489}, {"s": 300, "Iz": 565},
            ],
            "ground": [
                {"s": 16, "Iz": 79}, {"s": 25, "Iz": 99}, {"s": 35, "Iz": 123},
                {"s": 50, "Iz": 148}, {"s": 70, "Iz": 186}, {"s": 95, "Iz": 226},
                {"s": 120, "Iz": 261}, {"s": 150, "Iz": 298}, {"s": 185, "Iz": 340},
                {"s": 240, "Iz": 401}, {"s": 300, "Iz": 461},
            ],
            "duct": [
                {"s": 16, "Iz": 68}, {"s": 25, "Iz": 86}, {"s": 35, "Iz": 107},
                {"s": 50, "Iz": 130}, {"s": 70, "Iz": 162}, {"s": 95, "Iz": 196},
                {"s": 120, "Iz": 228}, {"s": 150, "Iz": 260}, {"s": 185, "Iz": 296},
                {"s": 240, "Iz": 348}, {"s": 300, "Iz": 400},
            ],
        },
        "pvc": {
            "air": [
                {"s": 16, "Iz": 64}, {"s": 25, "Iz": 82}, {"s": 35, "Iz": 103},
                {"s": 50, "Iz": 125}, {"s": 70, "Iz": 160}, {"s": 95, "Iz": 195},
                {"s": 120, "Iz": 226}, {"s": 150, "Iz": 261}, {"s": 185, "Iz": 298},
                {"s": 240, "Iz": 352}, {"s": 300, "Iz": 406},
            ],
            "ground": [
                {"s": 16, "Iz": 57}, {"s": 25, "Iz": 73}, {"s": 35, "Iz": 90},
                {"s": 50, "Iz": 110}, {"s": 70, "Iz": 138}, {"s": 95, "Iz": 167},
                {"s": 120, "Iz": 193}, {"s": 150, "Iz": 220}, {"s": 185, "Iz": 250},
                {"s": 240, "Iz": 294}, {"s": 300, "Iz": 337},
            ],
            "duct": [
                {"s": 16, "Iz": 52}, {"s": 25, "Iz": 66}, {"s": 35, "Iz": 82},
                {"s": 50, "Iz": 99}, {"s": 124, "Iz": 124}, {"s": 95, "Iz": 150},
                {"s": 120, "Iz": 174}, {"s": 150, "Iz": 198}, {"s": 185, "Iz": 226},
                {"s": 240, "Iz": 265}, {"s": 300, "Iz": 304},
            ],
        },
    },
}

TEMP_DERATING = {
    "xlpe": {15:1.15, 20:1.10, 25:1.05, 30:1.00, 35:0.95, 40:0.90, 45:0.84, 50:0.78, 55:0.72},
    "pvc":  {15:1.21, 20:1.15, 25:1.07, 30:1.00, 35:0.92, 40:0.84, 45:0.75, 50:0.66, 55:0.55},
}

GROUP_DERATING = {1:1.00, 2:0.87, 3:0.79, 4:0.75, 5:0.72, 6:0.70}

# معاملات السويدي للتربة والعمق (LV)
SOIL_THERMAL_MAP = {1.0: 1.05, 1.2: 1.00, 1.5: 0.92, 2.0: 0.83, 2.5: 0.76, 3.0: 0.71}
DEPTH_DIRECT_MAP = {0.5: 1.03, 0.6: 1.02, 0.8: 1.00, 1.0: 0.98, 1.25: 0.96, 1.5: 0.95}
DEPTH_DUCT_MAP   = {0.5: 1.00, 0.6: 0.99, 0.8: 0.98, 1.0: 0.96, 1.25: 0.95, 1.5: 0.94}

RESISTANCE = {
    "cu": {1.5:12.10, 2.5:7.41, 4:4.61, 6:3.08, 10:1.83, 16:1.15, 25:0.727,
           35:0.524, 50:0.387, 70:0.268, 95:0.193, 120:0.153, 150:0.124,
           185:0.0991, 240:0.0754, 300:0.0601},
    "al": {16:1.91, 25:1.20, 35:0.868, 50:0.641, 70:0.443, 95:0.320,
           120:0.253, 150:0.206, 185:0.164, 240:0.125, 300:0.100},
}
REACTANCE_DEFAULT = 0.08

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
    vdrop_ok: bool
    warnings: list

def get_temp_derating(insulation, temp_c):
    table = TEMP_DERATING[insulation]
    if temp_c in table:
        return table[temp_c]
    temps = sorted(table.keys())
    for i in range(len(temps) - 1):
        t1, t2 = temps[i], temps[i+1]
        if t1 <= temp_c <= t2:
            return table[t1] + (table[t2]-table[t1]) * (temp_c-t1)/(t2-t1)
    return table[temps[-1]]

def select_cable(load_kw, voltage_v, phases, pf, length_m,
                 temp_c, conductor, insulation, installation,
                 max_vdrop_pct, num_cables, soil_thermal, burial_depth):
    warnings = []
    sinpf = math.sqrt(max(0, 1 - pf**2))

    # Full load current
    if phases == 3:
        IFL = (load_kw * 1000) / (math.sqrt(3) * voltage_v * pf)
    else:
        IFL = (load_kw * 1000) / (voltage_v * pf)

    # Derating Calculation
    t_derate = get_temp_derating(insulation, temp_c)
    g_derate = GROUP_DERATING.get(num_cables, 0.65)
    
    # Soil Thermal & Depth Derating (Only for underground)
    st_derate = 1.0
    d_derate = 1.0
    if installation in ["ground", "duct"]:
        st_derate = SOIL_THERMAL_MAP.get(soil_thermal, 1.0)
        if installation == "duct":
            d_derate = DEPTH_DUCT_MAP.get(burial_depth, 1.0)
        else:
            d_derate = DEPTH_DIRECT_MAP.get(burial_depth, 1.0)

    total_derate = t_derate * g_derate * st_derate * d_derate
    I_required = IFL / total_derate

    table = CATALOG[conductor][insulation][installation]
    chosen = next((c for c in table if c["Iz"] >= I_required), None)
    if chosen is None:
        chosen = table[-1]
        warnings.append(f"Load ({I_required:.1f} A) exceeds catalog max. Consider parallel cables.")

    resist_table = RESISTANCE[conductor]

    def vdrop_pct(size):
        R = resist_table.get(size, 0.16)
        L = length_m / 1000
        imp = R * pf + REACTANCE_DEFAULT * sinpf
        vd = (math.sqrt(3) if phases == 3 else 2) * IFL * imp * L
        return vd, (vd / voltage_v) * 100

    vd_v, vd_pct = vdrop_pct(chosen["s"])

    if vd_pct > max_vdrop_pct:
        for cable in table:
            if cable["Iz"] >= I_required:
                _, candidate_pct = vdrop_pct(cable["s"])
                if candidate_pct <= max_vdrop_pct:
                    chosen = cable
                    break
        vd_v, vd_pct = vdrop_pct(chosen["s"])
        if vd_pct > max_vdrop_pct:
            warnings.append(f"Voltage drop ({vd_pct:.2f}%) still exceeds {max_vdrop_pct}%.")

    eff_cap = chosen["Iz"] * total_derate
    util = (IFL / eff_cap * 100) if eff_cap > 0 else 0

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
        vdrop_ok=vd_pct <= max_vdrop_pct,
        warnings=warnings,
    )

# ─────────────────────────────────────────────
# 5. Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    display_logo(150)
    st.markdown("### 👤 Senior Prescription Engineer")
    st.markdown("**Eng. Mohamed Tarek** \n📞 +966570514091  \n📧 Mohamed.abdelwahab@elsewedy.com")
    st.markdown("---")
    st.subheader("📥 Downloads")
    pdf_path = "EE KSA Brochure.pdf"
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Download EE KSA Brochure", f,
                               file_name="Elsewedy_KSA_Brochure.pdf",
                               mime="application/pdf")

# ─────────────────────────────────────────────
# 6. Main UI
# ─────────────────────────────────────────────
display_logo(200)
st.title(" Elsewedy Electric Smart Tool")
st.markdown("---")

tab1, tab2 = st.tabs(["🔌 Cable Size Calculator", " Technical Support"])

with tab1:
    st.subheader("Cable Size Selection — Elsewedy Catalog ")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Load Data**")
        load_kw = st.number_input("Load (kW)", min_value=0.1, value=50.0, step=0.5)
        voltage_v = st.selectbox("System Voltage", [230, 400, 415], index=1)
        phases = st.radio("System Type", [3, 1], format_func=lambda x: "Three Phase (3Ø)" if x==3 else "Single Phase (1Ø)")
        pf = st.slider("Power Factor (cosφ)", 0.5, 1.0, 0.85, 0.01)

    with col2:
        st.markdown("**Cable & Installation**")
        length_m = st.number_input("Cable Length (m)", min_value=1.0, value=100.0, step=5.0)
        temp_c = st.selectbox("Ambient Temperature (°C)", [25, 30, 35, 40, 45, 50, 55], index=3)
        conductor = st.selectbox("Conductor Material", ["cu", "al"], format_func=lambda x: "Copper (Cu)" if x=="cu" else "Aluminium (Al)")
        insulation = st.selectbox("Insulation Type", ["xlpe", "pvc"], format_func=lambda x: "XLPE (90°C)" if x=="xlpe" else "PVC (70°C)")
        installation = st.selectbox("Installation Method", ["air", "ground", "duct"],
                                    format_func=lambda x: {"air":"In air / Tray", "ground":"Direct buried", "duct":"In duct"}[x])

    # New Section for Soil and Burial Depth
    if installation in ["ground", "duct"]:
        st.markdown("---")
        st.markdown("**Soil & Burial Conditions (Elsewedy LV Standard)**")
        sc1, sc2 = st.columns(2)
        with sc1:
            soil_thermal = st.selectbox("Soil Thermal Resistivity (K.m/W)", options=list(SOIL_THERMAL_MAP.keys()), index=1)
        with sc2:
            burial_depth = st.selectbox("Depth of Laying (m)", options=list(DEPTH_DIRECT_MAP.keys()), index=2)
    else:
        soil_thermal = 1.2
        burial_depth = 0.8

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        max_vdrop = st.selectbox("Max Voltage Drop (%)", [3.0, 5.0], index=1)
    with col4:
        num_cables = st.selectbox("Number of Cables (grouping)", [1,2,3,4,5,6], index=0)

    if st.button("⚡ Calculate Cable Size", use_container_width=True):
        res = select_cable(load_kw, voltage_v, phases, pf, length_m, temp_c, conductor, insulation, installation, max_vdrop, num_cables, soil_thermal, burial_depth)

        st.markdown("### Results")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Recommended Size", f"{res.size_mm2} mm²", f"{conductor.upper()} {insulation.upper()}")
        col_b.metric("Load Current", f"{res.full_load_current} A", f"Iz = {res.catalog_iz} A")
        col_c.metric("Voltage Drop", f"{res.voltage_drop_pct}%", f"{'✓ OK' if res.vdrop_ok else '✗ FAIL'}")

        st.markdown("**Calculation Details**")
        details = {
            "Temp derating factor": f"× {res.temp_derating}",
            "Group derating factor": f"× {res.group_derating}",
            "Soil Thermal derating": f"× {res.soil_thermal_derating}" if installation != "air" else "N/A",
            "Depth derating factor": f"× {res.depth_derating}" if installation != "air" else "N/A",
            "Effective capacity": f"{res.effective_capacity} A",
            "Voltage drop": f"{res.voltage_drop_v} V",
        }
        for k, v in details.items():
            c1, c2 = st.columns([2, 3])
            c1.markdown(f"<span style='color:#888'>{k}</span>", unsafe_allow_html=True)
            c2.markdown(f"**{v}**")

        if res.warnings:
            for w in res.warnings: st.warning(f"⚠ {w}")
        else:
            st.success("✓ Cable selection is within all limits.")

with tab2:
    st.subheader("🤖 AI Technical Support")
    query = st.text_input("Ask about cables, standards, or specifications:")
    if query and model:
        with st.spinner("AI is thinking..."):
            response = model.generate_content(query)
            st.write(response.text)

st.markdown("---")
st.caption("© 2026 Developed by Eng. Mohamed Tarek | Elsewedy Electric KSA")
