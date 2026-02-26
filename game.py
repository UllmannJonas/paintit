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
    pg.Vector2(WIDTH * 0.8, HEIGHT * 0.5),
    pg.Vector2(WIDTH * 0.2, HEIGHT * 0.5)
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
        return (int(self.pos.x - self.radius), int(self.pos.y - self.radius))

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

    def draw_path(self, screen: pg.Surface, player_surfaces: list[pg.Surface] = None):
        # record current position and draw a circle onto the persistent path surface
        self._log_path()

        pg.draw.circle(self.path.area, self.path.color, self.pos, self.radius)

        if self.n == 1:
            other_player_surface = player_surfaces[1]
        else:
            other_player_surface = player_surfaces[0]
        if self._overlap_with_path(other_player_surface):
            self._blit_brush_head_on_path(other_player_surface)
        
        # blit the accumulated path onto the main screen
        screen.blit(self.path.area, (0, 0))

    def _overlap_with_path(self, other_player_surface: pg.Surface) -> bool:
        own_path_mask = pg.mask.from_surface(self.path.area)
        other_path_mask = pg.mask.from_surface(other_player_surface)

        overlap = own_path_mask.overlap(other_path_mask, offset=(0, 0))
        return overlap is not None
    
    def _blit_brush_head_on_path(self, other_player_surface: pg.Surface):
        other_player_surface.blit(self.path.area, (0, 0))


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

        player_surface_list = [p1.path.area, p2.path.area]
        p1.draw_path(screen, player_surfaces=player_surface_list)
        p2.draw_path(screen, player_surfaces=player_surface_list)
        
        screen.blit(p1.head, p1_location)
        screen.blit(p2.head, p2_location)
        

        dt = clock.tick(60) / 1000
        pg.display.update()


if __name__ == "__main__":
    main()
    pg.quit()


def calculate_paint_percentage(player_path_area: pg.Surface) -> float:
    # Create a mask from the player's path surface
    path_mask = pg.mask.from_surface(player_path_area)

    # Count the number of non-transparent (painted) pixels
    painted_pixels = path_mask.count()

    # Calculate the total screen area
    total_screen_area = WIDTH * HEIGHT

    # Calculate the percentage of the screen covered by the player's path
    percentage = (painted_pixels / total_screen_area) * 100
    return percentage


def calculate_winner(p1: Brush, p2: Brush) -> int:
    # Get the paint percentages for both players
    p1_percentage = calculate_paint_percentage(p1.path.area)
    p2_percentage = calculate_paint_percentage(p2.path.area)

    # Print the percentage for both players (for debugging or display)
    print(f"Player 1 painted {p1_percentage:.2f}% of the screen.")
    print(f"Player 2 painted {p2_percentage:.2f}% of the screen.")

    # Determine the winner based on the highest percentage
    if p1_percentage > p2_percentage:
        return 1  # Player 1 wins
    elif p2_percentage > p1_percentage:
        return 2  # Player 2 wins
    else:
        return 0  # Tie (both painted the same percentage)
