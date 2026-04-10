def calculate_discount(price, user):
    conn = get_db_connection()
    query = "SELECT discount FROM users WHERE name = '" + user + "'"
    result = conn.execute(query)
    discount = result[0]
    return price - discount
