import streamlit as st
import os
from main import generate_floorplan  # <--- Connecting to your Engine

# 1. Page Config
st.set_page_config(
    page_title="FloorplanAI - Automated Architect",
    page_icon="🏗️",
    layout="wide"
)

# 2. Sidebar (Inputs)
st.sidebar.header("🏗️ Project Settings")

# A. Dimensions (Inputs for Phase 8 Strict Limits)
plot_w = st.sidebar.number_input("Plot Width (meters)", 5.0, 50.0, 12.0)
plot_l = st.sidebar.number_input("Plot Length (meters)", 5.0, 50.0, 15.0)

# B. Rooms
num_beds = st.sidebar.slider("Bedrooms", 1, 5, 2)
kitchen_type = st.sidebar.selectbox("Kitchen Type", ["Open kitchen", "Closed kitchen"])
orientation = st.sidebar.selectbox("Entrance Facing", ["N", "E", "W", "S"])

# C. Advanced
vaastu = st.sidebar.checkbox("Enable Vaastu Shastra", value=True)

# 3. Main UI
st.title("🏗️ FloorplanAI: Generative Layout Engine")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.info(f"**Plot Size:** {plot_w}m x {plot_l}m")
    st.write("Ready to generate compliance-checked layout.")
    
    if st.button("🚀 Generate Floor Plan", use_container_width=True):
        with st.spinner("🤖 AI is thinking... (RAG -> Solver -> Renderer)"):
            # --- THE ENDPOINT CALL ---
            request = {
                "plot_width": plot_w,
                "plot_length": plot_l,
                "num_bedrooms": num_beds,
                "user_preferences": f"{kitchen_type}, modern layout",
                "vaastu_enabled": vaastu,
                "orientation": orientation
            }
            
            # Call your main.py engine
            result = generate_floorplan(request)
            
            if result["status"] == "success":
                st.session_state["result"] = result
                st.success("✅ Generation Complete!")
            else:
                st.error(f"❌ Failed: {result['message']}")

with col2:
    if "result" in st.session_state:
        res = st.session_state["result"]
        
        # Display SVG
        st.image(res["svg_path"], caption="Generated Blueprint (Maket Style)", use_container_width=True)
        
        # Download Buttons
        c1, c2 = st.columns(2)
        with c1:
            with open(res["svg_path"], "rb") as f:
                st.download_button("⬇️ Download SVG (Visual)", f, file_name="plan.svg", mime="image/svg+xml")
        with c2:
            with open(res["dxf_path"], "rb") as f:
                st.download_button("🏗️ Download DXF (CAD)", f, file_name="plan.dxf", mime="application/dxf")