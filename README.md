# SPARQList for TogoMedium
The API code of the SPARQList used by TogoMedium.

## Usage
To set up a local environment, first clone the sparqlist modules.
```
$ git clone https://github.com/dbcls/sparqlist.git
$ cd sparqlist

$ cat .gitignore
/cypress/screenshots/
/cypress/videos/
/node_modules/
/public/
/repository/  # add this line (recommend)

$ rm -rf repository # delete example code
```
Next, clone this repository as a `repository` directory
```
$ git clone https://github.com/dbcls/togomedium-sparqlist.git repository
```
Start the Docker container
```
$ docker run -v $(pwd)/repository:/app/repository --name growthmedium_sparqlist -p 3000:3000 -d ghcr.io/dbcls/sparqlist
```
You can access it in your browser at the following URL.
If you want to edit the API, refer to the `ADMIN_PASSWORD` listed in the `Docker` file in the `sparqlist` repository.
```
http://localhost:3000/sparqlist/
```