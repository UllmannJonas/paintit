import pygame as pg

# from paintit import controls


WIDTH = 720
HEIGHT = 480
BRUSH_RADIUS = 20
BRUSH_SPEED = 100


class Brush:
    def __init__(self, player_number: int = 1):
        self.radius = BRUSH_RADIUS
        self.speed = BRUSH_SPEED
        self.brush = self._init_player_defaults(player_number)
        self.path_locations = []
        
    @property
    def diameter(self):
        return self.radius * 2

    def max_players(self):
        return 2

    def _init_player_defaults(self, player_number):

        if player_number > self.max_players():
            raise ValueError(f"Max players: {self.max_players()}")
        if player_number not in [1, 2]:
            raise ValueError("Player number must be 1 or 2")
        
        colors = ["orange", "blue"]
        start_positions = [
            pg.Vector2(WIDTH * 0.2, HEIGHT * 0.5),
            pg.Vector2(WIDTH * 0.8, HEIGHT * 0.5)
        ]
        self.color = colors[player_number - 1]
        self.pos = start_positions[player_number - 1]
        brush = pg.Surface((self.diameter, self.diameter), pg.SRCALPHA)
        pg.draw.circle(brush, pg.Color(self.color), (self.radius, self.radius), self.radius)
        return brush

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

    def _trace_path(self):
        self.path_locations.append(self.pos.copy())

    def draw_path(self, screen: pg.Surface):
        self._trace_path()
        for pos in self.path_locations:
            draw_pos = (pos.x - self.radius, pos.y - self.radius)
            screen.blit(self.brush, draw_pos)


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
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            p1.move(dt, up=True)
        if keys[pg.K_DOWN]:
            p1.move(dt, down=True)
        if keys[pg.K_LEFT]:
            p1.move(dt, left=True)
        if keys[pg.K_RIGHT]:
            p1.move(dt, right=True)

        if keys[pg.K_w]:
            p2.move(dt, up=True)
        if keys[pg.K_s]:
            p2.move(dt, down=True)
        if keys[pg.K_a]:
            p2.move(dt, left=True)
        if keys[pg.K_d]:
            p2.move(dt, right=True)
        
        screen.blit(background, (0, 0))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        draw_p1 = (p1.pos.x - p1.brush.get_width() / 2, p1.pos.y - p1.brush.get_height() / 2)
        draw_p2 = (p2.pos.x - p2.brush.get_width() / 2, p2.pos.y - p2.brush.get_height() / 2)

        screen.blit(p1.brush, draw_p1)
        p1.draw_path(screen)
        screen.blit(p2.brush, draw_p2)
        p2.draw_path(screen)

        dt = clock.tick(60) / 1000
        pg.display.update()


if __name__ == "__main__":
    main()
    pg.quit()
