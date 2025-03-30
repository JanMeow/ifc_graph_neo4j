import numpy as np
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
import collision
from traversal import bfs_traverse, loop_detecton
# ====================================================================
# Geometry Processing
# ====================================================================
def get_bbox(arr):
  max = np.max(arr, axis = 0)
  min = np.min(arr, axis = 0)
  return np.vstack((min,max))
def get_geom_info(entity, get_global = False):
  if hasattr(entity, "Representation"):
    if entity.Representation != None:
      result = {
        "T_matrix": None,
        "vertex": None,
        "face": None,
        "bbox": None
      }
      try:
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, entity)
        result["T_matrix"] = ifcopenshell.util.shape.get_shape_matrix(shape)
        result["vertex"]  = np.around(ifcopenshell.util.shape.get_vertices(shape.geometry),2)
        result["face"] = ifcopenshell.util.shape.get_faces(shape.geometry)

        if get_global:
          vertex = result["vertex"]
          T_matrix = result["T_matrix"]
          ones = np.ones(shape = (vertex.shape[0],1))
          stacked = np.hstack((vertex, ones))
          global_coor = stacked@ T_matrix.T
          global_coor = np.around(global_coor[:,0:-1],2)
          result["vertex"] = global_coor

        result["bbox"] = get_bbox(result["vertex"])
        return result
      except:
        return None
def np_intersect_rows(arr1, arr2):
        set1 = set(map(tuple, arr1))
        set2 = set(map(tuple, arr2))
        shared = set1.intersection(set2)
        return np.array(list(shared))
# ====================================================================
# Graph helper functions 
# ====================================================================
def write_to_node(current_node):
  if current_node != None:
    geom_infos = get_geom_info(current_node, get_global = True)
    if geom_infos != None:
      # ignore id cause they are not relevant
      psets = {key: {k: v for k, v in subdict.items() if k != "id"}
    for key, subdict in ifcopenshell.util.element.get_psets(current_node).items()}
      node = Node(current_node.Name, current_node.is_a(), current_node.GlobalId, geom_infos, psets)
      return node
# ====================================================================
# Class Definition for Graph and Node 
# ====================================================================
class Graph:
  def __init__(self,root):
    self.root = root
    self.node_dict = {}
    self.bbox = None
    self.longest_axis = None
    self.bvh = None

  def __len__(self):
        return len(self.node_dict)
  def get_bbox(self):
    arr = np.vstack([node.geom_info["bbox"] for node in self.node_dict.values() 
                     if node.geom_info !=None])
    _max = np.max(arr, axis = 0)
    _min = np.min(arr, axis = 0)
    self.bbox = np.vstack((_min,_max))
    self.longest_axis = np.argmax((self.bbox[1] - self.bbox[0]))
    return 
  def sort_nodes_along_axis(self, axis):
    temp = sorted([node for node in self.node_dict.values()],key = lambda x: x.geom_info["bbox"][0][axis] )
    new_dict = {node.guid:node for node in temp}
    self.node_dict = new_dict
    return self.node_dict
  def build_bvh(self):
    sorted_nodes = list(self.sort_nodes_along_axis(self.longest_axis).values())
    self.bvh = collision.build_bvh(sorted_nodes)
    return 
  def bvh_query(self, bbox):
    collisions = []
    if self.bvh == None:
      print("BVH not built, building now")
      self.build_bvh()
    stack = [self.bvh]
    while stack:
      current_bvh = stack.pop()
      current_bbox = current_bvh.bbox
      if collision.intersect(bbox,current_bbox):
        if current_bvh.leaf:
          collisions.append(current_bvh.nodes)
        if current_bvh.left:
          stack.append(current_bvh.left)
        if current_bvh.right:
          stack.append(current_bvh.right)
    return [node.guid for node in collisions]
  def get_connections(self,guid):
    node = self.node_dict[guid]
    connections = [guid + "//" + node_n.guid for node_n in node.near
                   if node_n.guid != guid]
    return connections
  def loop_detection(self, guid, max_depth):
    node = self.node_dict[guid]
    return loop_detecton(node, max_depth)
  @classmethod
  def create(cls, root):
    cls = cls(root.GlobalId)
    for node in bfs_traverse(root, True,write_to_node):
      if node!= None:
        cls.node_dict[node.guid] = node
    cls.get_bbox()
    return cls
class Node:
  def __init__(self, name, _type, guid, geom_info, psets) :
    self.name = name
    self.geom_type = _type
    self.geom_info = geom_info
    self.guid = guid
    self.psets = psets
    self.near = []
  def intersect(node1,node2):
    bbox1 = node1.geom_info["bbox"]
    bbox2 = node2.geom_info["bbox"]
    return collision.intersect(bbox1,bbox2)