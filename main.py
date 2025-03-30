import var
import ifcopenshell
from utils import Graph
from neo4j_db import create_driver, push_graph_to_neo4j


file_path = "data/ifc/test1.ifc"
# ====================================================================
def main():
    # Load the IFC file
    model = ifcopenshell.open(file_path)
    root = model.by_type("IfcProject")[0]

    # Create a graph and establish BVH Tree
    # ====================================================================
    graph = Graph.create(root)
    graph.build_bvh()


    # Build the graph b ased on relationship
    # ====================================================================
    for node in graph.node_dict.values():
        if node.geom_info != None:
            node.near = [graph.node_dict[guid] for guid in graph.bvh_query(node.geom_info["bbox"])
                         if guid != node.guid]
    
    # Push the graph to Neo4j
    # ====================================================================
    # You need to install Neo4j and start the server locally or use a remote server
    # Save the name of your db and password as db_name and db_pw in var.py
    # By default, the neo4j runs locally on "bolt://localhost:7687"
    # User name by default is "neo4j" if you run locally
    # ====================================================================
    driver = create_driver(username=var.user_name, 
                           password=var.password,
                           server_uri="bolt://localhost:7687")
    push_graph_to_neo4j(driver, graph.node_dict)
    return

    # Open the Neo4j Browser at the uri here it is bolt://localhost:7687
    # Type MATCH (n) RETURN n LIMIT 25; to see your newly inserted nodes.
    # You can also do MATCH (a)-[r:NEAR]->(b) RETURN a,b; to visualize adjacency.
    # Or display a particular node by MATCH (n {guid: '19F6LEtSbAVBR1XKPuuhuV'})-[r]-(m) RETURN n, r, m
if __name__ == "__main__":
    main()