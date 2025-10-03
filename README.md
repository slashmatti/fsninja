### CRUD App
Manage and look at plots of sensor data.

### Instructions
1. clone this repo
2. create a `.env` file in the root directory and put in values:
```
POSTGRES_DB=dev_database
POSTGRES_USER=dev_user
POSTGRES_PASSWORD=test
DB_HOST=db
DB_PORT=5432
```
3. `make up` to build and run docker containers
4. `make migrate` to run db migrations
5. `make seed` to create user `testuser@example.com // password123` with seeded sensor data
6. log into app at `http://localhost:3000`
7. run tests with `make test`
