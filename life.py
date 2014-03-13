# coding: utf-8
import itertools


class LifeGame(object):
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

        cells = [[0 for col in range(cols)] for row in range(rows)]

        self.cells = cells
        self.alife_cells = set([])
        self.fill_alife()


    def fill_alife(self):
        self.alife_cells.update([
            (row, col)
                for (row, col) in itertools.product(range(self.rows), range(self.cols))
                    if self.cells[row][col] == 1
        ])

    def check_cell(self, cell, check_neighbors=True):
        already_checked = self.already_checked
        row, col = cell
        changed = []
        neighbors = []

        for row_delta, col_delta in itertools.product(range(-1, 2), repeat=2):
            if any((row_delta, col_delta)):
                neighbor_row = row + row_delta
                neighbor_col = col + col_delta

                if neighbor_row < 0:
                    neighbor_row = self.rows - 1
                if neighbor_col < 0:
                    neighbor_col = self.cols - 1

                if neighbor_row >= self.rows:
                    neighbor_row = 0

                if neighbor_col >= self.cols:
                    neighbor_col = 0

                neighbors.append((neighbor_row, neighbor_col))

        if check_neighbors:
            for neighbor in neighbors:
                if not neighbor in already_checked:
                    is_changed = self.check_cell(neighbor, check_neighbors=False)
                    if is_changed:
                        changed.append(neighbor)

        alife = len([ None for alife_cell in neighbors if self.cells[alife_cell[0]][alife_cell[1]] == 1 ])
        value = self.cells[row][col]

        if value == 0 and alife == 3:
            changed.append(cell)

        if value == 1 and (alife < 2 or alife > 3):
            changed.append(cell)

        already_checked.add(cell)

        return changed

    def change_cell(self, row, col, value=None):
        if not value is None:
            self.cells[row][col] = value
        else:
            self.cells[row][col] = 0 if self.cells[row][col] == 1 else 1

        if self.cells[row][col] == 1:
            self.alife_cells.add((row, col))
        else:
            try:
                self.alife_cells.remove((row, col))
            except KeyError:
                pass

    def clear(self):
        self.changed = set([])

        for cell in list(self.alife_cells):
            self.change_cell(cell[0], cell[1])
            self.changed.add(cell)

    def advance(self):
        self.already_checked = set([])
        self.changed = set([])

        for cell in self.alife_cells:
            self.changed.update(self.check_cell(cell))

        for row, col in self.changed:
            self.change_cell(row, col)
