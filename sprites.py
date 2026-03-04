import pygame as pg
from pygame.sprite import Sprite
from settings import *
from os import path
from utils import *

vec = pg.math.Vector2
def collide_hit_rect(one, two):
        return one.hit_rect.colliderect(two.rect)

def collide_with_walls(sprite, group, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                # print("collided with wall from x dir")
                if hits[0].rect.centerx > sprite.hit_rect.centerx:
                    sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
                if hits[0].rect.centerx < sprite.hit_rect.centerx:
                    sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
                sprite.vel.x = 0
                sprite.hit_rect.centerx = sprite.pos.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                # print("collided with wall from y dir")
                if hits[0].rect.centery > sprite.hit_rect.centery:
                    sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
                if hits[0].rect.centery < sprite.hit_rect.centery:
                    sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
                sprite.vel.y = 0
                sprite.hit_rect.centery = sprite.pos.y
class Player(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.spritesheet = Spritesheet(path.join(self.game.image_dir,"sprite_sheet.png"))
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image=self.spritesheet.get_image(0,0,TILESIZE,TILESIZE)
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE
        self.jumping = False
        self.walking = False
        self.last_update = 0
        self.current_frame = 0
    def get_keys(self):
        if self.vel != vec(0,0):
            self.moving = True
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.vel.x = -PLAYER_SPEED
        if keys[pg.K_d]:
            self.vel.x = PLAYER_SPEED
        if keys[pg.K_w]:
            self.vel.y = -PLAYER_SPEED
        if keys[pg.K_s]:
            self.vel.y = PLAYER_SPEED
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071
        if keys[pg.K_f]:
            print('fired a projectile')
            p = Projectile(self.game,self.rect.x,self.rect.y)
    def load_image(self):
        self.standing_frames = [self.spritesheet.get_image(0,0,TILESIZE,TILESIZE),self.spritesheet.get_image(TILESIZE,0,TILESIZE,TILESIZE)]
        self.moving_frames=[self.spritesheet.get_image(TILESIZE*2,0,TILESIZE,TILESIZE)],
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)
    def animate(self):
        now = pg.time.get_ticks()
        if not self.jumping and not self.walking:
            if now - self.last_update > 3500:
                self.last_update = now
                self.current_frame = (self.current_frame+1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image + self.standing_frame[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        elif self.jumping: 
            if now - self.last_update > 350:
                self.last_update=now
                self.current_frame = (self.current_frame+1) %len(self.moving_frames)
                bottom=self.rect.bottom
                self.image = self.moving_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        
    def update(self):
        # print("player updating")
        self.get_keys()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt

class Mob(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.vel = vec(1,0)
        self.pos = vec(x,y) * TILESIZE
        self.speed = 10
    def update(self):
        hits = pg.sprite.spritecollide(self, self.game.all_walls, True)
        if hits:
            print("collided")
            self.speed -=1
            self.new_rect = pg.Rect(self.pos.x, self.pos.y, 100, 100) 
            self.rect = self.new_rect
            self.image.fill(RED)
        if self.rect.x > WIDTH or self.rect.x < 0:
            self.speed *= -1
            self.pos.y += TILESIZE
        self.pos += self.speed * self.vel
        self.rect.center = self.pos


class Wall(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_img
        #self.image = pg.Surface((TILESIZE, TILESIZE))
        #self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0) 
        self.pos = vec(x,y) * TILESIZE
        self.rect.center = self.pos
    def update(self):
        pass


class Coin(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE
    def update(self):
        pass
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0) 
        self.pos = vec(x,y) * TILESIZE
        self.rect.center = self.pos
class Projectile(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_projectiles
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.vel = vec(1,0)
        self.pos = vec(x,y) * TILESIZE
        self.speed = 10
    def update(self):
        hits = pg.sprite.spritecollide(self, self.game.all_walls, True)
        print(hits)
        self.pos += self.speed * self.vel
        self.rect.cneter = self.pos
        
