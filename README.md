# Gesturiffic

## Control your computer with your hand and a webcam

### Usage

The cursor position is calculated based off where your index finger is in the camera frame.
Change ```HAND_MIN``` and ```HAND_MAX``` based on how easy it is to reach the edge of the computer screen.
Upping the scale will make it easier to reach the edge, but will make it less precise and faster. Lowering it will do the opposite.

Tap your index and thumb together to left click, middle to click and drag, tap thumb and pinky for right click. 

Press Escape while the capture window is in focus to close the program. Press H for help. 

### Note:

Everything is processed on-device. I do not receive any data from this program, it works offline. 
Also, this will not work in Task Manager, on the lock screen, or in the User Account Control box 
(Do you want this program to make changes to your computer?)

### Requirements
```pip install -r .\requirements.txt```