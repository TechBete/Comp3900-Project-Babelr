<h2><u> Babelr Software Development Documentation. </u></h2>

<h3><u> Babelr Setup </u></h3>

To correctly implement the software framework in docker the software user  will need use two terminals (Frontend/Backend). To make operation easier, shell scripts have been created for the user.

> ```dockerRebuild.sh```

This script will remove all volumes, containers, networks and saved data inside docker. The shell script will also create the overall framework. Use on initial boot up or if the user needs to reinitalize Babelr and its database.

> ```dockerBoot.sh```

This script will reboot docker. While this script does not remove any of the docker containers or volumes and should be used if the user has stopped Babelr and wants to restart it with data persistence.

> ```bootup.sh```

This script is found in the backend and is used to boot up the server.

<h5><u> Usage: </u></h5>

In order to initalize the software, the user will need two terminals.

* In the first terminal, run the ```dockerRebuild.sh``` script in the root directory to build the software framework.
* In the second terminal, navigate to the backend and run 
```bootup.sh``` to initalize the backend server for the software.

Once the software has completed building and is up and running, users can being interacting with the software through a web browser using the following route: 
```localhost:3000``` 

<u><h3> Currently in Development: </h3></u> 

#### FRONTEND - Completed Routes

once the server is up and running you should be able to connect to the frontend through a web browser by inserting the following addresses: 

```localhost:3000                       (takes user to login page)```
```localhost:3000/register_listener     (register user page)```
```localhost:3000/register_researcher   (register researcher page)```

#### BACKEND - Completed Routes

Backend routes can be connected to directly by navigating to:

```localhost:8016/registerListener      (registers a listener)```
```localhost:8016/registerResearcher    (registers a researcher)```
```localhost:8016/getListeners          (display Listeners in the database)```
```localhost:8016/getResearchers        (display Researchers in the database)```
```localhost:8016/resetPassword         (reset User Password)```
```localhost:8016/createProject         (creates a project for a Researcher)```

####  Connected Routes:

Register Researcher
Register Listener