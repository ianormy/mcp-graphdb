import json
import logging
from mcp_graphdb_server.graphdb_async_driver import GraphDBAsyncDriver
import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import Field

logger = logging.getLogger("mcp_graphdb_sparql")


def create_mcp_server(graphdb_driver: GraphDBAsyncDriver) -> FastMCP:
    mcp: FastMCP = FastMCP("mcp-graphdb-server", dependencies=["rdflib", "pydantic"])

    async def get_graphdb_schema() -> list[types.TextContent]:
        """List the schema for the GraphDB database
        """
        results_json_str = graphdb_driver.get_schema
        return [types.TextContent(type="text", text=results_json_str)]

    async def read_graphdb_sparql(
        query: str = Field(..., description="The SPARQL query to execute."),
    ) -> list[types.TextContent]:
        """Execute a read SPARQL query on the GraphDB database."""
        try:
            result_json = await graphdb_driver.query_native(query)
            result_txt = json.dumps(result_json)
            return [
                    types.TextContent(type="text", text=result_txt)
            ]
        except Exception as e:
            logger.error(f"Database error whilst executing query: {e}\n{query}")
            return [
                types.TextContent(type="text", text=f"Error: {e}\n{query}")
            ]


    mcp.add_tool(read_graphdb_sparql)
    mcp.add_tool(get_graphdb_schema)

    return mcp


def main(
    db_url: str,
    username: str,
    password: str,
    schema_file: str
) -> None:
    logger.info("Starting MCP GraphDB Server")
    graphdb_async_driver = GraphDBAsyncDriver(query_endpoint=db_url, local_file=schema_file)
    mcp = create_mcp_server(graphdb_async_driver)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main(db_url="http://127.0.0.1:7200/repositories/starwars", username="", password="", schema_file="D:\\Data\\StarWars\\starwars-ontology.trig")
