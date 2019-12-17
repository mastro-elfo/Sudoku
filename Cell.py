
# TODO: move to a different file
DIGITS2 = '01234'
DIGITS3 = '0123456789'
DIGITS4 = '0123456789ABCDEFG'
DIGITS5 = '0123456789ABCDEFGHIJKLMNOP'

class Cell(object):
    def __init__(self, size, row, col, start_value = '0'):
        self.size = size
        self.size2 = size**2
        self.size4 = size**4
        self.digits = [None, None, DIGITS2, DIGITS3, DIGITS4, DIGITS5][size]
        self.row = row
        self.col = col
        self.block = ((col -1) //size) + ((row -1) //size) *size +1
        self.start_value = start_value
        self.value = start_value
        self.candidates = list(self.digits[1:]) if start_value == '0' else [start_value]
        self.siblings = []
        self.row_siblings = []
        self.col_siblings = []
        self.block_siblings = []
        self.__try = False

    def to_ascii(self):
        # TODO: use __str__
        if self.value == '0':
            if len(self.candidates) == 0:
                return f'\033[1;31m {self.value} \033[0m'
            elif len(self.candidates) == 1:
                return f'\033[0;36m {self.candidates[0]} \033[0m'
            elif len(self.candidates) == 2:
                return f"\033[0;33m{' '.join(self.candidates)}\033[0m"
            elif len(self.candidates) == 3:
                return f"\033[0;33m{''.join(self.candidates)}\033[0m"
            else:
                # TODO: configure
                # return f'\033[0;33m+{len(self.candidates)} \033[0m'
                return f'\033[0;33m...\033[0m'
        elif self.value == self.start_value:
            return f'\033[1;37m {self.value} \033[0m'
        elif self.__try:
            return f'\033[0;94m {self.value} \033[0m'
        else:
            return f'\033[0;32m {self.value} \033[0m'

    # Setters
    def reset(self):
        # TODO: Don't use this
        self.value = start_value
        self.candidates = list(self.digits[1:]) if start_value == '0' else [start_value]

    def set_siblings(self, row_siblings, col_siblings, block_siblings):
        """
        """
        self.siblings = row_siblings + col_siblings + block_siblings
        self.row_siblings = row_siblings
        self.col_siblings = col_siblings
        self.block_siblings = block_siblings

    def set_value(self, value):
        """Sets the self value and updates self candidates
        """
        self.value = value
        self.candidates = [value]

    def set_try(self, value):
        """Sets self value, updates self candidates, and sets __try flag
        """
        self.value = value
        self.candidates = [value]
        self.__try = True

    def set_candidates(self, candidates):
        """Sets self candidates, and updates self value
        """
        self.candidates = candidates
        if len(self.candidates) == 1:
            self.set_value(self.candidates[0])

    def filter_candidates(self, candidates):
        """Filters self candidates and updates self value"""
        self.set_candidates([p for p in self.candidates if p not in candidates])

    # Getters
    def complete(self):
        """Returns the progress made as a number between 0.0 and 1.0
        """
        # TODO: Rename progress
        return 1 if self.value != '0' else (1 - len(self.candidates) /self.size2)

    def is_solved(self):
        """Returns `True` is self is solved
        """
        return self.value != '0'

    def is_valid(self):
        """Returns `True` if self has a valid value or is undefined
        """
        return self.value != '0' or len(self.candidates) > 0

    # Solvers
    def sole_candidate(self):
        """Removes candidates that are values of siblings"""
        self.candidates = [p for p in self.candidates if p not in [s.value for s in self.siblings]]
        if len(self.candidates) == 1:
            self.set_candidates(self.candidates)

    def unique_candidate(self):
        """Checks if self has a unique candidate in row/col/block"""
        self.__unique_candidate(self.row_siblings)
        self.__unique_candidate(self.col_siblings)
        self.__unique_candidate(self.block_siblings)

    def __unique_candidate(self, siblings):
        """Checks if self has a unique candidate in `siblings`"""
        candidates = [
            p for p in self.candidates if p not in [
                item for item in [s.candidates for s in siblings]
            ]
        ]
        if len(candidates) == 1:
            self.set_candidates(candidates)

    def naked_subset(self):
        """Checks for twins"""
        if not self.is_solved():
            self.__naked_subset(self.row_siblings)
            self.__naked_subset(self.col_siblings)
            self.__naked_subset(self.block_siblings)

    def __naked_subset(self, siblings):
        """Applies "naked subset" to siblings.
        """
        twins = [c for c in siblings if c.candidates == self.candidates]
        if len(twins) == len(self.candidates) -1:
            for cell in siblings:
                if cell not in twins and not cell.is_solved():
                    cell.filter_candidates(self.candidates)
