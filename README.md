# NovaVision-AI-proj3
## Overview
The program helps with balancing containers in a ship by reading the manifest file, 
checks out the current state of whether the ship is balanced or not and uses A* to figure out moves to balance the ship.
### Container.py
### Tool
* Python
* Terminal base

## Plan and Process
### method
* Read the manifest file
* Build the initial state of the ship(8x12 grid).
* Use A star search to get the most efficient path
* Find out whether the ship is balanced. If it's not, the algorithm continues to explore states until it is balanced
* Generate the output log files

## Running the program
* Clone the repository
```bash
  git clone https://github.com/LydaTaing/Container-Balance-.git
```
* Run the application
```bash
  python main.py
```
* Enter the manifest file name with the label "Manifest File" at the top of GUI and click "Load and Balance". Press Next to see each move.
* After the moves are done, the GUI will prompt you to include any comments for the log file. Click "Ok" to save the log file.
### Reference 
* A star with heapq : https://medium.com/@tahsinsoyakk/a-search-a-comprehensive-guide-8275ebdf8fae 
* A star https://www.redblobgames.com/pathfinding/a-star/implementation.html 
* Timestamp : https://www.w3schools.com/python/python_datetime.asp
* log file path: https://docs.python.org/3/library/os.path.html , https://www.w3schools.com/python/ref_func_open.asp
* Tkinter for GUI: https://docs.python.org/3/library/tkinter.html
* Copy module documentation: https://docs.python.org/3/library/copy.html


