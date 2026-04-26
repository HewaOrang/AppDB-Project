"""Neo4j Database Connection Module"""
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

class Neo4jDatabase:
    def __init__(self, uri="neo4j://localhost:7687", user="neo4j", password="password"):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
    
    def connect(self):
        """Establish connection to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            print("Successfully connected to Neo4j database")
            return True
        except ServiceUnavailable as e:
            print(f"Error connecting to Neo4j: {e}")
            return False
    
    def disconnect(self):
        """Close the database driver"""
        if self.driver:
            self.driver.close()
            print("Neo4j connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            with self.driver.session() as session:
                result = session.run(query, params or {})
                records = [record for record in result]
                return records
        except Exception as e:
            print(f"Error executing Neo4j query: {e}")
            return None
    
    def execute_write(self, query, params=None):
        """Execute a write query (CREATE, UPDATE, DELETE)"""
        try:
            with self.driver.session() as session:
                result = session.run(query, params or {})
                summary = result.consume()
                return True, summary
        except Exception as e:
            print(f"Error executing Neo4j write: {e}")
            return False, str(e)
