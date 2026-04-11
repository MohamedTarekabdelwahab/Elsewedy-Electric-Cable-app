import streamlit as st
import google.generativeai as genai
import os

# 1. إعداد الصفحة (يجب أن يكون أول سطر)
st.set_page_config(page_title="Elsewedy Smart Tool", layout="wide", page_icon="⚡")

# 2. إعداد الـ API Key (ضع مفتاحك المقسم هنا)
part1 = "AIzaSyD2J9a9RXLKjkC-"
part2 = "cw12JR7zxz3t7oVSA-Q"

try:
    genai.configure(api_key=part1 + part2)
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if available_models:
        model = genai.GenerativeModel(available_models[0])
except Exception as e:
    st.error(f"Configuration Error: {e}")

# 3. تنسيق الألوان (خلفية أوف وايت وكلام أسود صريح)
st.markdown("""
    <style>
    .stApp {
        background-color: #F5F5F5; 
    }
    /* توحيد اللون الأسود لكل النصوص */
    .stApp, p, span, h1, h2, h3, h4, label, .stMarkdown, .stTextInput {
        color: #000000 !important;
    }
    /* تنسيق الخطوط */
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* تنسيق زر التحميل */
    .stDownloadButton button {
        background-color: #FF0000; /* أحمر السويدي */
        color: white !important;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. وظيفة عرض اللوجو بأمان
def display_logo(w):
    if os.path.exists("logo.png"):
        st.image("logo.png", width=w)
    else:
        st.warning("Logo (logo.png) not found on GitHub.")

# 5. القائمة الجانبية (Sidebar)
with st.sidebar:
    display_logo(150)
    st.markdown("### 👤 Senior Prescription Engineer")
    st.markdown("""
    **Eng. Mohamed Tarek** 📞 +966570514091  
    📧 Mohamed.abdelwahab@elsewedy.com
    """)
    
    st.markdown("---")
    st.subheader("📥 Downloads")
    
    # إضافة ملف الـ PDF في السايد بار
    pdf_path = "EE KSA Brochure.pdf"
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📄 Download EE KSA Brochure",
                data=f,
                file_name="Elsewedy_KSA_Brochure.pdf",
                mime="application/pdf"
            )
    else:
        st.error("Brochure PDF not found.")

# 6. الواجهة الرئيسية
display_logo(200)
st.title("⚡ Elsewedy Electric Smart Tool")
st.markdown("---")

# خانة السؤال
query = st.text_input("Ask our AI Technical Support about cables:", placeholder="e.g. What is the current carrying capacity of 4x16mm2 PVC cable?")

if query:
    with st.spinner("AI is thinking..."):
        try:
            response = model.generate_content(query)
            # عرض الإجابة
            st.markdown("### 🤖 Answer:")
            st.write(response.text)
            
            # الرسالة الختامية الثابتة بعد كل سؤال
            st.markdown("---")
            st.markdown("#### **For more information Please contact:**")
            st.success("""
            **Eng. Mohamed Tarek** 📞 +966570514091  
            📧 Mohamed.abdelwahab@elsewedy.com
            """)
        except Exception as e:
            st.error(f"Error: {e}")

"""
Cable Selection Tool — Based on Elsewedy Electric Catalog
Standard: IEC 60287 / IEC 60502-1
"""

import math
from dataclasses import dataclass
from typing import Optional


# ─────────────────────────────────────────────
#  Catalog Data — Elsewedy LV Power Cables
#  Current ratings (Iz) in Amperes — 3-core or
#  single-core trefoil, 0.6/1 kV
# ─────────────────────────────────────────────

CATALOG = {
    "cu": {
        "xlpe": {
            "air": [
                {"s": 1.5,  "Iz": 26},
                {"s": 2.5,  "Iz": 36},
                {"s": 4,    "Iz": 49},
                {"s": 6,    "Iz": 63},
                {"s": 10,   "Iz": 86},
                {"s": 16,   "Iz": 115},
                {"s": 25,   "Iz": 149},
                {"s": 35,   "Iz": 185},
                {"s": 50,   "Iz": 225},
                {"s": 70,   "Iz": 289},
                {"s": 95,   "Iz": 352},
                {"s": 120,  "Iz": 410},
                {"s": 150,  "Iz": 473},
                {"s": 185,  "Iz": 542},
                {"s": 240,  "Iz": 641},
                {"s": 300,  "Iz": 741},
            ],
            "ground": [
                {"s": 1.5,  "Iz": 25},
                {"s": 2.5,  "Iz": 33},
                {"s": 4,    "Iz": 44},
                {"s": 6,    "Iz": 56},
                {"s": 10,   "Iz": 75},
                {"s": 16,   "Iz": 100},
                {"s": 25,   "Iz": 127},
                {"s": 35,   "Iz": 158},
                {"s": 50,   "Iz": 192},
                {"s": 70,   "Iz": 241},
                {"s": 95,   "Iz": 292},
                {"s": 120,  "Iz": 339},
                {"s": 150,  "Iz": 388},
                {"s": 185,  "Iz": 443},
                {"s": 240,  "Iz": 520},
                {"s": 300,  "Iz": 598},
            ],
            "duct": [
                {"s": 1.5,  "Iz": 22},
                {"s": 2.5,  "Iz": 29},
                {"s": 4,    "Iz": 38},
                {"s": 6,    "Iz": 49},
                {"s": 10,   "Iz": 66},
                {"s": 16,   "Iz": 88},
                {"s": 25,   "Iz": 111},
                {"s": 35,   "Iz": 138},
                {"s": 50,   "Iz": 168},
                {"s": 70,   "Iz": 210},
                {"s": 95,   "Iz": 255},
                {"s": 120,  "Iz": 296},
                {"s": 150,  "Iz": 339},
                {"s": 185,  "Iz": 387},
                {"s": 240,  "Iz": 455},
                {"s": 300,  "Iz": 523},
            ],
        },
        "pvc": {
            "air": [
                {"s": 1.5,  "Iz": 19.5},
                {"s": 2.5,  "Iz": 27},
                {"s": 4,    "Iz": 36},
                {"s": 6,    "Iz": 46},
                {"s": 10,   "Iz": 63},
                {"s": 16,   "Iz": 85},
                {"s": 25,   "Iz": 110},
                {"s": 35,   "Iz": 137},
                {"s": 50,   "Iz": 167},
                {"s": 70,   "Iz": 214},
                {"s": 95,   "Iz": 261},
                {"s": 120,  "Iz": 303},
                {"s": 150,  "Iz": 349},
                {"s": 185,  "Iz": 400},
                {"s": 240,  "Iz": 470},
                {"s": 300,  "Iz": 545},
            ],
            "ground": [
                {"s": 1.5,  "Iz": 18},
                {"s": 2.5,  "Iz": 24},
                {"s": 4,    "Iz": 31},
                {"s": 6,    "Iz": 39},
                {"s": 10,   "Iz": 52},
                {"s": 16,   "Iz": 67},
                {"s": 25,   "Iz": 86},
                {"s": 35,   "Iz": 107},
                {"s": 50,   "Iz": 130},
                {"s": 70,   "Iz": 163},
                {"s": 95,   "Iz": 197},
                {"s": 120,  "Iz": 227},
                {"s": 150,  "Iz": 259},
                {"s": 185,  "Iz": 295},
                {"s": 240,  "Iz": 346},
                {"s": 300,  "Iz": 396},
            ],
            "duct": [
                {"s": 1.5,  "Iz": 16},
                {"s": 2.5,  "Iz": 21},
                {"s": 4,    "Iz": 27},
                {"s": 6,    "Iz": 34},
                {"s": 10,   "Iz": 46},
                {"s": 16,   "Iz": 62},
                {"s": 25,   "Iz": 78},
                {"s": 35,   "Iz": 97},
                {"s": 50,   "Iz": 118},
                {"s": 70,   "Iz": 148},
                {"s": 95,   "Iz": 179},
                {"s": 120,  "Iz": 207},
                {"s": 150,  "Iz": 236},
                {"s": 185,  "Iz": 270},
                {"s": 240,  "Iz": 317},
                {"s": 300,  "Iz": 364},
            ],
        },
    },
    "al": {
        "xlpe": {
            "air": [
                {"s": 16,  "Iz": 87},
                {"s": 25,  "Iz": 114},
                {"s": 35,  "Iz": 141},
                {"s": 50,  "Iz": 172},
                {"s": 70,  "Iz": 220},
                {"s": 95,  "Iz": 269},
                {"s": 120, "Iz": 312},
                {"s": 150, "Iz": 361},
                {"s": 185, "Iz": 412},
                {"s": 240, "Iz": 489},
                {"s": 300, "Iz": 565},
            ],
            "ground": [
                {"s": 16,  "Iz": 79},
                {"s": 25,  "Iz": 99},
                {"s": 35,  "Iz": 123},
                {"s": 50,  "Iz": 148},
                {"s": 70,  "Iz": 186},
                {"s": 95,  "Iz": 226},
                {"s": 120, "Iz": 261},
                {"s": 150, "Iz": 298},
                {"s": 185, "Iz": 340},
                {"s": 240, "Iz": 401},
                {"s": 300, "Iz": 461},
            ],
            "duct": [
                {"s": 16,  "Iz": 68},
                {"s": 25,  "Iz": 86},
                {"s": 35,  "Iz": 107},
                {"s": 50,  "Iz": 130},
                {"s": 70,  "Iz": 162},
                {"s": 95,  "Iz": 196},
                {"s": 120, "Iz": 228},
                {"s": 150, "Iz": 260},
                {"s": 185, "Iz": 296},
                {"s": 240, "Iz": 348},
                {"s": 300, "Iz": 400},
            ],
        },
        "pvc": {
            "air": [
                {"s": 16,  "Iz": 64},
                {"s": 25,  "Iz": 82},
                {"s": 35,  "Iz": 103},
                {"s": 50,  "Iz": 125},
                {"s": 70,  "Iz": 160},
                {"s": 95,  "Iz": 195},
                {"s": 120, "Iz": 226},
                {"s": 150, "Iz": 261},
                {"s": 185, "Iz": 298},
                {"s": 240, "Iz": 352},
                {"s": 300, "Iz": 406},
            ],
            "ground": [
                {"s": 16,  "Iz": 57},
                {"s": 25,  "Iz": 73},
                {"s": 35,  "Iz": 90},
                {"s": 50,  "Iz": 110},
                {"s": 70,  "Iz": 138},
                {"s": 95,  "Iz": 167},
                {"s": 120, "Iz": 193},
                {"s": 150, "Iz": 220},
                {"s": 185, "Iz": 250},
                {"s": 240, "Iz": 294},
                {"s": 300, "Iz": 337},
            ],
            "duct": [
                {"s": 16,  "Iz": 52},
                {"s": 25,  "Iz": 66},
                {"s": 35,  "Iz": 82},
                {"s": 50,  "Iz": 99},
                {"s": 70,  "Iz": 124},
                {"s": 95,  "Iz": 150},
                {"s": 120, "Iz": 174},
                {"s": 150, "Iz": 198},
                {"s": 185, "Iz": 226},
                {"s": 240, "Iz": 265},
                {"s": 300, "Iz": 304},
            ],
        },
    },
}

# ─────────────────────────────────────────────
#  Derating Factors — Elsewedy Catalog Tables
# ─────────────────────────────────────────────

# Table 3 — Air temperature derating (ambient base = 30°C)
TEMP_DERATING = {
    "xlpe": {15: 1.15, 20: 1.10, 25: 1.05, 30: 1.00,
              35: 0.95, 40: 0.90, 45: 0.84, 50: 0.78, 55: 0.72},
    "pvc":  {15: 1.21, 20: 1.15, 25: 1.07, 30: 1.00,
              35: 0.92, 40: 0.84, 45: 0.75, 50: 0.66, 55: 0.55},
}

# Table 9 — Grouping derating (cables touching, in air)
GROUP_DERATING = {1: 1.00, 2: 0.87, 3: 0.79, 4: 0.75, 5: 0.72, 6: 0.70}

# Conductor DC resistance at 20°C (Ω/km) — IEC 60228
RESISTANCE = {
    "cu": {1.5: 12.10, 2.5: 7.41, 4: 4.61, 6: 3.08, 10: 1.83,
           16: 1.15, 25: 0.727, 35: 0.524, 50: 0.387, 70: 0.268,
           95: 0.193, 120: 0.153, 150: 0.124, 185: 0.0991,
           240: 0.0754, 300: 0.0601},
    "al": {16: 1.91, 25: 1.20, 35: 0.868, 50: 0.641, 70: 0.443,
           95: 0.320, 120: 0.253, 150: 0.206, 185: 0.164,
           240: 0.125, 300: 0.100},
}

# Approx reactance for LV multicore cables (Ω/km)
REACTANCE_DEFAULT = 0.08


# ─────────────────────────────────────────────
#  Data Classes
# ─────────────────────────────────────────────

@dataclass
class CableInput:
    load_kw: float          # Load in kilowatts
    voltage_v: float        # System voltage (e.g. 400)
    phases: int             # 1 = single phase, 3 = three phase
    power_factor: float     # cosφ (0.5 – 1.0)
    length_m: float         # Cable run in metres
    ambient_temp_c: int     # Ambient temperature in °C
    conductor: str          # "cu" or "al"
    insulation: str         # "xlpe" or "pvc"
    installation: str       # "air", "ground", or "duct"
    max_vdrop_pct: float    # Allowable voltage drop % (typically 3 or 5)
    num_cables: int = 1     # Number of cables for grouping derating


@dataclass
class CableResult:
    size_mm2: float
    catalog_iz: float
    full_load_current: float
    temp_derating: float
    group_derating: float
    effective_capacity: float
    utilisation_pct: float
    voltage_drop_v: float
    voltage_drop_pct: float
    resistance_ohm_km: float
    vdrop_ok: bool
    warnings: list


# ─────────────────────────────────────────────
#  Core Calculation Functions
# ─────────────────────────────────────────────

def calc_full_load_current(load_kw: float, voltage_v: float,
                            phases: int, pf: float) -> float:
    """Calculate full load current in Amperes."""
    if phases == 3:
        return (load_kw * 1000) / (math.sqrt(3) * voltage_v * pf)
    else:
        return (load_kw * 1000) / (voltage_v * pf)


def get_temp_derating(insulation: str, temp_c: int) -> float:
    """Return temperature derating factor from Elsewedy catalog Table 3."""
    table = TEMP_DERATING[insulation]
    if temp_c in table:
        return table[temp_c]
    # Interpolate between nearest steps
    temps = sorted(table.keys())
    for i in range(len(temps) - 1):
        t1, t2 = temps[i], temps[i + 1]
        if t1 <= temp_c <= t2:
            f1, f2 = table[t1], table[t2]
            return f1 + (f2 - f1) * (temp_c - t1) / (t2 - t1)
    return table[temps[-1]]


def get_group_derating(num_cables: int) -> float:
    """Return grouping derating factor from Elsewedy catalog Table 9."""
    if num_cables in GROUP_DERATING:
        return GROUP_DERATING[num_cables]
    if num_cables > 6:
        return 0.65  # Conservative estimate beyond catalog range
    return 1.0


def calc_voltage_drop(current_a: float, length_m: float,
                       resistance_ohm_km: float, reactance_ohm_km: float,
                       pf: float, voltage_v: float, phases: int) -> tuple:
    """
    Calculate voltage drop per IEC 60287 Section 9.
    Returns (Vdrop_volts, Vdrop_percent).
    """
    sinpf = math.sqrt(max(0, 1 - pf ** 2))
    L_km = length_m / 1000.0
    impedance = resistance_ohm_km * pf + reactance_ohm_km * sinpf

    if phases == 3:
        vd_v = math.sqrt(3) * current_a * impedance * L_km
    else:
        vd_v = 2 * current_a * impedance * L_km

    vd_pct = (vd_v / voltage_v) * 100
    return round(vd_v, 3), round(vd_pct, 3)


def select_cable(inp: CableInput) -> CableResult:
    """
    Main cable selection function.
    1. Calculate FLC
    2. Apply derating factors
    3. Select minimum size from catalog by ampacity
    4. Check voltage drop — upsize if needed
    5. Return full result
    """
    warnings = []

    # Validate inputs
    if inp.conductor not in ("cu", "al"):
        raise ValueError("conductor must be 'cu' or 'al'")
    if inp.insulation not in ("xlpe", "pvc"):
        raise ValueError("insulation must be 'xlpe' or 'pvc'")
    if inp.installation not in ("air", "ground", "duct"):
        raise ValueError("installation must be 'air', 'ground', or 'duct'")
    if not (0.5 <= inp.power_factor <= 1.0):
        raise ValueError("power_factor must be between 0.5 and 1.0")

    # Step 1 — Full load current
    IFL = calc_full_load_current(
        inp.load_kw, inp.voltage_v, inp.phases, inp.power_factor
    )

    # Step 2 — Derating factors
    t_derate = get_temp_derating(inp.insulation, inp.ambient_temp_c)
    g_derate = get_group_derating(inp.num_cables)
    total_derate = t_derate * g_derate

    # Current the cable must carry after derating
    I_required = IFL / total_derate

    # Step 3 — Select from catalog by ampacity
    table = CATALOG[inp.conductor][inp.insulation][inp.installation]
    chosen = next((c for c in table if c["Iz"] >= I_required), None)

    if chosen is None:
        chosen = table[-1]
        warnings.append(
            f"Load ({I_required:.1f} A required) exceeds maximum catalog size "
            f"({table[-1]['Iz']} A). Consider parallel cables."
        )

    # Step 4 — Check voltage drop, upsize if needed
    resist_table = RESISTANCE[inp.conductor]

    def get_vdrop(size):
        R = resist_table.get(size, REACTANCE_DEFAULT * 2)
        _, vd_pct = calc_voltage_drop(
            IFL, inp.length_m, R, REACTANCE_DEFAULT,
            inp.power_factor, inp.voltage_v, inp.phases
        )
        return vd_pct

    vd_pct = get_vdrop(chosen["s"])

    if vd_pct > inp.max_vdrop_pct:
        original_size = chosen["s"]
        for cable in table:
            if cable["Iz"] >= I_required:
                candidate_vd = get_vdrop(cable["s"])
                if candidate_vd <= inp.max_vdrop_pct:
                    chosen = cable
                    break
        if chosen["s"] == original_size:
            warnings.append(
                f"Voltage drop ({vd_pct:.2f}%) exceeds limit ({inp.max_vdrop_pct}%). "
                "Consider shorter cable run or splitting the circuit."
            )

    # Final values
    R_final = resist_table.get(chosen["s"], REACTANCE_DEFAULT * 2)
    vd_v, vd_pct_final = calc_voltage_drop(
        IFL, inp.length_m, R_final, REACTANCE_DEFAULT,
        inp.power_factor, inp.voltage_v, inp.phases
    )
    effective_cap = chosen["Iz"] * total_derate
    utilisation = (IFL / effective_cap) * 100 if effective_cap > 0 else 0

    if utilisation > 100:
        warnings.append(
            f"Cable utilisation is {utilisation:.1f}% — exceeds rated capacity."
        )

    return CableResult(
        size_mm2=chosen["s"],
        catalog_iz=chosen["Iz"],
        full_load_current=round(IFL, 2),
        temp_derating=round(t_derate, 3),
        group_derating=round(g_derate, 3),
        effective_capacity=round(effective_cap, 2),
        utilisation_pct=round(utilisation, 1),
        voltage_drop_v=vd_v,
        voltage_drop_pct=vd_pct_final,
        resistance_ohm_km=R_final,
        vdrop_ok=vd_pct_final <= inp.max_vdrop_pct,
        warnings=warnings,
    )


# ─────────────────────────────────────────────
#  Report Printer
# ─────────────────────────────────────────────

def print_report(inp: CableInput, res: CableResult) -> None:
    """Print a formatted cable selection report."""
    cond_name = "Copper (Cu)" if inp.conductor == "cu" else "Aluminium (Al)"
    ins_name  = inp.insulation.upper()
    inst_name = {"air": "In air / cable tray",
                 "ground": "Direct buried",
                 "duct": "In underground duct"}[inp.installation]
    phase_str = f"{inp.phases}Ø"

    print("=" * 55)
    print("  CABLE SELECTION REPORT — Elsewedy Electric Catalog")
    print("  Standard: IEC 60287 / IEC 60502-1")
    print("=" * 55)

    print("\n  INPUT DATA")
    print(f"  {'Load':<30} {inp.load_kw} kW")
    print(f"  {'Voltage':<30} {inp.voltage_v} V  ({phase_str})")
    print(f"  {'Power factor':<30} {inp.power_factor}")
    print(f"  {'Cable length':<30} {inp.length_m} m")
    print(f"  {'Ambient temperature':<30} {inp.ambient_temp_c} °C")
    print(f"  {'Conductor':<30} {cond_name}")
    print(f"  {'Insulation':<30} {ins_name}")
    print(f"  {'Installation':<30} {inst_name}")
    print(f"  {'Max voltage drop':<30} {inp.max_vdrop_pct}%")
    print(f"  {'Number of cables':<30} {inp.num_cables}")

    print("\n  RESULTS")
    print(f"  {'Recommended cable size':<30} {res.size_mm2} mm²")
    print(f"  {'Catalog ampacity (Iz)':<30} {res.catalog_iz} A")
    print(f"  {'Full load current (IFL)':<30} {res.full_load_current} A")
    print(f"  {'Temp derating factor':<30} × {res.temp_derating}")
    print(f"  {'Group derating factor':<30} × {res.group_derating}")
    print(f"  {'Effective capacity':<30} {res.effective_capacity} A")
    print(f"  {'Cable utilisation':<30} {res.utilisation_pct}%")
    print(f"  {'Voltage drop':<30} {res.voltage_drop_v} V  "
          f"({res.voltage_drop_pct}%)")
    vd_status = "PASS ✓" if res.vdrop_ok else "FAIL ✗"
    print(f"  {'Voltage drop check':<30} {vd_status}")

    if res.warnings:
        print("\n  WARNINGS")
        for w in res.warnings:
            print(f"  ⚠  {w}")

    print("=" * 55)


# ─────────────────────────────────────────────
#  Example Usage
# ─────────────────────────────────────────────

if __name__ == "__main__":

    project = CableInput(
        load_kw=75,
        voltage_v=400,
        phases=3,
        power_factor=0.85,
        length_m=120,
        ambient_temp_c=40,
        conductor="cu",
        insulation="xlpe",
        installation="air",
        max_vdrop_pct=5.0,
        num_cables=1,
    )

    result = select_cable(project)
    print_report(project, result)

    # Access results programmatically
    print(f"\nSelected size : {result.size_mm2} mm²")
    print(f"Voltage drop  : {result.voltage_drop_pct}%")
    print(f"Utilisation   : {result.utilisation_pct}%")

# Footer
st.markdown("---")
st.caption("© 2026 Developed by Eng. Mohamed Tarek | Elsewedy Electric KSA")
