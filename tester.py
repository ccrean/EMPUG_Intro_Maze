import Maze

def main():
    m = Maze.Maze()
    m.draw()

    m.load('maze.txt')
    m.draw()

if __name__ == '__main__':
    main()
