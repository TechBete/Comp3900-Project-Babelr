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

#### FRONTEND - Implemented Routes

once the server is up and running you should be able to connect to the frontend through a web browser by inserting the following addresses: 

```localhost:3000                       (takes user to login page)```
```localhost:3000/register_listener     (register user page)```
```localhost:3000/register_researcher   (register researcher page)```

#### BACKEND - Implemented Routes

Backend routes can be directly navigating to by using the following synta:

localhost:8016/(route)

* User login: ```/login``` 

* Register Listener User: ```/registerListener```
   
* Register Researcher User : ```/registerResearcher```   

* Reset User Password: ```/userResetPassword```

* Forgot Password (email): ```/blindEmailParse```  

* Forgot Password (reset Password): ```/blindPasswordReset```   

* Get all Listeners: ```/getListeners```

* Get all Researchers: ```/getResearchers```  

* Create a Project: ```/createProject```

* Update a Project Name: ```/updateProjectName```

* Add Tags to a Project: ```/addProjectTags```

* Remove Tags from a Project: ```/removeProjectTags```

* Update Project Status: ```/updateProjectStatus```

* Get all Projects for a Researcher: ```/getProjects```

* Get a specific Project for a Researcher: ```/getProject```

* Delete a Project: ```/deleteProject```

* Set Metrics for a Project: ```/setProjectMetricField```

* Get Metrics for a Project: ```/getProjectMetrics```

* Update Metrics for a Project: ```/updateProjectMetrics```

* Delete Metrics for a Project: ```/deleteProjectMetrics```

* Search Project by Tag: ```/searchProjectByTag```

####  Connected Routes:

User Login
Register Researcher
Register Listener
Create Project