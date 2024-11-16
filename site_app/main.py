import psycopg2

def main():
    conn = psycopg2.connect('postgres://avnadmin:AVNS_KMlR6yxJcuqiTSYfkny@miluz-i004-voltix-back.e.aivencloud.com:22219/defaultdb?sslmode=require')

    query_sql = 'SELECT VERSION()'

    cur = conn.cursor()
    cur.execute(query_sql)

    version = cur.fetchone()[0]
    print(version)

if __name__ == "__main__":
    main()

