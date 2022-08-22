# EM-Glue
EM-Glue is a software architecture and platform that decouples EMs from environments while facilitating communication between them. 
The platform enables the exchange of messages in a standardized way so that different EMs and environments can work together using a common architecture.

## Compatible Environments
Camelot with the use of [Camelot-Wrapper](https://github.com/liogiu2/Camelot-Wrapper)

## Project Status
The project is actively under developement. Once all the major components will be ready there will be a release. 

## Documentation
The documentation is under construction. 

## Installation
There are 5 main pieces of software that we need to create a succesfull experience. 
First, [Camelot](http://cs.uky.edu/~sgware/projects/camelot/v1-2/) that is a publicly available software and not part of the software developed for the paper. 
Second, [EV_PDDL](https://github.com/liogiu2/EV_PDDL/tree/camelot_dev), library that uses PDDL as representation of the state. 
Third, [Camelot-Wrapper](https://github.com/liogiu2/Camelot-Wrapper). This contains the python scripts used by Camelot to communicate with the Platform.
Fourth, EM-Glue, that is the platform that is created to manage the communication between experience manager and environment.
Fifth, Experiece Manager, a dummy experience manager that implements the communication protocol and the normal communication. It allows to receive messages from the environment, and send actions to the environments that the environment executes. To do so, we created a wizard to build a successful action before sending it to the environment.

For everything to work properly, we require to use Windows.
Installation instructions:
1) Install [python 3.8.10](https://www.python.org/downloads/release/python-3810/) (please select the "add to PATH" option)
2) Download and unzip [Camelot](http://cs.uky.edu/~sgware/projects/camelot/v1-2/)
3) (To be edited) Move the folder called "Platform" with all the files we provided into the Camelot folder (where the Camelot.exe is located). Please be sure that inside the "Platform" folder there are other 4 folders ("camelot_Wrapper", "EM-Glue", "EV_PDDL", "experience_manager") and one txt file ("requirement.txt"). The program works with relative paths and it is important to have the correct path. 
4) Open Camelot folder and edit the ```StartExperienceManager.bat``` file by deliting its content and writing:
   ```
   python Platform\camelot_wrapper\camelot_wrapper\camelot_wrapper.py
   ```
   Then, Save and close the file.
5) Open a Command Prompt, and navigate inside the Platform folder (that should be located inside the Camelot folder if instruction #3 was followed). Run the following command ```pip install -r requirements.txt```. This should install all the python dependencies that the program we wrote needs to work correctly.

How to run an experience using the platform.
1) Open a Command Prompt, and navigate inside the Camelot folder.
2) Write and execute the following instructions:
   ```
	cd Platform\EM-Glue\EM-Glue
	python EM_Glue_start.py
	```

As soon as the program starts executing it starts the APIs and the experience manager.
A new command prompt will open that contains the experience manager process.  
In the two terminals you can see that the experience manager and the platform executes the first phase of the communication protocol.
After the first phase, the environment will be started and a Unity game environment will start. 
In the two terminals, you can see that the communication protocol phases continues until everything is set-up correctly. 
At this point the normal communication starts, and if you move the character in the camelot environment, you will see that the worldstate updates and the experience managers receives these updates. 
The experience manager offers the ability to create an action that can be executed in Camelot. To do so, in the terminal with the experience manager process, press any key and press enter.
This will open a wizard for the creation of a new action to send to Camelot.
As an example we will build an action that moves the NPC from one room to the other.
You will see all the available actions to build and you can press 0 to select move-between-rooms.
Now, you will start building the action with all the parameters needed.
The first one will be "?who (character)" and you can press 1 to select the NPC.
Then "?from (location)", press 1 to select the location of the NPC.
Then, "?to (location)", press 0 to select the room that the NPC has to enter.
Then, "?entryfrom (entrypoint)", press 1 to select the entry point from the room that the NPC is currently in.
Then, "?entryto (entrypoint)", press 0 to select the entry point of the current room.
Now the wizard will check if the action can be sent, and if it can, it will be sent to the environemt for execution.
On the environment, you will see that the main door will open and a character will enter the room.

## Usage
Please contact [Giulio Mori](https://github.com/liogiu2) for any questions about how is it used.
If you use this software and you're writing a research paper, please cite our research paper where we showcase this software using the Github function for citation. 

## Contributing
Pull requests are welcome, but please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)

