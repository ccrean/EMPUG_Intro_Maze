import itertools, StringIO

class Maze:
    directions = ['N', 'E', 'S', 'W']

    def __init__(self):
        self.clear()

    def clear(self):
        self.grid = None
        self.n_rows = 0
        self.n_cols = 0
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

        self.n_rows = len(self.grid)
        self.n_cols = length

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
                for row_no, line in enumerate(self.grid):
                    for col_no, c in enumerate(line):
                        if (row_no, col_no) == self.position:
                            print self._getDirArrow(),
                        elif c == 1:
                            print "#",
                        elif c == 0:
                            print " ",
                        else:
                            print c,
                    print "\n",

        if self.isFinished():
            print "You win!"

    def turnRight(self):
        self.orientation = self.dirs.next()
        self.draw()

    def turnLeft(self):
        for i in range(len(self.directions) - 1):
            self.orientation = self.dirs.next()
        self.draw()

    def _getNext(self):
        if self.orientation == 'N':
            return self.position[0] - 1, self.position[1]
        elif self.orientation == 'E':
            return self.position[0], self.position[1] + 1
        elif self.orientation == 'S':
            return self.position[0] + 1, self.position[1]
        elif self.orientation == 'W':
            return self.position[0], self.position[1] - 1

    def moveForward(self):
        next_cell = self._getNext()
        if self.grid[next_cell[0]][next_cell[1]] != 1:
            self.position = next_cell
            moved = True
        else:
            moved = False
        self.draw()
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
