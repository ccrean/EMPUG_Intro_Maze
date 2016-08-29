import itertools, StringIO, pygame, random, time, threading, graphics
import MazeGenerator

class Maze:
    _directions = ['N', 'E', 'S', 'W']
    _cell_width = 20
    _cell_height = 20
    _cell_sep = 1
    _player_color = pygame.Color(255, 0, 0)
    _font_color = pygame.Color(0, 0, 0)
    _bg_color = pygame.Color(210, 180, 140)
    _wall_color = pygame.Color(0, 0, 0)
    _start_color = pygame.Color(0, 255, 0)
    _end_color = pygame.Color(0, 0, 255)

    _player_color_graphics = 'red'
    _font_color_graphics = 'white'
    _bg_color_graphics = 'tan'
    _wall_color_graphics = 'black'
    _start_color_graphics = 'green'
    _end_color_graphics = 'blue'

    def __init__(self):
        """
        Create a new, empty maze.
        """
        # Create a new thread to call pygame.event.pump()
        self._killPump = threading.Event()
        self._continuePump = threading.Event()
        self._continuePump.clear()
        # self._pump = threading.Thread(target=self._pumpEvent)
        # self._pump.daemon = True
        # self._pump.start()

        self.clear()
        self._screen = None
        self._breadcrumbs = []

        self._win = None
        self._player_graphics = None

        # Initialize fonts
        pygame.font.init()

        self._createGraphics()
        self._createWalls()
        self.setDraw(True)
        self._generator = MazeGenerator.MazeGenerator()
        self._trail = False

    def close(self):
        """
        Close the maze.  Should be called before the program
        terminates.  None of the maze's methods should be called after
        calling close.
        """
        self.clear()
        self._killPump.set()
        self._continuePump.set()
        self._pump.join()

    def _createGraphics(self):
        """
        Create the graphics objects that will be assembled into the full
        maze image.  Should be called every time the maze is resized.
        """
        self._createPlayer()

        transparent_color = pygame.Color(255, 0, 255)
        # Create an image to represent cells that the player has already
        # traveled through
        self._breadcrumb = pygame.Surface((self._cell_width,
                                           self._cell_height))
        self._breadcrumb.fill(transparent_color)
        self._breadcrumb.set_colorkey(transparent_color)
        radius = max(min(self._cell_width, self._cell_height) / 10, 1)
        pygame.draw.circle(self._breadcrumb, self._wall_color,
                           (self._cell_width / 2,
                            self._cell_height / 2), radius)

        # Create cells to represent the start and end points
        self._start_cell = pygame.Surface((self._cell_width,
                                           self._cell_height))
        self._start_cell.fill(self._start_color)
        self._end_cell = pygame.Surface((self._cell_width,
                                         self._cell_height))
        self._end_cell.fill(self._end_color)


        # Create an image to represent the background
        self._background = pygame.Surface((self._cell_width,
                                           self._cell_height))
        self._background.fill(self._bg_color)
        self._createWalls()

    def _createPlayer(self):
        """
        Create a triangle image to represent the player.  By default, the
        player will be facing north.
        """
        self._player = pygame.Surface((self._cell_width,
                                       self._cell_height))
        
        # Give the player image a transparent background
        transparent_color = pygame.Color(255, 0, 255)
        self._player.fill(transparent_color)
        self._player.set_colorkey(transparent_color)
        pygame.draw.polygon(self._player, self._player_color,
                            ((1, self._cell_height - 1),
                             (self._cell_width - 1, self._cell_height - 1),
                             (self._cell_width / 2, 1)))

    def _createWalls(self):
        """
        Create images to represent walls.
        """
        top_left_corner = (0, 0)
        top_right_corner = (self._cell_width + self._cell_sep, 0)
        bottom_right_corner = (self._cell_width + self._cell_sep,
                               self._cell_height + self._cell_sep)
        bottom_left_corner = (0, self._cell_height + self._cell_sep)

        self._left_wall = self._getTransparentCell()
        pygame.draw.line(self._left_wall, self._wall_color,
                         top_left_corner, bottom_left_corner)

        self._top_wall = self._getTransparentCell()
        pygame.draw.line(self._top_wall, self._wall_color,
                         top_left_corner, top_right_corner)

        self._right_wall = self._getTransparentCell()
        pygame.draw.line(self._right_wall, self._wall_color,
                         top_right_corner, bottom_right_corner)

        self._bottom_wall = self._getTransparentCell()
        pygame.draw.line(self._bottom_wall, self._wall_color,
                         bottom_right_corner, bottom_left_corner)

    def _getTransparentCell(self):
        """
        Returns a transparent cell of the current size specified by the
        maze's _cell_width and _cell_height properties.
        """
        transparent_color = pygame.Color(255, 0, 255)
        cell = pygame.Surface((self._cell_width + 2 * self._cell_sep,
                               self._cell_height + 2 * self._cell_sep))
        cell.fill(transparent_color)
        cell.set_colorkey(transparent_color)
        return cell

    def __del__(self):
        pygame.quit()

    def clear(self):
        """
        Return the maze to its initial (empty) state.
        """
        self._continuePump.clear()
        self._grid = None
        self._start = None
        self._finish = None
        self._position = (0, 0)

        # Re-create the player icon, to get it facing in the right
        # direction
        self._createPlayer()
        
        self._dirs = itertools.cycle(self._directions)
        self._orientation = self._dirs.next()

        self._screen = None
        pygame.display.quit()

    def setDraw(self, s):
        """
        Turn the maze graphics on or off.

        Args:
        s (boolean): If s is True, the graphics will be redrawn each
                     time the player makes a change to the maze.  If s
                     is False, the maze will not be redrawn.
        """
        self._show = s

    def load(self, filename):
        """
        Load a maze from a text file.

        Args:
        filename (string): The name of the text file containing a
                           description of the maze.
        """
        f = open(filename)
        if not f:
            print "Cannot find" + filename
        self._load(f)
        f.close()

    def _load(self, f):
        """
        Does the actual work of loading the maze.

        Args:
        f (file object): The file object containing the description of the
                         maze.
        """
        self.clear()
        self._grid = []
        for row_no, line in enumerate(f):
            self._grid.append([])
            cells = line.split()
            for col_no, c in enumerate(cells):
                self._grid[-1].append(c)
                if '^' in c:
                    self._start = (row_no, col_no)
                if '$' in c:
                    self._finish = (row_no, col_no)

        # check to make sure that all lines are the same length
        length = len(self._grid[0])
        for row in self._grid[1:]:
            if len(row) != length:
               print "Error: all rows must be the same length" 
               self.clear()
               return

        # check to make sure that a start and finish point are defined
        if not self._start:
            self.clear()
            raise ValueError("start point not defined (use '^' to mark " +
                             "the starting point)")
        if not self._finish:
            self.clear()
            raise ValueError("end point not defined (use '$' to mark " +
                             "the end point)")

        self._position = self._start
        self.draw()

    def draw(self):
        """
        Redraw the maze.
        """
        if self._show:
            if self._grid:
                # Pause pumping until we're done redrawing
                self._continuePump.clear()
                
                # Size of screen
                height = (self._cell_height + self._cell_sep) *\
                    len(self._grid) + self._cell_sep
                width = (self._cell_width + self._cell_sep) *\
                    len(self._grid[0]) + self._cell_sep
                if self._screen == None or \
                        (pygame.display.Info().current_w,
                         pygame.display.Info().current_h) !=\
                         (width, height):
                         self._screen = pygame.display.set_mode((width, height))
                         self._win = graphics.GraphWin("Maze", width, height)
                         self._win.setBackground(self._bg_color_graphics)
                self._screen.fill(self._bg_color)
                for row_no, line in enumerate(self._grid):
                    for col_no, c in enumerate(line):
                        x_coord = col_no * (self._cell_width +\
                                                self._cell_sep)
                        y_coord = row_no * (self._cell_height +\
                                                self._cell_sep)

                        left = col_no * (self._cell_width +\
                                             self._cell_sep)
                        right = (col_no + 1) * (self._cell_width +\
                                              self._cell_sep)
                        top = row_no * (self._cell_height +\
                                            self._cell_sep)
                        bottom = (row_no + 1) * (self._cell_height +\
                                                     self._cell_sep)
                        top_left_corner = graphics.Point(left, top)
                        top_right_corner = graphics.Point(right, top)
                        bottom_left_corner = graphics.Point(left, bottom)
                        bottom_right_corner = graphics.Point(right, bottom)
                                           
                        if 'N' not in c:
                            self._screen.blit(self._top_wall,
                                             (x_coord, y_coord))
                            line = graphics.Line(top_left_corner,
                                                 top_right_corner)
                            line.draw(self._win)
                        if 'E' not in c:
                            self._screen.blit(self._right_wall,
                                             (x_coord, y_coord))
                            line = graphics.Line(top_right_corner,
                                                 bottom_right_corner)
                            line.draw(self._win)
                        if 'S' not in c:
                            self._screen.blit(self._bottom_wall,
                                             (x_coord, y_coord))
                            line = graphics.Line(bottom_left_corner,
                                                 bottom_right_corner)
                            line.draw(self._win)
                        if 'W' not in c:
                            self._screen.blit(self._left_wall,
                                             (x_coord, y_coord))
                            line = graphics.Line(top_left_corner,
                                                 bottom_left_corner)
                            line.draw(self._win)
                        tl = graphics.Point(left + 1, top + 1)
                        br = graphics.Point(right - 1, bottom - 1)
                        rect = graphics.Rectangle(tl, br)
                        if (row_no, col_no) == self._start:
                            rect.setFill(self._start_color_graphics)
                            rect.setOutline(self._start_color_graphics)
                            rect.draw(self._win)
                        elif (row_no, col_no) == self._finish:
                            rect.setFill(self._end_color_graphics)
                            rect.setOutline(self._end_color_graphics)
                            rect.draw(self._win)
                        self._drawBackground((row_no, col_no))
                self._redrawPlayer(self._position)
                self._redrawBreadcrumbs()
                pygame.display.update()
                self._checkFinished()
                self._continuePump.set()

    def _drawBackground(self, pos):
        """
        Fill in the cell specified by pos with the background color.
        Should be called on a cell anytime the player moves out of
        that cell.
        
        Args:
        pos (tuple): (row, column) of the cell that is to be filled in.
        """
        if self._show and self._screen:
            row_no = pos[0]
            col_no = pos[1]
            x_coord = col_no * (self._cell_width +\
                                    self._cell_sep) + self._cell_sep
            y_coord = row_no * (self._cell_height +\
                                    self._cell_sep) + self._cell_sep
            c = self._grid[row_no][col_no]
            if (row_no, col_no) == self._start:
                self._screen.blit(self._start_cell,
                                 (x_coord, y_coord))
            elif (row_no, col_no) == self._finish:
                self._screen.blit(self._end_cell,
                                 (x_coord, y_coord))
            else:
                self._screen.blit(self._background,
                                 (x_coord, y_coord))
            if '*' in c and self._trail:
                self._screen.blit(self._breadcrumb,
                                 (x_coord, y_coord))

    def _redrawPlayer(self, old_pos):
        """
        Redraw the player icon after it has moved.

        Args:
        old_pos (tuple): (row, column) of the cell previously occupied by
                         the player.
        """
        if self._screen:
            self._drawBackground(old_pos)
            x_coord = self._position[1] * (self._cell_height +\
                                              self._cell_sep) +\
                                              self._cell_sep
            y_coord = self._position[0] * (self._cell_height +\
                                              self._cell_sep) +\
                                              self._cell_sep
            self._screen.blit(self._player, (x_coord, y_coord))
            self._checkFinished()
            
            # Need to do this to stop the pygame window from freezing
            # on Windows
            pygame.event.pump()
            
            pygame.display.update()

            if self._player_graphics:
                self._player_graphics.undraw()

            row_no, col_no = self.getPosition()
            left = col_no * (self._cell_width +\
                                 self._cell_sep) + self._cell_sep + 1
            right = (col_no + 1) * (self._cell_width +\
                                        self._cell_sep) - self._cell_sep - 1
            top = row_no * (self._cell_height +\
                                self._cell_sep) + self._cell_sep + 1
            bottom = (row_no + 1) * (self._cell_height +\
                                         self._cell_sep) -\
                                         self._cell_sep - 1
            vertical_center = (top + bottom) // 2
            horizontal_center = (left + right) // 2

            if self._orientation == 'N':
                self._player_graphics = graphics.Polygon(
                    graphics.Point(left, bottom),
                    graphics.Point(horizontal_center, top),
                    graphics.Point(right, bottom))
            elif self._orientation == 'E':
                self._player_graphics = graphics.Polygon(
                    graphics.Point(left, top),
                    graphics.Point(right, vertical_center),
                    graphics.Point(left, bottom))
            elif self._orientation == 'S':
                self._player_graphics = graphics.Polygon(
                    graphics.Point(left, top),
                    graphics.Point(right, top),
                    graphics.Point(horizontal_center, bottom))
            elif self._orientation == 'W':
                self._player_graphics = graphics.Polygon(
                    graphics.Point(right, top),
                    graphics.Point(right, bottom),
                    graphics.Point(left, vertical_center))
            self._player_graphics.setFill(self._player_color_graphics)
            self._player_graphics.draw(self._win)

            self._drawBreadcrumb(old_pos)

    def turnRight(self):
        """
        Turn the player to the right (clockwise).
        """
        self._orientation = self._dirs.next()
        self._player = pygame.transform.rotate(self._player, -90)
        self._redrawPlayer(self._position)

    def turnLeft(self):
        """
        Turn the player to the left (counter-clockwise).
        """
        for i in range(len(self._directions) - 1):
            self._orientation = self._dirs.next()
        self._player = pygame.transform.rotate(self._player, 90)
        self._redrawPlayer(self._position)

    def _getNext(self):
        """
        Returns the (row, column) tuple that locates the cell in front
        of the player, taking into account the player's orientation.
        Does not consider whether or not there is a wall in the way --
        the calling function must do that.
        """
        if self._orientation == 'N':
            pos = self._position[0] - 1, self._position[1]
        elif self._orientation == 'E':
            pos = self._position[0], self._position[1] + 1
        elif self._orientation == 'S':
            pos = self._position[0] + 1, self._position[1]
        elif self._orientation == 'W':
            pos = self._position[0], self._position[1] - 1
        # Make sure that the player doesn't move off the edge of the map
        pos = min(max(pos[0], 0), len(self._grid) - 1),\
            min(max(pos[1], 0), len(self._grid[0]) - 1)
        return pos

    def moveForward(self):
        """
        Move the player, if possible, to the next cell.

        Returns:
        True if the player was able to move forward (there was no wall
        in the way).
        False if the player was not able to move forward (there was a
        wall in the way).
        """
        if self._grid:
            old_pos = self._position
            self._placeBreadcrumb(old_pos)
            next_cell = self._getNext()
            if self._orientation in self._grid[old_pos[0]][old_pos[1]] and\
                    next_cell != self._position:
                self._position = next_cell
                moved = True
            else:
                moved = False
            self._redrawPlayer(old_pos)
            return moved

    def isFinished(self):
        """
        Returns True if the player is standing on the end square,
        False otherwise.
        """
        if self._grid:
            if self._position == self._finish:
                return True
        return False

    def pathIsClear(self):
        """
        Returns True if the player can move forward (there is no wall
        in the way), False otherwise.
        """
        if self._grid:
            next_cell = self._getNext()
            cell = self._grid[self._position[0]][self._position[1]]
            return self._orientation in cell and next_cell != cell

    def wasVisited(self):
        """
        Returns True if the player previously visited the cell in
        which he/she is currently located, False otherwise.
        """
        if self._grid:
            return '*' in self._grid[self._position[0]][self._position[1]]

    def _checkFinished(self):
        """
        Prints a message congratulating the player if he/she is standing on
        the end square.
        """
        if self.isFinished():
            font = pygame.font.SysFont('monospace', 30)
            congrats = font.render('You win!', 1, self._font_color)
            congrats_x = (self._cell_width * len(self._grid[0]) -\
                              congrats.get_width()) / 2
            congrats_y = (self._cell_height * len(self._grid) -\
                              congrats.get_height()) / 2
            self._screen.blit(congrats, (congrats_x, congrats_y))
            pygame.display.update()

            height = (self._cell_height + self._cell_sep) *\
                len(self._grid) + self._cell_sep
            width = (self._cell_width + self._cell_sep) *\
                len(self._grid[0]) + self._cell_sep
            congrats_x = width // 2
            congrats_y = height // 2
            congrats_graphics = graphics.Text(
                graphics.Point(congrats_x, congrats_y),
                'You win!')
            congrats_graphics.setFill(self._font_color_graphics)
            congrats_graphics.setSize(36)
            congrats_graphics.draw(self._win)

    def line(self, length):
        """
        Generates a straight-line maze.
        
        Args:
        length (int): The length (number of cells) of the maze.
        """
        self.clear()
        self._grid, self._start, self._finish = self._generator.line(length)
        self._position = self._start
        self.draw()

    def spiral(self, width, height):
        """
        Generates a spiral maze.
        
        Args:
        width (int): The width of the maze (number of cells).
        height (int): The height of the maze (number of cells).
        """
        self.clear()
        self._grid, self._start, self._finish =\
            self._generator.spiral(width, height)
        self._position = self._start
        self.draw()

    def random(self, width, height, seed = None):
        """
        Create a random maze with given dimensions.

        Args:
        width (int): The width of the maze (number of cells).
        height (int): The height of the maze (number of cells).
        seed (int) (optional): The seed for the random number
        generator.  If not specified, defaults to time.time().
        """
        self.clear()
        self._grid, self._start, self._finish =\
            self._generator.random(width, height, seed)
        self._position = self._start
        self.draw()

    def _placeBreadcrumb(self, position):
        """
        Place a "breadcrumb" in the current cell to indicate that the
        player has visited it.
        """
        self._grid[position[0]][position[1]] += '*'

    def setTrail(self, trail):
        """
        Turns on/off the markers that indicate the cells that have already
        been visited.

        Args: 
        trail (boolean): If trail is True, the markers will be turned
                         on.  If trail is False, they will be turned
                         off.
        """
        self._trail = trail
        self.draw()

    def setCellWidth(self, width):
        """
        Sets the width of the cells.

        Args:
        width (int): Width of the cells (in pixels).
        """
        self._cell_width = width
        self._createGraphics()
        self.draw()

    def setCellHeight(self, height):
        """
        Sets the height of the cells.
        
        Args:
        height (int): Height of the cells (in pixels).
        """
        self._cell_height = height
        self._createGraphics()
        self.draw()

    def save(self, filename):
        """
        Save the maze to a text file, which can be loaded later using
        the load method.

        Args:
        filename (string): The name of the file to which the maze
                           should be saved.
        """
        with open(filename, 'w') as output_file:
            if self._grid:
                for row in self._grid:
                    for cell in row:
                        output_file.write(cell + ' ')
                    output_file.write('\n')

    def screenshot(self, filename):
        """
        Save a screenshot of the maze.

        Args:
        filename (string): The file to which the screenshot should be
                           saved.
        """
        pygame.image.save(self._screen, filename)

    def getStart(self):
        """
        Returns the (row, column) tuple for the starting point of the
        maze.
        """
        return self._start

    def getFinish(self):
        """
        Returns the (row, column) tuple for the ending point of the
        maze.
        """
        return self._finish

    def getPosition(self):
        """
        Returns the (row, column) tuple corresponding to the player's
        current position.
        """
        return self._position

    def getOrientation(self):
        """
        Returns the orientation as a string.  The return value will be
        one of 'N' (north), 'S' (south), 'E' (east), or 'W' (west).
        """
        return self._orientation

    def _pumpEvent(self):
        """
        Call pygame.event.pump() in an infinite loop.  Necessary to
        prevent the pygame window from freezing on Windows, and also
        to prevent the window from being erased when it is obscured by
        another window.
        """
        # while True:
        #     self._continuePump.wait()
        #     if self._killPump.isSet():
        #         break
        #     pygame.event.pump()

    def _drawBreadcrumb(self, pos):
        row_no, col_no = pos
        if '*' in self._grid[row_no][col_no] and self._trail and\
                self._show and self._win:
            x_coord = col_no * (self._cell_width +\
                                    self._cell_sep) +\
                                    self._cell_sep +\
                                    self._cell_width / 2
            y_coord = row_no * (self._cell_height +\
                                    self._cell_sep) +\
                                    self._cell_sep +\
                                    self._cell_height / 2
            radius = max(min(self._cell_width,
                             self._cell_height) // 10, 1)
            pygame.draw.circle(self._breadcrumb,
                               self._wall_color,
                               (self._cell_width / 2,
                                self._cell_height / 2), radius)
            breadcrumb = graphics.Circle(
                graphics.Point(x_coord, y_coord), radius)
            breadcrumb.setFill(self._wall_color_graphics)
            breadcrumb.draw(self._win)
            self._breadcrumbs.append(breadcrumb)

    def _redrawBreadcrumbs(self):
        while len(self._breadcrumbs) > 0:
            bc = self._breadcrumbs.pop()
            bc.undraw()
        for row_no, line in enumerate(self._grid):
            for col_no, c in enumerate(line):
                self._drawBreadcrumb((row_no, col_no))
