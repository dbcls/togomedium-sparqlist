# TogoMedium SPARQList
## Prerequisites
* Docker
* Docker Compose

## Download source code
Download source code from this repository
```
$ cd /your/path/src/
$ git https://github.com/dbcls/togomedium-sparqlist.git
$ cd togomedium-sparqlist
```

## Configuration environment
Create `.env` file and set values for your environment.
```
$ cp template.env .env
```
### `CONTAINER_NAME`
(default: `togomedium_sparqlist`)

The name of the docker container. Must be unique in the system.

### `REPOSITORY_PATH`

(default: `./repository`)

Path to SPARQLet repository.

### `PORT`
(default: `3000`)

Port to listen on. Must be unique in the system.

### `ADMIN_PASSWORD`
(default: sercret)

Admin password.

### `SPARQLIST_TOGOMEDIUM_ENDPOINT`
(default: xxxxx)

URL of TogoMedium SPARQL endpoint.


## Start server
```
$ docker compose up -d
### Check of startup status
$ docker compose ps
NAME              IMAGE                     COMMAND                   SERVICE     CREATED         STATUS         PORTS
togomedium_sparqlist   ghcr.io/dbcls/sparqlist   "docker-entrypoint.s…"   sparqlist   4 minutes ago   Up 4 minutes   0.0.0.0:3000->3000/tcp
```
If you are using a version prior to Docker Compose v2.0.0, use the `docker-compose` command instead of `docker compose`
```
$ docker-compose up -d
```

Check the SPARQList page can be displayed from a browser on the port number specified in the `.env` file. e.g. `http://localhost:3000`


## Test API
The number of items retrieved by executing each API is output to the test directory.
### Development environment
```
python3 test/api_test.py http://localhost:3000
```

### Production environment
```
python3 test/api_test.py https://togomedium.org
```