import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

st.title("NexaPod Live Job Dashboard (Demo Only)")

# --- Demo Data for 10 Nodes, Jobs, and Contributors ---
dummy_nodes = [
    {"id": f"Node{i}", "tier": "CPU", "profile": {"os": "Linux", "os_version": "v1.0", "processor": "Intel Xeon"}}
    for i in range(1, 11)
]
dummy_jobs = [
    {"id": f"Job{i}", "status": "Completed" if i % 2 == 0 else "Pending", "result": f"Result {i}"}
    for i in range(1, 11)
]
dummy_contributors = [
    {"Name": f"Contributor {i}", "Compute": f"{1000 + i * 50} GFLOPS", "Tags": "GPU, Active" if i % 2 == 0 else "CPU, Inactive"}
    for i in range(1, 11)
]

# --- Mesh Network Overview ---
st.subheader("Mesh Network Overview")
st.write(f"Total Nodes in Mesh: {len(dummy_nodes)}")

# --- Interactive Network Graph (Demo Only) ---
st.subheader("Interactive Network Graph (Demo Only)")
# Build a complete graph using NetworkX.
G = nx.complete_graph(10)
# Initialize PyVis network.
net = Network(height="500px", width="100%", notebook=True)
net.from_nx(G)
# Optional: set additional PyVis options.
net.set_options("""
var options = {
  "nodes": {
    "shape": "dot",
    "size": 16
  },
  "physics": {
    "forceAtlas2Based": {
      "gravitationalConstant": -50,
      "centralGravity": 0.005,
      "springLength": 230,
      "springConstant": 0.18
    },
    "minVelocity": 0.75,
    "solver": "forceAtlas2Based"
  }
}
""")
net.show("network.html")
# Read and display the interactive network graph.
HtmlFile = open("network.html", 'r', encoding='utf-8')
components.html(HtmlFile.read(), height=550)

# --- Demo Network Statistics ---
st.subheader("Network Statistics (Demo Only)")
demo_stats = {
    "Total Connections": int((10 * 9) / 2),
    "Average Latency": "50ms",
    "Max Throughput": "500 Mbps",
    "Uptime": "99.9%"
}
st.write(demo_stats)

# --- Existing Node and Job Status Sections using Demo Data ---
st.subheader("Registered Nodes")
st.write(dummy_nodes)

st.subheader("Submitted Jobs")
st.write(dummy_jobs)

st.subheader("Node Status")
for node in dummy_nodes:
    st.write(f"Node ID: {node['id']}, Tier: {node['tier']}, Profile: {node['profile']}")

st.subheader("Job Status")
for job in dummy_jobs:
    st.write(f"Job ID: {job['id']}, Status: {job.get('status', 'Pending')}, Result: {job.get('result', 'N/A')}")

st.subheader("Node Profiles")
for node in dummy_nodes:
    st.write(f"Node ID: {node['id']}, Profile: {node['profile']}")

# --- Demo: Contributor Summary ---
st.subheader("Contributor Summary")
st.table(dummy_contributors)

# At the end of the dashboard file, add a link to the contributor wall.
st.markdown("""
<div style="text-align: center; margin-top: 30px;">
  <a href="./templates/contributor_wall.html" target="_blank" style="
      background-color:#2cbe4e; 
      color:white; 
      padding:12px 24px; 
      text-decoration:none; 
      border-radius:6px; 
      font-weight:bold;">
    View Contributor Wall
  </a>
</div>
""", unsafe_allow_html=True)
