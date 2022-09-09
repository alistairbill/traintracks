from traintracks.core import Piece, Puzzle

PUZZLE = Puzzle(
    8,
    [1, 4, 1, 3, 4, 5, 4, 4],
    [5, 4, 2, 3, 4, 3, 4, 1],
    3,
    3,
    {(3, 0): Piece.EW, (7, 3): Piece.NS, (5, 4): Piece.NE, (0, 3): Piece.EW},
)
CHRIS = "54-14134544-54234341-48EW.53NE"
PIPES = """
 14134544
 ...━....5
 ........4
 ........2
A━.......3
 ........4
 ....┗...3
 ........4
 ...┃....1
    B
"""
SOLUTION = """
 14134544
 .┏━━━┓..5
 .┃...┗━┓4
 .┃.....┃2
A━┛.....┃3
 ....┏━━┛4
 ....┗━┓.3
 ...┏━━┛.4
 ...┃....1
    B
"""