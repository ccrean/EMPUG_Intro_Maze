import itertools, StringIO, pygame

class Maze:
    directions = ['N', 'E', 'S', 'W']
    _cell_width = 20
    _cell_height = 20
    _cell_sep = 1
    _player_color = pygame.Color(255, 0, 0)
    _font_color = pygame.Color(0, 0, 0)
    _colormap = { 0: pygame.Color(100, 100, 100),
                  1: pygame.Color(210, 180, 140),
                  'S': pygame.Color(0, 255, 0),
                  'F': pygame.Color(0, 0, 255)
                  }

    def __init__(self):
        self.clear()
        self.screen = None

        # Create a triangle to represent the player
        player_size = 20
        self._player = pygame.Surface((player_size, player_size))
        # Give the player image a transparent background
        transparent_color = pygame.Color(255, 0, 255)
        self._player.fill(transparent_color)
        self._player.set_colorkey(transparent_color)
        pygame.draw.polygon(self._player, self._player_color,
                            ((1, player_size - 1),
                             (player_size - 1, player_size - 1),
                             (player_size / 2, 1)))
        # Resize the triangle to fit in a cell
        self._player = pygame.transform.scale(self._player,
                                              (self._cell_width,
                                               self._cell_height))

        # Create label to congratulate user when they win
        pygame.font.init()

    def __del__(self):
        pygame.quit()

    def clear(self):
        self.grid = None
        self.start = (0, 0)
        self.finish = (0, 0)
        self.position = (0, 0)
        self.dirs = itertools.cycle(self.directions)
        self.orientation = self.dirs.next()
        self.show = True

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
        self.grid = []
        for row_no, line in enumerate(f):
            self.grid.append([])
            cells = line.split()
            for col_no, c in enumerate(cells):
                if c == 'S':
                    self.start = (row_no, col_no)
                    self.position = (row_no, col_no)
                    self.grid[-1].append(c)
                elif c == 'F':
                    self.finish = (row_no, col_no)
                    self.grid[-1].append(c)
                else:
                    self.grid[-1].append(int(c))

        # check to make sure that all lines are the same length
        length = len(self.grid[0])
        for row in self.grid[1:]:
            if len(row) != length:
               print "Error: all rows must be the same length" 
               self.clear()
               return

        # check to make sure that a start and finish point are defined
        if not any(map(lambda x: 'S' in x, self.grid)):
            print "Error: maze does not contain a starting point"
            self.clear()
            return

        if not any(map(lambda x: 'F' in x, self.grid)):
            print "Error: maze does not contain an ending point"
            self.clear()
            return

    def draw(self):
        if self.show:
            if self.grid:
                height = (self._cell_height + self._cell_sep) *\
                    len(self.grid) - self._cell_sep
                width = (self._cell_width + self._cell_sep) *\
                    len(self.grid[0]) - self._cell_sep
                if self.screen == None or \
                        (pygame.display.Info().current_w,
                         pygame.display.Info().current_h) != (width, height):
                    self.screen = pygame.display.set_mode((width, height))
                for row_no, line in enumerate(self.grid):
                    for col_no, c in enumerate(line):
                        x_coord = col_no * self._cell_width +\
                            (col_no - 1) * self._cell_sep
                        y_coord = row_no * self._cell_height +\
                            (row_no - 1) * self._cell_sep
                        rect = pygame.Rect(x_coord, y_coord,
                                           self._cell_width,
                                           self._cell_height)
                        pygame.draw.rect(self.screen,
                                    self._colormap[self.grid[row_no][col_no]],
                                    rect)
                        self._redrawPlayer(self.position)
                pygame.display.update()
                self._checkFinished()

    def _redrawPlayer(self, old_pos):
        if self.screen:
            background = pygame.Surface((self._cell_width,
                                         self._cell_height))
            color = self._colormap[self.grid[old_pos[0]][old_pos[1]]]
            pygame.draw.polygon(background, color,
                                ((0, 0), (0, self._cell_height),
                                 (self._cell_width, self._cell_height),
                                 (self._cell_width, 0)))
            for position, shape in zip((old_pos, self.position),
                                       (background, self._player)):
                x_coord = position[1] * (self._cell_height +\
                                             self._cell_sep) -\
                                             self._cell_sep
                y_coord = position[0] * (self._cell_height +\
                                             self._cell_sep) -\
                                             self._cell_sep
                self.screen.blit(shape, (x_coord, y_coord))
            self._checkFinished()
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
        next_cell = self._getNext()
        if self.grid[next_cell[0]][next_cell[1]] != 1 and\
                next_cell != self.position:
            self.position = next_cell
            moved = True
        else:
            moved = False
        # self.draw()
        self._redrawPlayer(old_pos)
        return moved

    def isFinished(self):
        if self.grid:
            if self.grid[self.position[0]][self.position[1]] == 'F':
                return True
        return False

    def pathIsClear(self):
        next_cell = self._getNext()
        if self.grid[next_cell[0]][next_cell[1]] != 1:
            return True
        else:
            return False

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
        if length < 1:
            raise ValueError("length must be >= 1")
        self.grid = [ [ 1 ] * length, [ 0 ] * length, [ 1 ] * length ]
        self.grid[1][0] = 'S'
        self.grid[1][-1] = 'F'
        self.position = (1,0)
        self.draw()
