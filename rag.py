from openai import OpenAI
from pydantic import BaseModel
from utils import Node



def generate_cypher_query(text_query, api_key, model ="gpt-4o-mini"):

  client = OpenAI(
      api_key=api_key,
  )

  example_node = Node(
      guid="0iQBVm0_H9Wvgw3fWqEB3m",
      name="HÜLLKÖRPER",
      _type="IfcWall",
      psets={"example_pset": "example_value"},
      geom_info={
          "vertex": [[0, 0, 0], [1, 1, 1], [1, 2, 3], [5, 1, 3]],
          "face": [[0, 1, 2], [1, 2, 3]]
      }  )

  response = client.responses.create(
      model=model,
      input = [
        {
          "role":"developer",
          "content": f"Considering the following example node converted from an ifc element in a BIM model to a node in neo4j database with the following attributes {vars(example_node)} where psets and geom_info are Json objects, generate a cypher query that can be run in neo4j database. The cypher query should be in the format of a string that can be run directly in Neo4j."
        },
         {
          "role":"developer",
          "content": f"Only return your response in cypher query. Do not add any other text. The cypher query should be in the format of a string that can be run directly in Neo4j."
        },
        {
          "role":"user",
          "content": f"Generate an equivalent neo4j cypher query for the following usage: {text_query}"
        }
      ]

  )

  return response.output_text
