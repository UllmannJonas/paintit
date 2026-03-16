#region imports
import pygame as pg
import numpy as np
import os, sys
from time import time
#endregion imports

#region globals
WIDTH = 720
HEIGHT = 480
BRUSH_RADIUS = 20
BRUSH_SPEED = 150
MAX_PLAYERS = 2
BRUSH_COLORS = [
    pg.Color("darkorange2"),
    pg.Color("darkorchid3")]
PATH_COLORS = [
    pg.Color("orange"),
    pg.Color("orchid")]
ID_COLORS = [
    (1, 0, 0), # 65536 in 2D-surfarray
    (2, 0, 0)] # 131072 in 2D-surfarray
ARRAY_ID = [
    65536,
    131072
]
START_POS = [
    pg.Vector2(WIDTH * 0.8, HEIGHT * 0.5),
    pg.Vector2(WIDTH * 0.2, HEIGHT * 0.5)]

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
#endregion globals

#region player
class Brush:
    def __init__(self, player_number: int = 1):        
        self.n = player_number
        self.radius = BRUSH_RADIUS
        self.speed = BRUSH_SPEED
        self.color: pg.Color = BRUSH_COLORS[player_number - 1]
        self.pathcolor: pg.Color = PATH_COLORS[player_number - 1]
        self.id: pg.Color = pg.Color(ID_COLORS[player_number - 1])
        self.array_id: int = ARRAY_ID[player_number - 1]
        self.pos: pg.Vector2 = START_POS[player_number - 1]
        self.head = pg.Surface((self.diameter, self.diameter), pg.SRCALPHA)
        self.score: float = 0.0

    @property
    def diameter(self):
        return self.radius * 2

    @property
    def corner0(self):
        return (int(self.pos.x - self.radius), int(self.pos.y - self.radius))

    def move(self, dt):
        keys = pg.key.get_pressed()
        match self.n:
            case 1:
                if keys[pg.K_UP]:
                    self.pos.y -= self.speed * dt
                if keys[pg.K_DOWN]:
                    self.pos.y += self.speed * dt
                if keys[pg.K_LEFT]:
                    self.pos.x -= self.speed * dt
                if keys[pg.K_RIGHT]:
                    self.pos.x += self.speed * dt
            case 2:
                if keys[pg.K_w]:
                    self.pos.y -= self.speed * dt
                if keys[pg.K_s]:
                    self.pos.y += self.speed * dt
                if keys[pg.K_a]:
                    self.pos.x -= self.speed * dt
                if keys[pg.K_d]:
                    self.pos.x += self.speed * dt

        # stay inside game screen
        if self.pos.y < 0 + self.radius:
            self.pos.y = 0 + self.radius
        if self.pos.y > HEIGHT - self.radius:
            self.pos.y = HEIGHT - self.radius
        if self.pos.x < 0 + self.radius:
            self.pos.x = 0 + self.radius
        if self.pos.x > WIDTH - self.radius:
            self.pos.x = WIDTH - self.radius

    def paint(self, visual_surface: pg.Surface, score_surface: pg.Surface) -> None:
        pg.draw.circle(visual_surface, self.pathcolor, self.pos, self.radius)
        pg.draw.circle(score_surface, self.id, self.pos, self.radius)
        self._update_score(score_surface)

    def show_sprite(self) -> pg.Surface:
        self.head.fill((0, 0, 0, 0))
        pg.draw.circle(self.head, self.color, self.pos, self.radius)
        return self.head
    
    def _update_score(self, score_surface: pg.Surface) -> None:
        array = pg.surfarray.pixels2d(score_surface)
        total_px = array.size
        covered_px = np.sum(array == self.array_id)
        self.score = covered_px / total_px
# endregion player

#region init
pg.init()
running = True
pg.display.set_caption("Paint It!")

screen = pg.display.set_mode((WIDTH, HEIGHT))
visual_surf = pg.Surface((WIDTH, HEIGHT))
visual_surf.set_colorkey((0, 0, 0))
ownership = pg.Surface((WIDTH, HEIGHT))

clock = pg.time.Clock()
dt = 0

countdown_font = pg.font.Font(size=40)
score_font = pg.font.Font(size=24)
winner_font = pg.font.Font(size=100)

timelimit = 61
finish_sfx = pg.mixer.Sound(
    file=resource_path(r"assets\boxing_bell_multiple.wav")
)

background_source = pg.image.load(
    file=resource_path(r"assets\marble.jpg")
).convert()
background = pg.transform.scale(background_source, (WIDTH, HEIGHT))

p1 = Brush(player_number=1)
p2 = Brush(player_number=2)
players = [p1, p2]

t0 = time()
debug = False
#endregion init

#region game loop
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
    screen.blit(background)

    p1.move(dt)
    p2.move(dt)

    p1.paint(visual_surf, ownership)
    p2.paint(visual_surf, ownership)

    screen.blit(visual_surf)
    pg.draw.circle(screen, p1.color, p1.pos, p1.radius)
    pg.draw.circle(screen, p2.color, p2.pos, p2.radius)

    # Time ----------------------------------------------------- #
    time_left = int(timelimit - (time() - t0))
    screen.blit(countdown_font.render(str(time_left), False, "black"))

    # Score ---------------------------------------------------- #
    for p in players:
        score = f"{round(p.score * 100)}%"
        screen.blit(
            score_font.render(score, True, "black"),
            (p.pos.x - 16, p.pos.y - 8)
        )

    # Finish --------------------------------------------------- #
    if time_left < 0:
        finish_sfx.play()
        if max(p1.score, p2.score) == p1.score:
            winner_text = "Player 1 won!"
            winner = p1
        else:
            winner_text = "Player 2 won!"
            winner = p2
        endtimer = 3
        t0 = time()
        while True:
            pg.event.pump()
            pg.draw.circle(screen, winner.color, winner.pos, winner.radius)
            screen.blit(
                winner_font.render(winner_text, False, "black"),
                (WIDTH * 0.2, HEIGHT * 0.4)
            )
            winner.radius = min(winner.radius * 1.08, WIDTH * 2)
            dt = clock.tick(60) / 1000
            pg.display.update()
            if time() - t0 >= endtimer:
                running = False
                break


    # Update --------------------------------------------------- #
    dt = clock.tick(60) / 1000
    pg.display.update()

    # Debug ----------------------------------------------------- #
    if debug:
        print(p1.color)
        print(p1.head.get_flags())
        print(p1.head.get_bitsize())
        debug = False
#endregion game loop

pg.quit()
