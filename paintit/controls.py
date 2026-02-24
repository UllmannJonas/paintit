import pygame


def move_player(player_pos: pygame.Vector2, dt: float):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos.y -= 200 * dt
    if keys[pygame.K_s]:
        player_pos.y += 200 * dt
    if keys[pygame.K_a]:
        player_pos.x -= 200 * dt
    if keys[pygame.K_d]:
        player_pos.x += 200 * dt


def wall_collision(player_pos: pygame.Vector2, wall: pygame.Rect):
    ...
