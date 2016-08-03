import unittest, StringIO, sys, os, pygame, cv2
sys.path.append('..')
import Maze

import IPython

class MazeTest(unittest.TestCase):

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
        m.setDraw(False)
        m.load('test_maze.txt')

        self.assertEqual(m.position, (0, 0))
        self.assertEqual(m.orientation, 'N')

        self.assertFalse(m.wasVisited())
        self.assertFalse(m.pathIsClear())
        self.assertFalse(m.moveForward())
        self.assertEqual(m.position, (0, 0))

        m.turnRight()
        self.assertEqual(m.orientation, 'E')
        
        self.assertTrue(m.pathIsClear())
        self.assertTrue(m.moveForward())
        self.assertEqual(m.position, (0, 1))
        
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
        self.assertEqual(m.position, (0, 2))
        
        m.turnRight()
        self.assertEqual(m.orientation, 'S')
        
        self.assertTrue(m.pathIsClear())
        self.assertTrue(m.moveForward())
        self.assertEqual(m.position, (1, 2))

        self.assertTrue(m.pathIsClear())
        self.assertTrue(m.moveForward())
        self.assertEqual(m.position, (2, 2))

        self.assertFalse(m.pathIsClear())
        self.assertFalse(m.moveForward())
        self.assertEqual(m.position, (2, 2))
        
        m.turnLeft()
        self.assertTrue(m.pathIsClear())
        self.assertTrue(m.moveForward())
        self.assertEqual(m.position, (2, 3))

        m.turnRight()
        self.assertTrue(m.pathIsClear())
        self.assertTrue(m.moveForward())
        self.assertEqual(m.position, (3, 3))
        
        self.assertFalse(m.pathIsClear())
        self.assertFalse(m.moveForward())
        self.assertEqual(m.position, (3, 3))

        # Make sure that the player can't move off the edge of the map
        m.load('test_maze.txt')
        pos = m.position
        self.assertFalse(m.pathIsClear())
        self.assertFalse(m.moveForward())
        self.assertEqual(m.position, pos)

        m.position = m.finish
        self.assertTrue(m.isFinished())

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

    def testDraw(self):
        """
        Test the maze drawing methods.
        """
        input_dir = 'images'
        output_dir = 'output'
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        composite_command = ['compare', '-compose', 'src']

        m = Maze.Maze()
        m.setDraw(True)
        m.load('test_maze.txt')

        for direction in ['N', 'E', 'S', 'W']:
            filename = 'maze_{}.png'.format(direction)
            output_image = os.path.join(output_dir, filename)
            input_image = os.path.join(input_dir, filename)
            compare_image = os.path.join(output_dir,
                                         'cmp_' + filename)
            print input_image, output_image, compare_image

            m.screenshot(output_image)

            # Perform a pixel-by-pixel comparison of the two images
            img_ref = cv2.imread(input_image)
            img_test = cv2.imread(output_image)
            self.assertTrue((img_ref == img_test).all())

            m.turnRight()

if __name__ == '__main__':
    unittest.main()
