# Run the server

    pip install -r requirements.txt
    sudo apt-get update

    # Si no esta instalado 
    sudo apt-get install -y postgresql postgresql-contrib

    psql --version
    sudo service postgresql start
    sudo service postgresql status

    psql 'postgres://avnadmin:AVNS_KMlR6yxJcuqiTSYfkny@miluz-i004-voltix-back.e.aivencloud.com:22219/defaultdb?sslmode=require'
    \l
    \dt
    
    python3 site_app/manage.py runserver


    #para renovar requirements
    pip freeze > requirements.txt



#Para levantar servidor
    python3 site_app/manage.py runserver
