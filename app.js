const colorPalette = {};
for (let i = 0; i < 8; i++) {
    const color = getComputedStyle(document.documentElement).getPropertyValue(`--cluster-${i}`).trim();
    if (color) colorPalette[i] = color;
}

// Initialize Force Graph
const elem = document.getElementById('graph-container');
const Graph = ForceGraph()(elem)
    .backgroundColor('#0b0f19')
    .nodeRelSize(4)
    .nodeVal('val')
    .nodeLabel('name')
    .nodeColor(node => colorPalette[node.cluster])
    .linkColor(() => 'rgba(255,255,255,0.1)')
    .linkWidth(0.5)
    .cooldownTicks(100)
    .warmupTicks(20)
    .onNodeClick(node => {
        showNodePanel(node);
        // Center/zoom on node
        Graph.centerAt(node.x, node.y, 1000);
        Graph.zoom(4, 2000);
    })
    .onBackgroundClick(() => {
        hideNodePanel();
    })
    .onEngineStop(() => {
        Graph.zoomToFit(400, 50);
    });

// Fetch Data
async function loadNetworkData() {
    try {
        const btn = document.getElementById('btn-recluster');
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
        btn.disabled = true;

        const users = document.getElementById('input-users').value;
        const clusters = document.getElementById('input-clusters').value;

        const response = await fetch(`/api/network?n_users=${users}&clusters=${clusters}`);
        const data = await response.json();
        
        Graph.graphData(data);

        // Update UI Stats
        document.getElementById('stat-nodes').textContent = data.nodes.length;
        document.getElementById('stat-links').textContent = data.links.length;

        // Create Legend
        createLegend(data.nodes);

        btn.innerHTML = '<i class="fa-solid fa-rotate"></i> Re-Cluster Data';
        btn.disabled = false;

    } catch (error) {
        console.error("Failed to load network data:", error);
        alert("Failed to load data. Is the backend running?");
    }
}

function createLegend(nodes) {
    const legendContainer = document.getElementById('legend-items');
    legendContainer.innerHTML = '';
    
    // Extract unique personas and map them to their cluster
    const clusterMap = {};
    nodes.forEach(n => {
        if (!clusterMap[n.cluster]) {
            clusterMap[n.cluster] = n.persona;
        }
    });

    Object.keys(clusterMap).sort().forEach(cluster => {
        const item = document.createElement('div');
        item.className = 'legend-item';
        
        const color = colorPalette[cluster];
        
        item.innerHTML = `
            <div class="legend-color" style="background: ${color}; color: ${color}"></div>
            <span>${clusterMap[cluster]}</span>
        `;
        legendContainer.appendChild(item);
    });
}

// UI Interactions
function showNodePanel(node) {
    const panel = document.getElementById('node-panel');
    panel.classList.remove('hidden');
    
    document.getElementById('node-name').textContent = node.name;
    document.getElementById('node-persona').textContent = node.persona;
    document.getElementById('node-followers').textContent = Math.round(node.followers).toLocaleString();
    document.getElementById('node-posts').textContent = node.posts.toFixed(1);
    document.getElementById('node-likes').textContent = Math.round(node.likes).toLocaleString();
    
    const avatar = document.getElementById('node-avatar');
    avatar.style.background = colorPalette[node.cluster];
}

function hideNodePanel() {
    document.getElementById('node-panel').classList.add('hidden');
}

document.getElementById('close-panel').addEventListener('click', hideNodePanel);
document.getElementById('btn-recluster').addEventListener('click', loadNetworkData);

// Sliders UI
document.getElementById('input-users').addEventListener('input', e => {
    document.getElementById('users-val').textContent = e.target.value;
});
document.getElementById('input-clusters').addEventListener('input', e => {
    document.getElementById('clusters-val').textContent = e.target.value;
});

// Initial Load
loadNetworkData();

// Handle window resize
window.addEventListener('resize', () => {
    Graph.width(window.innerWidth);
    Graph.height(window.innerHeight);
});
