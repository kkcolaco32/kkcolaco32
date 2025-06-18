import networkx as nx
import matplotlib.pyplot as plt

# Define the graph
G = nx.DiGraph()

# Add nodes
nodes = [
    "Interpret User Intent",
    "Crawl and Extract",
    "Identify Failure Pattern",
    "Correlate Events",
    "Generate Insights",
    "Report Results"
]
G.add_nodes_from(nodes)

# Add edges
edges = [
    ("Interpret User Intent", "Crawl and Extract"),
    ("Crawl and Extract", "Identify Failure Pattern"),
    ("Identify Failure Pattern", "Correlate Events"),
    ("Correlate Events", "Generate Insights"),
    ("Generate Insights", "Report Results")
]
G.add_edges_from(edges)

# Manual horizontal layout
pos = {node: (i, 0) for i, node in enumerate(nodes)}

plt.figure(figsize=(14, 3))
nx.draw(G, pos, with_labels=True, node_color='#B3E5FC', node_size=3500, font_size=12, font_weight='bold', edge_color='#0288D1', arrowsize=30)
plt.title("Agentic Workflow: One-Line View", fontsize=16)
plt.axis('off')
plt.tight_layout()
plt.show()
