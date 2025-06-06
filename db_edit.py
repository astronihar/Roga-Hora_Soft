import sqlite3

def update_user(user_id, name=None, birthdate=None, birthtime=None, state=None, city=None, planet_data_id=None):
    conn = sqlite3.connect("astro_data.db")
    c = conn.cursor()

    # Build the dynamic SQL update query
    updates = []
    values = []

    if name:
        updates.append("name = ?")
        values.append(name)
    if birthdate:
        updates.append("birthdate = ?")
        values.append(birthdate)
    if birthtime:
        updates.append("birthtime = ?")
        values.append(birthtime)
    if state:
        updates.append("state = ?")
        values.append(state)
    if city:
        updates.append("city = ?")
        values.append(city)
    if planet_data_id:
        updates.append("planet_data_id = ?")
        values.append(planet_data_id)

    if not updates:
        print("No fields to update.")
        return

    values.append(user_id)
    query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"

    c.execute(query, values)
    conn.commit()
    conn.close()
    print("User data updated successfully.")


def delete_user(user_id):
    conn = sqlite3.connect("astro_data.db")
    c = conn.cursor()

    # Check if the user exists
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()

    if not user:
        print(f"No user found with id = {user_id}")
    else:
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        print(f"User with id = {user_id} deleted successfully.")

    conn.close()





#Edits ----------------------------------- I can do all my edits here :) 

delete_user(15)
