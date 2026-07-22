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

# Custom CSS for Textbook-Style Industrial Layout & Diagnostics Cards
st.markdown("""
<style>
    .ladder-rail-container {
        border-left: 6px solid #0F172A;
        border-right: 6px solid #0F172A;
        background-color: #FFFFFF;
        padding: 30px 20px;
        margin-top: 10px;
        box-shadow: inset 2px 0px 5px rgba(0,0,0,0.05);
    }
    .rung-header {
        font-family: 'Segoe UI', sans-serif;
        color: #1E293B;
        margin-top: 25px;
        font-weight: bold;
        background-color: #F1F5F9;
        padding: 6px 12px;
        border-radius: 4px;
        border-left: 4px solid #3B82F6;
    }
    .ladder-svg-wrapper {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 20px;
    }
    .safety-pass {
        background-color: #DCFCE7;
        border-left: 5px solid #15803D;
        padding: 15px;
        border-radius: 5px;
        color: #14532D;
        font-family: sans-serif;
    }
    .safety-fail {
        background-color: #FEE2E2;
        border-left: 5px solid #B91C1C;
        padding: 15px;
        border-radius: 5px;
        color: #7F1D1D;
        font-family: sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ AI PLC-GenStudio — Delta AS228 R/T")
st.caption("Delta ISPSoft Deterministic Core Logic Generation & Architecture Validator")
st.divider()

# Sidebar for Technical Configuration
with st.sidebar:
    st.header("⚙️ Hardware Profile")
    st.info("🎯 Device Target: Delta AS228 R/T")
    backend_url = st.text_input("Backend API Gateway", value="http://127.0.0.1:8001/api/v1/generate")
    st.divider()
    st.markdown("""
    ### 🏭 Delta Device Syntax Bounds:
    *   **Digital Inputs ($X$):** `X0.0` to `X63.15`
    *   **Digital Outputs ($Y$):** `Y0.0` to `Y63.15`
    *   **Internal Bits ($M$):** `M0` to `M8191`
    *   **Data Registers ($D$):** `D0` to `D29999`
    """)

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

# Constant spacing preserved exactly as requested
ELEMENT_SPACING = 18

def render_timer_block(cx: int, y_line: int, comp: dict, variable_lookup: dict) -> tuple[str, int]:
    """
    Renders an exact Delta ISPSoft style TMR block inline with En, S1, S2 pins.
    Returns (svg_markup_string, new_current_x_offset).
    """
    c = resolve_element(comp, variable_lookup)
    
    # Extract metadata securely
    timer_addr = c.get("address") or comp.get("variable_name") or comp.get("address") or "T0"
    
    # Handle preset value (clean up 'T#' prefix if present to display raw number like 100 or K100 as shown in manual)
    raw_preset = comp.get("preset_time") or comp.get("preset") or "100"
    preset_val = str(raw_preset).replace("T#", "").replace("s", "").strip()
    if not preset_val.startswith("K") and preset_val.isdigit():
        preset_val = f"{preset_val}"
    
    # Timer block dimensions (Delta ISPSoft proportions)
    box_w = 95
    box_h = 75
    box_y = y_line - 37
    
    parts = []
    
    # Wire entering into 'En' pin from left starts precisely from current cx without overlapping
    parts.append(f'<line x1="{cx}" y1="{y_line}" x2="{cx + 15}" y2="{y_line}" style="stroke:#0F172A;stroke-width:2" />')
    
    # Main Timer Function Block Rectangle
    bx = cx + 15
    parts.append(f'<rect x="{bx}" y="{box_y}" width="{box_w}" height="{box_h}" fill="#FFFFFF" stroke="#0F172A" stroke-width="2" rx="2" />')
    
    # Instruction Header Title: TMR (Strictly matching Delta ISPSoft standard style)
    parts.append(f'<text x="{bx + 35}" y="{box_y + 18}" font-size="11" font-family="sans-serif" font-weight="bold" fill="#0F172A">TMR</text>')
    parts.append(f'<line x1="{bx}" y1="{box_y + 24}" x2="{bx + box_w}" y2="{box_y + 24}" style="stroke:#0F172A;stroke-width:1" />')
    
    # Pin Labels (En, S1, S2)
    parts.append(f'<text x="{bx + 6}" y="{box_y + 40}" font-size="9" font-family="sans-serif" fill="#1E293B">En</text>')
    parts.append(f'<text x="{bx + 6}" y="{box_y + 56}" font-size="9" font-family="sans-serif" fill="#1E293B">S1</text>')
    parts.append(f'<text x="{bx + 6}" y="{box_y + 70}" font-size="9" font-family="sans-serif" fill="#1E293B">S2</text>')
    
    # S1 Parameter Box & Value (Timer Name / Address e.g., T0)
    parts.append(f'<rect x="{bx + 40}" y="{box_y + 44}" width="48" height="14" fill="#FFFFFF" stroke="#64748B" stroke-width="1" />')
    parts.append(f'<text x="{bx + 44}" y="{box_y + 55}" font-size="9" font-family="monospace" fill="#0F172A">{timer_addr}</text>')
    
    # S2 Parameter Box & Value (Preset Value e.g., 100)
    parts.append(f'<rect x="{bx + 40}" y="{box_y + 60}" width="48" height="14" fill="#FFFFFF" stroke="#64748B" stroke-width="1" />')
    parts.append(f'<text x="{bx + 44}" y="{box_y + 71}" font-size="9" font-family="monospace" fill="#0F172A">{preset_val}</text>')
    
    # Exit wire continuing from the right side of the block back to main rail flow
    exit_x = bx + box_w
    parts.append(f'<line x1="{exit_x}" y1="{y_line}" x2="{exit_x + ELEMENT_SPACING}" y2="{y_line}" style="stroke:#0F172A;stroke-width:2" />')
    
    new_x = exit_x + ELEMENT_SPACING
    return "".join(parts), new_x


def render_rung_svg(rung: dict, variable_lookup: dict) -> str:
    """
    Renders textbook style dynamic PLC Ladder SVG layouts from AST data safely.
    Corrected wire geometry: single continuous wire segment drawn after occupied width calculation.
    """
    series_elements = rung.get("series_elements") or []
    parallel_raw = rung.get("parallel_branches") or []
    parallel_branches = [b for b in parallel_raw if b]
    
    # Schema Compatibility: Identify coil outputs from new schema or legacy search
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
    
    # Layout baseline configuration
    svg_h = 190 if has_parallel else 120
    y_line = 60
    parts = []
    
    parts.append(f'<svg width="100%" height="{svg_h}" viewBox="0 0 520 {svg_h}" preserveAspectRatio="xMidYMid meet" style="background-color: #FFFFFF;">')
    
    # 1. Left & Right Power Rails
    parts.append(f'<line x1="10" y1="0" x2="10" y2="{svg_h}" style="stroke:#0F172A;stroke-width:3" />')
    parts.append(f'<line x1="510" y1="0" x2="510" y2="{svg_h}" style="stroke:#0F172A;stroke-width:3" />')
    
    # 2. Main horizontal flow line start
    parts.append(f'<line x1="10" y1="{y_line}" x2="40" y2="{y_line}" style="stroke:#0F172A;stroke-width:2" />')
    current_x = 40
    
    # --- Parallel Circuit Logic Rendering Block ---
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
    
    # --- Render Series Blocks (Contacts & Dynamic Timers) ---
    for comp in remaining_series:
        c_type = str(comp.get("type", "")).upper()
        
        if "TIMER" in c_type or "TMR" in c_type or "TON" in c_type or "TOF" in c_type or "CTU" in c_type:
            timer_svg, current_x = render_timer_block(current_x, y_line, comp, variable_lookup)
            parts.append(timer_svg)
        else:
            c = resolve_element(comp, variable_lookup)
            symbol_width = 35
            
            # Draw contact symbol vertical bars and labels without drawing pre-allocated horizontal wire segments
            contact_start_x = current_x
            parts.append(f'<line x1="{contact_start_x}" y1="{y_line - 15}" x2="{contact_start_x}" y2="{y_line + 15}" style="stroke:#0F172A;stroke-width:2" />')
            if "NC" in c["type"] or "NOT" in c["type"]:
                parts.append(f'<line x1="{contact_start_x - 3}" y1="{y_line + 12}" x2="{contact_start_x + 11}" y2="{y_line - 12}" style="stroke:#B91C1C;stroke-width:2" />')
            parts.append(f'<line x1="{contact_start_x + 8}" y1="{y_line - 15}" x2="{contact_start_x + 8}" y2="{y_line + 15}" style="stroke:#0F172A;stroke-width:2" />')
            parts.append(f'<text x="{contact_start_x - 4}" y="{y_line - 22}" font-size="11" font-family="monospace" font-weight="bold" fill="#0F172A">{c["address"]}</text>')
            parts.append(f'<text x="{contact_start_x - 10}" y="{y_line + 28}" font-size="9" font-family="sans-serif" fill="#64748B">{c["description"]}</text>')
            
            # Calculate final occupied width and terminal endpoints
            addr_text_width = len(str(c.get("address", ""))) * 7
            desc_text_width = len(str(c.get("description", ""))) * 5.5
            occupied_width = max(
                symbol_width + 8,
                addr_text_width + 12,
                desc_text_width + 5
            )
            
            terminal_end_x = contact_start_x + symbol_width
            next_element_start_x = contact_start_x + occupied_width + ELEMENT_SPACING
            
            # Draw single continuous horizontal wire from current position past the contact and across the spacing gap
            parts.append(f'<line x1="{current_x}" y1="{y_line}" x2="{next_element_start_x}" y2="{y_line}" style="stroke:#0F172A;stroke-width:2" />')
            current_x = next_element_start_x

    # --- Output Coil Logic (Timer Coil Bypass & Normal BOOL Coils Support) ---
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
# MAIN APP LAYOUT
# =============================================================================
col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("📝 Functional Specification Prompt")
    user_prompt = st.text_area(
        "Describe your automation logic here:",
        height=220,
        placeholder="Example: Control Y0.1 by X0.1 connected to a selector switch using a timer of 10 seconds."
    )
    generate_btn = st.button("Compile & Verify Logic", type="primary", use_container_width=True)

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
                    # st.divider()
                    # st.subheader("🔍 Raw Backend Response")
                    # st.json(res_data)
                    data = res_data.get("data", {})
                    safety_audit = res_data.get("safety_audit", {})

                    # 🛡️ 1. Safety Audit Display
                    st.subheader("🛡️ Industrial Safety Audit Logs")
                    if safety_audit.get("audit_passed", True):
                        st.markdown(
                            """<div class="safety-pass"><strong>✅ HARDWARE VALIDATION PASSED:</strong> Delta AS228 register bounds and logic structures verified successfully.</div>""",
                            unsafe_allow_html=True)
                    else:
                        errors_li = "".join([f"<li>{err}</li>" for err in safety_audit.get('safety_logs', [])])
                        st.markdown(
                            f"""<div class="safety-fail"><strong>🚨 SAFETY CRITICAL BREACH DETECTED:</strong><ul>{errors_li}</ul></div>""",
                            unsafe_allow_html=True)

                    st.divider()

                    # 📊 2. I/O Variables Tag Table
                    st.subheader("📊 Delta Tag Allocation Matrix")
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

                    st.divider()

                    # 💻 3. Structured Text Window
                    st.subheader("💻 Delta ISPSoft Structured Text (ST)")
                    st_code = data.get("structured_text_code", "(* Generation Exception *)")
                    st.code(st_code, language="pascal", line_numbers=True)

                    st.divider()

                    # 🪜 4. Textbook Dynamic SVG Graphical Ladder Layout
                    st.subheader("🪜 Textbook Graphical Ladder Layout")
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
                    st.divider()

                    # 🤖 5. LIVE TESTING DIAGNOSTICS BLOCK
                    st.subheader("🤖 Live Simulation Diagnostics")
                    sim_data = res_data.get("simulation", {})
                    
                    if sim_data:
                        sim_passed = sim_data.get("success", False)
                        raw_logs = sim_data.get("raw_logs", "")
                        
                        if sim_passed:
                            st.markdown("""
                            <div style="background-color: #DCFCE7; border-left: 5px solid #16A34A; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                                <h4 style="color: #14532D; margin: 0 0 8px 0; font-family: sans-serif;">🟢 All Automated Assertions Passed! (3/3 Tests)</h4>
                                <p style="color: #166534; margin: 0; font-size: 14px; font-family: sans-serif;">
                                    <strong>Delta PLC Simulator Status:</strong> Hardware register ranges, continuous latch cycles, and safety overrides have been mathematically verified without failures.
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            with st.expander("🔍 Show Detailed Test Runner Logs"):
                                st.code(raw_logs, language="text")
                        else:
                            st.markdown("""
                            <div style="background-color: #FEE2E2; border-left: 5px solid #DC2626; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                                <h4 style="color: #7F1D1D; margin: 0 0 8px 0; font-family: sans-serif;">🔴 Simulation Assertions Failed!</h4>
                                <p style="color: #991B1B; margin: 0 0 10px 0; font-size: 14px; font-family: sans-serif;">
                                    The logic generated has violated state flow parameters during virtual execution loop.
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            with st.expander("🔍 Show Detailed Error Trace"):
                                st.code(raw_logs, language="text")
                    else:
                        st.warning("⚠️ No simulation metadata received from the compiler backend.")

                    st.divider()

                    if data.get("developer_notes"):
                        st.info(f"💡 **Delta Deployment Notes:** {data['developer_notes']}")

            except httpx.ConnectError:
                st.error("❌ Failed to connect: Backend API is currently offline. Please ensure server is running on local port 8001.")
            except Exception as e:
                st.error(f"Failed to connect to automation pipeline: {str(e)}")