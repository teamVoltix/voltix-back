# Run the server

### 1. Crear un entorno virtual

Primero, crea y activa un entorno virtual para gestionar las dependencias del proyecto de manera aislada.

```bash
# Crear el entorno virtual
python3 -m venv venv

# Activar el entorno virtual
# En macOS/Linux
source venv/bin/activate
# En Windows
venv\Scripts\activate


    pip install -r requirements.txt
    sudo apt-get update

    # Si no esta instalado 
    sudo apt-get install -y postgresql postgresql-contrib

    psql --version
    sudo service postgresql start
    sudo service postgresql status

    #Ruta de nuestra base de datos
    psql 'postgres://avnadmin:AVNS_KMlR6yxJcuqiTSYfkny@miluz-i004-voltix-back.e.aivencloud.com:22219/defaultdb?sslmode=require'
    \l
    \dt
    
    python3 site_app/manage.py runserver


    #para renovar requirements
    pip freeze > requirements.txt



#Para levantar servidor
    python3 site_app/manage.py runserver

#acuedase del punto .ENV