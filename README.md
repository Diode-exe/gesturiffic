# Gesturiffic

## Control your computer with your hand and a webcam

### Usage

The cursor position is calculated based off where your index finger is in the camera frame.
Change ```HAND_MIN``` and ```HAND_MAX``` based on how easy it is to reach the edge of the computer screen.
Upping the scale will make it easier to reach the edge, but will make it less precise and faster. Lowering it will do the opposite.

Tap your index and thumb together to left click, middle to click and drag, tap thumb and pinky for right click.

Press Escape while the capture window is in focus to close the program. Press H for help.

### Note

Everything is processed on-device. I do not receive any data from this program, it works offline.
Also, this will not work in Task Manager, on the lock screen, or in the User Account Control box
(Do you want this program to make changes to your computer?)

### Requirements

```pip install -r .\requirements.txt```

### Compiling

Run ```python.exe compile.py --real --run-after-compile --archive``` to compile the program and run it immediately after. The --archive flag will create a zip file of the dist folder. The --real flag will compile the program without the test mode and simulation options (outdated). The --run-after-compile flag will run the program immediately after compiling. The compiled program will be in the dist folder. You can also run ```python.exe compile.py --help``` for more options. You need to have have a venv called .venv going otherwise this won't work. You can create one with ```python -m venv .venv``` and activate it with ```.\.venv\Scripts\activate``` on Windows or ```source .venv/bin/activate``` on Linux/Mac.
