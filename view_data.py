import sqlite3
import json

conn = sqlite3.connect("astro_data.db")
c = conn.cursor()

# View users
print("Users:")
for row in c.execute("SELECT * FROM users"):
    print(row)

# View planet data
print("\nPlanet Positions:")
for row in c.execute("SELECT * FROM planet_positions"):
    print(f"ID: {row[0]}")
    print(f"Hash: {row[1]}")
    print("Ascendant:", json.loads(row[2]))
    print("Planets:", json.loads(row[3]))
    print("-" * 30)

conn.close()
