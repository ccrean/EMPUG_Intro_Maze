import itertools, StringIO, pygame, random, time
import MazeGenerator

class Maze:
    directions = ['N', 'E', 'S', 'W']
    opposite_dir = { 'N': 'S',
                     'E': 'W',
                     'S': 'N',
                     'W': 'E'
                     }
    _cell_width = 20
    _cell_height = 20
    _cell_sep = 1
    _player_color = pygame.Color(255, 0, 0)
    _font_color = pygame.Color(0, 0, 0)
    _bg_color = pygame.Color(210, 180, 140),
    _wall_color = pygame.Color(0, 0, 0),
    _start_color = pygame.Color(0, 255, 0),
    _end_color = pygame.Color(0, 0, 255)

    def __init__(self):
        self.clear()
        self.screen = None

        # Initialize fonts
        pygame.font.init()

        self._createGraphics()
        self._createWalls()
        self.setDraw(True)
        self._generator = MazeGenerator.MazeGenerator()
        self._trail = False

    def _createGraphics(self):
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
        # Create a triangle to represent the player
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
        transparent_color = pygame.Color(255, 0, 255)
        cell = pygame.Surface((self._cell_width + 2 * self._cell_sep,
                               self._cell_height + 2 * self._cell_sep))
        cell.fill(transparent_color)
        cell.set_colorkey(transparent_color)
        return cell

    def __del__(self):
        pygame.quit()

    def clear(self):
        self.grid = None
        self.start = None
        self.finish = None
        self.position = (0, 0)

        # Re-create the player icon, to get it facing in the right
        # direction
        self._createPlayer()
        
        self.dirs = itertools.cycle(self.directions)
        self.orientation = self.dirs.next()

    def setDraw(self, s):
        self.show = s

    def _getDirArrow(self):
        if self.orientation == 'N':
            return '^'
        elif self.orientation == 'E':
            return '>'
        elif self.orientation == 'S':
            return 'v'
        elif self.orientation == 'W':
            return '<'

    def loadString(self, s):
        s = StringIO.StringIO(s)
        self._load(s)
        s.close()

    def load(self, filename):
        f = open(filename)
        if not f:
            print "Cannot find" + filename
        self._load(f)
        f.close()

    def _load(self, f):
        self.clear()
        self.grid = []
        for row_no, line in enumerate(f):
            self.grid.append([])
            cells = line.split()
            for col_no, c in enumerate(cells):
                self.grid[-1].append(c)
                if '^' in c:
                    self.start = (row_no, col_no)
                if '$' in c:
                    self.finish = (row_no, col_no)

        # check to make sure that all lines are the same length
        length = len(self.grid[0])
        for row in self.grid[1:]:
            if len(row) != length:
               print "Error: all rows must be the same length" 
               self.clear()
               return

        # check to make sure that a start and finish point are defined
        if not self.start:
            self.clear()
            raise ValueError("start point not defined (use '^' to mark " +
                             "the starting point)")
        if not self.finish:
            self.clear()
            raise ValueError("end point not defined (use '$' to mark " +
                             "the end point)")

        self.position = self.start

    def draw(self):
        if self.show:
            if self.grid:
                # Size of screen
                height = (self._cell_height + self._cell_sep) *\
                    len(self.grid) + self._cell_sep
                width = (self._cell_width + self._cell_sep) *\
                    len(self.grid[0]) + self._cell_sep
                if self.screen == None or \
                        (pygame.display.Info().current_w,
                         pygame.display.Info().current_h) != (width, height):
                    self.screen = pygame.display.set_mode((width, height))
                self.screen.fill(self._bg_color)
                for row_no, line in enumerate(self.grid):
                    for col_no, c in enumerate(line):
                        x_coord = col_no * (self._cell_width +\
                                                self._cell_sep)
                        y_coord = row_no * (self._cell_height +\
                                                self._cell_sep)
                        if 'N' not in c:
                            self.screen.blit(self._top_wall,
                                             (x_coord, y_coord))
                        if 'E' not in c:
                            self.screen.blit(self._right_wall,
                                             (x_coord, y_coord))
                        if 'S' not in c:
                            self.screen.blit(self._bottom_wall,
                                             (x_coord, y_coord))
                        if 'W' not in c:
                            self.screen.blit(self._left_wall,
                                             (x_coord, y_coord))
                        self._drawBackground((row_no, col_no))
                self._redrawPlayer(self.position)
                pygame.display.update()
                self._checkFinished()

    def _drawBackground(self, pos):
        if self.show and self.screen:
            row_no = pos[0]
            col_no = pos[1]
            x_coord = col_no * (self._cell_width +\
                                    self._cell_sep) + self._cell_sep
            y_coord = row_no * (self._cell_height +\
                                    self._cell_sep) + self._cell_sep
            c = self.grid[row_no][col_no]
            if (row_no, col_no) == self.start:
                self.screen.blit(self._start_cell,
                                 (x_coord, y_coord))
            elif (row_no, col_no) == self.finish:
                self.screen.blit(self._end_cell,
                                 (x_coord, y_coord))
            else:
                self.screen.blit(self._background,
                                 (x_coord, y_coord))
            if '*' in c and self._trail:
                self.screen.blit(self._breadcrumb,
                                 (x_coord, y_coord))

    def _redrawPlayer(self, old_pos):
        if self.screen:
            self._drawBackground(old_pos)
            x_coord = self.position[1] * (self._cell_height +\
                                              self._cell_sep) +\
                                              self._cell_sep
            y_coord = self.position[0] * (self._cell_height +\
                                              self._cell_sep) +\
                                              self._cell_sep
            self.screen.blit(self._player, (x_coord, y_coord))
            self._checkFinished()
            
            # Need to do this to stop the pygame window from freezing
            # on Windows
            pygame.event.pump()
            
            pygame.display.update()

    def turnRight(self):
        self.orientation = self.dirs.next()
        self._player = pygame.transform.rotate(self._player, -90)
        self._redrawPlayer(self.position)

    def turnLeft(self):
        for i in range(len(self.directions) - 1):
            self.orientation = self.dirs.next()
        self._player = pygame.transform.rotate(self._player, 90)
        self._redrawPlayer(self.position)

    def _getNext(self):
        if self.orientation == 'N':
            pos = self.position[0] - 1, self.position[1]
        elif self.orientation == 'E':
            pos = self.position[0], self.position[1] + 1
        elif self.orientation == 'S':
            pos = self.position[0] + 1, self.position[1]
        elif self.orientation == 'W':
            pos = self.position[0], self.position[1] - 1
        # Make sure that the player doesn't move off the edge of the map
        pos = min(max(pos[0], 0), len(self.grid) - 1),\
            min(max(pos[1], 0), len(self.grid[0]) - 1)
        return pos

    def moveForward(self):
        old_pos = self.position
        self._placeBreadcrumb(old_pos)
        next_cell = self._getNext()
        if self.orientation in self.grid[old_pos[0]][old_pos[1]] and\
                next_cell != self.position:
            self.position = next_cell
            moved = True
        else:
            moved = False
        self._redrawPlayer(old_pos)
        return moved

    def isFinished(self):
        if self.grid:
            if self.position == self.finish:
                return True
        return False

    def pathIsClear(self):
        next_cell = self._getNext()
        cell = self.grid[self.position[0]][self.position[1]]
        return self.orientation in cell and next_cell != cell

    def wasVisited(self):
        return '*' in self.grid[self.position[0]][self.position[1]]

    def _checkFinished(self):
        if self.isFinished():
            font = pygame.font.SysFont('monospace', 30)
            congrats = font.render('You win!', 1, self._font_color)
            congrats_x = (self._cell_width * len(self.grid[0]) -\
                              congrats.get_width()) / 2
            congrats_y = (self._cell_height * len(self.grid) -\
                              congrats.get_height()) / 2
            self.screen.blit(congrats, (congrats_x, congrats_y))
            pygame.display.update()

    def line(self, length):
        self.clear()
        self.grid, self.start, self.finish = self._generator.line(length)
        self.position = self.start
        self.draw()

    def random(self, width, height, seed = None):
        """
        Create a random maze with given dimensions.
        """
        self.clear()
        self.grid, self.start, self.finish = self._generator.random(width,
                                                                    height,
                                                                    seed)
        self.position = self.start
        self.draw()

    def _placeBreadcrumb(self, position):
        self.grid[position[0]][position[1]] += '*'

    def setTrail(self, trail):
        self._trail = trail

    def setCellWidth(self, width):
        self._cell_width = width
        self._createGraphics()
        self.draw()

    def setCellHeight(self, height):
        self._cell_height = height
        self._createGraphics()
        self.draw()
