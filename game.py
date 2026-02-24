import pygame as pg

# from paintit import controls


WIDTH = 720
HEIGHT = 480
BRUSH_RADIUS = 20
BRUSH_SPEED = 100


class Brush:
    def __init__(self, brush_image, start_pos, color):
        self.color = color
        self.radius = BRUSH_RADIUS
        self.brush = brush_image
        self.speed = BRUSH_SPEED
        self.pos = start_pos

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


def main():
    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    dt = 0
    background = pg.image.load("pics/wooden_floor.jpg").convert()
    background = pg.transform.scale(background, (WIDTH, HEIGHT))

    screen.blit(background, (0, 0))
    # give each player their own start position so they don't share the same Vector2
    p1_start = pg.Vector2(WIDTH / 2 - 40, HEIGHT / 2)
    p2_start = pg.Vector2(WIDTH / 2 + 40, HEIGHT / 2)
    # create a circular brush surface (no external file needed)
    brush_size = BRUSH_RADIUS * 2
    p1_image = pg.Surface((brush_size, brush_size), pg.SRCALPHA)
    pg.draw.circle(p1_image, pg.Color("orange"), (BRUSH_RADIUS, BRUSH_RADIUS), BRUSH_RADIUS)
    p1 = Brush(p1_image, p1_start, "orange")
    p2_image = pg.Surface((brush_size, brush_size), pg.SRCALPHA)
    pg.draw.circle(p2_image, pg.Color("blue"), (BRUSH_RADIUS, BRUSH_RADIUS), BRUSH_RADIUS)
    p2 = Brush(p2_image, p2_start, "blue")

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
        draw_pos = (p1.pos.x - p1.brush.get_width() / 2, p1.pos.y - p1.brush.get_height() / 2)
        screen.blit(p1.brush, draw_pos)
        draw_pos = (p2.pos.x - p2.brush.get_width() / 2, p2.pos.y - p2.brush.get_height() / 2)
        screen.blit(p2.brush, draw_pos)
        dt = clock.tick(60) / 1000
        pg.display.update()


if __name__ == "__main__":
    main()
    pg.quit()
