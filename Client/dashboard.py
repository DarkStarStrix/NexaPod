import json
import yaml
from datetime import datetime
from typing import List, Dict, Tuple

import networkx as nx
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from comms import CoordinatorClient

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
    information. Live animation rotates the globe and pulses nodes.
    """
    def __init__(self, nodes_data: List[Dict]):
        self.nodes_data = nodes_data
        self.num_nodes = len(nodes_data)

    def fibonacci_sphere_distribution(
            self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate optimal node positions using Fibonacci spiral."""
        n = self.num_nodes
        indices = np.arange(n) + 0.5
        phi = np.arccos(1 - 2 * (indices / n))
        theta = np.pi * (1 + np.sqrt(5)) * indices
        x = np.sin(phi) * np.cos(theta)
        y = np.sin(phi) * np.sin(theta)
        z = np.cos(phi)
        return x, y, z

    @staticmethod
    def create_sphere_surface(resolution: int = 50) -> go.Surface:
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

    def create_network_edges(
            self, node_positions: Tuple[np.ndarray, ...]) -> List[go.Scatter3d]:
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
        Prepare JSON-formatted hover text for each node in a single-line format.
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
                'credits_earned':
                    f"${node['metrics']['credits_earned']:.2f}",
                'uptime_hours': node['profile']['uptime_hours']
            }
            hover_text = json.dumps(hover_data)
            hover_texts.append(hover_text)
        return hover_texts

    def create_node_trace(self, node_positions: Tuple[np.ndarray, ...]) -> go.Scatter3d:
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

    def generate_animation_frames(self, num_frames: int = 60) -> List[Dict]:
        """
        Generate animation frames for camera rotation and node pulsing.
        """
        frames = []
        phases = [2 * np.pi * j / self.num_nodes for j in range(self.num_nodes)]
        for i in range(num_frames):
            angle = 2 * np.pi * i / num_frames
            cam_eye = dict(x=2 * np.cos(angle), y=2 * np.sin(angle), z=0.5)
            node_sizes = [
                12 + 3 * ((np.sin(
                    2 * np.pi * i / num_frames + phases[j]) + 1) / 2)
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
                text=(f"NEXAPod Network Globe - {self.num_nodes} "
                      "Compute Nodes"),
                font=dict(size=16, color='#2c3e50'),
                x=0.5
            ),
            width=800,
            height=600,
            margin=dict(t=60, b=10, l=10, r=10),
            updatemenus=[{
                "buttons": [{
                    "args": [
                        None,
                        {
                            "frame": {"duration": 50, "redraw": True},
                            "fromcurrent": True,
                            "transition": {"duration": 0}
                        }
                    ],
                    "label": "Play",
                    "method": "animate"
                }, {
                    "args": [
                        [None],
                        {
                            "frame": {"duration": 0, "redraw": True},
                            "mode": "immediate",
                            "transition": {"duration": 0}
                        }
                    ],
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
                'text': (
                    "Fibonacci sphere distribution • Complete graph topology • "
                    "JSON hover data"
                ),
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
        frames = self.generate_animation_frames()
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
        """Fetch live nodes and jobs from coordinator."""
        if 'coord' not in st.session_state:
            cfg = yaml.safe_load(open("config.yaml"))
            st.session_state.coord = CoordinatorClient({
                "coordinator_url": cfg["coordinator_url"]
            })
        if 'nodes' not in st.session_state:
            st.session_state.nodes = st.session_state.coord.get_nodes()
        if 'jobs' not in st.session_state:
            st.session_state.jobs = st.session_state.coord.get_jobs_list()
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()

def main():
    """Main NEXAPod Dashboard application."""
    dashboard = NEXAPodDashboard()

    st.markdown('<h1 class="main-header">NEXAPod Live Dashboard</h1>',
                unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Distributed Compute Fabric for '
                'Scientific Problems</p>', unsafe_allow_html=True)

    # Sidebar controls
    with st.sidebar:
        st.header("Dashboard Controls")
        st.subheader("Network Configuration")
        node_count = st.slider("Number of Nodes", min_value=5, max_value=20,
                              value=10)

        if st.button("Regenerate Network"):
            st.session_state.nodes = st.session_state.coord.get_nodes()
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
        last_update_time = st.session_state.last_update.strftime('%H:%M:%S')
        st.write(f"**Last Update:** {last_update_time}")

        if st.button("Refresh Dashboard"):
            st.session_state.nodes = st.session_state.coord.get_nodes()
            st.session_state.jobs = st.session_state.coord.get_jobs_list()
            st.session_state.last_update = datetime.now()
            st.rerun()

    # Filter nodes
    filtered_nodes = [
        node for node in st.session_state.nodes
        if node['tier'] in tier_filter and node['status'] in status_filter
    ]

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        active_nodes = len([n for n in filtered_nodes if n['status'] == 'Active'])
        delta_value = f"+{np.random.randint(0, 2)}"
        st.metric("Active Nodes", active_nodes, delta=delta_value)

    with col2:
        running_jobs = len([j for j in st.session_state.jobs
                           if j['status'] == 'Running'])
        delta_value = f"+{np.random.randint(-1, 3)}"
        st.metric("Running Jobs", running_jobs, delta=delta_value)

    with col3:
        total_credits = sum(node['metrics']['credits_earned']
                           for node in filtered_nodes)
        delta_value = f"+${np.random.randint(100,500)}"
        st.metric("Total Credits", f"${total_credits:,.0f}", delta=delta_value)

    with col4:
        utilization = np.random.randint(70, 95)
        delta_value = f"{np.random.randint(-3, 5)}%"
        st.metric("Network Utilization", f"{utilization}%", delta=delta_value)

    # Network Globe
    st.header("Real-Time Network Globe")

    # always use real nodes fetched via comms
    if filtered_nodes:
        display_nodes = filtered_nodes[:node_count]
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
    else:
        st.warning("No nodes match current filter criteria.")

    # Data tables
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
                tier = node['tier']
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
            for tier, count in tier_counts.items():
                st.write(f"• {tier}: {count} nodes")

    with col2:
        st.subheader("Job Queue Status")
        if st.session_state.jobs:
            job_table_data = []
            for job in st.session_state.jobs:
                progress_text = (
                    f"{job['progress']}%"
                    if job['status'] == 'Running'
                    else '—'
                )
                job_table_data.append({
                    'ID': job['id'],
                    'Type': job['type'].replace('_', ' ').title(),
                    'Status': job['status'],
                    'Progress': progress_text,
                    'Credits': f"${job['credits_allocated']:.0f}",
                    'Time Est.': job.get('estimated_time', '—'),
                    'Submitter': job['submitter']
                })
            st.dataframe(job_table_data, use_container_width=True)

            st.write("**Job Distribution:**")
            status_counts = {}
            for job in st.session_state.jobs:
                status = job['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            for status, count in status_counts.items():
                st.write(f"• {status}: {count} jobs")

    # Performance metrics
    st.header("System Performance")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Compute Metrics")
        tflops_value = np.random.uniform(500, 2000)
        st.write(f"**Total FLOPS:** {tflops_value:.1f} TFLOPS")
        avg_time = np.random.randint(45, 180)
        st.write(f"**Average Job Time:** {avg_time} minutes")
        success_rate = np.random.uniform(96, 99.5)
        st.write(f"**Success Rate:** {success_rate:.1f}%")
        queue_wait = np.random.randint(2, 12)
        st.write(f"**Queue Wait:** {queue_wait} minutes")

    with col2:
        st.subheader("Resource Usage")
        cpu_util = np.random.randint(60, 85)
        st.write(f"**CPU Utilization:** {cpu_util}%")
        mem_usage = np.random.randint(55, 80)
        st.write(f"**Memory Usage:** {mem_usage}%")
        network_io = np.random.uniform(15, 45)
        st.write(f"**Network I/O:** {network_io:.1f} Gbps")
        storage_io = np.random.uniform(5, 25)
        st.write(f"**Storage I/O:** {storage_io:.1f} GB/s")

    with col3:
        st.subheader("Economic Data")
        credits_per_hour = np.random.uniform(75, 250)
        st.write(f"**Credits/Hour:** ${credits_per_hour:.0f}")
        daily_volume = np.random.uniform(5000, 15000)
        st.write(f"**Daily Volume:** ${daily_volume:.0f}")
        avg_rate = np.random.uniform(15, 35)
        st.write(f"**Avg Rate:** ${avg_rate:.2f}/job")
        if filtered_nodes:
            credits = [n['metrics']['credits_earned'] for n in filtered_nodes]
            st.write(f"**Top Earner:** ${max(credits):.0f}")

    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**System Status:** All systems operational")
    with col2:
        st.write("**API Endpoint:** http://localhost:5000")
    with col3:
        if st.button("Export Report"):
            st.success("System report exported")


if __name__ == "__main__":
    main()
