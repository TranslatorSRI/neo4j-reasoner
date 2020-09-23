"""Neo4j lookup utilities."""
from abc import ABC, abstractmethod
import logging
from urllib.parse import urlparse

import httpx
from neo4j import GraphDatabase, basic_auth

logger = logging.getLogger(__name__)


class Neo4jDatabase():
    """Neo4j database.

    This is a thin wrapper that chooses whether to instantiate
    a Bolt interface or an HTTP interface.
    """

    def __new__(cls, url=None, **kwargs):
        """Generate database interface."""
        scheme = urlparse(url).scheme
        if scheme == 'http':
            return HttpInterface(url=url, **kwargs)
        if scheme == 'bolt':
            return BoltInterface(url=url, **kwargs)
        raise ValueError(f'Unsupported interface scheme "{scheme}"')

    @abstractmethod
    def run(self, statement, *args):
        """Run statement."""


class Neo4jInterface(ABC):
    """Abstract interface to Neo4j database."""

    def __init__(self, url=None, auth=None):
        """Initialize."""
        url = urlparse(url)
        self.hostname = url.hostname
        self.port = url.port
        self.auth = auth

    @abstractmethod
    def run(self, statement, *args):
        """Run statement."""


class HttpInterface(Neo4jInterface):
    """HTTP interface to Neo4j database."""

    def __init__(self, **kwargs):
        """Initialize."""
        super().__init__(**kwargs)
        self.url = f'http://{self.hostname}'
        if self.port:
            self.url += f':{self.port}'
        self.url += '/db/data/transaction/commit'

    def run(self, statement, *args):
        """Run statement."""
        response = httpx.post(
            self.url,
            auth=self.auth,
            json={"statements": [{"statement": statement}]},
            timeout=30.0,
        )
        if response.status_code == 401:
            raise ValueError('Unauthorized')
        # print(response.text)
        assert response.status_code < 300
        response = response.json()
        if response['errors']:
            raise RuntimeError(response['errors'][0]['message'])
        result = response['results'][0]
        result = [
            dict(zip(result['columns'], datum['row']))
            for datum in result['data']
        ]
        return result


class BoltInterface(Neo4jInterface):
    """Bolt interface to Neo4j database."""

    def __init__(self, **kwargs):
        """Initialize."""
        super().__init__(**kwargs)
        self.url = f'bolt://{self.hostname}:{self.port}'
        self.driver = GraphDatabase.driver(
            self.url,
            auth=self.auth and basic_auth(*self.auth)
        )

    def run(self, statement, *args):
        """Run statement."""
        with self.driver.session() as session:
            return [dict(row) for row in session.run(statement)]
