# Neo4j Reasoner API

__Access Swagger UI at `http://HOST:2304/docs`.__

## Installation

### Local Installation

```bash
pip install -r requirements
```

### Docker Installation

```bash
docker build -t neo4j_reasoner .
```

## Deployment

### Local Deployment

```bash
./main.sh
```

### Docker Deployment

```bash
docker run -p 2304:2304 --name neo4j_reasoner -d neo4j_reasoner
```
