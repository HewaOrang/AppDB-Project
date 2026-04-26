"""Conference Management Application - Main Module"""
from db_sqlite import SQLiteDatabase
from db_neo4j import Neo4jDatabase

# Global database instances
sqlite_db = None
neo4j_db = None
neo4j_available = False
rooms_cache = None  # Cache for rooms to satisfy requirement


def display_menu():
    """Display the main menu"""
    print("\nConference Management")
    print("-" * 21)
    print("\nMENU")
    print("====")
    print("1 - View Speakers & Sessions")
    print("2 - View Attendees by Company")
    print("3 - Add New Attendee")
    print("4 - View Connected Attendees")
    print("5 - Add Attendee Connection")
    print("6 - View Rooms")
    print("x - Exit application")
    return input("Choice: ").strip()





def initialize_databases():
    """Initialize database connections"""
    global sqlite_db, neo4j_db, neo4j_available
    
    print("Initializing database connections...")
    
    # Initialize SQLite
    sqlite_db = SQLiteDatabase(db_file="appdbproj.db")
    
    if not sqlite_db.connect():
        print("Failed to connect to SQLite database.")
        return False
    
    # Initialize Neo4j
    neo4j_db = Neo4jDatabase(
        uri="neo4j://localhost:7687",
        user="neo4j",
        password="password"
    )
    
    if not neo4j_db.connect():
        print("Warning: Neo4j not running. Graph features will be unavailable.")
        print("You can still use Options 1-3 and 6.")
        neo4j_available = False
    else:
        neo4j_available = True
    
    return True


def main():
    """Main application loop"""
    if not initialize_databases():
        print("Failed to initialize databases. Exiting.")
        return
    
    try:
        while True:
            choice = display_menu()
            
            if choice == "1":
                option_1_view_speakers_sessions()
            elif choice == "2":
                option_2_view_attendees_by_company()
            elif choice == "3":
                option_3_add_new_attendee()
            elif choice == "4":
                option_4_view_connected_attendees()
            elif choice == "5":
                option_5_add_attendee_connection()
            elif choice == "6":
                option_6_view_rooms()
            elif choice == "x":
                print("Exiting application...")
                break
            else:
                # Show menu again for invalid input
                continue
    
    except KeyboardInterrupt:
        print("\nApplication interrupted.")
    finally:
        # Close database connections
        if sqlite_db:
            sqlite_db.disconnect()
        if neo4j_db:
            neo4j_db.disconnect()


if __name__ == "__main__":
    main()
