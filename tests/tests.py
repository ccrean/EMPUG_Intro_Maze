import unittest
import Maze
import StringIO
import IPython

class MazeTest(unittest.TestCase):

    # grid = "1 1 1 1 1 1 1 1\nS 0 0 1 0 0 0 1\n1 1 0 1 0 1 1 1\n1 0 0 0 0 1 0 F\n1 0 1 1 0 1 0 1\n1 0 0 1 0 1 0 1\n1 1 0 1 0 0 0 1\n1 1 1 1 1 1 1 1"
    grid = "E WES W$\nE^ WENS WS\nE WN N"

    def testTurn(self):
        m = Maze.Maze()

        self.assertEqual(m.orientation, 'N')
        m.turnRight()
        self.assertEqual(m.orientation, 'E')
        m.turnRight()
        self.assertEqual(m.orientation, 'S')
        m.turnRight()
        self.assertEqual(m.orientation, 'W')
        m.turnRight()
        self.assertEqual(m.orientation, 'N')

        m.turnLeft()
        self.assertEqual(m.orientation, 'W')
        m.turnLeft()
        self.assertEqual(m.orientation, 'S')
        m.turnLeft()
        self.assertEqual(m.orientation, 'E')
        m.turnLeft()
        self.assertEqual(m.orientation, 'N')

    def testMove(self):
        m = Maze.Maze()
        m.loadString(self.grid)
        m.setDraw(False)
        # IPython.embed()

        self.assertEqual(m.position, (1, 0))
        self.assertEqual(m.orientation, 'N')

        self.assertFalse(m.wasVisited())
        self.assertFalse(m.pathIsClear())
        self.assertFalse(m.moveForward())
        self.assertEqual(m.position, (1, 0))

        m.turnRight()
        self.assertEqual(m.orientation, 'E')
        
        self.assertTrue(m.pathIsClear())
        self.assertTrue(m.moveForward())
        self.assertEqual(m.position, (1, 1))
        
        # Turn around and revisit the last cell
        m.turnRight()
        m.turnRight()
        self.assertTrue(m.moveForward())
        self.assertTrue(m.wasVisited())
        m.turnRight()
        m.turnRight()
        self.assertTrue(m.moveForward())
        self.assertTrue(m.wasVisited())

        self.assertTrue(m.pathIsClear())
        self.assertTrue(m.moveForward())
        self.assertEqual(m.position, (1, 2))
        
        self.assertFalse(m.pathIsClear())
        self.assertFalse(m.moveForward())
        self.assertEqual(m.position, (1, 2))
        
        m.turnRight()
        self.assertEqual(m.orientation, 'S')
        
        self.assertTrue(m.pathIsClear())
        self.assertTrue(m.moveForward())
        self.assertEqual(m.position, (2, 2))
        
        m.turnRight()
        self.assertFalse(m.pathIsClear())
        self.assertFalse(m.moveForward())
        self.assertEqual(m.position, (2, 2))

        m.turnRight()
        self.assertTrue(m.pathIsClear())
        self.assertTrue(m.moveForward())
        self.assertEqual(m.position, (1, 2))
        
        self.assertFalse(m.pathIsClear())
        self.assertFalse(m.moveForward())
        self.assertEqual(m.position, (1, 2))
        
        m.turnLeft()
        self.assertTrue(m.moveForward())
        self.assertEqual(m.position, (1, 1))

        # Make sure that the player can't move off the edge of the map
        m.loadString(self.grid)
        pos = m.position
        m.orientation = 'W'
        self.assertFalse(m.pathIsClear())
        self.assertFalse(m.moveForward())
        self.assertEqual(m.position, pos)

        m.position = (2, 2)
        m.orientation = 'E'
        self.assertFalse(m.pathIsClear())
        self.assertFalse(m.moveForward())
        self.assertEqual(m.position, (2, 2))

    def testLine(self):
        """
        Test method for generating straight-line mazes.
        """
        m = Maze.Maze()
        m.setDraw(False)
        with self.assertRaises(ValueError):
            m.line(-1)
            m.line(0)

        for length in [ 20, 100 ]:
            m.line(length)
            m.turnRight()

            for i in range(length - 1):
                self.assertTrue(m.moveForward())
            self.assertTrue(m.isFinished())
            self.assertFalse(m.moveForward())

if __name__ == '__main__':
    unittest.main()
