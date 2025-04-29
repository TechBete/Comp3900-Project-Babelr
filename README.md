<h2><u> Babelr ReadMe. </u></h2>

<h3><u> Introduction </u></h3> 

Our team, 3900-W16B-APPLE, was assigned to complete Project 24, an Online Audio Quality Rating System platform. The project's concept was to address a niche in the online evaluation environment that deals wholly with evaluating audio-related research due to the current limitations of available audio evaluation platforms. This would allow researchers who are working with AI text-to-speech models to connect with a wide range of research participants who would be able to evaluate and provide feedback on the audio clips based on a series of researcher-defined metrics.

<h3><u> Babelr Setup </u></h3>

To correctly implement the software framework in docker for the platform the software user will first need to open a terminal ( *assumption here is that installation will occur through a terminal* ) at the root level (where the ```docker-compose.yml``` file is present). To improve user experience, shell scripts have been created for the user's convenience.

<h4><u> Docker Shell Scripts </u></h4>

>```./dockerInstall.sh```

This shell script should be run on the first installation of the platform. It will install and build all the necessary containers, networks, packages, and volumes for the platform. A prompt will also present it self for validation for running the script.This script comprises of the following docker command ```docker-compose up --build```

> ```./dockerRebuild.sh```

This script will remove all volumes, containers, networks and saved data inside docker. The shell script will also create the overall framework. A prompt will also present it self for validation. This script comprises of the following docker commands ```docker-compose down -v and docker-compose up --build```

> ```./dockerBoot.sh```

This script should be used to reboot the platform in docker. This script does not remove any of the docker containers, netowrks or volumes. it should be used if the user has stopped Babelr and wants to restart it with data persistence. Additionally, this script will run docker in the backgroud. This script comprises of the following docker command ```docker-compose up -d```

>```./dockerUninstall.sh```

This script should be used if the user ever wants uninstall the Babelr platform as it will disassociate all containers, networks, packages and volumes from the platform. A prompt will also present it self for validation. This script will run the following docker command ```docker-compose down -v```

<h5><u> Babelr Installation: </u></h5>

If this is the first time the user is installing the platform, the user should run the ```./dockerInstall.sh``` script in the root directory to build the software framework.

Once the software has completed building and is up and running, users can being interacting with the software through a web browser using the following route on a web browser: ```localhost:3000``` 

<h3><u> Tutorial: </u></h3>

<h5><u> How to use the Babelr Platform: </u></h5>

The babelr platform consists of two user routes. 

<h5><u> Users: </u></h5>

The first user is the Researcher. These users will create projects, and upload to the platform their AI Text To Speech Audio clips for the general users to review. They should be able to create metrics for their projects, view analytics and download a copy of the statistical analytics.

The next user is the Listener (general population). These users will register with the platform, provide their profile data, language and language proficiencies and will be able to evaluate the audio clips associated with a project that a Researchers has created. The evaluation will be based on the metrics for the project in which the audio clip has been uploaded to. The user is then rewarded points in which they can redeem for rewards at the rewards shop.

<h5><u> Sample Tutorial of how the Platform Operates: </u></h5>

- First register a researcher
    - Go to login page, select researcher
    - Register as a researcher
	- Click the link in the verification email
	- Login with registered details
	- Input initial details
	- Create project
	- Open new project
 	- Upload a few audio clips with languages and proficiency set as you like
	- Logout
- Next, register a listener
    - Go to login page, select listener
    - Register as a listener
	- Click the link in the verification email
	- Login with listener details
	- Input demographics
	- <b> (Important) Set your languages and proficiency based on what clips you added before and which clips you'd like to listen to. </b>
	- Press start review button
	- You should be able to listen to the clip and change the inputs on the sliders
	- When you press submit you should be able to immediately play a different clip if you added more than one clip that was suitable for the previously added languages and proficiencies
	- After finishing all the submissions logout
- Finally, as the reseacher 
	- Login as the previous researcher once again
	- Open the project
	- the user should be able to notice how the evaluated and allocated user fields have been updated
	- The researcher can go to the analytics page to see the changes based on the submitted reviews.

<h3><u> Frontend Testing: </u></h3>

To run the frontend mock tests using jest. On a terminal go to the ```frontend/babler/``` folder and run ```npm install``` after a successfull install you can just run npm run test in the same directory and it'll run all the test suites.

To view tests go to ```frontend/babler/__tests__/```

<h3><u> Backend Documentation: </u></h3>

[This is an external link to where you can find the Backend Documentation](https://drive.google.com/file/d/1pS_ikL1DHQ_saxvLKmergcRi-vGCfBme/view?usp=sharing)

The backend documentation also contains the ```.env file contents``` for the implementation of the platform. the ```.env file``` will need to be created at the root level of the platform ```(where the .envc and docker-compose.yml files are)```.

(remove above block of text about the .env file once course has concluded)