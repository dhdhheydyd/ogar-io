from math import hypot, sin, cos, radians
from socket import socket, AF_INET, SOCK_STREAM
from pygame import *
from threading import Thread
from random import randint, random
from launcher import ConnectWindow

win = ConnectWindow()
win.mainloop()
name = win.name
port = win.port
host = win.host

sock = socket(AF_INET, SOCK_STREAM)
sock.connect((host, port))
my_data = list(map(int, sock.recv(64).decode().strip().split(',')))
my_id = my_data
sock.setblocking(False)

my_player = [randint(-1000, 1000), randint(-1000, 1000), 20]
init()
window = display.set_mode((1000, 1000))
clock = time.Clock()
f = font.Font(None, 50)
all_players = []
running = True
lose = False

# Межі карти, радіуси та налаштування зірки
MAP_LIMIT = 2000
MAX_RADIUS = 250
EAT_RADIUS = 10
STAR_RADIUS = EAT_RADIUS * 3

BASE_SPEED = 15
SPEED_MULTIPLIER = 2.24
STAR_SPAWN_INTERVAL = 125_000  # 125 секунд
BOOST_DURATION = 10_000        # 10 секунд

star_pos = [randint(-MAP_LIMIT, MAP_LIMIT), randint(-MAP_LIMIT, MAP_LIMIT)]
last_star_spawn = time.get_ticks()
boost_end_time = 0

# Одноразова суперсила-щит: 100% при спавні та 50/50 (щит або швидкість) від зірки
STAR_SHIELD_CHANCE = 0.50
SHIELD_DURATION = 10_000       # 10 секунд невразливості
has_shield = True              # 100% шанс при старті гри
shield_end_time = 0


def receive_data():
    global all_players, running, lose
    while running:
        try:
            data = sock.recv(4096).decode().strip()
            if data == "LOSE":
                if time.get_ticks() >= shield_end_time:
                    lose = True
            elif data:
                parts = data.strip('|').split('|')
                all_players = [
                    list(map(int, p.split(',')[:4])) + [p.split(',')]
                    for p in parts if len(p.split(',')) == 5
                ]
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
    return Eat(
        randint(-MAP_LIMIT, MAP_LIMIT),
        randint(-MAP_LIMIT, MAP_LIMIT),
        EAT_RADIUS,
        (randint(0, 255), randint(0, 255), randint(0, 255))
    )


def draw_star(surface, color, cx, cy, outer_r):
    points = []
    inner_r = outer_r * 0.45
    for i in range(10):
        angle = radians(i * 36 - 90)
        r = outer_r if i % 2 == 0 else inner_r
        points.append((cx + r * cos(angle), cy + r * sin(angle)))
    draw.polygon(surface, color, points)


eats = [spawn_eat() for _ in range(300)]
name_font = font.Font(None, 20)

while running:
    now = time.get_ticks()

    for e in event.get():
        if e.type == QUIT:
            running = False
        # Активація одноразового щита на клавішу F
        elif e.type == KEYDOWN and e.key == K_f:
            if has_shield and not lose:
                has_shield = False
                shield_end_time = now + SHIELD_DURATION

    if star_pos is None and now - last_star_spawn >= STAR_SPAWN_INTERVAL:
        star_pos = [randint(-MAP_LIMIT, MAP_LIMIT), randint(-MAP_LIMIT, MAP_LIMIT)]
        last_star_spawn = now

    window.fill((0, 0, 0))
    scale = max(0.3, min(50 / my_player, 1.5))

    # Малюємо червону рамку країв карти
    border_left = int((-MAP_LIMIT - my_player) * scale + 500)
    border_top = int((-MAP_LIMIT - my_player) * scale + 500)
    border_size = int((MAP_LIMIT * 2) * scale)
    draw.rect(window, (255, 0, 0), (border_left, border_top, border_size, border_size), 5)

    # Малюємо та перевіряємо підбір зірки: 50% щит АБО 50% швидкість x2.24
    if star_pos is not None:
        if hypot(star_pos - my_player, star_pos - my_player) <= STAR_RADIUS + my_player:
            star_pos = None
            last_star_spawn = now
            if random() < STAR_SHIELD_CHANCE:
                has_shield = True
            else:
                boost_end_time = now + BOOST_DURATION
        else:
            sx = int((star_pos - my_player) * scale + 500)
            sy = int((star_pos - my_player) * scale + 500)
            draw_star(window, (255, 215, 0), sx, sy, int(STAR_RADIUS * scale))

    for p in all_players:
        if p == my_id:
            continue
        sx = int((p - my_player) * scale + 500)
        sy = int((p - my_player) * scale + 500)
        draw.circle(window, (255, 0, 0), (sx, sy), int(p * scale))
        name_text = name_font.render(f'{p}', 1, (255, 255, 255))
        window.blit(name_text, (sx, sy))

    is_boosted = now < boost_end_time
    is_shielded = now < shield_end_time

    draw.circle(window, (0, 255, 0), (500, 500), int(my_player * scale))
    if is_boosted:
        draw.circle(window, (255, 215, 0), (500, 500), int(my_player * scale) + 4, 3)
    if is_shielded:
        draw.circle(window, (0, 191, 255), (500, 500), int(my_player * scale) + 9, 4)

    to_remove = []
    for eat in eats:
        if eat.check_collision(my_player, my_player, my_player):
            to_remove.append(eat)
            my_player = min(MAX_RADIUS, my_player + int(eat.radius * 0.2))
        else:
            sx = int((eat.x - my_player) * scale + 500)
            sy = int((eat.y - my_player) * scale + 500)
            draw.circle(window, eat.color, (sx, sy), int(eat.radius * scale))

    for eat in to_remove:
        eats.remove(eat)
        eats.append(spawn_eat())

    # HUD-підказки в лівому верхньому кутку
    hud_y = 15
    if is_boosted:
        rem = (boost_end_time - now) / 1000
        hud = name_font.render(f'Прискорення x2.24: {rem:.1f} с', 1, (255, 215, 0))
        window.blit(hud, (15, hud_y))
        hud_y += 25
    elif star_pos is not None:
        hud = name_font.render('Зірка на карті!', 1, (255, 215, 0))
        window.blit(hud, (15, hud_y))
        hud_y += 25

    if is_shielded:
        rem_s = (shield_end_time - now) / 1000
        hud_s = name_font.render(f'Щит (не можна з\'їсти): {rem_s:.1f} с', 1, (0, 191, 255))
        window.blit(hud_s, (15, hud_y))
    elif has_shield:
        hud_s = name_font.render('Суперсила готова: натисни [F]', 1, (0, 191, 255))
        window.blit(hud_s, (15, hud_y))

    if lose:
        t = f.render('здох!', 1, (244, 0, 0))
        window.blit(t, (400, 500))

    display.update()
    clock.tick(60)

    if not lose:
        current_speed = BASE_SPEED * SPEED_MULTIPLIER if is_boosted else BASE_SPEED
        keys = key.get_pressed()
        if keys[K_w] or keys[K_UP]:
            my_player -= current_speed
        if keys[K_s] or keys[K_DOWN]:
            my_player += current_speed
        if keys[K_a] or keys[K_LEFT]:
            my_player -= current_speed
        if keys[K_d] or keys[K_RIGHT]:
            my_player += current_speed

        my_player = max(-MAP_LIMIT, min(MAP_LIMIT, my_player))
        my_player = max(-MAP_LIMIT, min(MAP_LIMIT, my_player))

        try:
            msg = f"{my_id},{int(my_player)},{int(my_player)},{my_player},{name}"
            sock.send(msg.encode())
        except:
            pass

quit()


