class Maze:
    def __init__(self):
        self.clear()

    def clear(self):
        self.grid = None
        self.n_rows = 0
        self.n_cols = 0
        self.start = (0, 0)
        self.finish = (0, 0)
        self.position = (0, 0)

    def load(self, filename):
        self.grid = []
        f = open(filename)
        if not f:
            print "Cannot find" + filename
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
               clear()
               return

        n_rows = len(self.grid)
        n_cols = length

        # check to make sure that a start and finish point are defined
        if not any(map(lambda x: 'S' in x, self.grid)):
            print "Error: maze does not contain a starting point"
            clear()
            return

        if not any(map(lambda x: 'F' in x, self.grid)):
            print "Error: maze does not contain an ending point"
            clear()
            return

    def draw(self):
        if self.grid:
            for row_no, line in enumerate(self.grid):
                for col_no, c in enumerate(line):
                    if (row_no, col_no) == self.position:
                        print "X",
                    elif c == 1:
                        print "#",
                    elif c == 0:
                        print " ",
                    else:
                        print c,
                print "\n",
