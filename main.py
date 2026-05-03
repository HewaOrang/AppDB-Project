"""Conference Management Application - Main Module"""
import mysql.connector
from mysql.connector import Error as MySQLError
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError
import config

# Global database instances
mysql_connection = None
neo4j_driver = None
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


def option_1_view_speakers_sessions():
    """Option 1: View Speakers & Sessions"""
    print("Enter speaker name : ", end="")
    speaker_name = input().strip()
    
    try:
        cursor = mysql_connection.cursor(dictionary=True)
        query = """
        SELECT 
            s.speakerName,
            s.sessionTitle,
            r.roomName
        FROM session s
        JOIN room r ON s.roomID = r.roomID
        WHERE s.speakerName LIKE %s
        ORDER BY s.speakerName, s.sessionTitle
        """
        cursor.execute(query, (f"%{speaker_name}%",))
        results = cursor.fetchall()
        cursor.close()
        
        print(f"Session Details For : {speaker_name}")
        print("-" * 50)
        
        if results:
            for row in results:
                print(f"{row['speakerName']} | {row['sessionTitle']} | {row['roomName']}")
        else:
            print("No speakers found of that name")
    
    except MySQLError as err:
        print(f"*** ERROR *** {err}")


def option_2_view_attendees_by_company():
    """Option 2: View Attendees by Company"""
    while True:
        print("Enter Company ID : ", end="")
        try:
            company_id = int(input().strip())
            if company_id <= 0:
                continue
        except ValueError:
            continue
        
        try:
            cursor = mysql_connection.cursor(dictionary=True)
            
            # Check if company exists
            company_query = "SELECT companyName FROM company WHERE companyID = %s"
            cursor.execute(company_query, (company_id,))
            company_result = cursor.fetchone()
            
            if not company_result:
                print(f"Company with ID {company_id} doesn't exist")
                cursor.close()
                continue
            
            company_name = company_result['companyName']
            
            # Get attendees from this company
            attendees_query = """
            SELECT 
                a.attendeeName,
                a.attendeeDOB,
                s.sessionTitle,
                s.speakerName,
                r.roomName
            FROM attendee a
            JOIN registration reg ON a.attendeeID = reg.attendeeID
            JOIN session s ON reg.sessionID = s.sessionID
            JOIN room r ON s.roomID = r.roomID
            WHERE a.attendeeCompanyID = %s
            ORDER BY a.attendeeName
            """
            
            cursor.execute(attendees_query, (company_id,))
            results = cursor.fetchall()
            
            print(f"Enter Company ID : {company_id}")
            print(f"{company_name} Attendees")
            print("-" * 120)
            
            if results:
                for row in results:
                    print(f"{row['attendeeName']} | {row['attendeeDOB']} | {row['sessionTitle']} | {row['speakerName']} | {row['roomName']}")
            else:
                print(f"No attendees found for {company_name}")
            
            cursor.close()
            break
        
        except MySQLError as err:
            print(f"*** ERROR *** {err}")
            continue


def option_3_add_new_attendee():
    """Option 3: Add New Attendee"""
    print("Add New Attendee")
    print("-" * 16)
    
    # Get Attendee ID
    while True:
        print("Attendee ID : ", end="")
        attendee_id = input().strip()
        
        try:
            cursor = mysql_connection.cursor(dictionary=True)
            check_query = "SELECT attendeeID FROM attendee WHERE attendeeID = %s"
            cursor.execute(check_query, (attendee_id,))
            
            if cursor.fetchone():
                print(f"*** ERROR *** Attendee ID: {attendee_id} already exists")
                cursor.close()
                continue
            
            cursor.close()
            break
        except MySQLError as err:
            print(f"*** ERROR *** {err}")
            continue
    
    # Get Name
    print("Name : ", end="")
    name = input().strip()
    
    # Get DOB
    print("DOB : ", end="")
    dob = input().strip()
    
    # Get Gender
    print("Gender : ", end="")
    gender = input().strip()
    
    if gender not in ["Male", "Female"]:
        print("*** ERROR *** Gender must be Male/Female")
        return
    
    # Get Company ID
    while True:
        print("Company ID : ", end="")
        company_id = input().strip()
        
        try:
            cursor = mysql_connection.cursor(dictionary=True)
            company_check = "SELECT companyID FROM company WHERE companyID = %s"
            cursor.execute(company_check, (company_id,))
            
            if not cursor.fetchone():
                print(f"*** ERROR *** Company ID: {company_id} does not exist")
                cursor.close()
                continue
            
            cursor.close()
            break
        except MySQLError as err:
            print(f"*** ERROR *** {err}")
            continue
    
    # Insert the attendee
    try:
        cursor = mysql_connection.cursor()
        insert_query = """
        INSERT INTO attendee (attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (attendee_id, name, dob, gender, company_id))
        mysql_connection.commit()
        cursor.close()
        print("Attendee successfully added")
    
    except MySQLError as err:
        print(f"*** ERROR *** {err}")


def option_4_view_connected_attendees():
    """Option 4: View Connected Attendees"""
    if not neo4j_available:
        print("*** ERROR *** Neo4j is not available. Start Neo4j to use this feature.")
        return
    
    print("Enter Attendee ID : ", end="")
    try:
        attendee_id = int(input().strip())
    except ValueError:
        print("*** ERROR *** Invalid attendee ID")
        return
    
    try:
        cursor = mysql_connection.cursor(dictionary=True)
        sqlite_check = "SELECT attendeeName FROM attendee WHERE attendeeID = %s"
        cursor.execute(sqlite_check, (attendee_id,))
        sqlite_result = cursor.fetchone()
        cursor.close()
        
        if not sqlite_result:
            print("*** ERROR *** Attendee does not exist")
            return
        
        attendee_name = sqlite_result['attendeeName']
        print(f"Attendee Name: {attendee_name}")
        print("-" * 21)
        
        # Query Neo4j for connected attendees (bidirectional)
        with neo4j_driver.session(database=config.NEO4J_DATABASE) as session:
            neo4j_query = """
            MATCH (a:Attendee {AttendeeID: $id})
            OPTIONAL MATCH (a)-[:CONNECTED_TO]-(connected:Attendee)
            RETURN COLLECT(DISTINCT connected.AttendeeID) as connected_ids
            """
            
            result = session.run(neo4j_query, {"id": attendee_id})
            record = result.single()
            
            if record and record['connected_ids']:
                connected_ids = record['connected_ids']
                print("These attendees are connected:")
                
                # Query MySQL to get the names
                placeholders = ','.join(['%s'] * len(connected_ids))
                name_query = f"SELECT attendeeID, attendeeName FROM attendee WHERE attendeeID IN ({placeholders}) ORDER BY attendeeID"
                
                cursor = mysql_connection.cursor(dictionary=True)
                cursor.execute(name_query, connected_ids)
                name_results = cursor.fetchall()
                cursor.close()
                
                for row in name_results:
                    print(f"{row['attendeeID']} | {row['attendeeName']}")
            else:
                print("No connections")
    
    except (MySQLError, Neo4jError) as err:
        print(f"*** ERROR *** {err}")


def option_5_add_attendee_connection():
    """Option 5: Add Attendee Connection"""
    if not neo4j_available:
        print("*** ERROR *** Neo4j is not available. Start Neo4j to use this feature.")
        return
    
    print("Enter Attendee 1 ID : ", end="")
    try:
        attendee_1_id = int(input().strip())
    except ValueError:
        print("*** ERROR *** Attendee IDs must be numbers")
        return
    
    print("Enter Attendee 2 ID : ", end="")
    try:
        attendee_2_id = int(input().strip())
    except ValueError:
        print("*** ERROR *** Attendee IDs must be numbers")
        return
    
    # Check if same attendee
    if attendee_1_id == attendee_2_id:
        print("*** ERROR *** An attendee cannot connect to him/herself")
        print("Enter Attendee 1 ID : ")
        return
    
    try:
        # Check if both attendees exist in MySQL
        cursor = mysql_connection.cursor(dictionary=True)
        check_query = "SELECT attendeeID FROM attendee WHERE attendeeID IN (%s, %s)"
        cursor.execute(check_query, (attendee_1_id, attendee_2_id))
        results = cursor.fetchall()
        cursor.close()
        
        if len(results) != 2:
            print("*** ERROR *** One or both attendee IDs do not exist")
            print("Enter Attendee 1 ID : ")
            return
        
        # Check if connection already exists in Neo4j (bidirectional check)
        with neo4j_driver.session(database=config.NEO4J_DATABASE) as session:
            check_connection = """
            MATCH (a:Attendee {AttendeeID: $id1})-[:CONNECTED_TO]-(b:Attendee {AttendeeID: $id2})
            RETURN COUNT(*) as count
            """
            
            result = session.run(check_connection, {"id1": attendee_1_id, "id2": attendee_2_id})
            record = result.single()
            
            if record and record['count'] > 0:
                print("*** ERROR *** These attendees are already connected")
                print("Enter Attendee 1 ID : ")
                return
            
            # Create bidirectional connection
            create_connection = """
            MERGE (a:Attendee {AttendeeID: $id1})
            MERGE (b:Attendee {AttendeeID: $id2})
            CREATE (a)-[:CONNECTED_TO]->(b)
            CREATE (b)-[:CONNECTED_TO]->(a)
            """
            
            session.run(create_connection, {"id1": attendee_1_id, "id2": attendee_2_id})
        
        print(f"Attendee {attendee_1_id} is now connected to Attendee {attendee_2_id}")
    
    except (MySQLError, Neo4jError) as err:
        print(f"*** ERROR *** {err}")
        print("Enter Attendee 1 ID : ")


def initialize_databases():
    """Initialize database connections"""
    global mysql_connection, neo4j_driver, neo4j_available
    
    print("Initializing database connections...")
    
    # Initialize MySQL
    try:
        mysql_connection = mysql.connector.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE
        )
        print("Connected to MySQL database: appdbproj")
    except MySQLError as err:
        print(f"Failed to connect to MySQL database: {err}")
        return False
    
    # Initialize Neo4j
    try:
        neo4j_driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )
        # Test connection with specific database
        with neo4j_driver.session(database=config.NEO4J_DATABASE) as session:
            session.run("RETURN 1")
        print("Connected to Neo4j database: appdbprojNeo4j")
        neo4j_available = True
    except Neo4jError as err:
        print(f"Warning: Neo4j not running or connection failed: {err}")
        print("Graph features (Options 4-5) will be unavailable.")
        neo4j_available = False
    
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
        if mysql_connection and mysql_connection.is_connected():
            mysql_connection.close()
            print("MySQL connection closed.")
        if neo4j_driver:
            neo4j_driver.close()
            print("Neo4j connection closed.")


if __name__ == "__main__":
    main()

