import streamlit as st
import google.generativeai as genai
import math
import os
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
        st.markdown("### ⚡ Elsewedy Electric")

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
            # page 78 — 3-core Cu/PVC/SWA armoured
            "air": [
                {"s": 4,    "Iz": 36},
                {"s": 6,    "Iz": 45},
                {"s": 10,   "Iz": 61},
                {"s": 16,   "Iz": 83},
                {"s": 25,   "Iz": 106},
                {"s": 35,   "Iz": 130},
                {"s": 50,   "Iz": 157},
                {"s": 70,   "Iz": 198},
                {"s": 95,   "Iz": 242},
                {"s": 120,  "Iz": 277},
                {"s": 150,  "Iz": 317},
                {"s": 185,  "Iz": 362},
                {"s": 240,  "Iz": 425},
                {"s": 300,  "Iz": 484},
            ],
            "ground": [
                {"s": 4,    "Iz": 45},
                {"s": 6,    "Iz": 58},
                {"s": 10,   "Iz": 78},
                {"s": 16,   "Iz": 97},
                {"s": 25,   "Iz": 129},
                {"s": 35,   "Iz": 156},
                {"s": 50,   "Iz": 188},
                {"s": 70,   "Iz": 231},
                {"s": 95,   "Iz": 276},
                {"s": 120,  "Iz": 314},
                {"s": 150,  "Iz": 350},
                {"s": 185,  "Iz": 394},
                {"s": 240,  "Iz": 454},
                {"s": 300,  "Iz": 507},
            ],
            "duct": [
                {"s": 4,    "Iz": 36},
                {"s": 6,    "Iz": 43},
                {"s": 10,   "Iz": 57},
                {"s": 16,   "Iz": 71},
                {"s": 25,   "Iz": 97},
                {"s": 35,   "Iz": 117},
                {"s": 50,   "Iz": 140},
                {"s": 70,   "Iz": 174},
                {"s": 95,   "Iz": 210},
                {"s": 120,  "Iz": 238},
                {"s": 150,  "Iz": 271},
                {"s": 185,  "Iz": 307},
                {"s": 240,  "Iz": 358},
                {"s": 300,  "Iz": 405},
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
            # page 76 & 98 — 3-core Al/PVC armoured
            "air": [
                {"s": 16,  "Iz": 60},
                {"s": 25,  "Iz": 80},
                {"s": 35,  "Iz": 98},
                {"s": 50,  "Iz": 118},
                {"s": 70,  "Iz": 148},
                {"s": 95,  "Iz": 184},
                {"s": 120, "Iz": 212},
                {"s": 150, "Iz": 242},
                {"s": 185, "Iz": 278},
                {"s": 240, "Iz": 330},
                {"s": 300, "Iz": 380},
            ],
            "ground": [
                {"s": 16,  "Iz": 77},
                {"s": 25,  "Iz": 103},
                {"s": 35,  "Iz": 125},
                {"s": 50,  "Iz": 150},
                {"s": 70,  "Iz": 190},
                {"s": 95,  "Iz": 231},
                {"s": 120, "Iz": 269},
                {"s": 150, "Iz": 304},
                {"s": 185, "Iz": 347},
                {"s": 240, "Iz": 413},
                {"s": 300, "Iz": 473},
            ],
            "duct": [
                {"s": 16,  "Iz": 57},
                {"s": 25,  "Iz": 75},
                {"s": 35,  "Iz": 92},
                {"s": 50,  "Iz": 111},
                {"s": 70,  "Iz": 140},
                {"s": 95,  "Iz": 171},
                {"s": 120, "Iz": 197},
                {"s": 150, "Iz": 225},
                {"s": 185, "Iz": 260},
                {"s": 240, "Iz": 308},
                {"s": 300, "Iz": 355},
            ],
        },
    },
}

# ─────────────────────────────────────────────
# 5. Derating Tables — Elsewedy Catalog
# ─────────────────────────────────────────────

TEMP_DERATING = {
    "xlpe": {15:1.15, 20:1.10, 25:1.05, 30:1.00,
              35:0.95, 40:0.90, 45:0.84, 50:0.78, 55:0.72},
    "pvc":  {15:1.21, 20:1.15, 25:1.07, 30:1.00,
              35:0.92, 40:0.84, 45:0.75, 50:0.66, 55:0.55},
}

GROUP_DERATING    = {1:1.00, 2:0.87, 3:0.79, 4:0.75, 5:0.72, 6:0.70}
SOIL_THERMAL_MAP  = {0.8:1.05, 1.0:1.03, 1.2:1.00, 1.5:0.92, 2.0:0.83, 2.5:0.76, 3.0:0.71}
DEPTH_DIRECT_MAP  = {0.5:1.00, 0.6:0.98, 0.8:0.96, 1.0:0.94, 1.25:0.92, 1.5:0.91}
DEPTH_DUCT_MAP    = {0.5:1.00, 0.6:0.98, 0.8:0.97, 1.0:0.96, 1.25:0.95, 1.5:0.94}

RESISTANCE = {
    "cu": {1.5:12.10, 2.5:7.41, 4:4.61, 6:3.08, 10:1.83, 16:1.15,
           25:0.727, 35:0.524, 50:0.387, 70:0.268, 95:0.193,
           120:0.153, 150:0.124, 185:0.0991, 240:0.0754, 300:0.0601},
    "al": {16:1.91, 25:1.20, 35:0.868, 50:0.641, 70:0.443, 95:0.320,
           120:0.253, 150:0.206, 185:0.164, 240:0.125, 300:0.100},
}
REACTANCE_DEFAULT = 0.08


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
    vdrop_ok: bool
    warnings: list


def get_temp_derating(insulation, temp_c):
    table = TEMP_DERATING[insulation]
    if temp_c in table:
        return table[temp_c]
    temps = sorted(table.keys())
    for i in range(len(temps) - 1):
        t1, t2 = temps[i], temps[i + 1]
        if t1 <= temp_c <= t2:
            return table[t1] + (table[t2] - table[t1]) * (temp_c - t1) / (t2 - t1)
    return table[temps[-1]]


def select_cable(load_kw, voltage_v, phases, pf, length_m,
                 temp_c, conductor, insulation, installation,
                 max_vdrop_pct, num_cables, soil_thermal, burial_depth):

    warnings = []
    sinpf = math.sqrt(max(0, 1 - pf ** 2))

    if phases == 3:
        IFL = (load_kw * 1000) / (math.sqrt(3) * voltage_v * pf)
    else:
        IFL = (load_kw * 1000) / (voltage_v * pf)

    t_derate  = get_temp_derating(insulation, temp_c)
    g_derate  = GROUP_DERATING.get(num_cables, 0.65)
    st_derate = 1.0
    d_derate  = 1.0

    if installation in ["ground", "duct"]:
        st_derate = SOIL_THERMAL_MAP.get(soil_thermal, 1.0)
        depth_map = DEPTH_DUCT_MAP if installation == "duct" else DEPTH_DIRECT_MAP
        d_derate  = depth_map.get(burial_depth, 1.0)

    total_derate = t_derate * g_derate * st_derate * d_derate
    I_required   = IFL / total_derate

    table  = CATALOG[conductor][insulation][installation]
    chosen = next((c for c in table if c["Iz"] >= I_required), None)

    if chosen is None:
        chosen = table[-1]
        warnings.append(
            f"Load ({I_required:.1f} A required) exceeds max catalog size "
            f"({table[-1]['Iz']} A). Consider parallel cables."
        )

    def vdrop(size):
        R   = RESISTANCE[conductor].get(size, 0.16)
        L   = length_m / 1000
        imp = R * pf + REACTANCE_DEFAULT * sinpf
        vd  = (math.sqrt(3) if phases == 3 else 2) * IFL * imp * L
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

    eff_cap = chosen["Iz"] * total_derate
    util    = (IFL / eff_cap * 100) if eff_cap > 0 else 0
    if util > 100:
        warnings.append(f"Cable utilisation {util:.1f}% exceeds rated capacity.")

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
# 7. Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    display_logo(150)
    st.markdown("### 👤 Senior Prescription Engineer")
    st.markdown("**Eng. Mohamed Tarek**  \n📞 +966570514091  \n📧 Mohamed.abdelwahab@elsewedy.com")
    st.markdown("---")
    st.subheader("📥 Downloads")
    pdf_path = "EE KSA Brochure.pdf"
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Download EE KSA Brochure", f,
                               file_name="Elsewedy_KSA_Brochure.pdf",
                               mime="application/pdf")

# ─────────────────────────────────────────────
# 8. Main UI
# ─────────────────────────────────────────────
display_logo(200)
st.title("⚡ Elsewedy Electric Smart Tool")
st.markdown("---")

tab1, tab2 = st.tabs(["🔌 Cable Size Calculator", "🤖 Technical Support"])

with tab1:
    st.subheader("Cable Size Selection — Elsewedy Catalog (IEC 60287 / IEC 60502)")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Load Data**")
        load_kw   = st.number_input("Load (kW)", min_value=0.1, value=50.0, step=0.5)
        voltage_v = st.selectbox("System Voltage", [230, 400, 415], index=1)
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
        insulation   = st.selectbox("Insulation Type", ["xlpe", "pvc"],
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
                options=list(SOIL_THERMAL_MAP.keys()), index=2,
                help="Wet soil ≈ 0.8 | Normal ≈ 1.2 | Dry sandy ≈ 2.5")
        with sc2:
            burial_depth = st.selectbox(
                "Depth of Laying (m)",
                options=list(DEPTH_DIRECT_MAP.keys()), index=2)

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        max_vdrop  = st.selectbox("Max Voltage Drop (%)", [3.0, 5.0], index=1)
    with col4:
        num_cables = st.selectbox("Number of Cables (grouping)", [1,2,3,4,5,6], index=0)

    if st.button("⚡ Calculate Cable Size", use_container_width=True):
        try:
            res = select_cable(
                load_kw, voltage_v, phases, pf, length_m,
                temp_c, conductor, insulation, installation,
                max_vdrop, num_cables, soil_thermal, burial_depth
            )

            st.markdown("---")
            st.markdown("### Results")

            cond_label = "Cu" if conductor == "cu" else "Al"
            ins_label  = insulation.upper()

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Recommended Size",  f"{res.size_mm2} mm²",
                         f"{cond_label} / {ins_label} / 3-core")
            col_b.metric("Full Load Current", f"{res.full_load_current} A",
                         f"Iz catalog = {res.catalog_iz} A")
            col_c.metric("Voltage Drop",      f"{res.voltage_drop_pct}%",
                         f"Limit {max_vdrop}% — {'✓ OK' if res.vdrop_ok else '✗ FAIL'}")

            show_soil = installation in ["ground", "duct"]
            st.markdown("**Calculation Details**")
            details = {
                "Temp derating factor":     f"× {res.temp_derating}  (at {temp_c}°C)",
                "Group derating factor":    f"× {res.group_derating}  ({num_cables} cable(s))",
                "Soil thermal derating":    f"× {res.soil_thermal_derating}" if show_soil else "N/A",
                "Burial depth derating":    f"× {res.depth_derating}" if show_soil else "N/A",
                "Effective cable capacity": f"{res.effective_capacity} A",
                "Cable utilisation":        f"{res.utilisation_pct}%",
                "Voltage drop":             f"{res.voltage_drop_v} V  ({res.voltage_drop_pct}%)",
                "Catalog reference":        "3-core multicore — IEC 60502 / IEC 60287",
            }
            for k, v in details.items():
                c1, c2 = st.columns([2, 3])
                c1.markdown(f"<span style='color:#666'>{k}</span>", unsafe_allow_html=True)
                c2.markdown(f"**{v}**")

            if res.warnings:
                for w in res.warnings:
                    st.warning(f"⚠ {w}")
            else:
                st.success("✓ Cable selection is within all limits.")

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
