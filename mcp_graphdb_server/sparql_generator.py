from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import logging

generate_sparql_template = """
Write a SPARQL SELECT query for querying a graph database.
The ontology schema delimited by triple backticks in Turtle format is:
```
{schema}
```
Use only the classes and properties provided in the schema to construct the SPARQL query.
Do not use any classes or properties that are not explicitly provided in the SPARQL query.
Include all necessary prefixes.
Do not include any explanations or apologies in your responses.
Do not wrap the query in backticks.
Do not include any text except the SPARQL query generated.
The question I would like you to answer delimited by triple backticks is:
```
{prompt}
```
"""

logger = logging.getLogger("sparql_generator")

class SparqlGenerator:
    def __init__(self, ontology: str):
        self._ontology_ttl = ontology
        self._llm = self.init_llm()

    def init_llm(self):
        load_dotenv()
        azure_endpoint = os.getenv("OPENAI_API_BASE")
        api_version = os.getenv("OPENAI_API_VERSION")
        api_key = os.getenv("OPENAI_API_KEY")
        azure_deployment = os.getenv("LLM_DEPLOYMENT_NAME")
        # Create LLM
        self._llm = AzureChatOpenAI(
            azure_deployment=azure_deployment,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
            api_key=api_key,
            temperature=1,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        if self._llm is None:
            raise ValueError("failed to initialise LLM")
        generate_sparql_prompt = PromptTemplate(
        input_variables=["schema", "prompt"], 
        template=generate_sparql_template
        )
        self._generate_sparql_chain = generate_sparql_prompt | self._llm | StrOutputParser()


    def generate_sparql(self, query: str) -> str:
        generate_sparql_result = self._generate_sparql_chain.invoke(
                    {
                        "prompt": query,
                        "schema": self._ontology_ttl
                    }
                )
        return generate_sparql_result
