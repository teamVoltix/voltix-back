# Documentación del Proyecto

Este documento proporciona una guía paso a paso para configurar el entorno del proyecto, gestionar dependencias, ejecutar el servidor y solucionar problemas comunes.

<aside>
👋 ❤️

</aside>

## Equipo:

---

[Naty](https://github.com/NataliaIacono)

[Dario](https://github.com/darioduarte1)

[Denis](https://github.com/denis9diaz)

[Edu](https://github.com/EIAHRJAY)

[Matias](https://github.com/kamelmat)

[Ariel](https://github.com/ariellpcuba)

[Angie](https://github.com/ILMPI)

## Recursos Adicionales

---

- [Documentación de Django](https://docs.djangoproject.com/en/5.1/intro/tutorial01/)
- [Comandos de PostgreSQL](https://www.postgresql.org/docs/current/app-psql.html)
- [Documenatción de Docker](https://docs.docker.com/)
- [Documentacion de Tesseract](https://tesseract-ocr.github.io/)

### Configuración del Entorno

### Entorno Virtual

1. Crear y activar un entorno virtual:

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

1. Instalar PostgreSQL (# macOS/Linux):

```bash
sudo apt-get install -y postgresql postgresql-contrib
psql --version

```

- para Windows instalar pgAdmin

1. Iniciar y verificar PostgreSQL:

```bash
sudo service postgresql start
sudo service postgresql status

```

**Nota:** Asegúrate de que el archivo `.env` esté configurado con las credenciales necesarias para la base de datos y otras claves importantes.

### Gestión de la Base de Datos

1. Conexión a PostgreSQL

Conectar utilizando el terminal (macOS/Linux):

```bash
psql 'postgres://avnadmin:<PASSWORD>@<host>:<port>/defaultdb?sslmode=require'
```

| Comando    | Descripción                         |
|------------|-------------------------------------|
| `\l`       | Lista todas las bases de datos      |
| `\dt`      | Lista todas las tablas             |
| `\d <tabla>` | Muestra los detalles de una tabla |


### Ejecución del Servidor de Desarrollo

1. Iniciar el servidor:

```bash
python3 site_app/manage.py runserver 
python site_app/manage.py runserver # Windows
```

1. Actualizar requirements.txt:

```bash
pip freeze > requirements.txt
```

1. Instalar librerías adicionales (ejemplo):

```bash
pip install pymupdf opencv-python-headless
```

### Configuración con Docker

Se recomienda previamente hacer una copia del archivo **sampleEnviroment** a un `.env`  con los datos necesarios:

1. Crear la imagen Docker:

```bash
docker-compose -f docker-compose.dev.yml build
```

1. Desplegar el servicio:

```bash
docker-compose -f docker-compose.dev.yml up -d
```

1. Cargar los archivos estáticos:

```jsx
docker-compose -f docker-compose.dev.yml exec -it voltix-back python3 collectstati4c
```

1. Ejecutar migraciones de la base de datos:

```bash
docker-compose -f docker-compose.dev.yml exec -it voltix-back python3 manage.py makemigrations
docker-compose -f docker-compose.dev.yml exec -it voltix-back python3 manage.py migrate
```

1. Crear superusuario:

```jsx
docker-compose -f docker-compose.dev.yml exec -it voltix-back python3 manage.py createsuperuser
```

### Generación de PDFs

### Endpoint de la API

- **URL:** `/api/measurements/report/download/`
- **Ejemplo:** `https://example.com/api/measurements/report/download/?id=1`

### Generación de Mediciones

Ejecutar el script:

```bash
python site_app/measurements/scripts/load_measurements.py
```

### P.D.
[Notion](https://luxuriant-muscari-35c.notion.site/Documentaci-n-del-Proyecto-157991095be380228f5ac4cb7e0c660d)