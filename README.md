# EM-Glue
EM-Glue is a software architecture and platform that decouples EMs from environments while facilitating communication between them. 
The platform enables the exchange of messages in a standardized way so that different EMs and environments can work together using a common architecture.

# New release is about to come out. This page is under manteinance.
![work in progress](https://icambrogiolorenzetti.edu.it/wp-content/uploads/sites/91/Work-in-progress-1024x603-1.png?x67262)

## Compatible Environments
Camelot with the use of [Camelot-Wrapper](https://github.com/liogiu2/Camelot-Wrapper)

## Project Status
The project is actively under developement. Once all the major components will be ready there will be a release. 

## AIIDE 2022 build
[Here](https://drive.google.com/drive/folders/1NeWnOh8ikErnFRSn8KiRclOmUaI1r-2u?usp=sharing) you can find the build submitted with the AIIDE 2022 Paper. You can download it and follow the instructions in the README file to have it working.

## Documentation
The documentation is under construction. 

### Communication Protocol
![Alt text](graphics/communication_protocol.png?raw=true)

## Installation
There are 5 main pieces of software that we need to create a succesfull experience. 
First, [Camelot](http://cs.uky.edu/~sgware/projects/camelot/v1-2/) that is a publicly available software and not part of the software developed for the paper. 
Second, [EV_PDDL](https://github.com/liogiu2/EV_PDDL/tree/camelot_dev), library that uses PDDL as representation of the state. 
Third, [Camelot-Wrapper](https://github.com/liogiu2/Camelot-Wrapper). This contains the python scripts used by Camelot to communicate with the Platform.
Fourth, EM-Glue, that is the platform that is created to manage the communication between experience manager and environment.
Fifth, [PaSSAGE for EM-Glue](https://github.com/liogiu2/PaSSAGE-for-EMGlue), an implementation of PaSSAGE experience manager. It allows to set-up the communication with EM-Glue, receive messages from the environment, and send the execution of encouters once the preconditions are satisfied. It host a player model that is based on five values and it is retrieved from the environment messages. 

For everything to work properly, I require to use Windows.
Installation instructions:
1) Install [python 3.9.1](https://www.python.org/downloads/release/python-391/) (please select the "add to PATH" option)
2) Download and unzip [Camelot](http://cs.uky.edu/~sgware/projects/camelot/v1-2/)
3) (To be edited) Move the folder called "Platform" with all the files we provided into the Camelot folder (where the Camelot.exe is located). Please be sure that inside the "Platform" folder there are other 4 folders ("camelot_Wrapper", "EM-Glue", "EV_PDDL", "PaSSAGE-for-EMGlue") and one txt file ("requirement.txt"). The program works with relative paths and it is important to have the correct path. 
4) Open Camelot folder and edit the ```StartExperienceManager.bat``` file by deliting its content and writing:
   ```
   python Platform\camelot_wrapper\camelot_wrapper\camelot_wrapper.py
   ```
   Then, Save and close the file.
5) Open a Command Prompt, and navigate inside the Platform folder (that should be located inside the Camelot folder if instruction #3 was followed). Run the following command ```pip install -r requirements.txt```. This should install all the python dependencies that the program we wrote needs to work correctly.
6) Install the latest version of the [YarnSpinner-Console](https://github.com/YarnSpinnerTool/YarnSpinner-Console) program ```ysc```. This will be used by the conversation manager in the Camelot Wrapper to compile the ```.yarn``` files containing the conversation files. On Windows, once you downloaded the ysc program into your PC, make sure that the ```ysc.exe``` is in the path variable and accessible by the terminal. 

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
To test PaSSAGE, move the character from the initial room to the second room by clicking on the door.
You will see that the main character will change room. 
Once in the new room, as soon you start moving, the experience manager will send to the environment the start_scene command. 
At this point, you will lose the input ability and a scene will start. 
Your character will start a conversation with the NPC. While this conversation is happening, the experience manager will receive details of your player model. 
Once the conversation ended, you will gain back the controls and you can move in the next location (a city). 
Once in the next location, there are two possible encounters that can happen based on the player model learned by PaSSAGE in the previous conversation.
PaSSAGE will choose the best encouter based on the preferences listed in the encouter and the learned player model.

## Usage
Please contact [Giulio Mori](https://github.com/liogiu2) for any questions about how is it used.
If you use this software and you're writing a research paper, please cite our research paper where we showcase this software using the Github function for citation. 

## Contributing
Pull requests are welcome, but please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)

