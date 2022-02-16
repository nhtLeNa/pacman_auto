import pygame
import sys
import tkinter
import random

# =========================
BACKGROUND_COLOR = (32, 32, 32)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
TEXT_COLOR = (25, 0, 51)
# =========================
width = 800
height = 600
# =========================
TILE = 40
ghost_size = int(TILE/2)
pac_man_size = int(TILE/2)
food_size = int(TILE/6)
# =========================
PAC_MAN = 0
GHOST = 1
FOOD = 2
MONSTER = 3

SCAN = [-1, 0], [0, -1], [1, 0], [0, 1], \
       [-2, 0], [-1, -1], [0, -2], [1, -1], [2, 0], [1, 1], [0, 2], [-1, 1],\
       [-3, 0], [-2, -1], [-1, -2], [0, -3], [1, -2], [2, -1], [3, 0], [2, 1], [1, 2], [0, 3], [-1, 2], [-2, 1]

INIT_LOCATION = [-2, -2]


# =========================
def get_distance(point_a, point_b):
    return abs(point_a[0]-point_b[0]) + abs(point_a[1] - point_b[1])


# option: 0 for pac mac
# option: 1 for ghost
# return -1, if pac man hit wall, ghost or out side map
# return 1, if hit pac man food
# return 0, if nothing
def valid_pos(pos, map, char):
    x = pos[0]
    y = pos[1]
    if x not in range(0, map.size[0]) or y not in range(0, map.size[1]):
        return -1

    tile = map.matrix[x][y]

    if char == PAC_MAN:
        if tile == '1' or [x, y] in map.ghost_pos:
            return -1
        elif tile == '2':
            return 1

    if char == GHOST:
        if tile == '1':
            return -1
        elif tile == '2':
            return 1
    return 0


def create_ghosts(ghosts, map):
    num = 0
    for i in range(len(map.ghost_pos)):
        x = map.ghost_pos[i][0]
        y = map.ghost_pos[i][1]
        ghosts.append(Ghost([x, y]))
        num += 1
    return num


# =========================
class Previous:
    size = []
    pos = []

    def __init__(self, size):
        self.size = size
        self.pos = [[[0 for i in range(2)] for j in range(size[1])] for k in range(size[0])]

    def trace_back(self, food_pos, pac_pos):
        route = [food_pos]
        x = self.pos[food_pos[0]][food_pos[1]][0]
        y = self.pos[food_pos[0]][food_pos[1]][1]
        pos = [x, y]
        while pos != pac_pos:
            route.append(pos)
            x = self.pos[pos[0]][pos[1]][0]
            y = self.pos[pos[0]][pos[1]][1]
            pos = [x, y]
        route.append(pac_pos)
        return route


# =========================
class Map:
    size = []
    matrix = []
    food = 0
    ghost_pos = []

    food_pos = []  # level 1 + 2 only

    def set_up(self, lv):
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                val = self.matrix[i][j]
                if val == '2':
                    self.food += 1
                    if lv == 1 or lv == 2:
                        self.food_pos.append(i)
                        self.food_pos.append(j)
                if val == '3':
                    self.ghost_pos.append([i, j])
                    self.matrix[i][j] = '0'

    def show(self, scr, lv):    # scr = screen
        # scr.fill(BACKGROUND_COLOR)
        scr.blit(map_image, (0, 0))

        for i in range(self.size[0]):
            for j in range(self.size[1]):
                val = self.matrix[i][j]
                if val == '1':
                    scr.blit(wall_img, (j*TILE, i*TILE))
                    # pygame.draw.rect(scr, BLUE, (j * TILE, i * TILE, TILE, TILE))  # draw wall
                elif val == '2':
                    scr.blit(coin_image, (j*TILE, i*TILE))
                    # pygame.draw.circle(scr, YELLOW, (20 + j * TILE, 20 + i * TILE), food_size)  # draw food
                elif val == '3' and lv == 2:
                    scr.blit(ghost_img, (j * TILE, i * TILE))
                    # pygame.draw.circle(scr, RED, (20+j*TILE, 20+i*TILE), ghost_size)  # draw ghost if level 2

    def show_blind_pos(self, scr, pac_pos):
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if abs(i - pac_pos[0]) + abs(j - pac_pos[1]) > 3:
                    scr.blit(blind_image, (j * TILE, i * TILE))


class PacMan:
    init_pos = []
    pos = []
    game_over = False

    def show(self, scr):
        if self.pos[0] - self.init_pos[0] == 1:
            img = pac_down_img
        elif self.pos[1] - self.init_pos[1] == 1:
            img = pac_right_img
        elif self.pos[0] - self.init_pos[0] == -1:
            img = pac_up_img
        else:
            img = pac_left_img
        scr.blit(img, (self.pos[1]*TILE, self.pos[0]*TILE))

    def search(self, map, prev):
        expanded = []
        frontier = []
        fn = []
        gn = []
        step = 0
        cur = self.pos

        while True:
            if cur == map.food_pos:
                return True

            expanded.append(cur)
            step += 1

            x = cur[0]
            y = cur[1]
            next_pos = [[x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]]

            for i in range(4):
                if valid_pos(next_pos[i], map, PAC_MAN) != -1:  # -1 means wall or monster
                    if next_pos[i] not in expanded:

                        hn = get_distance(next_pos[i], map.food_pos)

                        if next_pos[i] not in frontier:
                            frontier.append(next_pos[i])
                            fn.append(step + hn)
                            gn.append(step)
                            prev.pos[next_pos[i][0]][next_pos[i][1]] = cur

                        elif next_pos[i] in frontier and gn[frontier.index(next_pos[i])] > step:
                            index = frontier.index(next_pos[i])
                            fn[index] = step + hn
                            gn[index] = step
                            prev.pos[next_pos[i][0]][next_pos[i][1]] = cur

            if len(frontier) <= 0:
                return False

            else:
                min_i = fn.index(min(fn))
                cur = frontier[min_i]
                step = gn[min_i]
                del frontier[min_i]
                del fn[min_i]
                del gn[min_i]

    def dls(self, pos, map, limit, invalid_pos, expanded, step, max_step):
        #print('--------- ' + str(limit))

        if map.matrix[pos[0]][pos[1]] == '2':
            return True, pos
        if limit <= 0:
            return False, pos

        if pos not in expanded:
            expanded.append(pos)
            step.append(max_step-limit)
        else:
            step[expanded.index(pos)] = max_step - limit

        x = pos[0]
        y = pos[1]
        next_pos = [[x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]]
        for i in range(4):
            if valid_pos(next_pos[i], map, PAC_MAN) != -1 and next_pos[i] not in invalid_pos:
                if (next_pos[i] not in expanded) \
                        or (next_pos[i] in expanded and step[expanded.index(next_pos[i]) > max_step-limit]):
                    had_found, p = self.dls(next_pos[i], map, limit-1, invalid_pos, expanded, step, max_step)
                    if had_found:
                        if pos != self.pos:
                            return True, pos
                        else:
                            return True, next_pos[i]
        return False, pos

    def ids(self, map, max_depth, invalid_pos):

        x = self.pos[0]
        y = self.pos[1]
        next_pos = [[x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]]
        count = 0
        for i in range(4):
            if valid_pos(next_pos[i], map, PAC_MAN) == -1:
                count += 1
        if count == 4:
            return self.pos

        for limit in range(max_depth):
            expanded = []
            step = []

            founded, next_pos = self.dls(self.pos, map, limit, invalid_pos, expanded, step, limit)
            if founded:
                return next_pos

        if valid_pos(self.pos, map, PAC_MAN) == -1:
            return self.run(map, invalid_pos)
        return self.pos

    def bfs(self, map, invalid_pos):
        frontier = [self.pos]
        expanded = []
        direct = [self.pos]

        while len(frontier) > 0:
            pos = frontier.pop(0)
            result = direct.pop(0)
            expanded.append(pos)

            x = pos[0]
            y = pos[1]
            next_pos = [[x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]]
            for i in range(4):
                if valid_pos(next_pos[i], map, PAC_MAN) == 1:
                    if pos == self.pos:
                        return next_pos[i]
                    else:
                        return result
                if valid_pos(next_pos[i], map, PAC_MAN) != -1 and next_pos[i] not in invalid_pos \
                        and next_pos[i] not in expanded and next_pos[i] not in frontier:
                    frontier.append(next_pos[i])
                    if pos == self.pos:
                        direct.append(next_pos[i])
                    else:
                        direct.append(result)

        if valid_pos(self.pos, map, PAC_MAN) == -1:
            return self.run(map, invalid_pos)
        return self.pos

    def run(self, map, invalid_pos):
        x = self.pos[0]
        y = self.pos[1]
        next_pos = [[x-1, y], [x+1, y], [x, y-1], [x, y+1]]
        for i in range(4):
            if valid_pos(next_pos[i], map, PAC_MAN) != -1 and next_pos[i] not in invalid_pos:
                return next_pos[i]
        return self.pos

    def move(self, map, score, pos):
        self.init_pos = self.pos
        self.pos = pos
        val = valid_pos(self.pos, map, PAC_MAN)
        if val == 0:  # no food here
            score.decrease()
        elif val == 1:  # food here
            score.increase()
            self.eat(map)
            if map.food <= 0:
                self.game_over = True

    def eat(self, map):
        map.food -= 1
        map.matrix[self.pos[0]][self.pos[1]] = '0'


class Ghost:
    pos = []
    init_pos = []
    prev_pos = []
    color = RED

    def __init__(self, pos):
        self.pos = pos
        self.init_pos = pos
        self.prev_pos = pos

    def show(self, scr):
        scr.blit(ghost_img, (self.pos[1]*TILE, self.pos[0]*TILE))

    # monster move around the initial location
    def wander_around(self, map):
        x = self.pos[0]
        y = self.pos[1]
        next_pos = [[x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]]
        while True:
            i = random.randint(0, 3)
            if valid_pos(next_pos[i], map, GHOST) != -1:
                if abs(next_pos[i][0]-self.init_pos[0]) <= 1 \
                        and abs(next_pos[i][1]-self.init_pos[1]) <= 1:
                    index = map.ghost_pos.index(self.pos)
                    self.prev_pos = self.pos
                    self.pos = next_pos[i]
                    map.ghost_pos[index] = self.pos
                    break

    # find the next position that lead to pac man
    def chase_pac_man(self, map, pac_pos):
        result = self.pos

        expanded = []
        frontier = []
        fn = []
        gn = []
        step = 0
        pos = self.pos
        while True:
            if pos == pac_pos:
                return result

            expanded.append(pos)
            step += 1

            x = pos[0]
            y = pos[1]
            next_pos = [[x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]]

            for i in range(4):
                if valid_pos(next_pos[i], map, GHOST) != -1 and next_pos[i] not in expanded:

                        hn = get_distance(next_pos[i], pac_pos)

                        if next_pos[i] not in frontier:
                            frontier.append(next_pos[i])
                            fn.append(step + hn)
                            gn.append(step)
                        else:
                            index = frontier.index(next_pos[i])
                            if gn[index] > step:
                                fn[index] = step + hn
                                gn[index] = step

            if len(frontier) <= 0:
                return result

            else:
                min_i = fn.index(min(fn))
                pos = frontier[min_i]
                step = gn[min_i]
                if step == 1:
                    result = pos
                del frontier[min_i]
                del fn[min_i]
                del gn[min_i]

    def move(self, map, pos):
        self.prev_pos = self.pos
        self.pos = pos
        index = map.ghost_pos.index(self.prev_pos)
        map.ghost_pos[index] = self.pos

    def is_hit_pac_man(self, pac_pos):
        if self.pos == pac_pos:
            return True
        return False


class Score:
    score = 1

    def show(self, scr, lv):
        text = 'Level: ' + str(lv) + '          ' + 'Score: ' + str(self.score)
        label = text_font.render(text, 1, TEXT_COLOR)
        scr.blit(label, (width/2, height - 20))
        return

    def increase(self):
        self.score += 20

    def decrease(self):
        self.score -= 1


# =========================
def create_menu_level():
    root = tkinter.Tk()
    root.geometry('500x500')
    root.resizable(0, 0)

    def play_lv1():
        _level[0] = 1
        root.destroy()
        create_menu_map()
        _quit[0] = False

    def play_lv2():
        _level[0] = 2
        root.destroy()
        create_menu_map()
        _quit[0] = False

    def play_lv3():
        _level[0] = 3
        root.destroy()
        create_menu_map()
        _quit[0] = False

    def play_lv4():
        _level[0] = 4
        root.destroy()
        create_menu_map()
        _quit[0] = False

    def quit_game():
        root.destroy()
        _quit[0] = True

    button = tkinter.Button(root, text='Level - 1', font=20, command=play_lv1)
    button.place(x=200, y=150)
    button = tkinter.Button(root, text='Level - 2', font=20, command=play_lv2)
    button.place(x=200, y=200)
    button = tkinter.Button(root, text='Level - 3', font=20, command=play_lv3)
    button.place(x=200, y=250)
    button = tkinter.Button(root, text='Level - 4', font=20, command=play_lv4)
    button.place(x=200, y=300)
    button = tkinter.Button(root, text='QUIT', font=20, command=quit_game)
    button.place(x=400, y=400)
    root.mainloop()


# =========================
def create_menu_map():
    root = tkinter.Tk()
    root.geometry('500x500')
    root.resizable(0, 0)

    def play_map1():
        _map[0] = 1
        root.destroy()

    def play_map2():
        _map[0] = 2
        root.destroy()

    def play_map3():
        _map[0] = 3
        root.destroy()

    def play_map4():
        _map[0] = 4
        root.destroy()

    def play_map5():
        _map[0] = 5
        root.destroy()

    button = tkinter.Button(root, text='Map 1', font=20, command=play_map1)
    button.place(x=200, y=150)
    button = tkinter.Button(root, text='Map 2', font=20, command=play_map2)
    button.place(x=200, y=200)
    button = tkinter.Button(root, text='Map 3', font=20, command=play_map3)
    button.place(x=200, y=250)
    button = tkinter.Button(root, text='Map 4', font=20, command=play_map4)
    button.place(x=200, y=300)
    button = tkinter.Button(root, text='Map 5', font=20, command=play_map5)
    button.place(x=200, y=350)

    root.mainloop()


# =========================
def display_result(pac_man_win):
    if pac_man_win:
        new_screen = pygame.display.set_mode((650, 450))
        new_screen.blit(win_image, (0, 0))
        text = 'SCORE:    ' + str(score.score)
        new_font = pygame.font.SysFont('Helvetica', 40, True)
        label = new_font.render(text, 1, TEXT_COLOR)
        new_screen.blit(label, (100, 250))
        pygame.display.update()
        pygame.time.delay(1000)
    else:
        new_screen = pygame.display.set_mode((1000, 550))
        new_screen.blit(game_over_image, (0, 0))
        pygame.display.update()
        pygame.time.delay(1000)


# =========================
def input_map(input_file):

    file = open(input_file, 'r')

    text = file.readline()
    num = ''
    for i in range(len(text)):
        if '0' <= text[i] <= '9':
            num += text[i]
        elif text[i] == ' ':
            game_map.size.append(int(num))
            num = ''
        else:
            game_map.size.append(int(num))

    game_map.matrix = [0 for i in range(game_map.size[0])]
    for i in range(game_map.size[0]):
        text = file.readline().rstrip()
        game_map.matrix[i] = list(text)

    text = file.readline()
    num = ''
    for i in range(len(text)):
        if '0' <= text[i] <= '9':
            num += text[i]
        elif text[i] == ' ':
            pac_man.pos.append(int(num))
            num = ''
        else:
            pac_man.pos.append(int(num))
    if len(pac_man.pos) < 2:
        pac_man.pos.append(int(num))
    pac_man.init_pos = pac_man.pos
    file.close()


# =========================
def level_1_2(lv):
    game_map.set_up(lv)
    game_map.show(screen, lv)
    pygame.display.update()

    ghosts = []
    num_ghost = create_ghosts(ghosts, game_map)

    prev = Previous(game_map.size)
    if pac_man.search(game_map, prev):

        route = prev.trace_back(game_map.food_pos, pac_man.pos)
        index = len(route)

        while not pac_man.game_over:
            game_map.show(screen, lv)

            for i in range(num_ghost):
                ghosts[i].show(screen)

            if index > 0:
                index -= 1
            pac_man.move(game_map, score, route[index])
            pac_man.show(screen)

            score.show(screen, lv)

            FPS.tick(10)
            pygame.display.update()
        pygame.time.delay(500)
        display_result(True)
    sys.exit()


def level_3(lv):
    score.decrease()
    game_map.set_up(lv)

    ghosts = []
    num_ghost = create_ghosts(ghosts, game_map)

    while not pac_man.game_over:
        game_map.show(screen, lv)
        score.show(screen, lv)
        pac_man.show(screen)
        invalid_pos = []

        for i in range(num_ghost):
            ghosts[i].show(screen)
            if ghosts[i].is_hit_pac_man(pac_man.pos):
                for j in range(num_ghost):
                    ghosts[j].show(screen)
                pygame.display.update()
                pygame.time.delay(500)
                display_result(False)
                sys.exit()
            ghosts[i].wander_around(game_map)
            if ghosts[i].pos == pac_man.pos:
                invalid_pos.append(ghosts[i].prev_pos)
        game_map.show_blind_pos(screen, pac_man.pos)

        # next_move = pac_man.ids(game_map, int(game_map.size[0] * game_map.size[1] / 2), invalid_pos)
        next_move = pac_man.bfs(game_map, invalid_pos)

        pac_man.move(game_map, score, next_move)

        FPS.tick(5)
        pygame.display.update()

    game_map.show(screen, lv)
    for i in range(num_ghost):
        ghosts[i].show(screen)
    pac_man.show(screen)
    score.show(screen, lv)
    FPS.tick(5)
    pygame.display.update()
    pygame.time.delay(500)
    display_result(True)
    sys.exit()


def level_4(lv):
    game_map.set_up(lv)

    ghosts = []
    num_ghost = create_ghosts(ghosts, game_map)

    while not pac_man.game_over:
        game_map.show(screen, lv)
        score.show(screen, lv)
        pac_man.show(screen)
        invalid_pos = []

        for i in range(num_ghost):
            ghosts[i].show(screen)
            if ghosts[i].is_hit_pac_man(pac_man.pos):
                for j in range(num_ghost):
                    ghosts[j].show(screen)
                pygame.display.update()
                pygame.time.delay(500)
                display_result(False)
                pygame.display.update()
                sys.exit()
            next_pos = ghosts[i].chase_pac_man(game_map, pac_man.pos)
            ghosts[i].move(game_map, next_pos)
            if ghosts[i].pos == pac_man.pos:
                invalid_pos.append(ghosts[i].prev_pos)

        next_move = pac_man.ids(game_map, int(game_map.size[0] * game_map.size[1] / 2), invalid_pos)

        pac_man.move(game_map, score, next_move)
        FPS.tick(5)
        pygame.display.update()

    game_map.show(screen, lv)
    for i in range(num_ghost):
        ghosts[i].show(screen)
    pac_man.show(screen)
    score.show(screen, lv)
    FPS.tick(5)
    pygame.display.update()
    pygame.time.delay(500)
    display_result(True)
    sys.exit()


# ==================================== MAIN ==================================
maps = [['map1_1.txt', 'map1_2.txt', 'map1_3.txt', 'map1_4.txt', 'map1_5.txt'],
        ['map2_1.txt', 'map2_2.txt', 'map2_3.txt', 'map2_4.txt', 'map2_5.txt'],
        ['map3_1.txt', 'map3_2.txt', 'map3_3.txt', 'map3_4.txt', 'map3_5.txt'],
        ['map4_1.txt', 'map4_2.txt', 'map4_3.txt', 'map4_4.txt', 'map4_5.txt']]

_level = [0]
_map = [0]
_quit = [0]

create_menu_level()

# while _quit[0] is False:

game_map = Map()
pac_man = PacMan()
score = Score()

input_map('map/' + maps[_level[0] - 1][_map[0] - 1])

width = game_map.size[1]*TILE
height = game_map.size[0]*TILE
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Pac man')
FPS = pygame.time.Clock()
text_font = pygame.font.SysFont('Helvetica', 20, True)

map_image = pygame.image.load('image/map.png')
blind_image = pygame.image.load('image/blind.png')
pac_icon = pygame.image.load('image/iconpacman.png')
nothing_img = pac_img = pygame.image.load('image/nothing.png')
pac_img = pygame.image.load('image/pacmanclose.png')
pac_up_img = pygame.image.load('image/pacman_up.png')
pac_down_img = pygame.image.load('image/pacman_down.png')
pac_left_img = pygame.image.load('image/pacman_left.png')
pac_right_img = pygame.image.load('image/pacman_right.png')
wall_img = pygame.image.load('image/wall.png')
ghost_img = pygame.image.load('image/blueghost.png')
coin_image = pygame.image.load('image/coin.png')
win_image = pygame.image.load('image/win.png')
game_over_image = pygame.image.load('image/gameover.png')

pygame.Surface([TILE, TILE])
pygame.display.set_icon(pac_icon)

if _level[0] == 3:
    level_3(_level[0])
elif _level[0] == 4:
    level_4(_level[0])
else:
    level_1_2(_level[0])

    # create_menu_level()
