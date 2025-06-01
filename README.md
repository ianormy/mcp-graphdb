# GraphDB MCP Server

## 🌟 Overview

A Model Context Protocol (MCP) server implementation that provides database interaction and allows graph exploration capabilities through GraphDB. 
This server enables running SPARQL graph queries.

## 🧩 Components

### 🛠️ Tools

The server offers these core tools:

#### 📊 Query Tools
- `read-graphdb-sparql`
   - Execute SPARQL read queries to read data from a repository
   - Input: 
     - `query` (string): The SPARQL query to execute
   - Returns: Query results as JSON serialized array of objects

#### 🕸️ Schema Tools
- `get-graphdb-schema`
   - Get a list of the RDF triples that define the ontology for the GraphDB database
   - No input required
   - Returns: JSON serialized list of the RDF triples that define the ontology of the GraphDB database

## 🔧 Usage with Claude Desktop

<details>
  <summary>Legacy Syntax</summary>

```json
"mcpServers": {
  "graphdb": {
    "command": "uvx",
    "args": [
      "mcp-graphdb@0.1.8",
      "--db-url",
      "http://localhost:7200/repositories/msft-graphrag-300",
      "--username",
      "graphdb",
      "--password",
      "<your-password>"
    ]
  }
}
```
</details>

## 🚀 Development

### 📦 Prerequisites

1. Install `uv` (Universal Virtualenv):
```bash
# Using pip
pip install uv

# Using Homebrew on macOS
brew install uv

# Using cargo (Rust package manager)
cargo install uv
```

2. Clone the repository and set up the development environment:
```bash
# Clone the repository
git clone https://github.com/ianormy/mcp-graphdb.git
cd mcp-graphdb

# Create and activate virtual environment using uv
uv venv
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows

# Install dependencies
uv pip install -e .
```

### 🔧 Development Configuration

```json
# Add the server to your claude_desktop_config.json
"mcpServers": {
  "graphdb": {
    "command": "uv",
    "args": [
      "--directory", "parent_of_servers_repo/mcp_graphdb_server",
      "run", "mcp-graphdb-server"],
    "env": {
      "GRAPHDB_URI": "http://localhost",
      "GRAPHDB_USERNAME": "<your-username>",
      "GRAPHDB_PASSWORD": "<your-password>",
      "GRAPHDB_REPOSITORY": "repo"
    }
  }
}
```

## 📄 License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
