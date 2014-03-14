# coding: utf-8
import random, pygame, sys, math
from pygame import Surface
from pygame.locals import *
from life import LifeGame
import itertools
from Tkinter import Tk, Button, Entry, Text, StringVar, END
import tkFileDialog
import pickle
import base64


GRAY  = (230, 230, 230)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Application(object):
    def __init__(self):
        default_rows = 50
        default_cols = 50

        default_fps = 15
        default_cell_size = 10
        default_cell_padding = 1

        pygame.init()
        self.FPSCLOCK = pygame.time.Clock()
        self.init_board(default_rows, default_cols, default_fps, default_cell_size, default_cell_padding, init_game=True)
        self.main()

    def init_board(self, rows, cols, fps, cell_size, cell_padding, init_game=None, alife_cells=None):
        config = {'FPS': fps, 'CELL_SIZE': cell_size, 'PADDING': cell_padding}

        width = cols * config['CELL_SIZE'] + config['PADDING'] * (cols + 1)
        height = rows * config['CELL_SIZE'] + config['PADDING'] * (rows + 1)

        self.config = config

        self.set_caption(False)
        self.screen = pygame.display.set_mode((width, height))
        self.bg = Surface((width, height))
        self.bg.fill(GRAY)

        if init_game or rows != self.life.rows or cols != self.life.cols:
            self.life = LifeGame(rows, cols)

        if alife_cells:
            for row, col in alife_cells:
                self.life.change_cell(row, col, value=1)

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

    def copy_state(self):
        state = {
            'rows': self.life.rows,
            'cols': self.life.cols,
            'config': self.config,
            'alife_cells': self.life.alife_cells
        }

        root = Tk()
        encoded = base64.b64encode(pickle.dumps(state))

        options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('text files', '.txt')]
        options['initialfile'] = 'board.txt'
        options['parent'] = root
        options['title'] = u'Сохранить доску'

        filename = tkFileDialog.asksaveasfilename(**options)

        if filename:
            state_file = open(filename, 'w')
            state_file.write(encoded)
            state_file.close()

        root.destroy()

    def restore_state(self):
        root = Tk()

        options = {}
        options['multiple'] = False
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('text files', '.txt')]
        options['parent'] = root
        options['title'] = u'Восстановить доску'

        filename = tkFileDialog.askopenfilename(**options)
        root.destroy()

        if filename:
            self.clear_board()
            state_file = open(filename, 'r')
            encoded_state = state_file.read().strip()
            state_file.close()

            pickled_state = base64.b64decode(encoded_state)
            state = pickle.loads(pickled_state)
            self.init_board(
                state['rows'],
                state['cols'],
                state['config']['FPS'],
                state['config']['CELL_SIZE'],
                state['config']['PADDING'],
                alife_cells=state['alife_cells']
            )

    def move_cells(self, direction):
        alife_cells_list = list(self.life.alife_cells)
        moved_alife_cells = set([])
        rows, cols = self.life.rows, self.life.cols

        if direction == 'up':
            alife_cells_list.sort(key=lambda cell: cell[0])

        elif direction == 'down':
            alife_cells_list.sort(key=lambda cell: cell[0], reverse=True)

        elif direction == 'left':
            alife_cells_list.sort(key=lambda cell: cell[1])

        elif direction == 'right':
            alife_cells_list.sort(key=lambda cell: cell[1], reverse=True)

        for cell in alife_cells_list:
            if direction == 'up':
                if cell[0] == 0:
                    next_cell = (rows - 1, cell[1])
                else:
                    next_cell = (cell[0] - 1, cell[1])

            elif direction == 'down':
                if cell[0] == (rows - 1):
                    next_cell = (0, cell[1])
                else:
                    next_cell = (cell[0] + 1, cell[1])

            elif direction == 'left':
                if cell[1] == 0:
                    next_cell = (cell[0], cols - 1)
                else:
                    next_cell = (cell[0], cell[1] - 1)

            elif direction == 'right':
                if cell[1] == (cols - 1):
                    next_cell = (cell[0], 0)
                else:
                    next_cell = (cell[0], cell[1] + 1)

            moved_alife_cells.add(next_cell)

        return moved_alife_cells

    def set_caption(self, started):
        title = "Conway's Game of Life. Speed: {0} ({1})"

        if started:
            started_str = 'started'
        else:
            started_str = 'paused'

        pygame.display.set_caption(title.format(self.config['FPS'], started_str))

    def main(self):
        started = False

        drawing = False
        erasing = False
        drawed = set([])

        arrow_keys = (K_UP, K_DOWN, K_LEFT, K_RIGHT)
        numpad_arrow_keys = (K_KP8, K_KP2, K_KP4, K_KP6)
        numpad_directions = {K_KP8: 'up', K_KP2: 'down', K_KP4: 'left', K_KP6: 'right'}

        field_modify_keys = arrow_keys + numpad_arrow_keys + (
            K_END, K_HOME,
            K_PAGEUP, K_PAGEDOWN,
            K_MINUS, K_EQUALS,
        )

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYUP:
                    if event.key == K_SPACE:
                        started = not started
                        self.set_caption(started)

                    elif event.key == K_BACKSPACE:
                        self.clear_board()

                    elif event.key == K_RETURN:
                        self.random_fill()

                    elif pygame.key.name(event.key) in '123456789':
                        self.lattice_fill(int(pygame.key.name(event.key)))

                    elif event.key == K_s:
                        if pygame.key.get_mods() & KMOD_CTRL:
                            self.copy_state()
                    elif event.key == K_r:
                        if pygame.key.get_mods() & KMOD_CTRL:
                            self.restore_state()

                    elif event.key in field_modify_keys:
                        rows, cols = self.life.rows, self.life.cols
                        config = self.config
                        alife_cells = None

                        if event.key in arrow_keys:
                            if pygame.key.get_mods() & KMOD_SHIFT:
                                delta = 10
                                bound = 10
                            else:
                                delta = 1
                                bound = 2
                            if event.key == K_UP and rows > bound:
                                rows -= delta
                            elif event.key == K_DOWN:
                                rows += delta
                            elif event.key == K_LEFT and cols > bound:
                                cols -= delta
                            elif event.key == K_RIGHT:
                                cols += delta

                        if event.key in numpad_arrow_keys:
                            alife_cells = self.move_cells(numpad_directions[event.key])
                            self.clear_board()

                        elif event.key == K_MINUS and config['CELL_SIZE'] > 1:
                            config['CELL_SIZE'] -= 1
                        elif event.key == K_EQUALS:
                            config['CELL_SIZE'] += 1

                        elif event.key == K_PAGEDOWN and config['PADDING'] > 0:
                            config['PADDING'] -= 1
                        elif event.key == K_PAGEUP:
                            config['PADDING'] += 1

                        elif event.key == K_HOME and config['FPS'] > 1:
                            config['FPS'] -= 1
                            self.set_caption(started)
                        elif event.key == K_END:
                            config['FPS'] += 1
                            self.set_caption(started)

                        args = (rows, cols, self.config['FPS'], self.config['CELL_SIZE'], self.config['PADDING'])
                        self.init_board(*args, alife_cells=alife_cells)

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
            if drawing or erasing:
                self.FPSCLOCK.tick(120)
            else:
                self.FPSCLOCK.tick(self.config['FPS'])


if __name__ == '__main__':
    app = Application()
