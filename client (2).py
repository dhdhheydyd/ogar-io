from math import hypot, sin, cos, radians
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from random import randint, random, uniform

from launcher import ConnectWindow
from pygame import *


init()
sound_2 = mixer.Sound("719053__unfa__oof-original.flac")
sound_1 = mixer.Sound("592346__axilirate__collect-crystal.wav")

win = ConnectWindow()
win.mainloop()
name = win.name
port = win.port
host = win.host
my_skin = win.skin

sock = socket(AF_INET, SOCK_STREAM)
sock.connect((host, port))
my_data = list(map(int, sock.recv(64).decode().strip().split(',')))
my_id = my_data[0]
sock.setblocking(False)

my_player = [randint(-1000, 1000), randint(-1000, 1000), 20]
window = display.set_mode((1000, 1000))
clock = time.Clock()
f = font.Font(None, 50)
all_players = []
running = True
lose = False
lose_sound_played = False

mixer.music.set_volume(0.2)

# Базовые цветовые стили (индексы 0-6): (основной цвет, цвет обводки)
SKIN_STYLES = [
    ((0, 230, 118), (0, 150, 70)),     # 0: Зелений неон
    ((41, 121, 255), (0, 60, 180)),    # 1: Кібер-синій
    ((213, 0, 249), (120, 0, 150)),    # 2: Фіолетовий космос
    ((255, 215, 0), (180, 130, 0)),    # 3: Золотий злиток
    ((255, 23, 68), (140, 0, 25)),     # 4: Кривавий рубін
    ((255, 110, 0), (200, 30, 0)),     # 5: Вогняна лава
    ((0, 229, 255), (200, 250, 255)),  # 6: Крижаний кристал
]


def draw_player_skin(surface, cx, cy, radius, skin_id):
    if radius <= 0:
        return
    border_w = max(2, int(radius * 0.12))

    # Скины 0-6: классические неоновые цвета
    if skin_id < len(SKIN_STYLES):
        main_c, border_c = SKIN_STYLES[skin_id]
        draw.circle(surface, main_c, (cx, cy), radius)
        draw.circle(surface, border_c, (cx, cy), radius, border_w)

    # Скин 7: Токсичный мутант
    elif skin_id == 7:
        draw.circle(surface, (170, 255, 0), (cx, cy), radius)
        draw.circle(surface, (20, 20, 20), (cx, cy), int(radius * 0.55), border_w)
        draw.circle(surface, (20, 20, 20), (cx, cy), int(radius * 0.2))
        draw.circle(surface, (50, 120, 0), (cx, cy), radius, border_w)

    # Скин 8: Мишень
    elif skin_id == 8:
        draw.circle(surface, (255, 255, 255), (cx, cy), radius)
        draw.circle(surface, (230, 0, 0), (cx, cy), int(radius * 0.7))
        draw.circle(surface, (255, 255, 255), (cx, cy), int(radius * 0.45))
        draw.circle(surface, (230, 0, 0), (cx, cy), int(radius * 0.2))


    elif skin_id == 9:
        draw.circle(surface, (240, 240, 240), (cx, cy), radius)
        draw.circle(surface, (20, 20, 20), (cx, cy), int(radius * 0.5))
        draw.circle(surface, (240, 240, 240), (cx, cy), int(radius * 0.2))
        draw.circle(surface, (100, 100, 100), (cx, cy), radius, border_w)


    elif skin_id == 10:
        draw.circle(surface, (240, 65, 80), (cx, cy), radius)
        draw.circle(surface, (20, 130, 40), (cx, cy), radius, border_w)
        seed_r = max(1, int(radius * 0.08))
        for ox, oy in [(-0.3, -0.2), (0.3, -0.2), (0, 0.3), (-0.25, 0.2), (0.25, 0.2)]:
            draw.circle(surface, (20, 20, 20), (int(cx + radius * ox), int(cy + radius * oy)), seed_r)






# Межі карти, радіуси та налаштування зірки
MAP_LIMIT = 2000
MAX_RADIUS = 250
EAT_RADIUS = 10
STAR_RADIUS = EAT_RADIUS * 3
SPARK_COLOR = (255, 255, 255)
BASE_SPEED = 15
SPEED_MULTIPLIER = 2.24
STAR_SPAWN_INTERVAL = 125_000  # 125 секунд
BOOST_DURATION = 10_000        # 10 секунд

star_pos = [randint(-MAP_LIMIT, MAP_LIMIT), randint(-MAP_LIMIT, MAP_LIMIT)]
last_star_spawn = time.get_ticks()
boost_end_time = 0

# Одноразова суперсила-щит: 100% при спавні та 50% від зірки
STAR_SHIELD_CHANCE = 0.50
SHIELD_DURATION = 10_000       # 10 секунд невразливості
has_shield = True              # 100% шанс при старті гри
shield_end_time = 0


class Particle:
    def __init__(self, x, y, color=SPARK_COLOR):
        self.x = x
        self.y = y
        self.vx = uniform(-3, 3)
        self.vy = uniform(-3, 3)
        self.life = 255
        self.size = randint(3, 6)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 7

    def draw(self, surface):
        if self.life > 0:
            p_surf = Surface((self.size * 2, self.size * 2), SRCALPHA)
            draw.circle(p_surf, (*self.color, self.life), (self.size, self.size), self.size)
            surface.blit(p_surf, (self.x - self.size, self.y - self.size))


particles = []


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
                    list(map(int, p.split(',')[:4])) + [p.split(',')[4]]
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
        elif e.type == KEYDOWN and e.key == K_f:
            if has_shield and not lose:
                has_shield = False
                shield_end_time = now + SHIELD_DURATION

    if star_pos is None and now - last_star_spawn >= STAR_SPAWN_INTERVAL:
        star_pos = [randint(-MAP_LIMIT, MAP_LIMIT), randint(-MAP_LIMIT, MAP_LIMIT)]
        last_star_spawn = now

    window.fill((0, 0, 0))
    scale = max(0.3, min(50 / my_player[2], 1.5))

    # Малюємо червону рамку країв карти
    border_left = int((-MAP_LIMIT - my_player[0]) * scale + 500)
    border_top = int((-MAP_LIMIT - my_player[1]) * scale + 500)
    border_size = int((MAP_LIMIT * 2) * scale)
    draw.rect(window, (255, 0, 0), (border_left, border_top, border_size, border_size), 5)

    # Малюємо та перевіряємо підбір зірки
    if star_pos is not None:
        if hypot(star_pos[0] - my_player[0], star_pos[1] - my_player[1]) <= STAR_RADIUS + my_player[2]:
            boost_end_time = now + BOOST_DURATION
            star_pos = None
            last_star_spawn = now
            if random() < STAR_SHIELD_CHANCE:
                has_shield = True
        else:
            sx = int((star_pos[0] - my_player[0]) * scale + 500)
            sy = int((star_pos[1] - my_player[1]) * scale + 500)
            draw_star(window, (255, 215, 0), sx, sy, int(STAR_RADIUS * scale))

    # Отрисовка других игроков с их скинами
    for p in all_players:
        if p[0] == my_id:
            continue
        sx = int((p[1] - my_player[0]) * scale + 500)
        sy = int((p[2] - my_player[1]) * scale + 500)

        # Разбираем строку "Имя:НомерСкина"
        raw_name = p[4]
        if ':' in raw_name:
            p_name, p_skin = raw_name.rsplit(':', 1)
            p_skin = int(p_skin) if p_skin.isdigit() else 0
        else:
            p_name, p_skin = raw_name, 0

        draw_player_skin(window, sx, sy, int(p[3] * scale), p_skin)
        name_text = name_font.render(f'{p_name}', 1, (255, 255, 255))
        window.blit(name_text, (sx - name_text.get_width() // 2, sy - int(p[3] * scale) - 18))

    is_boosted = now < boost_end_time
    is_shielded = now < shield_end_time

    # Отрисовка своего игрока с выбранным скином
    my_r_scaled = int(my_player[2] * scale)
    draw_player_skin(window, 500, 500, my_r_scaled, my_skin)

    if is_boosted:
        draw.circle(window, (255, 215, 0), (500, 500), my_r_scaled + 4, 3)
    if is_shielded:
        draw.circle(window, (0, 191, 255), (500, 500), my_r_scaled + 9, 4)

    to_remove = []
    for eat in eats:
        if eat.check_collision(my_player[0], my_player[1], my_player[2]):
            to_remove.append(eat)
            my_player[2] = min(MAX_RADIUS, my_player[2] + int(eat.radius * 0.2))
            sound_1.play()

            sx = int((eat.x - my_player[0]) * scale + 500)
            sy = int((eat.y - my_player[1]) * scale + 500)

            for _ in range(20):
                particles.append(Particle(sx, sy, eat.color))
        else:
            sx = int((eat.x - my_player[0]) * scale + 500)
            sy = int((eat.y - my_player[1]) * scale + 500)
            draw.circle(window, eat.color, (sx, sy), int(eat.radius * scale))

    for eat in to_remove:
        eats.remove(eat)
        eats.append(spawn_eat())

    for p in particles[:]:
        p.update()
        p.draw(window)
        if p.life <= 0:
            particles.remove(p)

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
        if not lose_sound_played:
            sound_2.play()
            lose_sound_played = True

    display.update()
    clock.tick(60)

    if not lose:
        current_speed = BASE_SPEED * SPEED_MULTIPLIER if is_boosted else BASE_SPEED
        keys = key.get_pressed()
        if keys[K_w] or keys[K_UP]:
            my_player[1] -= current_speed
        if keys[K_s] or keys[K_DOWN]:
            my_player[1] += current_speed
        if keys[K_a] or keys[K_LEFT]:
            my_player[0] -= current_speed
        if keys[K_d] or keys[K_RIGHT]:
            my_player[0] += current_speed

        my_player[0] = max(-MAP_LIMIT, min(MAP_LIMIT, my_player[0]))
        my_player[1] = max(-MAP_LIMIT, min(MAP_LIMIT, my_player[1]))
        try:
            msg = f"{my_id},{int(my_player[0])},{int(my_player[1])},{my_player[2]},{name}:{my_skin}"
            sock.send(msg.encode())
        except:
            pass
quit()




