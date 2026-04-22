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


def get_all_users(id):
    lst = []

    conn = sqlite3.connect("VPN_bot.db")
    cur = conn.cursor()

    cur.execute(f"SELECT id, name, user_name FROM users WHERE id={id}")
    data = cur.fetchall()
    print(data)
    id = data[0][0]
    name = data[0][1]
    user_name = data[0][2]
    lst.append([id, name, user_name])
    return lst
