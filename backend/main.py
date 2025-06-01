# from fastapi import FastAPI, Form

# app = FastAPI()

# @app.get('/')
# def read_root():
#     return {'Ping': 'Pong'}

# @app.get('/pipelines/parse')
# def parse_pipeline(pipeline: str = Form(...)):
#     return {'status': 'parsed'}



from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS for your frontend during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production
    allow_methods=["*"],
    allow_headers=["*"],
)

class Node(BaseModel):
    id: str
    # other node fields can be here if needed

class Edge(BaseModel):
    id: str = None  # optional edge id
    source: str
    target: str
    # other edge fields can be here if needed

class PipelineData(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

@app.post('/pipelines/parse')
async def parse_pipeline(pipeline: PipelineData):
    nodes = pipeline.nodes
    edges = pipeline.edges

    num_nodes = len(nodes)
    num_edges = len(edges)

    # Build adjacency list for graph
    graph = {node.id: [] for node in nodes}
    for edge in edges:
        if edge.source not in graph or edge.target not in graph:
            raise HTTPException(status_code=400, detail="Edge references invalid node IDs")
        graph[edge.source].append(edge.target)

    # Detect cycle with DFS to check if DAG
    visited = set()
    rec_stack = set()

    def dfs(node_id):
        if node_id in rec_stack:
            return True  # cycle found
        if node_id in visited:
            return False
        visited.add(node_id)
        rec_stack.add(node_id)
        for neighbor in graph[node_id]:
            if dfs(neighbor):
                return True
        rec_stack.remove(node_id)
        return False

    is_dag = not any(dfs(node_id) for node_id in graph)

    return {
        "num_nodes": num_nodes,
        "num_edges": num_edges,
        "is_dag": is_dag,
        
    }
