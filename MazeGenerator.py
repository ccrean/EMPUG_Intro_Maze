import random

class MazeGenerator:
    directions = ['N', 'E', 'S', 'W']
    opposite_dir = { 'N': 'S',
                     'E': 'W',
                     'S': 'N',
                     'W': 'E'
                     }

    def __init__(self):
        pass

    def line(self, length):
        if length < 1:
            raise ValueError("length must be >= 1")
        self.grid = [ [ '' ] * length ]
        if length > 1:
            self.grid[0][0] += 'E'
            self.grid[0][-1] += 'W'
        for i in range(1, length-1):
            self.grid[0][i] += 'WE'
        start = (0, 0)
        finish = (0, length - 1)
        return self.grid, start, finish

    def random(self, width, height, seed = None):
        """
        Create a random maze with given dimensions.
        """
        self.grid = [ [''] * width for i in range(height) ]
        random.seed(seed)
        start = ( random.randint(0, len(self.grid) - 1),
                  random.randint(0, len(self.grid[0]) - 1)
                  )
        visited = set([start])
        self._createPath(start, visited)
        start = ( random.randint(0, len(self.grid) - 1), 0 )
        finish = ( random.randint(0, len(self.grid) - 1),
                   len(self.grid[0]) - 1 )
        return self.grid, start, finish

    def eller(self, width, height, seed = None):
        """
        Generates a random maze with the given dimensions using Eller's
        algorithm.

        The following arguments must be specified:
        width - the number of cells in each row
        height - the number of cells in each column

        The following arguments are optional:
        seed - the seed for the random number generator
        """
        random.seed(seed)
        self.grid = [ [''] * width for i in range(height) ]

        sets = { i: i for i in range(width) } # map cells to sets
        cells = { i: [ i ] for i in range(width) } # map sets to cells
        for row in range(height - 1):
            self._makeConnections(sets, cells, width, False)
            sets, cells = self._makeDownwardConnections(sets, cells)
        self._makeConnections(sets, cells, height - 1, width, True)

    def _makeConnections(sets, cells, row, width, last):
        prob = 0.5
        if not last:
            for c in range(width - 1):
                if sets[c] != sets[c+1] and\
                        self._randomWithProb(prob):
                    self._merge(sets, cells, c, c+1)

    def _makeDownwardConnections(cells, width):
        prob = 0.3
        first_set = max(cells.keys()) + 1
        new_sets = { i: first_set + i for i in range(width) }
        new_cells = { first_set + i: [ i ] for i in range(width) }
        for s, c_list in cells:
            used = []
            c = random.choice(c_list)
            new_sets[c] = s
            new_cells[s].append(c)

    def _merge(sets, cells, c1, c2):
        s1 = sets[c1]
        s2 = sets[c2]
        for c in cells[s2]:
            sets[c] = s1
            cells[s1].append(c)
        del cells[s2]

    def _randomWithProb(prob):
        """
        Returns True with probability prob, and False with probability
        1 - prob.
        """
        return random.random() < prob
                
    def _createPath(self, cell, visited):
        while True:
            neighbors = self._getNeighbors(cell, visited)
            if not neighbors:
                return
            next_cell = random.choice(neighbors)
            direction = self._getRelativeDir(cell, next_cell)
            self.grid[cell[0]][cell[1]] += direction
            self.grid[next_cell[0]][next_cell[1]] +=\
                self.opposite_dir[direction]
            visited.add(next_cell)
            self._createPath(next_cell, visited)

    def _getNeighbors(self, cell, visited):
        potential_neighbors = [ (max(cell[0] - 1, 0), cell[1]),          # above
                                (min(cell[0] + 1, len(self.grid) - 1), cell[1]),  # below
                                (cell[0], max(cell[1] - 1, 0)),          # left
                                (cell[0], min(cell[1] + 1, len(self.grid[0]) - 1))# right
                                ]
        neighbors = [ c for c in potential_neighbors if c != cell and c not in visited]
        return neighbors

    def _getRelativeDir(self, c1, c2):
        if c2 == (c1[0] + 1, c1[1]):
            return 'S'
        elif c2 == (c1[0] - 1, c1[1]):
            return 'N'
        elif c2 == (c1[0], c1[1] - 1):
            return 'W'
        elif c2 == (c1[0], c1[1] + 1):
            return 'E'
        else:
            raise ValueError('cells are not neighbors')
