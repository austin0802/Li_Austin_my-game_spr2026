import pygame as pg
from pygame.sprite import Sprite
from settings import *
from os import path
import random as random 
import math as math
from utils import *

vec = pg.math.Vector2
def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)




#Used Claude AI to debug old collisions. It debugged it by instead of overlapping multiple different tiles, 
#new code measures overlap and reverts it. 

# this function checks for x and y collision in sequence and sets the position based on collision direction
def collide_with_walls(sprite, group, dir):
    hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
    if not hits:
        return
    if dir == 'x':
        if sprite.vel.x > 0:
            # moving right: push back by how far our right edge passed the wall's left edge
            wall = min(hits, key=lambda w: sprite.hit_rect.right - w.rect.left)
            penetration = sprite.hit_rect.right - wall.rect.left
            sprite.pos.x -= penetration
        elif sprite.vel.x < 0:
            # moving left: push back by how far our left edge passed the wall's right edge
            wall = min(hits, key=lambda w: w.rect.right - sprite.hit_rect.left)
            penetration = wall.rect.right - sprite.hit_rect.left
            sprite.pos.x += penetration
        sprite.vel.x = 0
        sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        if sprite.vel.y > 0:
            # moving down: push back by how far our bottom edge passed the wall's top edge
            wall = min(hits, key=lambda w: sprite.hit_rect.bottom - w.rect.top)
            penetration = sprite.hit_rect.bottom - wall.rect.top
            sprite.pos.y -= penetration
        elif sprite.vel.y < 0:
            # moving up: push back by how far our top edge passed the wall's bottom edge
            wall = min(hits, key=lambda w: w.rect.bottom - sprite.hit_rect.top)
            penetration = wall.rect.bottom - sprite.hit_rect.top
            sprite.pos.y += penetration
        sprite.vel.y = 0
        sprite.hit_rect.centery = sprite.pos.y

#adds a player class that the user will control
class Player(Sprite):
    #inits player
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
       #animated player sprite
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.load_images()
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = self.spritesheet.get_image(0,0,TILESIZE,TILESIZE)
        self.image.set_colorkey(BLACK)
        # self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE
        self.hit_rect = PLAYER_HIT_RECT.copy()
        self.jumping = False
        self.walking = False
        self.last_update = 0
        self.on_ground = False          
        self.current_frame = 0
        #self.state_machine = StateMachine()
        #self.states: Array[State] = [PlayerIdleState(self), PlayerMoveState(self)]
        #self.state_machine.start_machine(self.states)
    #defines the jump function by changing y velocity to jumping force if player is on ground
    def jump(self):
        if self.on_ground:
            self.vel.y = JUMP_FORCE
            self.on_ground = False
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            #when space or w is pressed it makes the player jump
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE or event.key == pg.K_w:
                    self.player.jump()
    def get_keys(self):
        #gets the player inputs
        self.vel.x = 0
        keys = pg.key.get_pressed()
        if keys[pg.K_f]:
            p = Projectile(self.game, self.rect.x, self.rect.y)
        if keys[pg.K_a]:
            self.vel.x = -PLAYER_SPEED
        if keys[pg.K_d]:
            self.vel.x = PLAYER_SPEED
    def load_images(self):
        #loads the image so it matches player direction 
        self.standing_frames = [
            self.spritesheet.get_image(0, TILESIZE*2, TILESIZE, TILESIZE),
        ]
        self.moving_right_frames = [
            self.spritesheet.get_image(TILESIZE*2, 0, TILESIZE, TILESIZE),
            self.spritesheet.get_image(TILESIZE*3, 0, TILESIZE, TILESIZE)
        ]
        self.moving_left_frames = [
            pg.transform.flip(f, True, False) for f in self.moving_right_frames
        ]
        # Flip right frames to get left frames
        self.moving_up_frames = [
            self.spritesheet.get_image(0, TILESIZE*2, TILESIZE, TILESIZE),
            self.spritesheet.get_image(TILESIZE, TILESIZE*2, TILESIZE, TILESIZE),
            self.spritesheet.get_image(TILESIZE*2, TILESIZE*2, TILESIZE, TILESIZE),
            self.spritesheet.get_image(TILESIZE*3, TILESIZE*2, TILESIZE, TILESIZE),

        ]
        self.moving_down_frames = [
            self.spritesheet.get_image(0, TILESIZE*3, TILESIZE, TILESIZE),
            self.spritesheet.get_image(TILESIZE, TILESIZE*3, TILESIZE, TILESIZE),
            self.spritesheet.get_image(TILESIZE*2, TILESIZE*3, TILESIZE, TILESIZE),
            self.spritesheet.get_image(TILESIZE*3, TILESIZE*3, TILESIZE, TILESIZE),

        ]

        #for frame in self.standing_frames:
            #frame.set_colorkey(BLACK)
        #for frame in self.moving_frames:
            #frame.set_colorkey(BLACK)
    def animate(self):
        now = pg.time.get_ticks()
#animates the sprite
        if not self.moving:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                self.image = self.standing_frames[self.current_frame]
        else:
            if now - self.last_update > 150:
                self.last_update = now
                #made a mistake when defining right and left frames, so have to revert here. 
                if self.direction == "left":
                    frames = self.moving_right_frames
                elif self.direction == "right":
                    frames = self.moving_left_frames
               
                elif self.direction == "down":
                    frames = self.moving_down_frames
                elif self.direction == "up":
                    frames = self.moving_up_frames
                else:
                    frames = self.standing_frames  # fallback for up/down
                self.current_frame = (self.current_frame + 1) % len(frames)
                self.image = frames[self.current_frame]
#had to change the y direction collision (sourced from claude)
    def collide_with_ground(self):
        hits = pg.sprite.spritecollide(self, self.game.all_walls, False, collide_hit_rect)
        if hits:
            if self.vel.y > 0:
                wall = min(hits, key=lambda w: self.hit_rect.bottom - w.rect.top)
                penetration = self.hit_rect.bottom - wall.rect.top
                self.pos.y -= penetration
                self.hit_rect.centery = self.pos.y
                self.vel.y = 0
                self.on_ground = True
            elif self.vel.y < 0:
                wall = min(hits, key=lambda w: w.rect.bottom - self.hit_rect.top)
                penetration = wall.rect.bottom - self.hit_rect.top
                self.pos.y += penetration
                self.hit_rect.centery = self.pos.y
                self.vel.y = 0

    def state_check(self):
        self.moving = self.vel.x != 0
        if self.vel.x > 0:
            self.direction = "right"
        elif self.vel.x < 0:
            self.direction = "left"
        elif not self.on_ground:
            self.direction = "up"  # or a jump frame
    def update(self):
        self.get_keys()
        self.state_check()
        self.animate()

        self.vel.y += GRAVITY 
        if self.vel.y > 20:
            self.vel.y = 20

        self.pos.x += self.vel.x * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x')
        self.pos.x = self.hit_rect.centerx

        self.on_ground = False
        self.pos.y += self.vel.y 
        self.hit_rect.centery = self.pos.y
        self.collide_with_ground()
        self.pos.y = self.hit_rect.centery
        self.rect.center = self.hit_rect.center

#adds a mob that will be teh enemy to the player
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
            self.speed -=1
            self.new_rect = pg.Rect(self.pos.x, self.pos.y, 100, 100) 
            self.rect = self.new_rect
            self.image.fill(RED)
        if self.rect.x > WIDTH or self.rect.x < 0:
            self.speed *= -1
            self.pos.y += TILESIZE
        self.pos += self.speed * self.vel
        self.rect.center = self.pos


#adding a wall sprite (need to fix collisions)
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

#adding a coin sprite
class Coin(Sprite):
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
    def update(self):
        pass
    #inits coin sprite
#adding a projectile class
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
        self.rect.center = self.pos
        
#ground sprite that classifies different types of grounds
#going to implement more ground types, so far only grass which is not used
class ground(Sprite):
    def __init__(self, game, x ,y, tile ):
        self.groups = game.all_grounds
        Sprite.__init__(self, self.groups) 
        self.game = game

        texture = 'S' # default texture if nothing in parenthesis
        if '(' in tile and ')' in tile: # checks whatis inside the parenthesis
            texture = tile[tile.find('(')+1:tile.find(')')]
    
        if texture == 'G':
            self.image = game.grass_img
        # elif texture == 'S':
        #     self.image = game.sand_img
        # elif texture == 'W':
        #     self.image = game.deep_water_img
        # elif texture == "w":
        #     self.image = game.shallow_water_img
        # else:
        #     self.image = game.sand_img
        else:
            self.image = game.grass_img

        self.rect = self.image.get_rect()
        self.pos = vec(x, y) * TILESIZE
        self.rect.center = self.pos
        #from stephen kobzar
#petal class for asthetics
class Petal(Sprite):
    def __init__(self, game, x=None):
        #new group because there are no collisions
        self.groups = game.all_petals
        Sprite.__init__(self, self.groups)
        self.game = game
        # Load petal image from the images folder
        self.original_image = pg.image.load(path.join(game.img_dir, 'petalimage.png')).convert_alpha()
        self.image = self.original_image.copy()
        # Spawn at a random x along the top of the screen
        start_x = x if x is not None else random.randint(0, WIDTH)
        #positions the petal 
        self.pos = vec(start_x, -self.image.get_height())
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        # Fall speed and  horizontal drift
       #randomizes downward speed
        self.fall_speed = random.uniform(60, 130)
        #randomizes horizontal speed
        self.drift_speed = random.uniform(-40, 40)
        #randomizes starting angle
        self.wobble_offset = random.uniform(0, math.pi * 2)
        #randomizes oscillation
        self.wobble_speed = random.uniform(1.5, 3.5)
        self.wobble_amplitude = random.uniform(20, 50)
        # Rotation
        self.angle = random.uniform(0, 360)
        self.spin_speed = random.uniform(-60, 60)  # degrees per second
    def update(self):
        dt = self.game.dt
        # Wobble side to side using a sine wave
        time_elapsed = pg.time.get_ticks() / 1000
        #uses sine wave to calculate the wobble with variables above
        wobble = math.sin(time_elapsed * self.wobble_speed + self.wobble_offset) * self.wobble_amplitude
        # Update position
        self.pos.y += self.fall_speed * dt
        self.pos.x += (self.drift_speed + wobble) * dt
        # Rotate using original image to avoid quality degradation
        self.angle += self.spin_speed * dt
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.pos)
        # Kill petal once it falls off the bottom of the screen
        if self.pos.y > HEIGHT + self.rect.height:
            self.kill()