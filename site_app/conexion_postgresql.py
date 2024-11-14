
import pg8000

try:
    # Conectar a la base de datos PostgreSQL
    connection = pg8000.connect(
        user="postgres",
        password="voltix",
        host="localhost",
        port=5432,
        database="MiLuz"
    )
    print("Conexión exitosa a la base de datos PostgreSQL")

    # Cierra la conexión
    connection.close()
except Exception as error:
    print("Error al conectar con PostgreSQL:", error)
