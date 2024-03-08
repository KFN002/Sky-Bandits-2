from game_objects.game_objects import Player, EnemyBase, AARocket, Decorations, Background
from settings import sc_size as size, height, width
import pygame
import random


def play(plane_data, player_data):
    pygame.init()
    k_spawn = 0
    k_spawn_aa = 0
    k_spawn_decs = 0
    score = 0

    screen = pygame.display.set_mode(size)
    img_path = random.choice(['data/backgrounds/jungles.png',
                              'data/backgrounds/forest.png',
                              'data/backgrounds/mountains.png'])
    font = pygame.font.Font('data/fonts/font.ttf', 30)

    enemies = pygame.sprite.Group()
    players = pygame.sprite.Group()
    decorations = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    enemy_aa = pygame.sprite.Group()

    background = Background(img_path, plane_data[3])
    player = Player(plane_data)
    players.add(player)

    running = True
    fps = 60

    clock = pygame.time.Clock()

    while running:
        key_pressed = pygame.key.get_pressed()

        if key_pressed[pygame.K_w] or key_pressed[pygame.K_UP]:
            player.move_up()

        if key_pressed[pygame.K_s] or key_pressed[pygame.K_DOWN]:
            player.move_down(height)

        if key_pressed[pygame.K_a] or key_pressed[pygame.K_LEFT]:
            player.move_left()

        if key_pressed[pygame.K_d] or key_pressed[pygame.K_RIGHT]:
            player.move_right(width)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    player.drop_bomb(bombs)

            if event.type == pygame.QUIT:
                running = False

        enemy_base = EnemyBase(plane_data[3], [random.randint(0, width - 150), 0])
        if enemy_base.check_collision(enemies) and k_spawn == 50 and enemy_base.check_collision(decorations):
            enemies.add(enemy_base)

        decor = Decorations(plane_data[3], *[random.randint(0, width - 150), 0])
        if decor.check_collision(decorations) and k_spawn_decs == 30 and decor.check_collision(enemies):
            decorations.add(decor)

        if k_spawn_aa == 150:
            aa = AARocket(plane_data[12], player.rect.x + 25, height)
            enemy_aa.add(aa)
            aa.chase()

        for rocket in enemy_aa:
            rocket.move(-1)
            rocket.update_animation(enemy_aa)
            if not rocket.check_collision(players) and not rocket.destroyed:
                rocket.exploded()
                player.hit()

        for dec in decorations:
            dec.move()
            dec.update(bombs)

        for enemy in enemies:
            enemy.move()
            if enemy.bombed(bombs):
                score += 1
                player.add_bombs()
            enemy.update_animation(enemies)

        for bmb in bombs:
            bmb.update(bombs)

        for gamer in players:
            gamer.update(players, player_data, plane_data, score)

        score_text = font.render(f'Score: {score}', True, (255, 255, 255))
        bomb_text = font.render(f'Bombs: {player.bombs}', True, (255, 255, 255))
        health_text = font.render(f'Health: {player.hits}', True, (255, 255, 255))

        score_rect = score_text.get_rect()
        bomb_rect = bomb_text.get_rect()
        health_rect = health_text.get_rect()

        health_rect.center = (width - 100, 110)
        bomb_rect.center = (width - 100, 80)
        score_rect.center = (width - 100, 50)

        background.update()
        background.render(screen)

        decorations.draw(screen)
        enemies.draw(screen)
        enemy_aa.draw(screen)
        bombs.draw(screen)
        players.draw(screen)

        screen.blit(score_text, score_rect)
        screen.blit(bomb_text, bomb_rect)
        screen.blit(health_text, health_rect)

        pygame.display.flip()
        clock.tick(fps)
        k_spawn_aa = (k_spawn_aa + 1) % 151
        k_spawn = (k_spawn + 1) % 51
        k_spawn_decs = (k_spawn_decs + 1) % 31

    pygame.quit()