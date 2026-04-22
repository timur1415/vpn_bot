import sqlite3


def create_table():
    conn = sqlite3.connect("VPN_bot.db")
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    user_name TEXT    
    )""")

    conn.commit()
    conn.close()


def create_user(id, name, user_name):
    conn = sqlite3.connect("VPN_bot.db")
    cur = conn.cursor()

    cur.execute(f"SELECT id FROM users WHERE id={id}")
    user_data = cur.fetchone()
    if user_data is None:
        cur.execute(f"INSERT INTO users VALUES({id}, '{name}', '{user_name}')")
        conn.commit()
    conn.close()


def get_all_users():
    lst = []

    conn = sqlite3.connect("VPN_bot.db")
    cur = conn.cursor()

    cur.execute("SELECT id, name, user_name FROM users")
    data = cur.fetchall()
    for user in data:
        print(user)
        id = user[0]
        name = user[1]
        user_name = user[2]
        lst.append([id, name, user_name])
    conn.close()
    return lst
