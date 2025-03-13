# To Be Updated With Documentation for Software Operation.

## Database Setup
in order to implement the database framework and the server framework that connects to it in docker
you will need two terminals. 
* In the first terminal, run docker compose up in the root directory.
* In the second terminal, navigate to the backend server and run 
```docker-compose up --build```
once the server is up and running you should be able to connect to the backend on through a web browser by inserting the following address: 
```localhost:8016``` 
##### currently for development purposes: 
you can connect to the backend routes by navigating directly
```localhost:8016/  (Home/add user test)```
```localhost:8016/getusers    (display users in the database)```
