# EMPUG Intro. to Python Class

This code was developed for the Eastern Michigan Python Users Group
Intro. to Python class.  It allows the user to visualize and generate
mazes, as well as to issue commands to solve the maze.  It is intended
to serve as a foundation upon which students can build maze-solving
algorithms.

## Usage

Better documentation will be available soon.

You can create a random maze as follows:

```
import Maze
m = Maze.Maze()
m.random(20, 20)
```

At this point, a pygame window should appear displaying the maze.  The
green square is the starting point, and the blue square is the ending
point.  The goal is to get to the ending pont by issuing some
combination of the following commands:

```
m.turnRight()
m.turnLeft()
m.moveForward()
```

After each of these commands, the display should be updated to show
the player's new position/orientation.

A few other commands are also available.  pathIsClear() will return
False if there is a wall in front of the player, True otherwise.
wasVisited() will return True if player has previously visited the
square that he/she currently occupies, False otherwise.  Finally,
isFinished() will return True if the player currently occupies the end
square, False otherwise.