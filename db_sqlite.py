"""SQLite Database Connection Module"""
import sqlite3
from sqlite3 import Error

class SQLiteDatabase:
    def __init__(self, db_file="appdbproj.db"):
        self.db_file = db_file
        self.connection = None
    
    def connect(self):
        """Establish connection to SQLite database"""
        try:
            self.connection = sqlite3.connect(self.db_file)
            self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
            print(f"Successfully connected to SQLite database: {self.db_file}")
            return True
        except Error as e:
            print(f"Error connecting to SQLite: {e}")
            return False
    
    def disconnect(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            print("SQLite connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a SELECT query and return results"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            # Convert Row objects to dictionaries for compatibility
            return [dict(row) for row in results]
        except Error as e:
            print(f"Error executing query: {e}")
            return None
    
    def execute_insert_update_delete(self, query, params=None):
        """Execute INSERT, UPDATE, or DELETE query"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            self.connection.rollback()
            print(f"Error executing statement: {e}")
            return False
    
    def create_schema(self):
        """Create database schema"""
        schema_queries = [
            """
            CREATE TABLE IF NOT EXISTS company (
                companyID INTEGER PRIMARY KEY,
                companyName TEXT NOT NULL,
                industry TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS attendee (
                attendeeID INTEGER PRIMARY KEY,
                attendeeName TEXT NOT NULL,
                attendeeDOB TEXT NOT NULL,
                attendeeGender TEXT NOT NULL,
                attendeeCompanyID INTEGER NOT NULL,
                FOREIGN KEY (attendeeCompanyID) REFERENCES company(companyID)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS room (
                roomID INTEGER PRIMARY KEY,
                roomName TEXT NOT NULL,
                capacity INTEGER NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS session (
                sessionID INTEGER PRIMARY KEY,
                sessionTitle TEXT NOT NULL,
                speakerName TEXT NOT NULL,
                sessionDate TEXT NOT NULL,
                roomID INTEGER NOT NULL,
                FOREIGN KEY (roomID) REFERENCES room(roomID)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS registration (
                registrationID INTEGER PRIMARY KEY,
                attendeeID INTEGER NOT NULL,
                sessionID INTEGER NOT NULL,
                registeredAt TEXT NOT NULL,
                FOREIGN KEY (attendeeID) REFERENCES attendee(attendeeID),
                FOREIGN KEY (sessionID) REFERENCES session(sessionID)
            )
            """
        ]
        
        try:
            cursor = self.connection.cursor()
            for query in schema_queries:
                cursor.execute(query)
            self.connection.commit()
            cursor.close()
            print("Database schema created successfully")
            return True
        except Error as e:
            print(f"Error creating schema: {e}")
            return False
