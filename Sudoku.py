import re
import logging
from argparse import ArgumentParser
from random import shuffle, choice
from sys import setrecursionlimit

from Cell import Cell
from Pickable import dumps, loads

# TODO: move to a different file
DIGITS2 = '01234'
DIGITS3 = '0123456789'
DIGITS4 = '0123456789ABCDEFG'
DIGITS5 = '0123456789ABCDEFGHIJKLMNOP'

class Sudoku(object):
    def __init__(self, size, values):
        """Constructor.

        `size` is in `[2, 3, 4, 5]`.
        `values` is a list containing the start values.

        Accepted values are:
        * `size == 2`: '01234'
        * `size == 3`: '0123456789'
        * `size == 4`: '0123456789ABCDEFG'
        * `size == 5`: '0123456789ABCDEFGHIJKLMNOP'
        """

        # TODO: Add config for optional config parameters

        assert size in [2, 3, 4, 5], f"{size}"
        self.size = size
        self.size2 = size**2
        self.size4 = size**4
        self.digits = [None, None, DIGITS2, DIGITS3, DIGITS4, DIGITS5][size]
        # Assert there are size**4 digit values
        _values_len = len([v for v in values if v in self.digits])
        assert _values_len == self.size4, f"values: {_values_len}, expected: {self.size4}"
        # Set cells
        self.cells = [
            Cell(size, row, col, values[(col -1) +(row -1) *self.size2])
            for row in range(1, self.size2 +1)
            for col in range(1, self.size2 +1)
        ]
        # Set cells siblings
        for cell in self.cells:
            cell.set_siblings(
                [c for c in self.cells if c != cell and c.row == cell.row],
                [c for c in self.cells if c != cell and c.col == cell.col],
                [c for c in self.cells if c != cell and c.block == cell.block]
            )
        # Options
        self.shuffle = False
        self.only_backtrack = False
        self.no_backtrack = False
        # Complete
        self.__complete = 0
        self.steps = 0
        self.__tries = []

    def to_ascii(self):
        """Prints the scheme.
        """
        # TODO: Use __str__
        # TODO: Use single borders for inner blocks: ╟╢╤╧╪╫┼┬├┤
        # https://en.wikipedia.org/wiki/Box-drawing_character#DOS

        # Print top border
        output = "╔═" + "═╦═".join(["═"] *self.size2) +"═╗\n"
        # Print each cell in each row, separated by ║
        for i in range(1, self.size2 +1):
            output += "║" + "║".join(c.to_ascii() for c in self.cells if c.row == i) + "║\n"
            if i < self.size2:
                output += "╠═" + "═╬═".join(["═"] *self.size2) + "═╣\n"
        # Print bottom border
        output += "╚═" + "═╩═".join(["═"] *self.size2) +"═╝"
        return output

    def to_fen(self):
        # TODO:
        pass

    def solve(self):
        """Returns `False` when is solved, or can't find a solution.
        """
        # TODO: Add loop here

        if self.is_solved():
            return False

        self.steps += 1

        if not self.only_backtrack:
            # Apply logic
            for cell in [c for c in self.cells if not c.is_solved()]:
                cell.sole_candidate()

            for cell in [c for c in self.cells if not c.is_solved()]:
                cell.unique_candidate()

            for cell in [c for c in self.cells if not c.is_solved()]:
                cell.naked_subset()

        # Check for progress
        complete = self.complete()
        if complete == self.__complete or not self.is_valid():
            if self.no_backtrack:
                return False
            # Try guesses
            return self.with_try()

        self.__complete = complete

        return True

    def with_try(self):
        """Solve trying to guess values.
        """
        # TODO: Should be "private"
        if not self.is_valid():
            # Something went wrong, try a different guess
            while len(self.__tries):
                # TODO: maybe I should load everything, see dump below
                (cells, candidates, _first) = self.__tries.pop()
                # Restore previous state
                self.cells = loads(cells)
                if len(candidates) > 0:
                    # Retrieve cell
                    first = [c for c in self.cells if c.row == _first.row and c.col == _first.col][0]
                    c0 = candidates.pop()
                    # TODO: We can't use first as cell, store only row and col to retrieve it later
                    self.__tries.append((dumps(self.cells), candidates, first))
                    first.set_try(c0)
                    return True
        else:
            # Try to guess a new cell
            to_solve = [c for c in self.cells if not c.is_solved()]
            if len(to_solve) > 0:
                # Get a cell to solve with the minimum length of candidates
                min_len = min(len(c.candidates) for c in to_solve)
                to_solve = [c for c in to_solve if len(c.candidates) == min_len]
                first = choice(to_solve) if self.shuffle else to_solve[0]
                candidates = first.candidates
                if self.shuffle:
                    shuffle(candidates)
                c0 = candidates.pop()
                # TODO: maybe I should dump everything
                self.__tries.append((dumps(self.cells), candidates, first))
                first.set_try(c0)
                return True
        # Nothing worked, give up
        return False

    def complete(self):
        """Returns the progress made as a number between 0.0 and 1.0
        """
        # TODO: rename progress
        return sum(c.complete() for c in self.cells) /self.size4

    def is_solved(self):
        """Returns `True` when puzzle is solved
        """
        return all(c.is_solved() for c in self.cells)

    def is_valid(self):
        """Returns `True` if puzzle is valid without counting undefined cells.
        """
        for i in range(1, self.size2 +1):
            row = [c.value for c in self.cells if c.row == i and c.value != '0']
            # print(row, set(row), len(row), len(set(row)))
            if len(set(row)) != len(row):
                return False
        for i in range(1, self.size2 +1):
            col = [c.value for c in self.cells if c.col == i and c.value != '0']
            if len(set(col)) != len(col):
                return False
        for i in range(1, self.size2 +1):
            block = [c.value for c in self.cells if c.block == i and c.value != '0']
            if len(set(block)) != len(block):
                return False
        return all(c.is_valid() for c in self.cells)

    @classmethod
    def from_full_fen(cls, full_fen):
        """Returns a `Sudoku` instance from a full FEN.

        A full FEN contains all values for all cells, so the length depends on the size.

        Each row is separated by a '/'.

        Each undefined value is '0'.
        """
        # TODO: separate size from fen
        [size, fen] = full_fen.split(' ')
        size = int(size)
        fen = re.sub(r'[^\d\/]', '', fen)
        cells = []
        for (i, row) in enumerate(fen.split('/'), 1):
            for (j, value) in enumerate(list(row), 1):
                cells.append(value)
        return cls(size, cells)

    @classmethod
    def from_fen(cls, _fen):
        """Returns a `Sudoku` instance from FEN.

        Each row is separated by a '/'.

        Each undefined value is '0'.

        Each '-' completes with '0's the row until the next block.

        A row shorter than the expected length is filled with '0's.
        """
        # TODO: separate size from fen
        if len(_fen) == 1:
            _fen += ' '
        [size, fen] = _fen.split(' ')
        size = int(size)
        fen = re.sub(r'[^\d\/\-]', '', fen)
        out = []
        for row in fen.split('/'):
            outrow = ''
            col = 1
            for value in list(row):
                if value == '-':
                    outrow += '0' * (size +1 -col)
                    col = 1
                else:
                    outrow += value
                    col = col +1 if col < size else 1
            if len(outrow) < size**2:
                outrow += '0' * (size**2 -len(outrow))
            out.append(outrow)
        if len(out) < size**2:
            out.extend(['0' *size**2] *(size**2 -len(out)))
        return Sudoku.from_full_fen(f"{size} {'/'.join(out)}")

from time import sleep, time
if __name__ == '__main__':
    parser = ArgumentParser("Solve Sudoku puzzles")
    parser.add_argument('fen',
        metavar = "FEN",
        help = "Forsyth-Edwards notation")
    parser.add_argument('-d', '--delay',
        metavar = "DELAY",
        type = float,
        default = 0,
        help = "Delay in seconds")
    parser.add_argument('--shuffle',
        action = 'store_const',
        const = True,
        default = False,
        help = 'Shuffle when trying')
    parser.add_argument('-v', '--verbose',
        action = 'store_const',
        const = True,
        default = False,
        help = "Verbose output")
    parser.add_argument('--recursion',
        metavar = 'LIMIT',
        type = int,
        default = -1,
        help = 'Set recursion limit if not enough to dump objects')
    parser.add_argument('--only-backtrack',
        action = 'store_const',
        const = True,
        default = False,
        help = 'Solve using only backtrack')
    parser.add_argument('--no-backtrack',
        action = 'store_const',
        const = True,
        default = False,
        help = "Don't use backtrack to solve")
    args = parser.parse_args()

    if args.recursion > 0:
        setrecursionlimit(args.recursion)

    # TODO: Apply options
    s = Sudoku.from_fen(args.fen)

    # Apply options
    s.shuffle = args.shuffle
    s.only_backtrack = args.only_backtrack
    s.no_backtrack = args.no_backtrack

    keep = True
    start = time()
    sleep(0.001)
    while keep:
        diff = time() -start
        print(f' {s.steps:4d} - {(s.complete() *100):4.1f}% - {diff:.3f}s - {(s.steps /diff):.1f}sps', end = ("\n" if args.verbose else "\r"))
        if args.verbose:
            print(s.to_ascii())
        keep = s.solve()
        if keep:
            sleep(args.delay)
    if not args.verbose:
        print()
        print(s.to_ascii())

# Hardest
# "8/0036/07-09-2/05-007/-0457/-1-03/001-068/0085-01/09--4"
# Harder
# "71/-09-507/-03-06/-80605/-1/196-4/-6-003/9040072/028-07"
# Hard
# "0007049/7-60208/109-4/85--36/-2-1/01-5-009/02-07-008/-009004/601-09"
# Medium
# "003102006/6-03708/108-002/09-00605/05-04-9/03-5-46/7--805/00401-009/5-208"
# Easy
# "9-07-081/04-039005/0728/0010042/-76201/409-6/-18603/803-19/61--002"
