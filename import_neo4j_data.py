"""Import Neo4j data for attendee connections"""
from db_neo4j import Neo4jDatabase

def import_neo4j_data():
    """Import attendee nodes and connections into Neo4j"""
    
    # Initialize Neo4j database
    neo4j_db = Neo4jDatabase(
        uri="neo4j://localhost:7687",
        user="neo4j",
        password="password"
    )
    
    if not neo4j_db.connect():
        print("Failed to connect to Neo4j. Make sure Neo4j is running.")
        print("Run: .\\START-NEO4J.ps1 in another terminal first.")
        return False
    
    # Clear existing data
    clear_query = "MATCH (a:Attendee) DETACH DELETE a"
    try:
        neo4j_db.execute_write(clear_query, {})
    except:
        pass
    
    # Create ONLY the 18 attendee nodes from the support database
    # (Missing: 112, 119)
    attendee_ids = [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 113, 114, 115, 116, 117, 118, 120]
    
    create_nodes = """
    CREATE
    (:Attendee {AttendeeID: 101}),
    (:Attendee {AttendeeID: 102}),
    (:Attendee {AttendeeID: 103}),
    (:Attendee {AttendeeID: 104}),
    (:Attendee {AttendeeID: 105}),
    (:Attendee {AttendeeID: 106}),
    (:Attendee {AttendeeID: 107}),
    (:Attendee {AttendeeID: 108}),
    (:Attendee {AttendeeID: 109}),
    (:Attendee {AttendeeID: 110}),
    (:Attendee {AttendeeID: 111}),
    (:Attendee {AttendeeID: 113}),
    (:Attendee {AttendeeID: 114}),
    (:Attendee {AttendeeID: 115}),
    (:Attendee {AttendeeID: 116}),
    (:Attendee {AttendeeID: 117}),
    (:Attendee {AttendeeID: 118}),
    (:Attendee {AttendeeID: 120})
    """
    
    try:
        neo4j_db.execute_write(create_nodes, {})
        print(f"✓ Created {len(attendee_ids)} attendee nodes")
    except Exception as e:
        print(f"Error creating nodes: {e}")
        neo4j_db.disconnect()
        return False
    
    # Define directed connections EXACTLY as per support database
    # 12 directed relationships total
    connections = [
        (101, 109),  # Ava Murphy -> Ella Finn
        (101, 107),  # Ava Murphy -> Mia O'Brien
        (102, 110),  # Liam Byrne -> Cian Roche
        (103, 111),  # Noah Doyle -> Grace Power
        (104, 120),  # Emma Walsh -> Sean Dempsey
        (105, 113),  # Sophia Ryan -> Ruby Keane
        (106, 114),  # Jack Kelly -> Adam Hayes
        (107, 115),  # Mia O'Brien -> Chloe Hunt
        (108, 116),  # Charlie Nolan -> Ben Casey
        (111, 101),  # Grace Power -> Ava Murphy
        (106, 103),  # Jack Kelly -> Noah Doyle
        (120, 103),  # Sean Dempsey -> Noah Doyle
    ]
    
    # Create directed relationships (as per support database)
    success_count = 0
    for from_id, to_id in connections:
        create_connection = """
        MATCH (a:Attendee {AttendeeID: $from_id})
        MATCH (b:Attendee {AttendeeID: $to_id})
        CREATE (a)-[:CONNECTED_TO]->(b)
        """
        try:
            neo4j_db.execute_write(create_connection, {"from_id": from_id, "to_id": to_id})
            success_count += 1
        except Exception as e:
            print(f"Warning: Could not create connection {from_id}->{to_id}: {e}")
    
    print(f"✓ Created {success_count} CONNECTED_TO relationships")
    
    # Verify connections
    verify_query = """
    MATCH (a:Attendee)-[r:CONNECTED_TO]->(b:Attendee)
    RETURN COUNT(r) as connection_count
    """
    try:
        results = neo4j_db.execute_query(verify_query, {})
        if results:
            print(f"✓ Neo4j ready! Total connections: {results[0].get('connection_count', 0)}")
    except:
        pass
    
    neo4j_db.disconnect()
    return True


if __name__ == "__main__":
    print("Importing data into Neo4j graph database...\n")
    if import_neo4j_data():
        print("\n✓ Neo4j data import complete!")
    else:
        print("\n✗ Neo4j data import failed")
