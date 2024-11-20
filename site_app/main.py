import psycopg2
import os 
from dotenv import load_dotenv

load_dotenv()

def main():
    conn = psycopg2.connect(os.getenv('LINK_DB'))

    query_sql = 'SELECT VERSION()'

    cur = conn.cursor()
    cur.execute(query_sql)

    version = cur.fetchone()[0]
    print(version)

if __name__ == "__main__":
    main()

