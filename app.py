import streamlit as st
import httpx
import pandas as pd

# =============================================================================
# Page Configuration
# =============================================================================
st.set_page_config(
    page_title="AI-PLC Delta AS228 Studio",
    page_icon="⚡",
    layout="wide"
)

# =============================================================================
# Design Tokens + Custom CSS (Premium Industrial Theme)
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --color-bg: #F8FAFC;
        --color-surface: #FFFFFF;
        --color-border: #E2E8F0;
        --color-border-strong: #CBD5E1;
        --color-text-primary: #0F172A;
        --color-text-secondary: #475569;
        --color-text-muted: #94A3B8;
        --color-accent: #2563EB;
        --color-accent-soft: #EFF6FF;
        --color-success: #15803D;
        --color-success-bg: #F0FDF4;
        --color-success-border: #86EFAC;
        --color-danger: #B91C1C;
        --color-danger-bg: #FEF2F2;
        --color-danger-border: #FCA5A5;
        --radius-sm: 6px;
        --radius-md: 10px;
        --radius-lg: 14px;
        --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.04);
        --shadow-md: 0 4px 16px rgba(15, 23, 42, 0.06);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    .stApp {
        background-color: var(--color-bg);
    }

    /* ---------- Hero Header ---------- */
    .app-hero {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 60%, #1E3A8A 100%);
        border-radius: var(--radius-lg);
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: var(--shadow-md);
    }
    .app-hero-eyebrow {
        color: #93C5FD;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .app-hero-title {
        color: #FFFFFF;
        font-size: 28px;
        font-weight: 800;
        margin: 0 0 6px 0;
        letter-spacing: -0.3px;
    }
    .app-hero-subtitle {
        color: #CBD5E1;
        font-size: 14px;
        font-weight: 400;
        margin: 0;
    }
    .app-hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.15);
        color: #E2E8F0;
        font-size: 12px;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 999px;
        margin-top: 12px;
    }

    /* ---------- Section Cards ---------- */
    .section-card {
        background: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-md);
        padding: 20px 22px;
        margin-bottom: 18px;
        box-shadow: var(--shadow-sm);
    }
    .section-title {
        font-size: 15px;
        font-weight: 700;
        color: var(--color-text-primary);
        margin: 0 0 4px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-subtitle {
        font-size: 12.5px;
        color: var(--color-text-muted);
        margin-bottom: 14px;
    }

    /* ---------- Ladder Rendering ---------- */
    .rung-header {
        font-family: 'Inter', sans-serif;
        color: var(--color-text-primary);
        margin-top: 22px;
        margin-bottom: 4px;
        font-weight: 600;
        font-size: 13.5px;
        background-color: var(--color-accent-soft);
        padding: 8px 14px;
        border-radius: var(--radius-sm);
        border-left: 3px solid var(--color-accent);
    }
    .ladder-rail-container {
        border-left: 6px solid var(--color-text-primary);
        border-right: 6px solid var(--color-text-primary);
        background-color: var(--color-surface);
        padding: 26px 20px;
        margin-top: 4px;
        border-radius: 4px;
        box-shadow: inset 2px 0px 6px rgba(0,0,0,0.04);
    }
    .ladder-svg-wrapper {
        background-color: var(--color-surface);
        border: 1px solid var(--color-border);
        padding: 14px;
        border-radius: var(--radius-sm);
        margin-bottom: 16px;
    }

    /* ---------- Status Banners ---------- */
    .status-banner {
        border-radius: var(--radius-md);
        padding: 16px 18px;
        margin-bottom: 4px;
        font-family: 'Inter', sans-serif;
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    .status-banner.pass {
        background-color: var(--color-success-bg);
        border: 1px solid var(--color-success-border);
    }
    .status-banner.fail {
        background-color: var(--color-danger-bg);
        border: 1px solid var(--color-danger-border);
    }
    .status-icon {
        font-size: 20px;
        line-height: 1;
        margin-top: 1px;
    }
    .status-title-pass {
        color: var(--color-success);
        font-weight: 700;
        font-size: 14px;
        margin: 0 0 2px 0;
    }
    .status-title-fail {
        color: var(--color-danger);
        font-weight: 700;
        font-size: 14px;
        margin: 0 0 4px 0;
    }
    .status-body {
        color: var(--color-text-secondary);
        font-size: 13px;
        margin: 0;
        line-height: 1.5;
    }
    .status-body ul {
        margin: 6px 0 0 0;
        padding-left: 18px;
    }

    /* Legacy class names kept as aliases so nothing else breaks visually */
    .safety-pass {
        background-color: var(--color-success-bg);
        border-left: 5px solid var(--color-success);
        padding: 15px;
        border-radius: var(--radius-sm);
        color: #14532D;
        font-family: 'Inter', sans-serif;
    }
    .safety-fail {
        background-color: var(--color-danger-bg);
        border-left: 5px solid var(--color-danger);
        padding: 15px;
        border-radius: var(--radius-sm);
        color: #7F1D1D;
        font-family: 'Inter', sans-serif;
    }

    /* ---------- Empty State ---------- */
    .empty-state {
        border: 1.5px dashed var(--color-border-strong);
        border-radius: var(--radius-lg);
        padding: 48px 32px;
        text-align: center;
        background: var(--color-surface);
    }
    .empty-state-icon {
        font-size: 34px;
        margin-bottom: 12px;
    }
    .empty-state-title {
        font-size: 16px;
        font-weight: 700;
        color: var(--color-text-primary);
        margin-bottom: 6px;
    }
    .empty-state-body {
        font-size: 13px;
        color: var(--color-text-muted);
        max-width: 420px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* ---------- Example Prompt Chips ---------- */
    .chip-label {
        font-size: 12px;
        font-weight: 600;
        color: var(--color-text-muted);
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin: 4px 0 8px 0;
    }
    div[data-testid="stButton"] > button {
        border-radius: var(--radius-sm) !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
    }
    div[data-testid="stButton"] > button:hover {
        border-color: var(--color-accent) !important;
        color: var(--color-accent) !important;
    }

    /* ---------- Pipeline Progress ---------- */
    .pipeline-step {
        font-size: 12.5px;
        color: var(--color-text-secondary);
        padding: 2px 0;
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background-color: #FFFFF;
    }
    section[data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] .stTextInput input {
        color: #FFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# Hero Header
# =============================================================================

import streamlit as st

st.set_page_config(
    page_title="AI PLC-GenStudio",
    page_icon="app.ico",
    layout="wide"
)
st.markdown("""
<div class="app-hero">
    <div class="app-hero-eyebrow">Scientech Technologies Private Limited · Industrial Automation</div>
    <div class="app-hero-title">⚡ AI PLC-GenStudio</div>
    <p class="app-hero-subtitle">Delta AS228 R/T · Deterministic Ladder Logic Generation & Hardware-Bound Validation</p>
    <span class="app-hero-badge">🟢 Alpha Release</span>
</div>
""", unsafe_allow_html=True)

# Sidebar for Technical Configuration
with st.sidebar:
    st.markdown("### ⚙️ Hardware Profile")
    st.markdown(
        """<div style="background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.12);
        border-radius:8px; padding:10px 12px; font-size:13px; margin-bottom:14px;">
        🎯 Device Target<br><strong>Delta AS228 R/T</strong></div>""",
        unsafe_allow_html=True
    )

    with st.expander("🔧 Developer / Connection Settings"):
        backend_url = st.text_input("Backend API Gateway", value="https://ai-plc-genstudio.onrender.com/api/v1/generate")

    st.markdown("---")
    st.markdown("### 🏭 Delta Device Syntax Bounds")
    st.markdown("""
    | Type | Range |
    |---|---|
    | Digital In (`X`) | `X0.0` – `X63.15` |
    | Digital Out (`Y`) | `Y0.0` – `Y63.15` |
    | Internal Bits (`M`) | `M0` – `M8191` |
    | Data Registers (`D`) | `D0` – `D29999` |
    """)

    st.markdown(
        """<div style="margin-top:24px; padding-top:14px; border-top:1px solid rgba(255,255,255,0.1);
        font-size:11px; color:#94A3B8;">
        © Scientech Technologies Private Limited<br>Built for internal alpha release</div>""",
        unsafe_allow_html=True
    )

# resolve_element
def resolve_element(element: dict, variable_lookup: dict) -> dict:
    """
    Resolves metadata. Priority for description: meta.description -> label (identifier)
    """
    identifier = (
        element.get("variable_name")
        or element.get("name")
        or element.get("address")
        or ""
    )

    meta = variable_lookup.get(identifier, {})

    return {
        "type": str(element.get("type", "CONTACT")).upper(),
        "address": meta.get("address", identifier),
        "label": identifier,
        "description": meta.get("description") or identifier,
    }

# =============================================================================
# DETAILED SVG RENDERING CONTROLLER (EXACT DELTA ISPSoft TMR STYLE)
# =============================================================================

ELEMENT_SPACING = 18

def render_timer_block(cx: int, y_line: int, comp: dict, variable_lookup: dict) -> tuple[str, int]:
    c = resolve_element(comp, variable_lookup)
    timer_addr = c.get("address") or comp.get("variable_name") or comp.get("address") or "T0"
    
    raw_preset = comp.get("preset_time") or comp.get("preset") or "100"
    preset_val = str(raw_preset).replace("T#", "").replace("s", "").strip()
    if not preset_val.startswith("K") and preset_val.isdigit():
        preset_val = f"{preset_val}"
    
    box_w = 95
    box_h = 75
    box_y = y_line - 37
    
    parts = []
    parts.append(f'<line x1="{cx}" y1="{y_line}" x2="{cx + 15}" y2="{y_line}" style="stroke:#0F172A;stroke-width:2" />')
    
    bx = cx + 15
    parts.append(f'<rect x="{bx}" y="{box_y}" width="{box_w}" height="{box_h}" fill="#FFFFFF" stroke="#0F172A" stroke-width="2" rx="2" />')
    parts.append(f'<text x="{bx + 35}" y="{box_y + 18}" font-size="11" font-family="sans-serif" font-weight="bold" fill="#0F172A">TMR</text>')
    parts.append(f'<line x1="{bx}" y1="{box_y + 24}" x2="{bx + box_w}" y2="{box_y + 24}" style="stroke:#0F172A;stroke-width:1" />')
    
    parts.append(f'<text x="{bx + 6}" y="{box_y + 40}" font-size="9" font-family="sans-serif" fill="#1E293B">En</text>')
    parts.append(f'<text x="{bx + 6}" y="{box_y + 56}" font-size="9" font-family="sans-serif" fill="#1E293B">S1</text>')
    parts.append(f'<text x="{bx + 6}" y="{box_y + 70}" font-size="9" font-family="sans-serif" fill="#1E293B">S2</text>')
    
    parts.append(f'<rect x="{bx + 40}" y="{box_y + 44}" width="48" height="14" fill="#FFFFFF" stroke="#64748B" stroke-width="1" />')
    parts.append(f'<text x="{bx + 44}" y="{box_y + 55}" font-size="9" font-family="monospace" fill="#0F172A">{timer_addr}</text>')
    
    parts.append(f'<rect x="{bx + 40}" y="{box_y + 60}" width="48" height="14" fill="#FFFFFF" stroke="#64748B" stroke-width="1" />')
    parts.append(f'<text x="{bx + 44}" y="{box_y + 71}" font-size="9" font-family="monospace" fill="#0F172A">{preset_val}</text>')
    
    exit_x = bx + box_w
    parts.append(f'<line x1="{exit_x}" y1="{y_line}" x2="{exit_x + ELEMENT_SPACING}" y2="{y_line}" style="stroke:#0F172A;stroke-width:2" />')
    
    new_x = exit_x + ELEMENT_SPACING
    return "".join(parts), new_x


def render_rung_svg(rung: dict, variable_lookup: dict) -> str:
    series_elements = rung.get("series_elements") or []
    parallel_raw = rung.get("parallel_branches") or []
    parallel_branches = [b for b in parallel_raw if b]
    
    output_coil = rung.get("output_coil")
    if output_coil:
        coils_in_rung = [output_coil]
        remaining_series = series_elements
    else:
        coils_in_rung = [e for e in series_elements if "COIL" in resolve_element(e, variable_lookup)["type"]]
        if not coils_in_rung and parallel_branches:
            flat_parallel = [item for sublist in parallel_branches for item in (sublist if isinstance(sublist, list) else [sublist])]
            coils_in_rung = [e for e in flat_parallel if "COIL" in resolve_element(e, variable_lookup)["type"]]
        remaining_series = [e for e in series_elements if "COIL" not in resolve_element(e, variable_lookup)["type"]]

    has_parallel = len(parallel_branches) > 0
    
    svg_h = 190 if has_parallel else 120
    y_line = 60
    parts = []
    
    parts.append(f'<svg width="100%" height="{svg_h}" viewBox="0 0 520 {svg_h}" preserveAspectRatio="xMidYMid meet" style="background-color: #FFFFFF;">')
    
    parts.append(f'<line x1="10" y1="0" x2="10" y2="{svg_h}" style="stroke:#0F172A;stroke-width:3" />')
    parts.append(f'<line x1="510" y1="0" x2="510" y2="{svg_h}" style="stroke:#0F172A;stroke-width:3" />')
    
    parts.append(f'<line x1="10" y1="{y_line}" x2="40" y2="{y_line}" style="stroke:#0F172A;stroke-width:2" />')
    current_x = 40
    
    if has_parallel:
        parts.append(f'<line x1="{current_x}" y1="{y_line}" x2="{current_x}" y2="{y_line + 70}" style="stroke:#0F172A;stroke-width:2" />')
        parts.append(f'<line x1="{current_x}" y1="{y_line}" x2="{current_x + 15}" y2="{y_line}" style="stroke:#0F172A;stroke-width:2" />')
        
        top_comp = remaining_series[0] if remaining_series else {"type": "NO_CONTACT"}
        top = resolve_element(top_comp, variable_lookup)
        
        t_cx = current_x + 15
        parts.append(f'<line x1="{t_cx}" y1="{y_line - 15}" x2="{t_cx}" y2="{y_line + 15}" style="stroke:#0F172A;stroke-width:2" />')
        parts.append(f'<line x1="{t_cx + 8}" y1="{y_line - 15}" x2="{t_cx + 8}" y2="{y_line + 15}" style="stroke:#0F172A;stroke-width:2" />')
        parts.append(f'<text x="{t_cx - 4}" y="{y_line - 22}" font-size="11" font-family="monospace" font-weight="bold" fill="#1E293B">{top["address"]}</text>')
        parts.append(f'<text x="{t_cx - 10}" y="{y_line + 26}" font-size="9" font-family="sans-serif" fill="#64748B">{top["description"]}</text>')
        parts.append(f'<line x1="{t_cx + 8}" y1="{y_line}" x2="{current_x + 105}" y2="{y_line}" style="stroke:#0F172A;stroke-width:2" />')
        
        parts.append(f'<line x1="{current_x}" y1="{y_line + 70}" x2="{current_x + 15}" y2="{y_line + 70}" style="stroke:#0F172A;stroke-width:2" />')
        
        p_branch = parallel_branches[0]
        p_comp = p_branch[0] if isinstance(p_branch, list) and len(p_branch) > 0 else p_branch
        p = resolve_element(p_comp, variable_lookup)
        
        b_cx = current_x + 15
        parts.append(f'<line x1="{b_cx}" y1="{y_line + 55}" x2="{b_cx}" y2="{y_line + 85}" style="stroke:#0F172A;stroke-width:2" />')
        if "NC" in p["type"] or "NOT" in p["type"]:
            parts.append(f'<line x1="{b_cx - 3}" y1="{y_line + 82}" x2="{b_cx + 11}" y2="{y_line + 58}" style="stroke:#B91C1C;stroke-width:2" />')
        parts.append(f'<line x1="{b_cx + 8}" y1="{y_line + 55}" x2="{b_cx + 8}" y2="{y_line + 85}" style="stroke:#0F172A;stroke-width:2" />')
        parts.append(f'<text x="{b_cx - 4}" y="{y_line + 50}" font-size="11" font-family="monospace" font-weight="bold" fill="#1E293B">{p["address"]}</text>')
        parts.append(f'<text x="{b_cx - 10}" y="{y_line + 98}" font-size="9" font-family="sans-serif" fill="#64748B">{p["description"]}</text>')
        parts.append(f'<line x1="{b_cx + 8}" y1="{y_line + 70}" x2="{current_x + 105}" y2="{y_line + 70}" style="stroke:#0F172A;stroke-width:2" />')
        parts.append(f'<line x1="{current_x + 105}" y1="{y_line + 70}" x2="{current_x + 105}" y2="{y_line}" style="stroke:#0F172A;stroke-width:2" />')
        
        current_x += 105
        remaining_series = [e for e in remaining_series if e != top_comp]
    
    for comp in remaining_series:
        c_type = str(comp.get("type", "")).upper()
        
        if "TIMER" in c_type or "TMR" in c_type or "TON" in c_type or "TOF" in c_type or "CTU" in c_type:
            timer_svg, current_x = render_timer_block(current_x, y_line, comp, variable_lookup)
            parts.append(timer_svg)
        else:
            c = resolve_element(comp, variable_lookup)
            symbol_width = 35
            
            contact_start_x = current_x
            parts.append(f'<line x1="{contact_start_x}" y1="{y_line - 15}" x2="{contact_start_x}" y2="{y_line + 15}" style="stroke:#0F172A;stroke-width:2" />')
            if "NC" in c["type"] or "NOT" in c["type"]:
                parts.append(f'<line x1="{contact_start_x - 3}" y1="{y_line + 12}" x2="{contact_start_x + 11}" y2="{y_line - 12}" style="stroke:#B91C1C;stroke-width:2" />')
            parts.append(f'<line x1="{contact_start_x + 8}" y1="{y_line - 15}" x2="{contact_start_x + 8}" y2="{y_line + 15}" style="stroke:#0F172A;stroke-width:2" />')
            parts.append(f'<text x="{contact_start_x - 4}" y="{y_line - 22}" font-size="11" font-family="monospace" font-weight="bold" fill="#0F172A">{c["address"]}</text>')
            parts.append(f'<text x="{contact_start_x - 10}" y="{y_line + 28}" font-size="9" font-family="sans-serif" fill="#64748B">{c["description"]}</text>')
            
            addr_text_width = len(str(c.get("address", ""))) * 7
            desc_text_width = len(str(c.get("description", ""))) * 5.5
            occupied_width = max(
                symbol_width + 8,
                addr_text_width + 12,
                desc_text_width + 5
            )
            
            terminal_end_x = contact_start_x + symbol_width
            next_element_start_x = contact_start_x + occupied_width + ELEMENT_SPACING
            
            parts.append(f'<line x1="{current_x}" y1="{y_line}" x2="{next_element_start_x}" y2="{y_line}" style="stroke:#0F172A;stroke-width:2" />')
            current_x = next_element_start_x

    has_timer_coil = False
    if coils_in_rung:
        c_coil = resolve_element(coils_in_rung[0], variable_lookup)
        c_coil_type = str(c_coil.get("type", "")).upper()
        c_coil_addr = str(c_coil.get("address", "")).upper()
        if "TIMER" in c_coil_type or "TMR" in c_coil_type or "TON" in c_coil_type or c_coil_addr.startswith("T"):
            has_timer_coil = True

    if coils_in_rung and not has_timer_coil:
        parts.append(f'<line x1="{current_x}" y1="{y_line}" x2="435" y2="{y_line}" style="stroke:#0F172A;stroke-width:2" />')
        c = resolve_element(coils_in_rung[0], variable_lookup)
        parts.append(f'<path d="M 435 {y_line - 15} Q 428 {y_line} 435 {y_line + 15}" stroke="#0F172A" stroke-width="2" fill="none"/>')
        parts.append(f'<path d="M 450 {y_line - 15} Q 457 {y_line} 450 {y_line + 15}" stroke="#0F172A" stroke-width="2" fill="none"/>')
        
        if "SET" in c["type"] or "LATCH" in c["type"]:
            parts.append(f'<text x="439" y="{y_line + 4}" font-size="10" font-family="sans-serif" font-weight="bold">S</text>')
        elif "RESET" in c["type"] or "UNLATCH" in c["type"]:
            parts.append(f'<text x="439" y="{y_line + 4}" font-size="10" font-weight="bold">R</text>')
        
        parts.append(f'<text x="427" y="{y_line - 22}" font-size="11" font-family="monospace" font-weight="bold" fill="#0F172A">{c["address"]}</text>')
        parts.append(f'<text x="420" y="{y_line + 28}" font-size="9" font-family="sans-serif" fill="#64748B">{c["description"]}</text>')
        parts.append(f'<line x1="450" y1="{y_line}" x2="510" y2="{y_line}" style="stroke:#0F172A;stroke-width:2" />')
    else:
        parts.append(f'<line x1="{current_x}" y1="{y_line}" x2="510" y2="{y_line}" style="stroke:#0F172A;stroke-width:2" />')
    
    parts.append("</svg>")
    return "".join(parts)


# =============================================================================
# MAIN APP LAYOUT WITH CALLBACK RESET
# =============================================================================

# Callback function to clear the prompt state safely before widget renders
def clear_text():
    st.session_state.user_prompt = ""
    st.session_state.prompt_input_field = ""

def set_example_prompt(example_text: str):
    st.session_state.user_prompt = example_text
    st.session_state.prompt_input_field = example_text

# Initialize session state for prompt tracking if not present
if "user_prompt" not in st.session_state:
    st.session_state.user_prompt = ""

EXAMPLE_PROMPTS = [
    "Control Y0.1 by X0.1 connected to a selector switch using a timer of 10 seconds.",
    "Start/Stop motor Y0.0 with push buttons X0.0 (start) and X0.1 (stop), with seal-in latch.",
    "Conveyor belt Y0.2 runs when X0.2 is active, auto-stops after 30s using a timer.",
]

col1, col2 = st.columns([2, 3])

with col1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">📝 Functional Specification Prompt</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Describe the automation behavior in plain English — the AI compiler handles the rest.</p>', unsafe_allow_html=True)

    # Text area bound directly via key
    user_prompt = st.text_area(
        "Describe your automation logic here:",
        value=st.session_state.user_prompt,
        height=180,
        placeholder="Example: Control Y0.1 by X0.1 connected to a selector switch using a timer of 10 seconds.",
        key="prompt_input_field",
        label_visibility="collapsed",
    )
    
    st.session_state.user_prompt = user_prompt

    st.markdown('<p class="chip-label">Quick Start Examples</p>', unsafe_allow_html=True)
    for i, example in enumerate(EXAMPLE_PROMPTS):
        st.button(
            example if len(example) <= 60 else example[:57] + "...",
            key=f"example_{i}",
            use_container_width=True,
            on_click=set_example_prompt,
            args=(example,),
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        generate_btn = st.button("⚙️ Compile & Verify Logic", type="primary", use_container_width=True)
    with btn_col2:
        # Using on_click callback so state is cleared prior to widget instantiation
        reset_btn = st.button("🧹 Clear & Reset", type="secondary", use_container_width=True, on_click=clear_text)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="section-card" style="background:var(--color-accent-soft); border-color:#BFDBFE;">
        <p class="section-title" style="font-size:13px; color:var(--color-text-secondary);">💡 How it works</p>
        <p class="section-subtitle" style="margin-bottom:0;">
        Prompt → AI Logic Generation → Hardware Validation → Safety Audit → Tag Allocation → Ladder Diagram
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if not generate_btn or not user_prompt:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🪜</div>
            <div class="empty-state-title">No logic compiled yet</div>
            <div class="empty-state-body">
                Describe your automation requirement on the left, or pick a quick-start example,
                then hit <strong>Compile &amp; Verify Logic</strong> to generate a validated Delta AS228
                ladder diagram with a full safety audit.
            </div>
        </div>
        """, unsafe_allow_html=True)

if generate_btn and user_prompt:
    with col2:
        with st.spinner("Compiling Delta logic & running hardware boundary checks..."):
            try:
                with httpx.Client() as client:
                    response = client.post(backend_url, json={"prompt": user_prompt}, timeout=30.0)

                if response.status_code != 200:
                    st.error(f"❌ Automation Pipeline Blocked: {response.json().get('detail', response.text)}")
                else:
                    res_data = response.json()
                    data = res_data.get("data", {})
                    safety_audit = res_data.get("safety_audit", {})

                    # 🛡️ 1. Safety Audit Display
                    st.markdown('<div class="section-card">', unsafe_allow_html=True)
                    st.markdown('<p class="section-title">🛡️ Industrial Safety Audit</p>', unsafe_allow_html=True)
                    if safety_audit.get("audit_passed", True):
                        st.markdown(
                            """<div class="status-banner pass">
                                <div class="status-icon">✅</div>
                                <div>
                                    <p class="status-title-pass">Hardware Validation Passed</p>
                                    <p class="status-body">Delta AS228 register bounds and logic structures verified successfully.</p>
                                </div>
                            </div>""",
                            unsafe_allow_html=True)
                    else:
                        errors_li = "".join([f"<li>{err}</li>" for err in safety_audit.get('safety_logs', [])])
                        st.markdown(
                            f"""<div class="status-banner fail">
                                <div class="status-icon">🚨</div>
                                <div>
                                    <p class="status-title-fail">Safety Critical Breach Detected</p>
                                    <div class="status-body"><ul>{errors_li}</ul></div>
                                </div>
                            </div>""",
                            unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                    # 📊 2. I/O Variables Tag Table
                    st.markdown('<div class="section-card">', unsafe_allow_html=True)
                    st.markdown('<p class="section-title">📊 Delta Tag Allocation Matrix</p>', unsafe_allow_html=True)
                    v_list = data.get("variables_table", [])
                    variable_lookup = {}

                    if isinstance(v_list, list) and len(v_list) > 0:
                        for v in v_list:
                            if isinstance(v, dict):
                                name_key = v.get('name') or v.get('variable_name') or v.get('Variable Name')
                                if name_key:
                                    variable_lookup[str(name_key).strip()] = {
                                        "address": v.get('address') or v.get('Delta Hardware Address') or "???",
                                        "description": v.get('description') or "No description"
                                    }
                        df_tags = pd.DataFrame(v_list)
                        st.dataframe(df_tags, use_container_width=True, hide_index=True)
                    else:
                        st.info("No variable tags found in project.")
                    st.markdown('</div>', unsafe_allow_html=True)

                    # 💻 3. Structured Text Window (Conditional Rendering to Avoid Empty Exceptions)
                    st_code = data.get("structured_text_code", "")
                    if st_code and st_code.strip() and st_code != "(* Generation Exception *)":
                        st.markdown('<div class="section-card">', unsafe_allow_html=True)
                        st.markdown('<p class="section-title">💻 Delta ISPSoft Structured Text (ST)</p>', unsafe_allow_html=True)
                        st.code(st_code, language="pascal", line_numbers=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                    # 🪜 4. Textbook Dynamic SVG Graphical Ladder Layout
                    st.markdown('<div class="section-card">', unsafe_allow_html=True)
                    st.markdown('<p class="section-title">🪜 Graphical Ladder Layout</p>', unsafe_allow_html=True)
                    st.markdown("<div class='ladder-rail-container'>", unsafe_allow_html=True)

                    variable_lookup = {}
                    if isinstance(v_list, list):
                        for v in v_list:
                            if isinstance(v, dict):
                                name_key = v.get('name') or v.get('variable_name') or v.get('Variable Name')
                                if name_key:
                                    variable_lookup[str(name_key).strip()] = {
                                        "address": v.get('address') or v.get('Delta Hardware Address') or "???",
                                        "description": v.get('description') or "No description"
                                    }

                    rungs = data.get("rungs", [])
                    if rungs:
                        for rung in rungs:
                            if isinstance(rung, dict):
                                rung_num = rung.get('rung_number', '?')
                                rung_desc = rung.get('description', '')
                                
                                st.markdown(
                                    f"<div class='rung-header'>🔗 Network {rung_num}: {rung_desc}</div>",
                                    unsafe_allow_html=True
                                )
                                
                                svg_markup = render_rung_svg(rung, variable_lookup)
                                st.markdown(f"<div class='ladder-svg-wrapper'>{svg_markup}</div>", unsafe_allow_html=True)
                    else:
                        st.info("No rungs to show for current compilation state.")

                    st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                    # 🤖 5. LIVE TESTING DIAGNOSTICS BLOCK
                    st.markdown('<div class="section-card">', unsafe_allow_html=True)
                    st.markdown('<p class="section-title">🤖 Live Simulation Diagnostics</p>', unsafe_allow_html=True)
                    sim_data = res_data.get("simulation", {})
                    
                    if sim_data:
                        sim_passed = sim_data.get("success", False)
                        raw_logs = sim_data.get("raw_logs", "")
                        
                        if sim_passed:
                            st.markdown("""
                            <div class="status-banner pass">
                                <div class="status-icon">🟢</div>
                                <div>
                                    <p class="status-title-pass">All Automated Assertions Passed</p>
                                    <p class="status-body">Delta PLC Simulator: hardware register ranges, continuous latch cycles, and safety overrides verified without failures.</p>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            with st.expander("🔍 Show Detailed Test Runner Logs"):
                                st.code(raw_logs, language="text")
                        else:
                            st.markdown("""
                            <div class="status-banner fail">
                                <div class="status-icon">🔴</div>
                                <div>
                                    <p class="status-title-fail">Simulation Assertions Failed</p>
                                    <p class="status-body">The logic generated has violated state flow parameters during virtual execution loop.</p>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            with st.expander("🔍 Show Detailed Error Trace"):
                                st.code(raw_logs, language="text")
                    else:
                        st.warning("⚠️ No simulation metadata received from the compiler backend.")
                    st.markdown('</div>', unsafe_allow_html=True)

                    if data.get("developer_notes"):
                        st.info(f"💡 **Delta Deployment Notes:** {data['developer_notes']}")

            except httpx.ConnectError:
                st.error("❌ Failed to connect: Backend API is currently offline. Please ensure server is running on local port 8001.")
            except Exception as e:
                st.error(f"Failed to connect to automation pipeline: {str(e)}")
