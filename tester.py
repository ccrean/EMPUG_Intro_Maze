import Maze

m = Maze.Maze()
m.draw()

m.load('maze.txt')
m.draw()

# while not m.isFinished():
#     m.turnRight()
#     if not m.moveForward():
#         while not m.moveForward():
#             m.turnLeft()

