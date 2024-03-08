from game_objects.game_objects import Player, Enemy, Background
from settings import sc_size as size, height, width
import pygame
import random


def play(plane_data, player_data):  # аналогично 1 уровню, но с вражескими самолетами
    pygame.init()
    k_spawn = 0
    k_shoot = 0
    score = 0

    screen = pygame.display.set_mode(size)
    img_path = random.choice(['data/backgrounds/jungles.png',
                              'data/backgrounds/forest.png',
                              'data/backgrounds/mountains.png'])
    font = pygame.font.Font('data/fonts/font.ttf', 30)

    enemies = pygame.sprite.Group()
    players = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()

    background = Background(img_path, plane_data[3])

    player = Player(plane_data)
    players.add(player)

    running = True
    screen.fill('white')
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
                    player.shoot(player_bullets)

            if event.type == pygame.QUIT:
                running = False

        enemy = Enemy([random.randint(0, width - 150), 0])
        if enemy.check_collision(enemies) and k_spawn == 70:
            enemies.add(enemy)

        for enemy in enemies:
            enemy.move()
            if k_shoot == 80:
                enemy.shoot(enemy_bullets)
            if enemy.shot(player_bullets):
                score += 1
                player.add_bullets()
            enemy.update_animation(enemies)

        for gamer in players:
            gamer.update(players, player_data, plane_data, score)
            gamer.check_collision(enemies)
            gamer.shot(enemy_bullets)

        for elem in player_bullets:
            elem.update()

        for elem in enemy_bullets:
            elem.update(-1)

        score_text = font.render(f'Score: {score}', True, (255, 255, 255))
        health_text = font.render(f'Health: {player.hits}', True, (255, 255, 255))
        bullets_text = font.render(f'Bullets: {player.bullets}', True, (255, 255, 255))

        bullets_rect = bullets_text.get_rect()
        score_rect = score_text.get_rect()
        health_rect = health_text.get_rect()

        bullets_rect.center = (width - 100, 80)
        health_rect.center = (width - 100, 110)
        score_rect.center = (width - 100, 50)

        background.update()
        background.render(screen)
        players.draw(screen)
        enemies.draw(screen)
        enemy_bullets.draw(screen)
        player_bullets.draw(screen)
        screen.blit(score_text, score_rect)
        screen.blit(bullets_text, bullets_rect)
        screen.blit(health_text, health_rect)

        clock.tick(fps)
        k_spawn = (k_spawn + 1) % 71
        k_shoot = (k_shoot + 1) % 81
        pygame.display.flip()
    pygame.quit()