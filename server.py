"""Neo4j Reasoner with FastAPI, reasoner-pydantic, and reasoner."""
import json
import logging
import os

from fastapi import FastAPI, Body
from reasoner.cypher import get_query
from reasoner_pydantic import Request, Message

from neo4jx import Neo4jDatabase

LOGGER = logging.getLogger(__name__)

NEO4J_URL = os.environ.get('NEO4J_URL', 'http://localhost:7474')
NEO4J_USER = os.environ.get('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.environ.get('REASONER_VERSION', 'pword')
TITLE = os.environ.get('REASONER_TITLE', 'Neo4j Reasoner API')
VERSION = os.environ.get('REASONER_VERSION', '1.0.0')

APP = FastAPI(
    title=TITLE,
    version=VERSION,
)

with open('examples/request.json', 'r') as stream:
    request_example = json.load(stream)


@APP.post('/query', response_model=Message)
async def answer_question(
        request: Request = Body(
            ...,
            example=request_example
        ),
) -> Message:
    """Answer question using Neo4j."""
    message = request.message.dict()
    query = get_query(message['query_graph'])
    neo4jx = Neo4jDatabase(
        url=NEO4J_URL,
        auth=(NEO4J_USER, NEO4J_PASSWORD),
    )
    results = neo4jx.run(query)
    message.update(results[0])
    if not message['results']:
        LOGGER.info(
            'The following Cypher query produced 0 results:\n%s',
            query,
        )
    return message
