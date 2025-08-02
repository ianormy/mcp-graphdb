import json
import logging
from mcp_graphdb_server.graphdb_async_driver import GraphDBAsyncDriver
from mcp_graphdb_server.sparql_generator import SparqlGenerator
import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from typing import Any
import httpx
import mcp.types as types
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn
import argparse
from dotenv import load_dotenv


load_dotenv()  # Loads env variables
logger = logging.getLogger("mcp_graphdb_sparql")


def create_mcp_server(graphdb_driver: GraphDBAsyncDriver, sparql_generator: SparqlGenerator) -> FastMCP:
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
        
    async def generate_sparql_query(question: str = Field(..., description="The question to be answered.")) -> types.TextContent:
        """Generate a SPARQL query that will answer the provided question
        """
        sparql_str = sparql_generator.generate_sparql(query=question)
        return types.TextContent(type="text", text=sparql_str)


    mcp.add_tool(read_graphdb_sparql)
    mcp.add_tool(get_graphdb_schema)
    mcp.add_tool(generate_sparql_query)

    return mcp


def create_starlette_app(mcp_server: Server, *, debug: bool=False) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE.
    
    :param mcp_server: the MCP server to use
    :param debug: if True then apply extra debugging
    """
    sse = SseServerTransport("/messages/")
    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )
    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


def main() -> None:
    logger.info("Starting MCP GraphDB Server")
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    parser.add_argument('--db-url', default='https://vf56dd311683f4e689be.sandbox.graphwise.ai/repositories/era', help="GraphDB repository endpoint")
    parser.add_argument('--schema-file', default='D:\\Data\\ERA\\data_interop_era_europa_eu_era_vocabulary_v3_20240618_ontology.ttl', help="GraphDB schema file")
    args = parser.parse_args()
    graphdb_async_driver = GraphDBAsyncDriver(query_endpoint=args.db_url, local_file=args.schema_file)
    sparql_generator = SparqlGenerator(graphdb_async_driver.get_schema)
    mcp = create_mcp_server(graphdb_async_driver, sparql_generator=sparql_generator)
    mcp_server = mcp._mcp_server
    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)
    uvicorn.run(starlette_app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
