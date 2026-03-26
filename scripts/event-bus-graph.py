#!/usr/bin/env python3
"""
Mycelium Event Bus — Graphical Visualizer

Generates interactive HTML/SVG visualization of colony event tendrils.
Reads events.jsonl, outputs an HTML file with D3.js force-directed graph.

Usage:
  python3 event-bus-graph.py [--project <id>] [--since <min>] [--output <file>]
  
Output: events-visual.html (open in browser)
"""

import json
import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

WORKSPACE = Path(os.environ.get("WORKSPACE", Path(__file__).parent.parent))
EVENT_FILE = WORKSPACE / "events.jsonl"

def load_events(project=None, since_minutes=None):
    """Load events from JSONL file."""
    events = []
    cutoff = None
    if since_minutes:
        cutoff = datetime.utcnow() - timedelta(minutes=since_minutes)
    
    with open(EVENT_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                if project and event.get("project") != project:
                    continue
                if cutoff:
                    ts = datetime.fromisoformat(event["ts"].replace("Z", "+00:00"))
                    if ts.replace(tzinfo=None) < cutoff:
                        continue
                events.append(event)
            except (json.JSONDecodeError, KeyError):
                continue
    return events

def build_graph_data(events):
    """Build nodes and links for force-directed graph."""
    nodes = {}  # agent -> {role, event_count, type_counts}
    links = []  # {source, target, type, count}
    
    # Track agent interactions
    agent_timeline = defaultdict(list)
    
    for event in events:
        agent = event.get("agent", "unknown")
        role = event.get("role", "")
        etype = event.get("type", "")
        project = event.get("project", "default")
        
        if agent not in nodes:
            nodes[agent] = {
                "id": agent,
                "role": role,
                "event_count": 0,
                "types": defaultdict(int),
                "project": project
            }
        nodes[agent]["event_count"] += 1
        nodes[agent]["types"][etype] += 1
        
        agent_timeline[agent].append(event)
    
    # Build links from sequential events (tendrils)
    prev_agent = None
    for event in events:
        agent = event.get("agent", "unknown")
        if prev_agent and prev_agent != agent:
            links.append({
                "source": prev_agent,
                "target": agent,
                "type": event.get("type", "unknown"),
                "message": event.get("message", "")[:50],
                "ts": event.get("ts", "")
            })
        prev_agent = agent
    
    # Deduplicate links
    link_counts = defaultdict(int)
    for link in links:
        key = (link["source"], link["target"], link["type"])
        link_counts[key] += 1
    
    unique_links = []
    seen = set()
    for link in links:
        key = (link["source"], link["target"], link["type"])
        if key not in seen:
            seen.add(key)
            link["count"] = link_counts[key]
            unique_links.append(link)
    
    # Convert defaultdicts
    for node in nodes.values():
        node["types"] = dict(node["types"])
    
    return {
        "nodes": list(nodes.values()),
        "links": unique_links,
        "total_events": len(events)
    }

def generate_html(graph_data, output_file):
    """Generate interactive HTML visualization."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🌊 Mycelium Event Bus — Colony Flow</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { 
    font-family: 'SF Mono', 'Fira Code', monospace; 
    background: #0a0a0a; 
    color: #e0e0e0; 
    overflow: hidden;
  }
  #header {
    position: fixed; top: 0; left: 0; right: 0;
    padding: 16px 24px;
    background: linear-gradient(180deg, rgba(10,10,10,0.95), transparent);
    z-index: 100;
  }
  h1 { font-size: 18px; font-weight: 600; }
  .subtitle { color: #888; font-size: 13px; margin-top: 4px; }
  #stats {
    position: fixed; bottom: 16px; left: 16px;
    background: rgba(20,20,20,0.9); border: 1px solid #333;
    border-radius: 8px; padding: 12px 16px;
    font-size: 12px; z-index: 100;
  }
  #tooltip {
    position: fixed; pointer-events: none;
    background: rgba(20,20,20,0.95); border: 1px solid #444;
    border-radius: 6px; padding: 10px 14px;
    font-size: 12px; display: none; z-index: 200;
    max-width: 300px;
  }
  .role-brain { fill: #ffd700; }
  .role-sensor { fill: #00bfff; }
  .role-protector { fill: #ff6347; }
  .role-builder { fill: #32cd32; }
  .role-default { fill: #888; }
  .link { stroke-opacity: 0.4; }
  .link-label { fill: #666; font-size: 9px; }
  .node-label { fill: #ccc; font-size: 11px; font-weight: 500; }
</style>
</head>
<body>
<div id="header">
  <h1>🌊 Mycelium Event Bus</h1>
  <div class="subtitle">Colony activity flow — """ + str(graph_data["total_events"]) + """ events</div>
</div>
<div id="stats"></div>
<div id="tooltip"></div>
<svg id="graph"></svg>

<script>
const data = """ + json.dumps(graph_data) + """;

const width = window.innerWidth;
const height = window.innerHeight;

const svg = d3.select("#graph")
  .attr("width", width)
  .attr("height", height);

// Zoom
const g = svg.append("g");
svg.call(d3.zoom()
  .scaleExtent([0.3, 3])
  .on("zoom", (event) => g.attr("transform", event.transform)));

// Role colors
function roleColor(role) {
  switch(role) {
    case "brain": case "mycelium": return "#ffd700";
    case "sensor": case "scout": return "#00bfff";
    case "protector": case "army-ant": return "#ff6347";
    case "builder": case "dynamic-ant": return "#32cd32";
    default: return "#888";
  }
}

function roleIcon(role) {
  switch(role) {
    case "brain": case "mycelium": return "🧠";
    case "sensor": case "scout": return "🔍";
    case "protector": case "army-ant": return "🛡️";
    case "builder": case "dynamic-ant": return "🔨";
    default: return "•";
  }
}

// Arrow markers
svg.append("defs").selectAll("marker")
  .data(["tendril"])
  .enter().append("marker")
  .attr("id", d => d)
  .attr("viewBox", "0 -5 10 10")
  .attr("refX", 25)
  .attr("refY", 0)
  .attr("markerWidth", 6)
  .attr("markerHeight", 6)
  .attr("orient", "auto")
  .append("path")
  .attr("d", "M0,-5L10,0L0,5")
  .attr("fill", "#555");

// Simulation
const simulation = d3.forceSimulation(data.nodes)
  .force("link", d3.forceLink(data.links).id(d => d.id).distance(120))
  .force("charge", d3.forceManyBody().strength(-300))
  .force("center", d3.forceCenter(width/2, height/2))
  .force("collision", d3.forceCollide().radius(40));

// Links (tendrils)
const link = g.append("g")
  .selectAll("line")
  .data(data.links)
  .enter().append("line")
  .attr("class", "link")
  .attr("stroke", d => {
    const src = data.nodes.find(n => n.id === (d.source.id || d.source));
    return src ? roleColor(src.role) : "#555";
  })
  .attr("stroke-width", d => Math.min(d.count * 2, 6))
  .attr("marker-end", "url(#tendril)");

// Link labels
const linkLabel = g.append("g")
  .selectAll("text")
  .data(data.links)
  .enter().append("text")
  .attr("class", "link-label")
  .text(d => d.type);

// Nodes
const node = g.append("g")
  .selectAll("g")
  .data(data.nodes)
  .enter().append("g")
  .call(d3.drag()
    .on("start", dragStart)
    .on("drag", dragging)
    .on("end", dragEnd));

node.append("circle")
  .attr("r", d => 12 + Math.sqrt(d.event_count) * 4)
  .attr("fill", d => roleColor(d.role))
  .attr("fill-opacity", 0.3)
  .attr("stroke", d => roleColor(d.role))
  .attr("stroke-width", 2);

node.append("text")
  .attr("class", "node-label")
  .attr("dy", d => 24 + Math.sqrt(d.event_count) * 4)
  .attr("text-anchor", "middle")
  .text(d => d.id);

node.append("text")
  .attr("text-anchor", "middle")
  .attr("dy", 5)
  .text(d => roleIcon(d.role));

// Tooltip
const tooltip = d3.select("#tooltip");
node.on("mouseover", (event, d) => {
  tooltip.style("display", "block")
    .html(`<strong>${d.id}</strong><br>
      Role: ${d.role}<br>
      Events: ${d.event_count}<br>
      Types: ${JSON.stringify(d.types)}`);
})
.on("mousemove", (event) => {
  tooltip.style("left", (event.pageX + 10) + "px")
    .style("top", (event.pageY - 10) + "px");
})
.on("mouseout", () => tooltip.style("display", "none"));

// Tick
simulation.on("tick", () => {
  link
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y);
  
  linkLabel
    .attr("x", d => (d.source.x + d.target.x) / 2)
    .attr("y", d => (d.source.y + d.target.y) / 2);
  
  node.attr("transform", d => `translate(${d.x},${d.y})`);
});

// Stats panel
const stats = d3.select("#stats");
stats.html(`
  <div>📊 <strong>Colony Stats</strong></div>
  <div>Agents: ${data.nodes.length}</div>
  <div>Events: ${data.total_events}</div>
  <div>Tendrils: ${data.links.length}</div>
`);

// Drag
function dragStart(event, d) {
  if (!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x; d.fy = d.y;
}
function dragging(event, d) {
  d.fx = event.x; d.fy = event.y;
}
function dragEnd(event, d) {
  if (!event.active) simulation.alphaTarget(0);
  d.fx = null; d.fy = null;
}
</script>
</body>
</html>"""
    
    with open(output_file, "w") as f:
        f.write(html)
    print(f"✅ Generated: {output_file}")

def main():
    project = None
    since = 120  # last 2 hours
    output = str(WORKSPACE / "events-visual.html")
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] in ("--project", "-p") and i+1 < len(args):
            project = args[i+1]; i += 2
        elif args[i] in ("--since", "-s") and i+1 < len(args):
            since = int(args[i+1]); i += 2
        elif args[i] in ("--output", "-o") and i+1 < len(args):
            output = args[i+1]; i += 2
        else:
            i += 1
    
    events = load_events(project=project, since_minutes=since)
    if not events:
        print("⚠️  No events found. Run some agents first!")
        sys.exit(1)
    
    graph_data = build_graph_data(events)
    generate_html(graph_data, output)

if __name__ == "__main__":
    main()
