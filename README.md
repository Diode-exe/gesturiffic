# Gesturiffic

## Control your computer with your hand and a webcam

### Usage

The cursor position is calculated based off where your index finger is in the camera frame.
Change ```HAND_MIN``` and ```HAND_MAX``` based on how easy it is to reach the edge of the computer screen.
Upping the scale will make it easier to reach the edge, but will make it less precise and faster. Lowering it will do the opposite.

Tap your index and thumb together to left click, middle to click and drag, tap thumb and pinky for right click.

Press Q while the capture window is in focus to close the program.

### Note

Everything is processed on-device. I do not receive any data from this program, it works offline.
Also, this will not work in Task Manager, on the lock screen, or in the User Account Control box
(Do you want this program to make changes to your computer?)

### Requirements

- Python 3.11 or higher
- A webcam (built in or external)
Run ```python.exe checker.py --make-changes``` to create the necessary virtual environment and install dependencies. This only needs to be done once.

### Compiling (Optional)

Run ```python.exe compile.py --real --run-after-compile --archive``` to compile the program and run it immediately after. The --archive flag will create a zip file of the dist folder. The --real flag will compile the program without the test mode and simulation options (outdated). The --run-after-compile flag will run the program immediately after compiling. The compiled program will be in the ```main.dist``` folder. You can also run ```python.exe compile.py --help``` for help.
