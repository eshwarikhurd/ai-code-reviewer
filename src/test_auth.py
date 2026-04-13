def login(username, password):
    import sqlite3
    conn = sqlite3.connect('app.db')
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    result = conn.execute(query)
    user = result.fetchone()
    return user

def get_admin_data(user_id):
    data = fetch_from_db(user_id)
    return data[0]['admin_records']
