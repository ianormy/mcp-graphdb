import argparse
import asyncio
import os

from . import server
from . import graphdb_async_driver

def main():
    """Main entry point for the package."""
    parser = argparse.ArgumentParser(description="GraphDB SPARQL MCP Server")
    parser.add_argument("--db-url", default=None, help="GraphDB connection URL")
    parser.add_argument("--username", default=None, help="GraphDB username")
    parser.add_argument("--password", default=None, help="GraphDB password")
    parser.add_argument("--schema-file", default=None, help="path to the ontology")

    args = parser.parse_args()
    asyncio.run(
        server.main(
            args.db_url or os.getenv("DB_URI", "http://localhost:7687"),
            args.username or os.getenv("GRAPHDB_USERNAME", "graphdb"),
            args.password or os.getenv("GRAPHDB_PASSWORD", "password"),
            args.schema_file or os.getenv("SCHEMA_FILE", ""),
        )
    )


__all__ = ["main", "server", "graphdb_async_driver"]
