"""
Configuration module for database connections.
Load credentials from environment variables or use defaults.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MySQL Configuration
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'appdbproj')

# Neo4j Configuration
NEO4J_URI = os.getenv('NEO4J_URI', 'neo4j://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'appdbneo4j')
NEO4J_DATABASE = os.getenv('NEO4J_DATABASE', 'appdbprojNeo4j')


# MySQL connection parameters
MYSQL_CONFIG = {
    'host': MYSQL_HOST,
    'user': MYSQL_USER,
    'password': MYSQL_PASSWORD,
    'database': MYSQL_DATABASE
}

# Neo4j connection parameters
NEO4J_CONFIG = {
    'uri': NEO4J_URI,
    'user': NEO4J_USER,
    'password': NEO4J_PASSWORD
}
