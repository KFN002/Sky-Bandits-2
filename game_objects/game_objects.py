import os
import pygame
from pygame import mixer
from utils import data_master
from random import choice
import threading

cwd = os.getcwd()


class BasicSprite(pygame.sprite.Sprite):
    def __init__(self, frames, speed):
        pygame.sprite.Sprite.__init__(self)
        self.frames = frames
        self.cur_frame = 0
        self.image = frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.speed = speed
        self.destroyed = False

    def update_animation(self, group):
        if self.cur_frame < len(self.frames) - 1 and self.destroyed:
            self.cur_frame += 1
            self.image = self.frames[self.cur_frame]
        elif self.destroyed:
            group.remove(self)
            self.sound.set_volume(0.5)
            self.sound.play()

    def move(self, vector=1):
        self.rect.y += self.speed * vector

    def check_collision(self, objects):
        if not pygame.sprite.spritecollideany(self, objects):
            return True
        return False


class Player(BasicSprite):
    def __init__(self, plane_data):
        BasicSprite.__init__(self,
                             [pygame.image.load(os.path.join(cwd, 'data', 'planes', '0', plane_data[2]))] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', f'boom{i}.png')) for i in
                              range(1, 7)] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', 'blank_space.png'))],
                             plane_data[5])
        self.bullets = plane_data[9]
        self.bombs = int(plane_data[8])
        self.hits = int(plane_data[6])
        self.explosion = mixer.Sound(os.path.join(cwd, 'data', 'music', 'explosion.wav'))
        self.explosion.set_volume(0.5)
        self.down = False
        self.exploding = False
        self.rect.x = 600
        self.rect.y = 300

    def move_up(self):
        if self.rect.y <= 0:
            self.rect.y = 0
        else:
            self.rect.y -= self.speed

    def move_down(self, height):
        if self.rect.y >= height - self.rect.height:
            self.rect.y = height - self.rect.height
        else:
            self.rect.y += self.speed

    def move_left(self):
        if self.rect.x <= 0:
            self.rect.x = 0
        else:
            self.rect.x -= self.speed

    def move_right(self, width):
        if self.rect.x >= width - self.rect.width:
            self.rect.x = width - self.rect.width
        else:
            self.rect.x += self.speed

    def update(self, group, player_data, plane_data, score):
        if self.down and self.cur_frame < len(self.frames) - 1 and self.exploding:
            self.cur_frame += 1
            self.image = self.frames[self.cur_frame]
        elif self.down:
            self.exploding = False
            group.remove(self)
        if self.down and not self.exploding:
            group.remove(self)
            mixer.stop()

            add_points = threading.Thread(target=data_master.change_score_money(player_data, int(int(plane_data[11])
                                                                                                 * score)))
            add_points.start()
            _, user_data = data_master.check_player(player_data[0], player_data[1])
            data_master.show_info(user_data)

    def shoot(self, group):
        if self.bullets > 0:
            bullet = Bullet(pygame.image.load(os.path.join(cwd, 'data', 'arms', 'bullet.png')), self.speed,
                            self.rect.midtop)
            group.add(bullet)
            self.bullets -= 1

    def drop_bomb(self, bombs):
        if self.bombs >= 1:
            bmb = Bomb(self.rect.midbottom, self.speed)
            bombs.add(bmb)
            self.bombs -= 1

    def hit(self):
        self.hits -= 1
        if self.hits <= 0:
            self.hits = 0
            self.down = True
            self.exploding = True
            self.explosion.play()
            mixer.stop()

    def add_bombs(self):
        self.bombs += 1

    def add_bullets(self):
        self.bullets += 1

    def check_collision(self, objects):
        collided = pygame.sprite.spritecollideany(self, objects)
        if collided and not collided.destroyed:
            collided.kill()
            self.hit()

    def shot(self, bullets):
        collided = pygame.sprite.spritecollideany(self, bullets)
        if collided:
            bullets.remove(collided)
            self.hit()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, image, speed, px):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = int(px[0]) - 10
        self.rect.y = int(px[1])
        self.hit = False
        self.sound = mixer.Sound(os.path.join(cwd, 'data', 'music', 'bullet.wav'))
        self.sound.set_volume(0.3)
        self.sound.play()

    def update(self, vector=1):
        self.rect.y -= self.speed * 2 * vector


class Bomb(BasicSprite):
    def __init__(self, mid_bottom, speed):
        BasicSprite.__init__(self, [pygame.image.load(os.path.join(cwd, 'data', 'arms', 'bomb.png'))] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', f'boom{i}.png')) for i in
                              range(1, 7)] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', 'blank_space.png'))],
                             speed * 0.5)
        self.rect.x = mid_bottom[0] - 10
        self.rect.y = mid_bottom[1] - 60
        self.size_x = 20
        self.size_y = 36
        self.hit = False
        self.sound = mixer.Sound(os.path.join(cwd, 'data', 'music', 'bomb.wav'))
        self.explosion = mixer.Sound(os.path.join(cwd, 'data', 'music', 'explosion.wav'))
        self.explosion.set_volume(0.5)
        self.sound.set_volume(0.5)
        self.sound.play(1)

    def update(self, group):
        if not self.hit and self.size_x >= 10:
            self.rect.y += self.speed
            self.size_x *= 0.99
            self.size_y *= 0.99
            self.image = pygame.transform.smoothscale(self.image, (int(self.size_x), int(self.size_y)))
        elif not self.hit:
            self.hit = True
            self.explosion.play()
        elif self.hit and self.cur_frame < len(self.frames) - 1:
            self.cur_frame += 1
            self.image = self.frames[self.cur_frame]
        else:
            group.remove(self)


class EnemyBase(BasicSprite):
    def __init__(self, speed, base_pos):
        BasicSprite.__init__(self, [pygame.image.load(os.path.join(cwd, 'data', 'backgrounds', 'enemy_base.png'))] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', f'boom{i}.png')) for i in
                              range(1, 7)] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', 'blank_space.png'))],
                             speed * 0.5)
        self.rect.x = base_pos[0]
        self.rect.y = base_pos[1]
        self.sound = mixer.Sound(os.path.join(cwd, 'data', 'music', 'explosion.wav'))

    def bombed(self, bmbs):
        collided = pygame.sprite.spritecollideany(self, bmbs)
        if collided:
            if collided.size_x <= 10:
                collided.sound.stop()
                bmbs.remove(collided)
                self.destroyed = True
                return True
        return False


class AARocket(BasicSprite):
    def __init__(self, x, height):
        BasicSprite.__init__(self, [pygame.image.load(os.path.join(cwd, 'data', 'arms', 'aa_rocket.png'))] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', f'boom{i}.png')) for i in
                              range(1, 7)] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', 'blank_space.png'))],
                             20)
        self.rect.x = x
        self.rect.y = height
        self.sound = mixer.Sound(os.path.join(cwd, 'data', 'music', 'explosion.wav'))
        self.sound.set_volume(0.5)

    def chase(self):
        if not self.destroyed:
            start = mixer.Sound(os.path.join(cwd, 'data', 'music', 'missile.wav'))
            start.set_volume(0.4)
            start.play()

    def exploded(self):
        self.destroyed = True


class Enemy(BasicSprite):
    def __init__(self, enemy_pos):
        BasicSprite.__init__(self, [pygame.image.load(os.path.join(cwd, 'data', 'planes', '0',
                                                                   '0.png'))] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', f'boom{i}.png')) for i in
                              range(1, 7)] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'booms', 'blank_space.png'))], 10)
        self.rect.x = enemy_pos[0]
        self.rect.y = enemy_pos[1]
        self.sound = mixer.Sound(os.path.join(cwd, 'data', 'music', 'explosion.wav'))

    def move_left(self):
        if self.rect.x <= 0:
            self.rect.x = 0
        else:
            self.rect.x -= self.speed

    def move_right(self, width):
        if self.rect.x >= width - self.rect.width:
            self.rect.x = width - self.rect.width
        else:
            self.rect.x += self.speed

    def shot(self, bullets):
        collided = pygame.sprite.spritecollideany(self, bullets)
        if collided:
            bullets.remove(collided)
            self.destroyed = True
            return True
        return False

    def shoot(self, group):
        bullet = Bullet(pygame.image.load(os.path.join(cwd, 'data', 'arms', 'bullet.png')), self.speed,
                        self.rect.midbottom)
        group.add(bullet)

    def kill(self):
        self.destroyed = True


class Decorations(BasicSprite):
    def __init__(self, speed, x, y):
        building = choice(['building1', 'building2', 'building3', 'building4', 'building5', 'building6',
                           'building7'])
        BasicSprite.__init__(self,
                             [pygame.image.load(os.path.join(cwd, 'data', 'backgrounds', building, 'image1.png'))] +
                             [pygame.image.load(os.path.join(cwd, 'data', 'backgrounds', building, 'image4.png'))],
                             speed * 0.5)
        self.rect.x = x
        self.rect.y = y

    def update(self, bmbs):
        collided = pygame.sprite.spritecollideany(self, bmbs)

        if collided:
            if collided.size_x <= 10:
                collided.sound.stop()
                if self.cur_frame < len(self.frames) - 1:
                    self.cur_frame += 1
                return True
            return False
        self.image = self.frames[self.cur_frame]


class Background:
    def __init__(self, img, speed):
        self.bgimage = pygame.image.load(os.path.join(cwd, img))
        self.rectBGimg = self.bgimage.get_rect()

        self.bgY1 = 0
        self.bgX1 = 0

        self.bgY2 = -self.rectBGimg.height
        self.bgX2 = 0

        self.moving_speed = int(abs(speed) * 0.5)

    def update(self):
        self.bgY1 += self.moving_speed
        self.bgY2 += self.moving_speed
        if self.bgY1 >= self.rectBGimg.height:
            self.bgY1 = -self.rectBGimg.height
        if self.bgY2 >= self.rectBGimg.height:
            self.bgY2 = -self.rectBGimg.height

    def render(self, screen):
        screen.blit(self.bgimage, (self.bgX1, self.bgY1))
        screen.blit(self.bgimage, (self.bgX2, self.bgY2))
