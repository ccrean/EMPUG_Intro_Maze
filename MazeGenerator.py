import random, math

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

    def spiral(self, width, height):
        """
        Generates a spiral maze.
        
        Args:
        width (int): The width of the maze (number of cells).
        height (int): The height of the maze (number of cells).
        """
        grid = [ [''] * width for i in range(height) ]
        n_layers = int(min(math.ceil(height / 2.0),
                           math.ceil(width / 2.0)))
        for layer in range(n_layers):
            # Carve the first row
            start_col = max(1, layer)
            row = layer
            for col in range(start_col, width - layer):
                grid[row][col-1] += 'E'
                grid[row][col] += 'W'

            # Carve the last column
            col = width - layer - 1
            for row in range(layer + 1, height - layer):
                grid[row-1][col] += 'S'
                grid[row][col] += 'N'

            # Carve the last row
            if height % 2 == 0 or layer < n_layers - 1:
                start_col = width - layer - 2
                for col in range(width - layer - 2, layer - 1, -1):
                    row = height - layer - 1
                    grid[row][col+1] += 'W'
                    grid[row][col] += 'E'
            
            # Carve the first column
            if width % 2 == 0 or layer < n_layers - 1:
                for row in range(height - layer - 2, layer, -1):
                    col = layer
                    grid[row+1][col] += 'N'
                    grid[row][col] += 'S'
            
        start = (0, 0)
        end = (row, col)
        grid[start[0]][start[1]] += '^'
        grid[end[0]][end[1]] += '$'
        return grid, start, end

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
        self.grid[start[0]][start[1]] += '^'
        self.grid[finish[0]][finish[1]] += '$'
        return self.grid, start, finish

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
