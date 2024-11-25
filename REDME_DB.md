Para hacer RESET DE DB:

Accedemos a la base de datos con psql terminal
Utilizamos el comando:
\dt
Este comando eliminará todas las tablas, índices y restricciones:
DROP SCHEMA public CASCADE;

CREATE SCHEMA public;
miramos otra vez que no tenemos nada
\dt
vamos a ver mensaje 
"
defaultdb=> \dt
Did not find any relations.
"
Entramos a nuestro proyecto, 
*si hay problemas en voltix.admin.py (como referencias a campos eliminados), comentamos temporalmente las configuraciones problemáticas.

*una opcion, eliminar todo excepto __init__.py dentro de la carpeta voltix.migraciones
*y llamamos estos dos comandos:

Generas las migraciones con:
python3 site_app/manage.py makemigrations

Aplicas las migraciones con:
python3 site_app/manage.py migrate

*Asegúrate de que las configuraciones en admin.py coincidan con los modelos actuales antes de ejecutar las migraciones.
----
Como crear un superusuario
Superuser Data

    DNI: <superuser DNI>
    Fullname: <name>
    Email: <email>
    Password: <password>
    
    1.python manage.py shell
2. enter script
# Import the custom User model
from voltix.models import User

# Create a superuser with the provided data
superuser = User.objects.create_superuser(
    dni="<superuser DNI>",
    fullname="<name>",
    email="<email>",
    password="<password>"
)

# Print confirmation
print(f"Superuser created: {superuser.fullname} ({superuser.email})")
3. exit from shell
exit()
 
