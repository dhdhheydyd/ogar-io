from math import hypot
from socket import socket, AF_INET, SOCK_STREAM
from pygame import *
from threading import Thread
from random import randint
from launcher import ConnectWindow

win = ConnectWindow()
win.mainloop()

name = win.name
port = win.port
host = win.host
sock = socket(AF_INET, SOCK_STREAM)
sock.connect((host, port))
my_data = list(map(int, sock.recv(64).decode().strip().split(',')))
my_id = my_data[0]
sock.setblocking(False)
my_player = [randint(-1000, 1000), randint(-1000, 1000), 20]

init()
window = display.set_mode((1000, 1000))
clock = time.Clock()
f = font.Font(None, 50)
all_players = []
running = True
lose = False

# Межі карти
MAP_LIMIT = 2000


def receive_data():
    global all_players, running, lose
    while running:
        try:
            data = sock.recv(4096).decode().strip()
            if data == "LOSE":
                lose = True
            elif data:
                parts = data.strip('|').split('|')
                all_players = [list(map(int, p.split(',')[:4])) + [p.split(',')[4]] for p in parts if
                               len(p.split(',')) == 5]
                print(all_players)
        except:
            pass


Thread(target=receive_data, daemon=True).start()


class Eat:
    def __init__(self, x, y, r, c):
        self.x = x
        self.y = y
        self.radius = r
        self.color = c

    def check_collision(self, player_x, player_y, player_r):
        dx = self.x - player_x
        dy = self.y - player_y
        return hypot(dx, dy) <= self.radius + player_r


def spawn_eat():
    return Eat(randint(-MAP_LIMIT, MAP_LIMIT), randint(-MAP_LIMIT, MAP_LIMIT), 10,
               (randint(0, 255), randint(0, 255), randint(0, 255)))


eats = [spawn_eat() for _ in range(300)]
name_font = font.Font(None, 20)

while running:
    for e in event.get():
        if e.type == QUIT:
            running = False

    window.fill((0, 0, 0))
    scale = max(0.3, min(50 / my_player[2], 1.5))

    # Малюємо червону рамку країв карти
    border_left = int((-MAP_LIMIT - my_player[0]) * scale + 500)
    border_top = int((-MAP_LIMIT - my_player[1]) * scale + 500)
    border_size = int((MAP_LIMIT * 2) * scale)
    draw.rect(window, (255, 0, 0), (border_left, border_top, border_size, border_size), 5)

    for p in all_players:
        if p[0] == my_id:
            continue
        sx = int((p[1] - my_player[0]) * scale + 500)
        sy = int((p[2] - my_player[1]) * scale + 500)
        draw.circle(window, (255, 0, 0), (sx, sy), int(p[3] * scale))
        name_text = name_font.render(f'{p[4]}', 1, (255, 255, 255))
        window.blit(name_text, (sx, sy))

    draw.circle(window, (0, 255, 0), (500, 500), int(my_player[2] * scale))

    to_remove = []
    for eat in eats:
        if eat.check_collision(my_player[0], my_player[1], my_player[2]):
            to_remove.append(eat)
            my_player[2] += int(eat.radius * 0.2)
        else:
            sx = int((eat.x - my_player[0]) * scale + 500)
            sy = int((eat.y - my_player[1]) * scale + 500)
            draw.circle(window, eat.color, (sx, sy), int(eat.radius * scale))

    for eat in to_remove:
        eats.remove(eat)
        eats.append(spawn_eat())

    if lose:
        t = f.render('здох!', 1, (244, 0, 0))
        window.blit(t, (400, 500))

    display.update()
    clock.tick(60)

    if not lose:
        keys = key.get_pressed()
        # Керування на WASD або стрілочки
        if keys[K_w] or keys[K_UP]:
            my_player[1] -= 15
        if keys[K_s] or keys[K_DOWN]:
            my_player[1] += 15
        if keys[K_a] or keys[K_LEFT]:
            my_player[0] -= 15
        if keys[K_d] or keys[K_RIGHT]:
            my_player[0] += 15

        # Обмеження, щоб гравець не виходив за краї карти
        my_player[0] = max(-MAP_LIMIT, min(MAP_LIMIT, my_player[0]))
        my_player[1] = max(-MAP_LIMIT, min(MAP_LIMIT, my_player[1]))

        try:
            msg = f"{my_id},{my_player[0]},{my_player[1]},{my_player[2]},{name}"
            sock.send(msg.encode())
        except:
            pass

quit()

