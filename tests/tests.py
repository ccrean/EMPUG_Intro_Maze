import unittest, sys, os, cv2, filecmp, subprocess
sys.path.append('..')
import Maze

class MazeTest(unittest.TestCase):

    def testTurn(self):
        m = Maze.Maze()

        self.assertEqual(m.getOrientation(), 'N')
        m.turnRight()
        self.assertEqual(m.getOrientation(), 'E')
        m.turnRight()
        self.assertEqual(m.getOrientation(), 'S')
        m.turnRight()
        self.assertEqual(m.getOrientation(), 'W')
        m.turnRight()
        self.assertEqual(m.getOrientation(), 'N')

        m.turnLeft()
        self.assertEqual(m.getOrientation(), 'W')
        m.turnLeft()
        self.assertEqual(m.getOrientation(), 'S')
        m.turnLeft()
        self.assertEqual(m.getOrientation(), 'E')
        m.turnLeft()
        self.assertEqual(m.getOrientation(), 'N')

    def testMove(self):
        m = Maze.Maze()
        m.setDraw(False)
        m.load('test_maze.txt')

        self.assertEqual(m.getPosition(), (0, 0))
        self.assertEqual(m.getOrientation(), 'N')

        self.assertFalse(m.wasVisited())
        self.assertFalse(m.pathIsClear())
        self.assertFalse(m.moveForward())
        self.assertEqual(m.getPosition(), (0, 0))

        m.turnRight()
        self.assertEqual(m.getOrientation(), 'E')
        
        self.assertTrue(m.pathIsClear())
        self.assertTrue(m.moveForward())
        self.assertEqual(m.getPosition(), (0, 1))
        
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
        self.assertEqual(m.getPosition(), (0, 2))
        
        m.turnRight()
        self.assertEqual(m.getOrientation(), 'S')
        
        self.assertTrue(m.pathIsClear())
        self.assertTrue(m.moveForward())
        self.assertEqual(m.getPosition(), (1, 2))

        self.assertTrue(m.pathIsClear())
        self.assertTrue(m.moveForward())
        self.assertEqual(m.getPosition(), (2, 2))

        self.assertFalse(m.pathIsClear())
        self.assertFalse(m.moveForward())
        self.assertEqual(m.getPosition(), (2, 2))
        
        m.turnLeft()
        self.assertTrue(m.pathIsClear())
        self.assertTrue(m.moveForward())
        self.assertEqual(m.getPosition(), (2, 3))

        m.turnRight()
        self.assertTrue(m.pathIsClear())
        self.assertTrue(m.moveForward())
        self.assertEqual(m.getPosition(), (3, 3))
        
        self.assertFalse(m.pathIsClear())
        self.assertFalse(m.moveForward())
        self.assertEqual(m.getPosition(), (3, 3))

        # Make sure that the player can't move off the edge of the map
        m.load('test_maze.txt')
        pos = m.getPosition()
        self.assertFalse(m.pathIsClear())
        self.assertFalse(m.moveForward())
        self.assertEqual(m.getPosition(), pos)

        m._position = m.getFinish()
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

        m = Maze.Maze()
        m.setDraw(True)
        m.load('test_maze.txt')

        for direction in ['N', 'E', 'S', 'W']:
            filename = 'maze_{}'.format(direction)
            output_ps = os.path.join(output_dir, filename + '.ps')
            output_png = os.path.join(output_dir, filename + '.png')
            input_image = os.path.join(input_dir, filename + '.png')

            m.screenshot(output_ps)
            subprocess.call(['convert', output_ps, output_png])

            # Perform a pixel-by-pixel comparison of the two images
            img_ref = cv2.imread(input_image)
            img_test = cv2.imread(output_png)
            self.assertTrue((img_ref == img_test).all())

            m.turnRight()

    def testResize(self):
        """
        Test the methods for resizing the maze.
        """
        filename = 'maze_large'
        input_file = os.path.join('images', filename + '.png')
        output_ps = os.path.join('output', filename + '.ps')
        output_png = os.path.join('output', filename + '.png')

        m = Maze.Maze()
        m.setDraw(True)
        m.load('test_maze.txt')

        m.setCellWidth(50)
        m.setCellHeight(50)
        m.screenshot(output_ps)

        subprocess.call(['convert', output_ps, output_png])

        img_ref = cv2.imread(input_file)
        img_test = cv2.imread(output_png)
        self.assertTrue((img_ref == img_test).all())

    def testSave(self):
        """
        Test the save method.
        """
        filename = 'test_maze.txt'
        output_file = os.path.join('output', filename)

        m = Maze.Maze()
        m.setDraw(False)
        m.load(filename)
        m.save(output_file)

        self.assertTrue(filecmp.cmp(filename, output_file))

    def testSpiral(self):
        """
        Test the spiral maze generation.
        """
        m = Maze.Maze()
        m.setDraw(False)
        
        m.spiral(1, 1)
        self.assertEqual(m.getStart(), (0, 0))
        self.assertEqual(m.getFinish(), (0, 0))

        m.spiral(10, 1)
        self.assertEqual(m.getStart(), (0, 0))
        self.assertEqual(m.getFinish(), (0, 9))

        m.spiral(10, 2)
        self.assertEqual(m.getStart(), (0, 0))
        self.assertEqual(m.getFinish(), (1, 0))

        m.spiral(10, 3)
        self.assertEqual(m.getStart(), (0, 0))
        self.assertEqual(m.getFinish(), (1, 8))

        m.spiral(10, 4)
        self.assertEqual(m.getStart(), (0, 0))
        self.assertEqual(m.getFinish(), (2, 1))
       
        m.spiral(3, 4)
        self.assertEqual(m.getStart(), (0, 0))
        self.assertEqual(m.getFinish(), (2, 1))

        m.spiral(4, 4)
        self.assertEqual(m.getStart(), (0, 0))
        self.assertEqual(m.getFinish(), (2, 1))

        m.spiral(3, 10)
        self.assertEqual(m.getStart(), (0, 0))
        self.assertEqual(m.getFinish(), (8, 1))

        m.spiral(4, 10)
        self.assertEqual(m.getStart(), (0, 0))
        self.assertEqual(m.getFinish(), (2, 1))

    def testTrail(self):
        m = Maze.Maze()
        m.load('test_maze.txt')
        
        m.setTrail(False)

        m.turnRight()
        m.moveForward()
        m.moveForward()
        m.turnRight()
        m.moveForward()
        m.moveForward()
        m.turnLeft()
        m.moveForward()
        m.turnRight()
        m.moveForward()

        m.setTrail(True)
        output_on = os.path.join('output', 'maze_trail_on.png')
        m.screenshot(output_on)

        m.setTrail(False)
        output_off = os.path.join('output', 'maze_trail_off.png')
        m.screenshot(output_off)

        input_on = os.path.join('images', 'maze_trail_on.png')
        img_ref = cv2.imread(input_on)
        img_test = cv2.imread(output_on)
        self.assertTrue((img_ref == img_test).all())

        input_off = os.path.join('images', 'maze_trail_off.png')
        img_ref = cv2.imread(input_off)
        img_test = cv2.imread(output_off)
        self.assertTrue((img_ref == img_test).all())

    def testClear(self):
        """
        Make sure that the maze methods do not raise errors when they are
        called on an empty maze.
        """
        m = Maze.Maze()
        m.setDraw(False)

        self.assertIsNone(m.draw())
        self.assertIsNone(m.getFinish())
        self.assertEqual(m.getOrientation(), 'N')
        self.assertEqual(m.getPosition(), (0, 0))
        self.assertIsNone(m.getStart())
        self.assertFalse(m.isFinished())
        self.assertIsNone(m.moveForward())
        self.assertIsNone(m.pathIsClear())
        self.assertIsNone(m.turnLeft())
        self.assertIsNone(m.turnRight())
        self.assertIsNone(m.wasVisited())

        m.random(10, 10)
        m.clear()

        self.assertIsNone(m.draw())
        self.assertIsNone(m.getFinish())
        self.assertEqual(m.getOrientation(), 'N')
        self.assertEqual(m.getPosition(), (0, 0))
        self.assertIsNone(m.getStart())
        self.assertFalse(m.isFinished())
        self.assertIsNone(m.moveForward())
        self.assertIsNone(m.pathIsClear())
        self.assertIsNone(m.turnLeft())
        self.assertIsNone(m.turnRight())
        self.assertIsNone(m.wasVisited())

if __name__ == '__main__':
    unittest.main()
