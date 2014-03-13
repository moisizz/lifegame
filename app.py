# coding: utf-8
import random, pygame, sys, math
from pygame import Surface
from pygame.locals import *
from life import LifeGame
import itertools


GRAY  = (230, 230, 230)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Application(object):
    def __init__(self):
        default_rows = 20
        default_cols = 20

        default_fps = 15
        default_cell_size = 10
        default_cell_padding = 1

        pygame.init()
        self.FPSCLOCK = pygame.time.Clock()
        pygame.display.set_caption('"Life" game')
        self.init_board(default_rows, default_cols, default_fps, default_cell_size, default_cell_padding, first=True)
        self.main()

    def init_board(self, rows, cols, fps, cell_size, cell_padding, first=False):
        config = {'FPS': fps, 'CELL_SIZE': cell_size, 'PADDING': cell_padding}

        width = cols * config['CELL_SIZE'] + config['PADDING'] * (cols + 1)
        height = rows * config['CELL_SIZE'] + config['PADDING'] * (rows + 1)

        self.config = config

        self.screen = pygame.display.set_mode((width, height))
        self.bg = Surface((width, height))
        self.bg.fill(GRAY)

        if first or rows != self.life.rows or cols != self.life.cols:
            self.life = LifeGame(rows, cols)

        for row, col in itertools.product(range(rows), range(cols)):
            self.draw_cell(row, col)

    def change_cell(self, row, col, value=None):
        self.life.change_cell(row, col, value=value)
        self.draw_cell(row, col)

    def draw_cell(self, row, col):
        color = BLACK if self.life.cells[row][col] == 1 else WHITE

        # top left
        x1 = col * self.config['CELL_SIZE'] + self.config['PADDING'] * (col + 1)
        y1 = row * self.config['CELL_SIZE'] + self.config['PADDING'] * (row + 1)

        # bottom right
        x2 = x1 + self.config['CELL_SIZE']
        y2 = y1 + self.config['CELL_SIZE']

        s = Surface((x2 - x1, y2 - y1))
        s.fill(color)

        self.bg.blit(s, (x1, y1))

    def clear_board(self):
        self.life.clear()

        for row, col in self.life.changed:
            self.draw_cell(row, col)

    def random_fill(self):
        self.clear_board()

        for row, col in itertools.product(range(self.life.rows), range(self.life.cols)):
            if random.randint(0, 1) == 1:
                self.change_cell(row, col)

    def lattice_fill(self, step):
        self.clear_board()

        for row, col in itertools.product(range(self.life.rows), range(self.life.cols)):
            if (row % step == 0) or (col % step == 0):
                self.change_cell(row, col)

    def main(self):
        started = False

        drawing = False
        erasing = False
        drawed = set([])

        while True:
            for event in pygame.event.get():
                if event.type == QUIT or event.type == KEYUP and event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYUP:
                    key_name = pygame.key.name(event.key)

                    if event.key == K_SPACE:
                         started = not started

                    elif event.key == K_BACKSPACE:
                        self.clear_board()

                    elif event.key == K_RETURN:
                        self.random_fill()

                    elif key_name in '123456789':
                        self.lattice_fill(int(pygame.key.name(event.key)))

                    elif key_name in ('up', 'right', 'down', 'left', '-', '=', 'page up', 'page down', 'home', 'end'):
                        rows, cols = self.life.rows, self.life.cols
                        config = self.config
                        if key_name == 'up' and rows > 2:
                            rows -= 1
                        elif key_name == 'down':
                            rows += 1
                        elif key_name == 'left' and cols > 2:
                            cols -= 1
                        elif key_name == 'right':
                            cols += 1
                        elif key_name == '-' and config['CELL_SIZE'] > 1:
                            config['CELL_SIZE'] -= 1
                        elif key_name == '=':
                            config['CELL_SIZE'] += 1
                        elif key_name == 'page down' and config['PADDING'] > 0:
                            config['PADDING'] -= 1
                        elif key_name == 'page up':
                            config['PADDING'] += 1
                        elif key_name == 'home' and config['FPS'] > 1:
                            config['FPS'] -= 1
                        elif key_name == 'end':
                            config['FPS'] += 1

                        args = (rows, cols, self.config['FPS'], self.config['CELL_SIZE'], self.config['PADDING'])
                        self.init_board(*args)

                elif event.type == MOUSEBUTTONDOWN and not started:
                    if event.button == 1:
                        drawing = True

                    elif event.button == 3:
                        erasing = True

                    drawed = set([])

                elif event.type == MOUSEBUTTONUP and not started:
                    drawing = False
                    erasing = False 

            if started:
                self.life.advance()
                for row, col in self.life.changed:
                    self.draw_cell(row, col)

            else:
                if drawing or erasing:
                    mousex, mousey = pygame.mouse.get_pos()
                    row, col = (
                        math.floor(float(mousey) / (self.config['CELL_SIZE'] + self.config['PADDING'])),
                        math.floor(float(mousex) / (self.config['CELL_SIZE'] + self.config['PADDING'])),
                    )
                    row, col = int(row), int(col)

                    if not (row, col) in drawed and row < self.life.rows and col < self.life.cols:
                        value = 1 if drawing else 0
                        self.change_cell(row, col, value=value)
                        drawed.add((row, col))

            self.screen.blit(self.bg, (0, 0))
            pygame.display.update()
            self.FPSCLOCK.tick(self.config['FPS'])


if __name__ == '__main__':
    app = Application()
