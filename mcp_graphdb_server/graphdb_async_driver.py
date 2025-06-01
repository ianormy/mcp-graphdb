import json
import rdflib
from rdflib.plugins.stores import sparqlstore
from rdflib.exceptions import ParserError
from rdflib.query import ResultRow
from pyparsing import ParseException
from rdflib.plugins.sparql import prepareQuery
import os
from typing import List, Optional, Union


class GraphDBAsyncDriver:
    def __init__(self,
                 query_endpoint: str,
                 local_file: str,
                 local_file_format: Optional[str] = None,
    ) -> None:
        """Set up the GraphDB driver.

        :param query_endpoint: SPARQL endpoint for queries, read access
            If GraphDB is secured, set the environment variables 'GRAPHDB_USERNAME' and 'GRAPHDB_PASSWORD'.

        :param local_file: a local RDF ontology file.
            Supported RDF formats:
            Turtle, RDF/XML, JSON-LD, N-Triples, Notation-3, Trig, Trix, N-Quads.
            If the rdf format can't be determined from the file extension,
            pass explicitly the rdf format in `local_file_format` param.

        :param local_file_format: Used if the rdf format can't be determined from the local file extension.
            One of "json-ld", "xml", "n3", "turtle", "nt", "trig", "nquads", "trix"
        """
        auth = self._get_auth()
        store = sparqlstore.SPARQLStore(auth=auth)
        store.open(query_endpoint)

        self.graph = rdflib.Graph(store, identifier=None, bind_namespaces="none")
        self._check_connectivity()

        ontology_schema_graph = self._load_ontology_schema_from_file(
            local_file,
            local_file_format,
        )
        self.schema = ontology_schema_graph.serialize(format="turtle")

    @staticmethod
    def _get_auth() -> Union[tuple, None]:
        """Returns the basic authentication configuration
        """
        username = os.environ.get("GRAPHDB_USERNAME", None)
        password = os.environ.get("GRAPHDB_PASSWORD", None)

        if username:
            if not password:
                raise ValueError(
                    "Environment variable 'GRAPHDB_USERNAME' is set, "
                    "but 'GRAPHDB_PASSWORD' is not set."
                )
            else:
                return username, password
        return None

    def _check_connectivity(self) -> None:
        """Executes a simple `ASK` query to check connectivity
        """
        try:
            self.graph.query("ASK { ?s ?p ?o }")
        except ValueError:
            raise ValueError(
                "Could not query the provided endpoint. "
                "Please, check, if the value of the provided "
                "query_endpoint points to the right repository. "
                "If GraphDB is secured, please, "
                "make sure that the environment variables "
                "'GRAPHDB_USERNAME' and 'GRAPHDB_PASSWORD' are set."
            )

    @staticmethod
    def _load_ontology_schema_from_file(local_file: str, local_file_format: str = None) -> rdflib.ConjunctiveGraph:
        """Parse the ontology schema statements from the provided file

        :param local_file: a local RDF ontology file.
        :param local_file_format: the file format of the local ontology file.
        """
        if not os.path.exists(local_file):
            raise FileNotFoundError(f"File {local_file} does not exist.")
        if not os.access(local_file, os.R_OK):
            raise PermissionError(f"Read permission for {local_file} is restricted")
        graph = rdflib.ConjunctiveGraph()
        try:
            graph.parse(local_file, format=local_file_format)
        except Exception as e:
            raise ValueError(f"Invalid file format for {local_file} : ", e)
        return graph

    @property
    def get_schema(self) -> str:
        """Returns the schema of the graph database in turtle format
        """
        return self.schema

    async def query_native(self, query: str):
        """Query the graph.

        :param query: The SPARQL query
        """
        res = self.graph.query(query)
        results_json = res.serialize(format="json")
        bindings = json.loads(results_json)["results"]["bindings"]
        bindings = [{k: v["value"] for k, v in result.items()} for result in bindings]
        return bindings
