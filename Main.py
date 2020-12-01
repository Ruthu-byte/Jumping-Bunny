import pygame as pg
import random
import sys
from settings import *
from sprites import *
from os import path


class Game():
    # Initialize games
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.running = True
        self.screen = pg.display.set_mode((width, height))
        pg.display.set_caption(title)
        self.clock = pg.time.Clock()
        self.font_name = pg.font.match_font(font_name)
        self.load_data()

    def load_data(self):
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, "Spritesheets")
        #make a cloud
        #self.cloud_images = []
       # for i in range[1,4]:
            #self.cloud_images(pg.image.load(path.join(img_dir, '')))
        with open(path.join(self.dir, highscore), 'r') as f:
            try:
                self.h_s = int(f.read())
            except:
                self.h_s = 0
        #load spritesheet
        self.spritesheet = Spritesheets(path.join(img_dir, "spritesheet_jumper.png"))
        self.snd_dir = path.join(self.dir, 'sound')
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'jump.wav'))
        self.boost_sound = pg.mixer.Sound(path.join(self.snd_dir, 'boost.wav'))

    #Starting new game
    def new(self):
        #Score
        self.score = 0
        #Create sprite group
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platform_sprites = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.clouds = pg.sprite.Group()
        #Create variables for classes
        self.player = Player(self)
        for plat in platform_list:
            Platform(self, *plat)
        #Last time a mob spawned
        self.mob_timer = 0
        #Add class to sprite group
        self.all_sprites.add(self.player)
        #Play some bg muse
        pg.mixer.music.load(path.join(self.snd_dir, 'downtown.ogg'))


        self.run()

    #game update
    def update(self):
        self.all_sprites.update()
        #To spawn mob or not to spawn mob
        now = pg.time.get_ticks()
        if now - self.mob_timer > 5000  + random.choice([-1000, -500, 0, 500, 1000]):
            self.mob_timer = now
            Mob(self)
        #Did I hit the mob
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False, pg.sprite.collide_mask)
        if mob_hits:
            self.playing = False


        if self.player.vel.y > 0:
            lands = pg.sprite.spritecollide(self.player, self.platform_sprites, False)
            if lands:
                lowest = lands[0]
                for land in lands:
                    if land.rect.bottom > lowest.rect.bottom:
                        lowest = land
                if self.player.pos.x < lowest.rect.right +15 and self.player.pos.x > lowest.rect.left - 15:
                    if self.player.pos.y < lowest.rect.centery:
                        self.player.pos.y = lowest.rect.top
                        self.player.vel.y = 0
                        self.player.jumping = False
        # Moving the screen up
        if self.player.rect.top <= height/4:
            self.player.pos.y += max(abs(self.player.vel.y),2)
            for mob in self.mobs:
                mob.rect.y += max(abs(round(self.player.vel.y)),2)
            for plat in self.platform_sprites:
                plat.rect.y += max(abs(round(self.player.vel.y)),2)
                if plat.rect.top > height:
                    plat.kill()
                    self.score += 10

        #if powerup hit
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == "boost":
                self.boost_sound.play()
                self.player.vel.y =  -boost_power
                self.player.jumping = False

        #Death
        if self.player.rect.bottom > height:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(round(self.player.vel.y), 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platform_sprites) == 0:
            self.playing = False


        while len(self.platform_sprites) < 6:
            Width = random.randrange(50, 200)
            Platform(self, random.randrange(0, width-Width),random.randrange(-15, 0))


    #Running game
    def run(self):
        pg.mixer.music.play(loops= -1)
        self.playing = True
        while self.playing:
            self.clock.tick(fps)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500)

    #Game events
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()
                if event.key == pg.K_DOWN:
                    self.player.jump_down()
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_cut()

    #Draw game display
    def draw(self):
        self.screen.fill(lightblue)
        self.text_draw(str(self.score), 20, black, width- 25, 15)
        self.text_draw("Highscore: " + str(self.h_s), 20, black, 75, 15)
        self.all_sprites.draw(self.screen)
        pg.display.flip()

    #Show start screen
    def start_screen(self):
        pg.mixer.music.load(path.join(self.snd_dir, 'allthat.ogg'))
        pg.mixer.music.play(loops = -1)
        self.screen.fill(lightblue)
        self.text_draw(title, 50, pink, width/2, height/4)
        self.text_draw("Have fun", 40, black, width/2, (3*height)/4)
        self.text_draw("Press any key", 22, red, width/2, height/2)
        self.text_draw("HighScore:" + str(self.h_s), 20, red, 85, 15)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(50)


    #Show game over screen
    def go_screen(self):
        pg.mixer.music.load(path.join(self.snd_dir, 'awesomeness.ogg'))
        pg.mixer.music.play(loops = -1)
        self.screen.fill(black)
        self.text_draw("Game Over", 60, white, width/2, height/2)
        self.text_draw("Press 'p' to play again", 30, red, width/2, height*3/4)

        if self.score > self.h_s:
            self.h_s = self.score
            self.text_draw("NEW HIGH SCORE", 40, gold, width/2, 15)
            self.text_draw("Score: " + str(self.score), 30, gold, width / 2, height / 4)
            with open(path.join(self.dir, highscore), 'r+') as f:
                f.write(str(self.score))
        else:
            self.text_draw("Highscore: " + str(self.h_s), 20, gold, width / 2, 15)
            self.text_draw("Score: " + str(self.score), 30, red, width / 2, height / 4)
        pg.display.flip()
        self.wait_for_key_go()
        pg.mixer.music.fadeout(500)

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(fps)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    waiting = False

    def wait_for_key_go(self):
        waiting = True
        while waiting:
            self.clock.tick(fps)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_p:
                        waiting = False

    #def is_go(self):
     #   self.running= False

    def text_draw(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (round(x), round(y))
        self.screen.blit(text_surface, text_rect)


g = Game()
g.start_screen()
while g.running:
    g.new()
    g.run()
    g.events()
    g.update()
    g.draw()
    g.go_screen()