# coding: utf-8

import random, pygame, sys, math
from pygame import Surface
from pygame.locals import *

FPS = 15
CELL_SIZE = 10

WIDTH_CELLS = 50
HEIGHT_CELLS = 50
PADDING = 1

WIDTH  = WIDTH_CELLS * CELL_SIZE + PADDING * (WIDTH_CELLS + 1)
HEIGHT = HEIGHT_CELLS * CELL_SIZE + PADDING * (HEIGHT_CELLS + 1)

GRAY  = (230, 230, 230)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# cells = [[random.randint(0, 1) for j in range(0, HEIGHT_CELLS)] for i in range(0, WIDTH_CELLS)]
cells = [[0 for j in range(0, HEIGHT_CELLS)] for i in range(0, WIDTH_CELLS)]

# glider
# cells[5][5] = 1
# cells[6][5] = 1
# cells[7][5] = 1
# cells[7][4] = 1
# cells[6][3] = 1

for i in range(0, WIDTH):
    row = []
    for j in range(0, HEIGHT):
        row.append(0)

def draw_cell(surf, i, j, draw_padding=False):
    color = BLACK if cells[i][j] == 1 else WHITE
    x1 = i * CELL_SIZE + PADDING * (i + 1)
    y1 = j * CELL_SIZE + PADDING * (j + 1)

    x2 = x1 + CELL_SIZE
    y2 = y1 + CELL_SIZE

    s = Surface((x2 - x1, y2 - y1))
    s.fill(color)
    surf.blit(s, (x1, y1))

def check_cell(cell, check_neighbors=True):
    i, j = cell
    changed = []
    neighbors = []

    for row in range(i-1, i+2):
        for col in range(j-1, j+2):
            if row != i or col != j:
                cell_row = row
                cell_col = col

                if cell_row < 0:
                    cell_row = HEIGHT_CELLS - 1
                if cell_col < 0:
                    cell_col = WIDTH_CELLS - 1

                if cell_row >= HEIGHT_CELLS:
                    cell_row = 0
                if cell_col >= WIDTH_CELLS:
                    cell_col = 0

                neighbors.append((cell_row, cell_col))

    if check_neighbors:
        for neighbor in neighbors:
            is_changed = check_cell(neighbor, check_neighbors=False)
            if is_changed:
                changed.append(neighbor)

    alife = len([ None for alife_cell in neighbors if cells[alife_cell[0]][alife_cell[1]] == 1 ])
    value = cells[cell[0]][cell[1]]

    if value == 0 and alife == 3:
        changed.append(cell)

    if value == 1 and (alife < 2 or alife > 3):
        changed.append(cell)

    return changed


def main():
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('"Life" game')
    started = False
    alife_cells_filled = False
    alife_cells = set([])

    bg = Surface((WIDTH, HEIGHT))
    bg.fill(GRAY)

    for i in range(0, len(cells)):
        for j in range(0, len(cells[i])):
            draw_cell(bg, i, j)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYUP and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.type == KEYUP and event.key == K_SPACE:
                started = not started

            elif event.type == MOUSEBUTTONUP and not started:
                mousex, mousey = event.pos
                i, j = math.floor(float(mousex) / (CELL_SIZE + PADDING)), math.floor(float(mousey) / (CELL_SIZE + PADDING))
                i, j = int(i), int(j)
                cells[i][j] = 0 if cells[i][j] == 1 else 1
                if cells[i][j] == 1:
                    alife_cells.add((i, j))
                else:
                    try:
                        alife_cells.remove((i, j))
                    except KeyError:
                        pass
                draw_cell(bg, i, j)

        if started:
            if not alife_cells_filled:
                alife_cells.update([
                    (i, j)
                        for i in range(0, WIDTH_CELLS)
                            for j in range(0, HEIGHT_CELLS) if cells[i][j] == 1
                ])
                alife_cells_filled = True

            changed = set([])
            for cell in alife_cells:
                changed.update(check_cell(cell))

            for i, j in changed:
                if cells[i][j] == 0:
                    alife_cells.add((i, j))
                else:
                    try:
                        alife_cells.remove((i, j))
                    except KeyError:
                        pass

                cells[i][j] = 0 if cells[i][j] == 1 else 1
                draw_cell(bg, i, j)

        screen.blit(bg, (0, 0))
        pygame.display.update()
        FPSCLOCK.tick(FPS)


if __name__ == '__main__':
    main()
