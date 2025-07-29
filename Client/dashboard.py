import json
from datetime import datetime
from typing import List, Dict, Tuple

import networkx as nx
import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="NEXAPod Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .status-active { color: #27ae60; font-weight: bold; }
    .status-busy { color: #f39c12; font-weight: bold; }
    .status-offline { color: #e74c3c; font-weight: bold; }
    .status-maintenance { color: #8e44ad; font-weight: bold; }
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
        border-left: 3px solid #3498db;
    }
    .data-table {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


class SpinningGlobeNetwork:
    """
    3D Spinning Globe Network Visualization

    Creates an interactive 3D visualization of a complete graph
    network with nodes distributed on a sphere using a Fibonacci
    spiral. Nodes use larger markers and show single-line JSON hover
    information. Live animation rotates the globe and pulses nodes;
    the animation frames now only update the node trace for stability.
    """
    def __init__(self, nodes_data: List[Dict]):
        self.nodes_data = nodes_data
        self.num_nodes = len(nodes_data)

    def fibonacci_sphere_distribution(self
                                      ) -> Tuple[np.ndarray, np.ndarray,
                                                   np.ndarray]:
        """Generate optimal node positions using Fibonacci spiral."""
        n = self.num_nodes
        indices = np.arange(n) + 0.5
        phi = np.arccos(1 - 2 * (indices / n))
        theta = np.pi * (1 + np.sqrt(5)) * indices
        x = np.sin(phi) * np.cos(theta)
        y = np.sin(phi) * np.sin(theta)
        z = np.cos(phi)
        return x, y, z

    def create_sphere_surface(self, resolution: int = 50) -> go.Surface:
        """Create the background sphere surface."""
        u = np.linspace(0, np.pi, resolution)
        v = np.linspace(0, 2 * np.pi, resolution)
        U, V = np.meshgrid(u, v)
        X_sphere = np.sin(U) * np.cos(V)
        Y_sphere = np.sin(U) * np.sin(V)
        Z_sphere = np.cos(U)
        return go.Surface(
            x=X_sphere, y=Y_sphere, z=Z_sphere,
            colorscale='Viridis',
            opacity=0.5,
            showscale=False,
            hoverinfo='skip'
        )

    def create_network_edges(self, node_positions: Tuple[np.ndarray, ...]
                             ) -> List[go.Scatter3d]:
        """Create edge traces for complete graph connectivity."""
        x_coords, y_coords, z_coords = node_positions
        G = nx.complete_graph(self.num_nodes)
        edge_traces = []
        for edge in G.edges():
            i, j = edge
            edge_trace = go.Scatter3d(
                x=[x_coords[i], x_coords[j]],
                y=[y_coords[i], y_coords[j]],
                z=[z_coords[i], z_coords[j]],
                mode='lines',
                line=dict(color='rgba(100, 149, 237, 0.6)', width=2),
                hoverinfo='skip',
                showlegend=False
            )
            edge_traces.append(edge_trace)
        return edge_traces

    def prepare_hover_information(self) -> List[str]:
        """
        Prepare JSON-formatted hover text for each node in a single-line
        format.
        """
        hover_texts = []
        for node in self.nodes_data:
            hover_data = {
                'id': node['id'],
                'tier': node['tier'],
                'status': node['status'],
                'region': node['region'],
                'cpu_usage': f"{node['metrics']['cpu_usage']}%",
                'memory_usage': f"{node['metrics']['memory_usage']}%",
                'jobs_completed': node['metrics']['jobs_completed'],
                'reputation_score': node['metrics']['reputation_score'],
                'credits_earned': f"${node['metrics']['credits_earned']:.2f}",
                'uptime_hours': node['profile']['uptime_hours']
            }
            hover_text = json.dumps(hover_data)
            hover_texts.append(hover_text)
        return hover_texts

    def create_node_trace(self, node_positions: Tuple[np.ndarray, ...]
                          ) -> go.Scatter3d:
        """Create the main node scatter trace with larger markers."""
        x_coords, y_coords, z_coords = node_positions
        hover_texts = self.prepare_hover_information()
        return go.Scatter3d(
            x=x_coords, y=y_coords, z=z_coords,
            mode='markers+text',
            marker=dict(
                symbol='circle',
                size=[12] * self.num_nodes,
                color='red',
                line=dict(width=2, color='white'),
                opacity=0.9
            ),
            text=[f"Node {i}" for i in range(self.num_nodes)],
            textposition='middle center',
            textfont=dict(size=10, color='white'),
            hovertext=hover_texts,
            hoverinfo='text',
            showlegend=False
        )

    def generate_animation_frames(self, node_positions: Tuple[np.ndarray, ...],
                                  num_frames: int = 60) -> List[Dict]:
        """
        Generate animation frames for camera rotation and node pulsing.

        The frames now only update the node trace (index 1) to avoid
        injecting empty update dicts for other traces.
        """
        frames = []
        phases = [2 * np.pi * j / self.num_nodes
                  for j in range(self.num_nodes)]
        for i in range(num_frames):
            angle = 2 * np.pi * i / num_frames
            cam_eye = dict(x=2 * np.cos(angle), y=2 * np.sin(angle), z=0.5)
            node_sizes = [
                12 + 3 * ((np.sin(2 * np.pi * i / num_frames + phases[j]) + 1) / 2)
                for j in range(self.num_nodes)
            ]
            frame = dict(
                data=[dict(marker=dict(size=node_sizes))],
                traces=[1],
                layout=dict(scene=dict(camera=dict(eye=cam_eye)))
            )
            frames.append(frame)
        return frames

    def create_visualization(self) -> go.Figure:
        """Create the complete 3D spinning globe network visualization."""
        node_positions = self.fibonacci_sphere_distribution()
        sphere_trace = self.create_sphere_surface()
        node_trace = self.create_node_trace(node_positions)
        edge_traces = self.create_network_edges(node_positions)
        data = [sphere_trace, node_trace] + edge_traces
        layout = dict(
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                aspectmode='cube',
                bgcolor='rgba(0,0,0,0.05)'
            ),
            title=dict(
                text=f"NEXAPod Network Globe - {self.num_nodes} "
                     "Compute Nodes",
                font=dict(size=16, color='#2c3e50'),
                x=0.5
            ),
            width=800,
            height=600,
            margin=dict(t=60, b=10, l=10, r=10),
            updatemenus=[{
                "buttons": [{
                    "args": [None, {"frame": {"duration": 50, "redraw": True},
                                    "fromcurrent": True,
                                    "transition": {"duration": 0}}],
                    "label": "Play",
                    "method": "animate"
                }, {
                    "args": [[None], {"frame": {"duration": 0,
                                                 "redraw": True},
                                      "mode": "immediate",
                                      "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }],
                "direction": "left",
                "pad": {"r": 10, "t": 70},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0.02,
                "yanchor": "top"
            }],
            annotations=[{
                'text': 'Fibonacci sphere distribution • Complete graph '
                        'topology • JSON hover data',
                'showarrow': False,
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.5,
                'y': 0.02,
                'xanchor': 'center',
                'yanchor': 'bottom',
                'font': {'size': 11, 'color': 'gray'}
            }]
        )
        fig = go.Figure(data=data, layout=layout)
        frames = self.generate_animation_frames(node_positions)
        fig.frames = frames
        return fig


class NEXAPodDashboard:
    """
    Clean, streamlined NEXAPod Dashboard that displays key metrics,
    data tables, and the 3D live network globe.
    """
    def __init__(self):
        self.initialize_session_state()

    def initialize_session_state(self):
        """Initialize session state variables."""
        if 'nodes' not in st.session_state:
            st.session_state.nodes = self.generate_demo_nodes(10)
        if 'jobs' not in st.session_state:
            st.session_state.jobs = self.generate_demo_jobs(6)
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()

    def generate_demo_nodes(self, count: int) -> List[Dict]:
        """Generate realistic demo node data."""
        tiers = ['CPU', 'CONSUMER_GPU', 'HPC']
        statuses = ['Active', 'Busy', 'Maintenance', 'Offline']
        regions = ['US-East', 'US-West', 'EU-Central', 'APAC', 'Americas']
        nodes = []
        for i in range(count):
            tier = np.random.choice(tiers, p=[0.6, 0.3, 0.1])
            status = np.random.choice(statuses, p=[0.7, 0.2, 0.07, 0.03])
            node = {
                'id': f"node_{i:03d}",
                'tier': tier,
                'status': status,
                'region': np.random.choice(regions),
                'profile': {
                    'cpu': f"Intel Xeon E5-{2600 + i*10}",
                    'cores': int(np.random.randint(8, 32)),
                    'ram_gb': int(np.random.choice([16, 32, 64, 128])),
                    'uptime_hours': int(np.random.randint(100, 8000))
                },
                'metrics': {
                    'jobs_completed': int(np.random.randint(50, 800)),
                    'cpu_usage': int(np.random.randint(20, 85)),
                    'memory_usage': int(np.random.randint(25, 75)),
                    'reputation_score': round(np.random.uniform(0.8, 1.0), 3),
                    'credits_earned': round(np.random.uniform(500, 8000), 2)
                }
            }
            nodes.append(node)
        return nodes

    def generate_demo_jobs(self, count: int) -> List[Dict]:
        """Generate demo job data."""
        job_types = ['protein_folding', 'weather_simulation',
                     'quantum_computation', 'materials_modeling',
                     'ml_training', 'molecular_dynamics']
        statuses = ['Queued', 'Running', 'Completed', 'Failed']
        jobs = []
        for i in range(count):
            job_type = np.random.choice(job_types)
            status = np.random.choice(statuses, p=[0.2, 0.3, 0.45, 0.05])
            job = {
                'id': f"job_{i:04d}",
                'type': job_type,
                'status': status,
                'submitter': f"researcher_{chr(97+i%5)}",
                'progress': int(np.random.randint(0, 100)) if status == 'Running' else (100 if status == 'Completed' else 0),
                'credits_allocated': round(np.random.uniform(50, 500), 2),
                'estimated_time': f"{np.random.randint(30, 240)} min"
            }
            jobs.append(job)
        return jobs


def main():
    """Main NEXAPod Dashboard application."""
    dashboard = NEXAPodDashboard()
    st.markdown('<h1 class="main-header">NEXAPod Live Dashboard</h1>',
                unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Distributed Compute Fabric for '
                'Scientific Problems</p>', unsafe_allow_html=True)
    with st.sidebar:
        st.header("Dashboard Controls")
        st.subheader("Network Configuration")
        node_count = st.slider("Number of Nodes", min_value=5, max_value=20,
                               value=10)
        if st.button("Regenerate Network"):
            st.session_state.nodes = dashboard.generate_demo_nodes(node_count)
            st.rerun()
        st.subheader("Filters")
        tier_filter = st.multiselect(
            "Node Tiers",
            options=['CPU', 'CONSUMER_GPU', 'HPC'],
            default=['CPU', 'CONSUMER_GPU', 'HPC']
        )
        status_filter = st.multiselect(
            "Node Status",
            options=['Active', 'Busy', 'Maintenance', 'Offline'],
            default=['Active', 'Busy']
        )
        st.subheader("System Status")
        st.write("**Coordinator:** Online")
        st.write("**Database:** Connected")
        st.write(f"**Last Update:** "
                 f"{st.session_state.last_update.strftime('%H:%M:%S')}")
        if st.button("Refresh Dashboard"):
            st.session_state.last_update = datetime.now()
            st.rerun()
    filtered_nodes = [
        node for node in st.session_state.nodes
        if node['tier'] in tier_filter and node['status'] in status_filter
    ]
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        active_nodes = len([
            n for n in filtered_nodes if n['status'] == 'Active'
        ])
        st.metric("Active Nodes", active_nodes,
                  delta=f"+{np.random.randint(0, 2)}")
    with col2:
        running_jobs = len([
            j for j in st.session_state.jobs if j['status'] == 'Running'
        ])
        st.metric("Running Jobs", running_jobs,
                  delta=f"+{np.random.randint(-1, 3)}")
    with col3:
        total_credits = sum(
            node['metrics']['credits_earned'] for node in filtered_nodes
        )
        st.metric("Total Credits", f"${total_credits:,.0f}",
                  delta=f"+${np.random.randint(100,500)}")
    with col4:
        utilization = np.random.randint(70, 95)
        st.metric("Network Utilization", f"{utilization}%",
                  delta=f"{np.random.randint(-3, 5)}%")
    st.header("Real-Time Network Globe")
    st.markdown("<p style='text-align:center; color:#e74c3c;'>Disclaimer: "
                "This is demo data only & the globe animation is experimental "
                "and may crash.</p>", unsafe_allow_html=True)
    if filtered_nodes:
        display_nodes = (
            filtered_nodes if len(filtered_nodes) != len(st.session_state.nodes)
            else st.session_state.nodes[:node_count]
        )
        globe_network = SpinningGlobeNetwork(display_nodes)
        fig = globe_network.create_visualization()
        config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': [
                'pan3d', 'orbitRotation', 'tableRotation',
                'resetCameraDefault3d', 'resetCameraLastSave3d'
            ]
        }
        st.plotly_chart(fig, use_container_width=True, config=config)
        st.info("Note: The globe animation is experimental and subject to "
                "stability issues. This is demo data only.")
    else:
        st.warning("No nodes match current filter criteria.")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Node Registry")
        if filtered_nodes:
            node_table_data = []
            for node in filtered_nodes[:8]:
                node_table_data.append({
                    'ID': node['id'],
                    'Tier': node['tier'],
                    'Status': node['status'],
                    'Region': node['region'],
                    'Jobs': node['metrics']['jobs_completed'],
                    'Credits': f"${node['metrics']['credits_earned']:.0f}",
                    'Reputation': f"{node['metrics']['reputation_score']:.3f}"
                })
            st.dataframe(node_table_data, use_container_width=True)
            st.write("**Node Distribution:**")
            tier_counts = {}
            for node in filtered_nodes:
                tier_counts[node['tier']] = (
                    tier_counts.get(node['tier'], 0) + 1
                )
            for tier, count in tier_counts.items():
                st.write(f"• {tier}: {count} nodes")
    with col2:
        st.subheader("Job Queue Status")
        if st.session_state.jobs:
            job_table_data = []
            for job in st.session_state.jobs:
                job_table_data.append({
                    'ID': job['id'],
                    'Type': job['type'].replace('_', ' ').title(),
                    'Status': job['status'],
                    'Progress': (
                        f"{job['progress']}%"
                        if job['status'] == 'Running' else '—'
                    ),
                    'Credits': f"${job['credits_allocated']:.0f}",
                    'Time Est.': job.get('estimated_time', '—'),
                    'Submitter': job['submitter']
                })
            st.dataframe(job_table_data, use_container_width=True)
            st.write("**Job Distribution:**")
            status_counts = {}
            for job in st.session_state.jobs:
                status_counts[job['status']] = (
                    status_counts.get(job['status'], 0) + 1
                )
            for status, count in status_counts.items():
                st.write(f"• {status}: {count} jobs")
    st.header("System Performance")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Compute Metrics")
        st.write(f"**Total FLOPS:** "
                 f"{np.random.uniform(500,2000):.1f} TFLOPS")
        st.write(f"**Average Job Time:** {np.random.randint(45,180)} "
                 "minutes")
        st.write(f"**Success Rate:** "
                 f"{np.random.uniform(96,99.5):.1f}%")
        st.write(f"**Queue Wait:** {np.random.randint(2,12)} minutes")
    with col2:
        st.subheader("Resource Usage")
        st.write(f"**CPU Utilization:** {np.random.randint(60,85)}%")
        st.write(f"**Memory Usage:** {np.random.randint(55,80)}%")
        st.write(f"**Network I/O:** "
                 f"{np.random.uniform(15,45):.1f} Gbps")
        st.write(f"**Storage I/O:** "
                 f"{np.random.uniform(5,25):.1f} GB/s")
    with col3:
        st.subheader("Economic Data")
        st.write(f"**Credits/Hour:** ${np.random.uniform(75,250):.0f}")
        st.write(f"**Daily Volume:** ${np.random.uniform(5000,15000):.0f}")
        st.write(f"**Avg Rate:** ${np.random.uniform(15,35):.2f}/job")
        st.write(f"**Top Earner:** "
                 f"${max(n['metrics']['credits_earned'] for n in filtered_nodes):.0f}")
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**System Status:** All systems operational")
    with col2:
        st.write("**API Endpoint:** http://localhost:5000")
    with col3:
        if st.button("Export Report"):
            st.success("System report exported")
    # Remove embedded contributor wall HTML and disclaimer.
    # Instead, add a button that opens the separate contributor wall sub‑app.
    st.markdown("""
    <div style="text-align:center; margin-top:20px;">
      <a href="contributor_wall_app.py" target="_blank">
        <button style="font-size:1rem; padding:10px 20px; background-color:#2cbe4e; color:white; border:none; border-radius:5px;">
          Show Contributor Wall (Demo)
        </button>
      </a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
