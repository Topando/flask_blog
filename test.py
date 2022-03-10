import psycopg2
host="127.0.0.1"
user="postgres"
password="28012005"
db_name="db"

try:
    connect = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

    with connect.cursor() as cursor:
        cursor.execute("""
        SELECT version();""")
        print(cursor.fetchone())
except Exception:
    print("[eq")
finally:
    if connect:
        connect.close()
        print("GG")