import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from utils import *
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
    def load_data(self, map):
        self.game_dir = path.dirname(__file__)
        self.img_dir = path.join(self.game_dir, 'images')
        self.wall_img = pg.image.load(path.join(self.img_dir, 'wall_art.png')).convert_alpha()
        self.grass_img = pg.transform.scale(pg.image.load(path.join(self.img_dir, 'grass.png')).convert_alpha(),
                (TILESIZE, TILESIZE)
            )#sourced from Claude
        self.ground_img = pg.image.load(path.join(self.img_dir, 'grass.png')).convert_alpha()  # ADD THIS
        self.snd_dir = path.join(self.game_dir, "sounds")
        self.map = Map(path.join(self.game_dir, map))
        self.background_img = pg.transform.scale(
        pg.image.load(path.join(self.img_dir, 'background.png')).convert(),
        (WIDTH, HEIGHT))

    #adds all the sprites 
    #next level
    def next_level(self):
        #kills it so it doesn't stay loaded, kills player so there isn't two players
        for w in self.all_walls:
            w.kill()
        for m in self.all_mobs:
            m.kill()
        for g in self.all_grass:
            g.kill()
            Player.kill()
        self.load_data(map)
        # self.player = Player(self, 15, 15)
        # self.mob = Mob(self, 4, 4) 
        # self.wall = Wall(self, WIDTH/2/TILESIZE, HEIGHT/2/TILESIZE)
        for row, twiles in enumerate(self.map.data):
            for col, tile, in enumerate(tiles):
                if tile == '1':
                    # call class constructor without assigning variable...when
                    Wall(self, col, row)
                if tile == 'P':
                    self.player = Player(self, col, row)
                if tile == 'M':
                    Mob(self, col, row)
                if tile == 'C':
                    Coin(self, col, row)
        
        self.run()
        
    
    def new(self):
        #loads all data and adds sprites
        self.load_data('level1.txt')
        self.all_sprites = pg.sprite.Group()
        self.all_walls = pg.sprite.Group()
        self.all_mobs = pg.sprite.Group()
        self.all_projectiles = pg.sprite.Group()
        self.all_grounds = pg.sprite.Group()
        self.all_petals = pg.sprite.Group()
        self.petal_timer = 0
        self.petal_spawn_interval = 0.3  # seconds between spawns
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
                # skip spaces (used as separators in the map file)
                if tile == ' ':
                    continue
                if tile.startswith('G'):
                    ground(self, col, row, tile)
                if tile == '1':
                    Wall(self, col, row)
                if tile.startswith('P'):
                    self.player = Player(self, col, row)
                if tile.startswith('M'):
                    Mob(self, col, row)
                if tile.startswith('C'):
                    Coin(self, col, row)
                col += 1
#sourced from Claude
        pg.mixer.music.load(path.join(self.snd_dir, "soundtrack1.mp3"))
        pg.mixer.music.play(loops=-1)
        self.run()
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
    #not done with how to update
    def update(self):
        self.all_sprites.update()
        self.all_petals.update()

        # Spawn petals periodically
        self.petal_timer += self.dt
        if self.petal_timer >= self.petal_spawn_interval:
            self.petal_timer = 0
            Petal(self)
    #draws map and sprites
    def draw(self):
        self.screen.blit(self.background_img, (0, 0))  # replace screen.fill(BLUE)
        self.all_grounds.draw(self.screen)
        self.all_petals.draw(self.screen)   # petals behind player/walls
        self.all_sprites.draw(self.screen) # player/walls drawn on top
        #self.draw_text("Hello World", 24, WHITE, WIDTH/2, TILESIZE)
        #self.draw_text(str(self.dt), 24, WHITE, WIDTH/2, HEIGHT/4)
        #self.draw_text(str(self.game_cooldown.ready()), 24, WHITE, WIDTH/2, HEIGHT/3)
        #self.draw_text(str(self.player.pos), 24, WHITE, WIDTH/2, HEIGHT-TILESIZE*3)
        pg.display.flip()
    #draws the text
    def draw_text(self, text, size, color, x, y):
        font_name = pg.font.match_font('arial')
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