import sqlite3

conn = sqlite3.connect("astro_data.db")
c = conn.cursor()

# Table to store planetary positions (unique combination)
c.execute('''
CREATE TABLE IF NOT EXISTS planet_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_hash TEXT UNIQUE,
    ascendant TEXT,
    planets TEXT
)
''')

# Table to store users (with unique constraint to prevent duplicates)
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    birthdate TEXT,
    birthtime TEXT,
    state TEXT,
    city TEXT,
    planet_data_id INTEGER,
    FOREIGN KEY (planet_data_id) REFERENCES planet_positions(id),
    UNIQUE(name, birthdate, planet_data_id)
)
''')

conn.commit()
conn.close()
