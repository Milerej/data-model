import streamlit as st
from pyvis.network import Network
import networkx as nx
import streamlit.components.v1 as components
import tempfile
import os

# Clear cache at start
st.cache_data.clear()
st.cache_resource.clear()

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == "Showmethemoney":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("⚠️ Password incorrect")
        return False
    else:
        # Password correct.
        return True

@st.cache_data
def create_network_data():
    # Define entity modules and colors
    entities = {
        "System Management": {
            "color": "Dark Green", 
            "size": 50, 
            "shape": "dot",
            "title": "System Management Module"
        },
        # Main Modules
        "System Identity & Classification": {
            "color": "Green", 
            "size": 25, 
            "shape": "dot",
            "title": "System Identity & Classification Sub-Module"
        },
        "Criticality & Risk": {
            "color": "Green", 
            "size": 25,
            "shape": "dot",
            "title": "Criticality & Risk Sub-Module"
        },
        "System Resilience": {
            "color": "Green", 
            "size": 25,
            "shape": "dot",
            "title": "System Resilience Sub-Module"
        },
        "Hosting and System Dependencies": {
            "color": "Green", 
            "size": 25,
            "shape": "dot",
            "title": "Hosting and System Dependencies Sub-Module"
        },
        # [Rest of your entities dictionary...]
    }

    # Define edges with the hierarchical structure
    edges = [
        # Main module connections
        ("System Management", "System Identity & Classification", "", ""),
        ("System Management", "Criticality & Risk", "", ""),
        ("System Management", "System Resilience", "", ""),
        ("System Management", "Hosting and System Dependencies", "", ""),
        # [Rest of your edges list...]
    ]

    return entities, edges

def create_network_graph(entities, edges):
    # Create NetworkX graph
    G = nx.DiGraph()
    for node, attributes in entities.items():
        node_attrs = {
            "color": attributes["color"],
            "size": attributes["size"],
            "shape": attributes["shape"],
            "title": attributes["title"],
            "label": node
        }
        G.add_node(node, **node_attrs)

    # Add edges
    for source, target, label, direction in edges:
        G.add_edge(source, target, title=label, label=label, arrows=direction)

    # Create interactive PyVis network
    net = Network(height="900px", width="100%", directed=True, notebook=True)
    net.from_nx(G)

    # Set options
    net.set_options("""
    {
        "physics": {
            "enabled": true,
            "stabilization": {
                "enabled": true,
                "iterations": 2000,
                "updateInterval": 25,
                "onlyDynamicEdges": false,
                "fit": true
            },
            "barnesHut": {
                "gravitationalConstant": -60000,
                "centralGravity": 0.1,
                "springLength": 1000,
                "springConstant": 0.08,
                "damping": 0.12,
                "avoidOverlap": 20
            },
            "minVelocity": 0.75,
            "maxVelocity": 30
        },
        "edges": {
            "smooth": {
                "type": "curvedCW",
                "roundness": 0.2,
                "forceDirection": "horizontal"
            },
            "length": 300,
            "font": {
                "size": 11,
                "strokeWidth": 2,
                "strokeColor": "#ffffff"
            },
            "color": {
                "inherit": false,
                "color": "#2E7D32",
                "opacity": 0.8
            },
            "width": 1.5
        },
        "nodes": {
            "font": {
                "size": 12,
                "strokeWidth": 2,
                "strokeColor": "#ffffff"
            },
            "margin": 12,
            "scaling": {
                "min": 10,
                "max": 30
            },
            "fixed": {
                "x": false,
                "y": false
            }
        },
        "layout": {
            "improvedLayout": true,
            "randomSeed": 42,
            "hierarchical": {
                "enabled": false,
                "nodeSpacing": 300,
                "levelSeparation": 300,
                "treeSpacing": 300
            }
        }
    }
    """)

    return net

def display_network(net):
    """Function to display the network with fullscreen capability"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8') as tmp_file:
        net.save_graph(tmp_file.name)
        with open(tmp_file.name, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        fullscreen_html = """
        <button 
            style="
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                padding: 8px 16px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-family: Arial, sans-serif;
                font-size: 14px;
            "
            onclick="toggleFullscreen()"
        >
            Full Screen
        </button>
        <script>
            function toggleFullscreen() {
                let elem = document.documentElement;
                if (!document.fullscreenElement) {
                    if (elem.requestFullscreen) {
                        elem.requestFullscreen();
                    } else if (elem.webkitRequestFullscreen) {
                        elem.webkitRequestFullscreen();
                    } else if (elem.msRequestFullscreen) {
                        elem.msRequestFullscreen();
                    }
                } else {
                    if (document.exitFullscreen) {
                        document.exitFullscreen();
                    } else if (document.webkitExitFullscreen) {
                        document.webkitExitFullscreen();
                    } else if (document.msExitFullscreen) {
                        document.msExitFullscreen();
                    }
                }
            }
        </script>
        """
        
        modified_html = html_content.replace('</body>', f'{fullscreen_html}</body>')
        
    try:
        components.html(modified_html, height=900)
    finally:
        # Clean up the temporary file
        try:
            os.unlink(tmp_file.name)
        except:
            pass

def main():
    if 'graph_version' not in st.session_state:
        st.session_state.graph_version = 0

    if check_password():
        st.set_page_config(page_title="Interactive Interdependency Graph", layout="wide")
        
        # Add title and refresh button in the same row
        col1, col2 = st.columns([6, 1])
        with col1:
            st.title("⚙️ Data Model : System Management")
        with col2:
            if st.button('Refresh Graph'):
                st.session_state.graph_version += 1
                st.experimental_rerun()

        # Create and display the network
        try:
            entities, edges = create_network_data()
            net = create_network_graph(entities, edges)
            display_network(net)
        except Exception as e:
            st.error(f"An error occurred while generating the graph: {str(e)}")

if __name__ == "__main__":
    main()
