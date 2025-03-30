import json
from neo4j import GraphDatabase

# ====================================================================
# Connecting to the graph DB
# ====================================================================
def create_driver(username, password, server_uri = "bolt://localhost:7687"):
    """
    Create a Neo4j driver instance.
    :param server_uri: URI of the Neo4j server (e.g., "bolt://localhost:7687")
    :param username: Username for authentication
    :param password: Password for authentication
    :return: Neo4j driver instance
    """
    return GraphDatabase.driver(server_uri, auth=(username, password))

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
# ====================================================================
# Push GTaph to neo4j 
# ====================================================================
def push_graph_to_neo4j(driver, node_dict):
    """
    :param driver: an instance of neo4j.GraphDatabase.driver
    :param node_dict: e.g. graph.node_dict, a dict of {guid: Node}
    """

    with driver.session() as session:
        # First create (merge) each node
        for guid, node in node_dict.items():
            # Dont save BBox/ T matrix and translating np array to JSON serialisable
            skip_keys = ["bbox", "t_matrix"]
            geom_info_to_db = {
                k:v.tolist() 
                for k,v in node.geom_info.items() 
                if k in skip_keys
                }
            
            label = node.geom_type  # e.g. "IfcWall", "IfcBeam", etc.
            cypher_query = f"""
            MERGE (n:{label} {{guid: $guid}})
            ON CREATE SET
                n.name = $name,
                n.geom_type = $geom_type,
                n.psets = $psets,
                n.geom_info = $geom_info
            """

            session.run(
                cypher_query,
                {
                    "guid": node.guid,
                    "name": node.name,
                    "geom_type": node.geom_type,
                    "psets": json.dumps(node.psets),
                    "geom_info": json.dumps(geom_info_to_db)
                }
            )

        # Then create relationships
        # node.near is a list of other node references
        for guid, node in node_dict.items():
            for near_node in node.near:
                guid_a = guid
                guid_b = near_node.guid
                label_a = node.geom_type
                label_b = near_node.geom_type
                cypher_query = f"""
                    MATCH (a:{label_a} {{guid: $guid_a}})
                    MATCH (b:{label_b} {{guid: $guid_b}})
                    MERGE (a)-[:NEAR]->(b)
                    """
                session.run(
                    cypher_query,
                    {"guid_a": guid_a, "guid_b": guid_b}
                )