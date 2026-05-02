# Conference Management Application

A Python application for managing conference attendees, speakers, sessions, rooms, and attendee connections using **MySQL** for relational data and **Neo4j** for graph-based relationships.

## Quick Start

### Requirements

- Python 3.7+
- MySQL 5.7+
- Neo4j 4.0+

### Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Update credentials in config.py:**
```python
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'your_password_here'  # Change this!
MYSQL_DATABASE = 'appdbproj'

NEO4J_URI = 'neo4j://localhost:7687'
NEO4J_USER = 'neo4j'
NEO4J_PASSWORD = 'your_password_here'  # Change this!
NEO4J_DATABASE = 'appdbprojNeo4j'
```

3. **Set up databases:**

**MySQL:**
```bash
mysql -u root -p < appdbproj.sql.txt
```

**Neo4j:**
- Start Neo4j: `http://localhost:7474`
- Create database: `CREATE DATABASE appdbprojNeo4j;`
- Import `appdbprojNeo4j.json`

4. **Run the application:**
```bash
python main.py
```

## Menu Options

1. **View Speakers & Sessions** - Search speakers by name, display their sessions
2. **View Attendees by Company** - View all attendees from a company
3. **Add New Attendee** - Register new attendee (ID, Name, DOB, Gender, Company ID)
4. **View Connected Attendees** - Show attendee connections (Neo4j)
5. **Add Attendee Connection** - Create connection between two attendees
6. **View Rooms** - Display all rooms and capacity
7. **Exit (x)** - Exit application

## Implementation Requirements

### Option 1: View Speakers & Sessions
- **Input:** Speaker name (partial match)
- **Output:** Speaker name | Session title | Room name
- **Error:** "No speakers found of that name"

### Option 2: View Attendees by Company
- **Input:** Company ID (numeric, > 0)
- **Output:** Name | DOB | Session | Speaker | Room
- **Validation:** Re-prompt if invalid; error if company doesn't exist

### Option 3: Add New Attendee
- **Input:** Attendee ID, Name, DOB (YYYY-MM-DD), Gender (Male/Female), Company ID
- **Validation:** Unique ID, valid gender, existing company
- **Success:** "Attendee successfully added"
- **Errors:**
  - Duplicate ID: "*** ERROR *** Attendee ID: {id} already exists"
  - Invalid gender: "*** ERROR *** Gender must be Male/Female"
  - Non-existent company: "*** ERROR *** Company ID: {id} does not exist"

### Option 4: View Connected Attendees
- **Input:** Attendee ID (numeric)
- **Cases:**
  - In both DBs: Show name and connected attendees
  - Only in MySQL: Show name with "No connections"
  - Not in any DB: "*** ERROR *** Attendee does not exist"

### Option 5: Add Attendee Connection
- **Input:** Two Attendee IDs
- **Validation:** Both numeric, both exist, not same ID, not already connected
- **Success:** "Attendee {id1} is now connected to Attendee {id2}"
- **Errors:**
  - Self-connection: "*** ERROR *** An attendee cannot connect to him/herself"
  - Already connected: "*** ERROR *** These attendees are already connected"
  - Non-numeric: "*** ERROR *** Attendee IDs must be numbers"
  - Non-existent: "*** ERROR *** One or both attendee IDs do not exist"

### Option 6: View Rooms
- **Output:** RoomID | RoomName | Capacity
- **Note:** Data is cached after first access

## Database Structure

**MySQL Tables:**
- `attendee` - Attendee records
- `speaker` - Speaker information
- `session` - Sessions with speaker and room
- `room` - Conference rooms
- `company` - Companies
- `registration` - Attendee-Session junction

**Neo4j:**
- Nodes: `Attendee` with `attendeeID` property
- Relationships: `CONNECTED_TO` (bidirectional)

## Troubleshooting

**MySQL issues:**
- Check running: `mysql -u root -p`
- Verify database: `mysql -u root -p -e "SHOW DATABASES;"`

**Neo4j issues:**
- Check running: `http://localhost:7474`
- Verify database exists: `appdbprojNeo4j`

**Application issues:**
- Room cache: Restart app to reload
- No data: Verify imports completed
- Hangs: Ensure both databases running

## Notes

- Room data is cached on first access
- Neo4j connections are bidirectional
- All dates: YYYY-MM-DD format
- Use `localhost` for database connections
