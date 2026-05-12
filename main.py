import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from utils import *
import random as random
vec = pg.math.Vector2

# import settings


# the game class that will be instantiated in order to run the game...
class Game:
    def __init__(self):
        pg.init()
        # setting up pygame screen using tuple value for width height
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.playing = True
        self.game_cooldown = Cooldown(5000)
        self.levels = ['leve1.txt','level2.txt','level3.txt','level4.txt']
        self.petal_timer = 0
        self.petal_spawn_interval = 0.3
        #print('game instantiated...')
    # a method is a function tied to a Class
    #loads the data (images)
    #sourced from Claude
    #how do i make it so when the map loads it knows layers
    def get_wall_layer_map(self):
        wall_rows = set()
        for row, line in enumerate(self.map.data):
            i = 0
            while i < len(line):
                if i + 1 < len(line) and line[i + 1] == '(':
                    end = line.find(')', i)
                    tile = line[i:end + 1] if end != -1 else line[i]
                    i = end + 1 if end != -1 else i + 1
                else:
                    tile = line[i]
                    i += 1
                if tile == '1':
                    wall_rows.add(row)
                    break  # one confirmed hit per row is enough
        wall_rows = sorted(wall_rows)
        if not wall_rows:
            return {}
        total = len(wall_rows)
        third = max(1, total // 3)
        layer_map = {}
        for i, r in enumerate(wall_rows):
            if i < third:
                layer_map[r] = 'top'
            elif i >= total - third:
                layer_map[r] = 'bot'
            else:
                layer_map[r] = 'mid'
        return layer_map

    def load_data(self, map):
        self.game_dir = path.dirname(__file__)
        self.img_dir = path.join(self.game_dir, 'images')
        self.wall_img = pg.image.load(path.join(self.img_dir, 'wall_art.png')).convert_alpha()
        self.grass_img = pg.transform.scale(pg.image.load(path.join(self.img_dir, 'grass.png')).convert_alpha(),
                (TILESIZE, TILESIZE)
            )
        self.ground_img = pg.image.load(path.join(self.img_dir, 'grass.png')).convert_alpha() 
        self.snd_dir = path.join(self.game_dir, "sounds")
        self.map = Map(path.join(self.game_dir, map))
        self.portal = pg.image.load(path.join(self.img_dir, 'portal.png')).convert_alpha()  
        self.WindStreak = pg.image.load(path.join(self.img_dir,'wind.png')).convert_alpha()
        self.cloud_top_img = pg.transform.scale(
            pg.image.load(path.join(self.img_dir, 'cloud_top.png')).convert_alpha(),
            (TILESIZE, TILESIZE))
        self.cloud_mid_img = pg.transform.scale(
            pg.image.load(path.join(self.img_dir, 'cloud_middle.png')).convert_alpha(),
            (TILESIZE, TILESIZE))
        self.cloud_bot_img = pg.transform.scale(
            pg.image.load(path.join(self.img_dir, 'cloud_bottom.png')).convert_alpha(),
            (TILESIZE, TILESIZE))
        bg_filename = LEVEL_BACKGROUNDS.get(map, 'background.png')
        self.background_img = pg.transform.scale(
        pg.image.load(path.join(self.img_dir, bg_filename)).convert(),
        (WIDTH, HEIGHT))
        self.meteor_img = pg.transform.scale(
        pg.image.load(path.join(self.img_dir,'meteor.png')).convert(),
        (WIDTH, HEIGHT))
    #adds all the sprites 
    #next level
   
            

    def new(self):
        #inits all sprites
        self.current_level_index = 0        
        #adding more levels, but for now keep these levels
        self.levels = ['level1.txt', 'level2.txt','level3.txt','level4.txt']
        self.all_sprites = pg.sprite.Group()
        self.all_walls = pg.sprite.Group()      
        self.all_mobs = pg.sprite.Group()       
        self.all_projeactiles = pg.sprite.Group()
        self.all_grounds = pg.sprite.Group()    
        self.all_petals = pg.sprite.Group()     
        self.all_portals = pg.sprite.Group()  
        self.petal_timer = 0
        self.all_dash_trails = pg.sprite.Group()
        self.all_jumppetals = pg.sprite.Group()
        self.all_moving_platforms = pg.sprite.Group()
        self.wind_force = 0      #force of   wind
        self.wind_timer = 4.0   #intervals between gusts
        self.wind_active = False
        self.wind_streak_timer = 0
        self.all_wind_streaks = pg.sprite.Group()
        self.all_meteors = pg.sprite.Group()
        self.meteor_timer = 0
        self.meteor_spawn_interval = random.uniform(3.0, 7.0)
        #interactable spawn interval for petals, will change eventually for each level
        self.petal_spawn_interval = 0.3
        self.load_data(self.levels[self.current_level_index])

        wall_layers = self.get_wall_layer_map()

#looks through each line in map to add the sprite
        for row, line in enumerate(self.map.data):
            col = 0
            i = 0
            while i < len(line):
                if i + 1 < len(line) and line[i+1] == '(':
                    end = line.find(')', i)
                    tile = line[i:end+1]
                    i = end + 1
                else:
                    tile = line[i]
                    i += 1
                if tile == ' ':
                    continue
                if tile.startswith('G'):
                    ground(self, col, row, tile)
                if tile == '1':
                    Wall(self, col, row, layer=wall_layers.get(row, 'mid'))
                if tile.startswith('P'):
                    self.player = Player(self, col, row)
                    self.spawn_pos = pg.math.Vector2(col, row) * TILESIZE

                if tile.startswith('M'):
                    Mob(self, col, row)
                if tile.startswith('C'):
                    Coin(self, col, row)
                if tile.startswith('A'):
                    Portal(self,col,row)
                if tile.startswith('F'):
                    MovingPlatform(self, col, row)           
                if tile.startswith('J'):
                    MovingPlatform(self, col, row, axis='y') 
                col += 1
        pg.mixer.music.load(path.join(self.snd_dir, "soundtrack1.mp3"))
        pg.mixer.music.play(loops=-1)
        self.run()
    def next_level(self):
        self.current_level_index += 1
        if self.current_level_index >= len(self.levels):
            print("You win!")
            self.running = False
            return

        # Kill all sprites
        for sprite in self.all_sprites:
            sprite.kill()
        for sprite in self.all_grounds:
            sprite.kill()
        for sprite in self.all_petals:
            sprite.kill()
        for sprite in self.all_jumppetals:
            sprite.kill()
        for sprite in self.all_dash_trails:
            sprite.kill()
        for sprite in self.all_moving_platforms:
            sprite.kill()
        for sprite in self.all_meteors:
            sprite.kill()
        for sprite in self.all_wind_streaks:
            sprite.kill()
        # Load next map
        self.load_data(self.levels[self.current_level_index])
        wall_layers = self.get_wall_layer_map()

        # Rebuild sprite groups (they still exist, just emptied)
        for row, line in enumerate(self.map.data):
            col = 0
            i = 0
            while i < len(line):
                if i + 1 < len(line) and line[i+1] == '(':
                    end = line.find(')', i)
                    tile = line[i:end+1]
                    i = end + 1 
                else:
                    tile = line[i]
                    i += 1
                if tile == ' ':
                    continue
                if tile == '1':
                        Wall(self, col, row, layer=wall_layers.get(row, 'mid'))
                if tile.startswith('P'):
                    self.player = Player(self, col, row)
                    self.spawn_pos = pg.math.Vector2(col, row) * TILESIZE 
#stores the spawn position value
                if tile.startswith('M'):
                    Mob(self, col, row)
                if tile.startswith('O'):
                    Orb(self, col, row)
                if tile.startswith('A'):
                    Portal(self, col, row)   #the new Portal sprite
                if tile.startswith('F'):
                    MovingPlatform(self, col, row)           
                if tile.startswith('J'):
                    MovingPlatform(self, col, row, axis='y') 
                col += 1
    #respawns player once they fall below certain y pos
    def respawn(self):
        self.player.pos = self.spawn_pos.copy()
        self.player.vel = pg.math.Vector2(0, 0)
        self.player.on_ground = False
    #defines how to run
    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
    #adds the events
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
           #calls jump function 
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_w:
                    self.player.jump()  # call jump once on keypress
    def quit(self):
        pass
    def update(self):
        self.all_sprites.update()
        self.all_petals.update()
        self.all_dash_trails.update()
        self.all_jumppetals.update()  
        self.all_wind_streaks.update()
        self.all_meteors.update()

        #meteor spawning
        self.meteor_timer += self.dt
        if self.meteor_timer >= self.meteor_spawn_interval:
            self.meteor_timer = 0
            self.meteor_spawn_interval = random.uniform(2.0, 6.0)
            Meteor(self)
        # checks if the player reached the portal
        portal_hits = pg.sprite.spritecollide(self.player, self.all_portals, False)
        #boolean value determines if player moves onto next level
        if portal_hits:
            self.next_level()
        self.wind_timer -= self.dt
        if self.wind_timer <= 0:
            if self.wind_active:
                # when gust is over enter calm period between 3-8s
                self.wind_active = False
                self.wind_force = 0
                self.wind_timer = random.uniform(3.0, 6.0)
            else:
                # start a new gust with random strength
                self.wind_active = True
                self.wind_force = -random.uniform(40, 160)
                self.wind_timer = random.uniform(1.5, 4.0)

        # spawn visual streaks while wind is blowing
        if self.wind_active:
            self.wind_streak_timer -= self.dt
            if self.wind_streak_timer <= 0:
                self.wind_streak_timer = random.uniform(0.02, 0.08)
                WindStreak(self)

        # Petal spawning
        self.petal_timer += self.dt
        if self.petal_timer >= self.petal_spawn_interval:
            self.petal_timer = 0
            Petal(self)
            if random.randint(1, 5) == 1:   # 1 in 5 chance to spawn a jump petal
                JumpPetal(self)
        if self.player.pos.y > HEIGHT + TILESIZE * 2:
            self.respawn()
    #draws map and sprites and petals
    def draw(self):
        self.screen.blit(self.background_img, (0, 0)) 
        self.all_grounds.draw(self.screen)
        self.all_petals.draw(self.screen)   # petals behind player/walls
        self.all_meteors.draw(self.screen)      # meteors behind petals/player

        self.all_sprites.draw(self.screen) # player/walls drawn on top
        #self.draw_text("Petals in the Wind", 30, BGPINK, WIDTH/2, TILESIZE^2)
        #self.draw_text(str(self.dt), 24, WHITE, WIDTH/2, HEIGHT/4)
        #self.draw_text(str(self.game_cooldown.ready()), 24, WHITE, WIDTH/2, HEIGHT/3)
        self.all_dash_trails.draw(self.screen)  # trail behind player
        self.all_jumppetals.draw(self.screen)
        self.all_wind_streaks.draw(self.screen)  # wind behind petals/player
        #self.draw_text(str(self.player.pos), 24, WHITE, WIDTH/2, HEIGHT-TILESIZE*3)
        pg.display.flip()
    #draws the text
    def draw_text(self, text, size, color, x, y):
        font_name = pg.font.match_font('Comfortaa')
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x,y)
        self.screen.blit(text_surface, text_rect)
    
#calls Game
if __name__ == "__main__":
    g = Game()
#runs game
while g.running:
    g.new()
#closes game
pg.quit()