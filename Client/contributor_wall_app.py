import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="NEXAPod Contributor Wall - Demo",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
  body { font-family: sans-serif; background: #0c0c0c; color: #e0e0e0; }
  .header { text-align: center; margin-top: 1rem; }
  .header h1 { font-size: 2.5rem; font-weight: bold; background: linear-gradient(135deg, #00d4ff, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .disclaimer { text-align: center; padding: 10px; background:#f8d7da; color:#721c24; border:1px solid #f5c6cb; margin: 1rem 0; }
  .section-title { font-size: 1.8rem; margin-top: 2rem; margin-bottom: 1rem; }
  .graph-container { margin-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# Header and disclaimer.
st.markdown('<div class="header"><h1>NEXAPod Contributor Wall (Demo)</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="disclaimer">Disclaimer: This data is for demo purposes only and not live.</div>', unsafe_allow_html=True)

# Sample contributor data.
contributors = [
    {"Name": "Dr. Sarah Chen", "Compute": "2.4 TFLOPS", "Type": "HPC", "Status": "Active", "Performance": "99.8%", "Avatar": "SC"},
    {"Name": "Alex Rodriguez", "Compute": "1.8 TFLOPS", "Type": "GPU", "Status": "Active", "Performance": "98.2%", "Avatar": "AR"},
    {"Name": "Emma Thompson", "Compute": "1.5 TFLOPS", "Type": "GPU", "Status": "Active", "Performance": "97.9%", "Avatar": "ET"},
    {"Name": "Michael Park", "Compute": "1.2 TFLOPS", "Type": "CPU", "Status": "Active", "Performance": "96.5%", "Avatar": "MP"},
    {"Name": "Lisa Wang", "Compute": "1.1 TFLOPS", "Type": "GPU", "Status": "Inactive", "Performance": "95.1%", "Avatar": "LW"},
    {"Name": "David Kumar", "Compute": "980 GFLOPS", "Type": "CPU", "Status": "Active", "Performance": "94.7%", "Avatar": "DK"},
    {"Name": "Rachel Green", "Compute": "850 GFLOPS", "Type": "GPU", "Status": "Active", "Performance": "93.2%", "Avatar": "RG"},
    {"Name": "Tom Anderson", "Compute": "720 GFLOPS", "Type": "CPU", "Status": "Inactive", "Performance": "92.8%", "Avatar": "TA"},
    {"Name": "Maria Santos", "Compute": "650 GFLOPS", "Type": "GPU", "Status": "Active", "Performance": "91.4%", "Avatar": "MS"},
    {"Name": "James Wilson", "Compute": "580 GFLOPS", "Type": "CPU", "Status": "Active", "Performance": "90.9%", "Avatar": "JW"}
]

# Display contributor table.
st.subheader("Contributor List")
df_contributors = pd.DataFrame(contributors)
st.dataframe(df_contributors, use_container_width=True)

# Show contributor graph.
st.subheader("Contributor Graph")
# Create a simple bar chart, e.g., Compute power (dummy numerical conversion).
names = [c["Name"] for c in contributors]
# Convert compute values to numerical approximate (assuming TFLOPS > 1, GFLOPS less than 1)
compute_values = []
for c in contributors:
    value = c["Compute"]
    if "TFLOPS" in value:
        compute_values.append(float(value.replace(" TFLOPS", "")) * 1000)
    else:
        compute_values.append(float(value.replace(" GFLOPS", "")))
fig = go.Figure(data=[go.Bar(x=names, y=compute_values, marker_color='rgba(16, 185, 129, 0.7)')])
fig.update_layout(
    title="Contributor Compute Power (in GFLOPS)",
    xaxis_title="Contributor",
    yaxis_title="Compute (GFLOPS)",
    template="plotly_dark",
    margin=dict(t=50, b=50)
)
st.plotly_chart(fig, use_container_width=True)

# Add button to return to main dashboard.
st.markdown("""
<div style="text-align:center; margin-top:20px;">
  <a href="dashboard.py">
    <button style="font-size:1rem; padding:10px 20px; background-color:#2cbe4e; color:white; border:none; border-radius:5px;">
      Return to Dashboard
    </button>
  </a>
</div>
""", unsafe_allow_html=True)

