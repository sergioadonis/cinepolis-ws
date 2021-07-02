# cinepolis-ws
Plataforma de extracción de datos de Cinepolis.

## Funciones principales
Entre sus funciones podemos destacar:
- Programar tareas para la extracción de la cartelera de películas de los cines de Cinepolis, así como de los horarios de todas las funciones encontradas. 
- Extraer el número de asientos disponibles, ocupados y deshabilitados en cada función minutos antes que inicie el show.
- Configurar los cines por país y ciudades.
- Explorar los datos en tablas y pivots con SQL. También, permite exportar a los formatos más comunes como Excel, Csv o Json.

## Servicios y componentes
La plataforma está compuesta por una serie de servicios:
- Un _website_ desarrollado con Python y Django, cuya función es ser la interfaz administrativa para configurar y programar las tareas de extracción, explorar los datos obtenidos, administrar usuarios.
- Un _worker_ desarrollado con Python y Celery, cuya función es ejecutar las tareas programadas para la extracción de datos.
- Una _database_ para la persistencia de las tareas y los resultados, para el caso se usar una base de datos Postgres.
- Una _broker_ para la comunicación entre los servicios _website_ y _worker_, para el caso se usa una base de datos Redis.
- Un _webserver_ para exponer el _website_, para el caso Nginx funciona en modo _reverse proxy_.


## Puesta en marcha
Para ejecutar la aplicación y todos los servicios es necesario tener instalado Docker y Docker Compose.

Crear un archivo de configuración con el nombre _.env_ para las variables de entorno con el siguiente contenido:
```txt
# Used on docker-compose.yml in development env
SECRET_KEY=<TU LLAVE SECRETA>
POSTGRES_DB=<NOMBRE DE TU BASE DE DATOS>
POSTGRES_HOST_AUTH_METHOD=trust
DATABASE_URL=postgres://postgres@database:5432/<NOMBRE DE TU BASE DE DATOS>
REDIS_URL=redis://broker:6379/
DEBUG=0
CELERY_APP=cinepolis
RETRY_TIMES=10

# Cinepolis credentials
CINEPOLIS_GRANT_TYPE=client_credentials
CINEPOLIS_CLIENT_ID=<CLIENT_ID DE CINEPOLIS>
CINEPOLIS_CLIENT_SECRET=<CLIENT_SECRET DE CINEPOLIS>
CINEPOLIS_SCOPE=USER
```

Generar la imagen basada en el Dockerfile
```bash
docker build . -t cinepolis-ws
```

Ejecutar los servicios con docker-compose
```bash
docker-compose up -d
```

Verificar servicios
```bash
docker-compose ps
```
La salida puede ser similar a la seiguiente:
```
         Name                        Command               State          Ports       
--------------------------------------------------------------------------------------
cinepolis-ws_broker_1     docker-entrypoint.sh redis ...   Up       6379/tcp          
cinepolis-ws_database_1   docker-entrypoint.sh postgres    Up       5432/tcp          
cinepolis-ws_web_1        /docker-entrypoint.sh ngin ...   Up       0.0.0.0:80->80/tcp
cinepolis-ws_website_1    bash -c python manage.py m ...   Exit 1                     
cinepolis-ws_worker_1     celery --app config worker ...   Up                         
```
En esta salida el servicio _website_ se terminó con error. Para inspeccionar puede revisar el log:
```bash
docker-compose logs -f website
```
Si la salida es como la siguiente, se debe a que el servicio _website_ se inició antes que el servicio _database_:
```bash
website_1   | django.db.utils.OperationalError: could not connect to server: Connection refused
website_1   |   Is the server running on host "database" (172.19.0.4) and accepting
website_1   |   TCP/IP connections on port 5432?
website_1   | 
```
El servicio _database_ puede tardarse un por la primera vez, pero una vez que esté listo, puede repetir el proceso y debe conseguir todo con exito:
```bash
docker-compose up -d && docker-compose ps
```

Si todo es _Up_ significa que los servicios están funcionando correctamente, por ejemplo:
```bash
         Name                        Command               State         Ports       
-------------------------------------------------------------------------------------
cinepolis-ws_broker_1     docker-entrypoint.sh redis ...   Up      6379/tcp          
cinepolis-ws_database_1   docker-entrypoint.sh postgres    Up      5432/tcp          
cinepolis-ws_web_1        /docker-entrypoint.sh ngin ...   Up      0.0.0.0:80->80/tcp
cinepolis-ws_website_1    bash -c python manage.py m ...   Up      8000/tcp          
cinepolis-ws_worker_1     celery --app config worker ...   Up
```

## Configuración inicial
Crear un usuario administrador
```bash
docker-compose exec website ./manage.py createsuperuser
```

Completar los datos solicitados:
```bash
Username (leave blank to use 'root'): root
Email address: 
Password: 
Password (again): 
Superuser created successfully.
```

Abrir un navegador web, y explorar el _website_ localmente http://localhost/admin

Si todo salió bien, debería ver el formulario para iniciar sesión con el usuario recién creado.

Listo!


## ToDos
- que los campos sean solo lectura si el status es diferente a To Do
- agregar created_by y updated_by 
- refactorizar para usar services y no el codigo directamente en tasks
- guardar el task_id para cancelar en caso se modifique la fecha de ejecucion, o se elimine la tarea programada
- investigar sobre reintentos cuando haya error
- celery monitor
- usuario readonly para django-sql-explorer
- investigar el numero de workers ideal
- agregar soporte para https con LetsEncrypt
