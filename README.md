
#IFC to Graph + Neo4j Integration
This script demonstrates how to:

Load an IFC model using ifcopenshell.

Build a graph of IFC elements and their bounding volumes.

Compute a BVH (Bounding Volume Hierarchy) for efficient spatial queries.

Identify “near” elements based on overlapping bounding volumes.

Push the resulting graph (nodes and relationships) into a Neo4j database.

Prerequisites
Python 3.7+ (or a recent version).

ifcopenshell to read and parse IFC files.

Install with pip install ifcopenshell (or see IfcOpenShell docs).

Neo4j (installed locally or accessible remotely).

The script assumes a running Neo4j instance at bolt://localhost:7687.

Alternatively, modify the URI if using a remote server or different port.

Neo4j Python driver for connecting to Neo4j.

Install with pip install neo4j.

A file named var.py containing your Neo4j username/password:

python
Kopieren
Bearbeiten
user_name = "neo4j"
password = "your_db_password"
Adjust these accordingly.

How It Works
Load IFC file:
The script opens an IFC file (in this example data/ifc/test1.ifc) using ifcopenshell.open(file_path).

Build a Graph:

Graph.create(root) traverses the IFC’s spatial hierarchy and creates a node (Node) for each IFC element.

Each node contains guid, geom_info (including bounding boxes), and IFC attributes.

Construct BVH:

graph.build_bvh() builds a bounding volume hierarchy for all elements. This accelerates spatial queries (e.g., finding overlapping bounding boxes).

Near Relationship:

For each node with a bounding box, the script queries the BVH to find other nodes that potentially intersect in space.

The script assigns a list of “near” node references: node.near = [...].

Push to Neo4j:

A Neo4j driver is created with create_driver(), connecting to a user-specified server URI and credentials from var.py.

push_graph_to_neo4j(driver, graph.node_dict) iterates through each node, inserting them (with their properties) into Neo4j, and creating “NEAR” relationships between nodes that are spatially close.

How to Run
Install dependencies:

bash
Kopieren
Bearbeiten
pip install ifcopenshell neo4j
Set up Neo4j:

Install Neo4j (see neo4j.com/download).

Start the Neo4j server (e.g., on bolt://localhost:7687).

Note your username/password (defaults might be neo4j / neo4j).

Create var.py:

python
Kopieren
Bearbeiten
# var.py
user_name = "neo4j"
password = "mysecretpassword"
Run the script:

bash
Kopieren
Bearbeiten
python main.py
(assuming your script is named main.py with the main() function).

Check in Neo4j:

Open Neo4j Browser at http://localhost:7474.

Run:

cypher
Kopieren
Bearbeiten
MATCH (n) RETURN n LIMIT 25;
You should see newly inserted IFC elements labeled (depending on your code) such as :IfcElement, plus their relationships.

Customizing
IFC File: Change file_path = "data/ifc/test1.ifc" to your own IFC file path.

Neo4j credentials: Adjust var.py for your environment.

BVH logic: Modify how bounding boxes are calculated or how “near” is determined, if needed.

Labels and Properties in Neo4j: You can map element types or psets to separate labels, relationships, or property keys.

Troubleshooting
No geometry or missing bounding boxes: Ensure geom_info is populated in your IFC processing logic. Some IFC elements may lack geometric representations.

Authentication errors: Check that user_name and password in var.py match your Neo4j credentials.

Cannot open IFC: IfcOpenShell might not support certain IFC versions or partial geometry. Update IfcOpenShell or test with simpler IFCs.

Enjoy exploring your IFC model in Neo4j!
