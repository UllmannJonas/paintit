from dataclasses import dataclass, field

import pygame as pg

# from paintit import controls


WIDTH = 720
HEIGHT = 480
BRUSH_RADIUS = 20
BRUSH_SPEED = 100
BRUSH_COLORS = [pg.Color("darkorange2"), pg.Color("darkorchid3")]
PATH_COLORS = [pg.Color("orange"), pg.Color("orchid")]
START_POS = [
    pg.Vector2(WIDTH * 0.2, HEIGHT * 0.5),
    pg.Vector2(WIDTH * 0.8, HEIGHT * 0.5)
]


@dataclass
class Path:
    color: pg.Color
    area: pg.Surface
    locations: list[pg.Vector2] = field(default_factory=list)


class Brush:
    def __init__(self, player_number: int = 1):
        if player_number > self.max_players():
            raise ValueError(f"Max players: {self.max_players()}")
        if player_number not in [1, 2]:
            raise ValueError("Player number must be 1 or 2")
        
        self.n = player_number
        self.radius = BRUSH_RADIUS
        self.speed = BRUSH_SPEED
        self.color: pg.Color = BRUSH_COLORS[player_number - 1]
        self.pos: pg.Vector2 = START_POS[player_number - 1]
        self.head = self._init_head()
        self.path = self._init_path()
        
    @property
    def diameter(self):
        return self.radius * 2

    def max_players(self):
        return 2

    def _init_head(self):
        head = pg.Surface((self.diameter, self.diameter), pg.SRCALPHA)
        pg.draw.circle(head, self.color, (self.radius, self.radius), self.radius)
        return head
    
    def _init_path(self):
        area = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        color = PATH_COLORS[BRUSH_COLORS.index(self.color)]
        return Path(color=color, area=area)
    
    @property
    def corner0(self):
        return (self.pos.x - self.radius, self.pos.y - self.radius)

    def move(self, dt, up=False, down=False, left=False, right=False):
        if up:
            self.pos.y -= self.speed * dt
        if down:
            self.pos.y += self.speed * dt
        if left:
            self.pos.x -= self.speed * dt
        if right:
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

    def _log_path(self):
        self.path.locations.append(self.pos.copy())

    def draw_path(self, screen: pg.Surface):
        # record current position and draw a circle onto the persistent path surface
        self._log_path()

        pg.draw.circle(self.path.area, self.path.color, self.pos, self.radius)
        # blit the accumulated path onto the main screen
        screen.blit(self.path.area, (0, 0))


def player_move(player: Brush, dt) -> tuple[float, float]:
    keys = pg.key.get_pressed()
    match player.n:
        case 1:
            if keys[pg.K_UP]:
                player.move(dt, up=True)
            if keys[pg.K_DOWN]:
                player.move(dt, down=True)
            if keys[pg.K_LEFT]:
                player.move(dt, left=True)
            if keys[pg.K_RIGHT]:
                player.move(dt, right=True)
        case 2:
            if keys[pg.K_w]:
                player.move(dt, up=True)
            if keys[pg.K_s]:
                player.move(dt, down=True)
            if keys[pg.K_a]:
                player.move(dt, left=True)
            if keys[pg.K_d]:
                player.move(dt, right=True)

    return player.corner0


def main():
    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    dt = 0
    background = pg.image.load("pics/wooden_floor.jpg").convert()
    background = pg.transform.scale(background, (WIDTH, HEIGHT))

    screen.blit(background, (0, 0))
    # give each player their own start position so they don't share the same Vector2
    p1 = Brush(player_number=1)
    p2 = Brush(player_number=2)

    pg.display.set_caption("Paint It!")

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return

        p1_location = player_move(p1, dt)
        p2_location = player_move(p2, dt)

        screen.blit(background, (0, 0))

        p2.draw_path(screen)
        p1.draw_path(screen)
        screen.blit(p1.head, p1_location)
        screen.blit(p2.head, p2_location)
        

        dt = clock.tick(60) / 1000
        pg.display.update()


if __name__ == "__main__":
    main()
    pg.quit()
