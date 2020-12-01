import pygame as pg
from settings import *
import random
vec = pg.math.Vector2


class Spritesheets:
    # for loading spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        #grab image out of larger spritesheet
        image = pg.Surface((width,height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width//2, height//2))
        return image


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = player_layer
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        #Create block
        self.load_images()
        self.image = self.standing_frames[0]
        #Create rectangle
        self.rect = self.image.get_rect()
        self.rect.center = (35, width - 70)
        #Create position for calculating movements
        self.pos = (35, width - 70)
        #add velocity
        self.vel = vec(0, 0)
        #add acceleration
        self.acc = vec(0, 0)

    def load_images(self):
        self.standing_frames = [ self.game.spritesheet.get_image(614, 1063, 120, 191),
                                 self.game.spritesheet.get_image(690, 406, 120, 201)]
        for frame in self.standing_frames:
            frame.set_colorkey(black)
        self.walk_frames_r = [ self.game.spritesheet.get_image(678, 860, 120, 201),
                               self.game.spritesheet.get_image(692, 1458, 120, 207)]
        self.walk_frames_l = []
        for frames in self.walk_frames_r:
            frames.set_colorkey(black)
            self.walk_frames_l.append(pg.transform.flip(frames, True, False))
        self.jump_frame = self.game.spritesheet.get_image(382,763 ,150, 181)
        self.jump_frame.set_colorkey(black)

    def update(self):
        self.animate()
        self.acc = vec(0, player_grav)
        keys = pg.key.get_pressed()
        if keys[pg.K_RIGHT]:
            self.acc.x = player_acc
        if keys[pg.K_LEFT]:
            self.acc.x = -player_acc
        if keys[pg.K_LSHIFT] and keys[pg.K_RIGHT]:
            self.acc.x = player_sprint
        if keys[pg.K_LSHIFT] and keys[pg.K_LEFT]:
            self.acc.x = -player_sprint

        #Apply friction
        self.acc.x += self.vel.x * player_frition
        #Equations of motion
        self.vel += self.acc
        if abs(self.vel.x) < 0.5:
            self.vel.x = 0
        self.pos += self.vel + 0.5*self.acc

        #create looping wall
        if self.pos.x > width + self.rect.width/2:
            self.pos.x = 0 - self.rect.width/2
        elif self.pos.x < 0 - self.rect.width/2:
            self.pos.x = width + self.rect.width/2
        #Attach change to character
        self.rect.midbottom = self.pos

    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False
        #show walking animation
        if self.walking:
            if now - self.last_update >200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                else:
                    self.image = self.walk_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        #show idle animation
        if not self.jumping and not self.walking:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect =self.image.get_rect()
                self.rect.bottom = bottom
        self.mask = pg.mask.from_surface(self.image)

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3

    def jump(self):
        self.rect.y += 2
        lands = pg.sprite.spritecollide(self,self.game.platform_sprites, False)
        self.rect.y -= 2
        if lands and not self.jumping:
            self.game.jump_sound.play()
            self.jumping = True
            self.vel.y = -jump_power

    def bounce(self):
        self.game.jump_sound.play()
        self.jumping = True
        self.vel.y = -jump_power

    def jump_down(self):
        self.rect.y += 2
        lands = pg.sprite.spritecollide(self,self.game.platform_sprites, False)
        self.rect.y -= 2
        if lands and not self.jumping:
            self.game.jump_sound.play()
            self.jumping = True
            self.vel.y = +jump_down_power


class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = platform_layer
        self.groups = game.all_sprites, game.platform_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        images = [self.game.spritesheet.get_image(0 , 288, 380, 94),
                       self.game.spritesheet.get_image(213, 1662, 201, 100)]
        self.image = random.choice(images)
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if random.randrange(100) < pow_spawn_prob:
            Pow(self.game, self)

class Pow(pg.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = pow_layer
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.image = self.game.spritesheet.get_image(820, 1805, 71, 70)
        self.type = random.choice(["boost"])
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.bottom - 10

    def update(self):
        self.rect.bottom = self.plat.rect.top - 10
        if not self.game.platform_sprites.has(self.plat):
            self.kill()

class Mob(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = mob_layer
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image_up = self.game.spritesheet.get_image(566, 510, 122, 139)
        self.image_up.set_colorkey(black)
        self.image_down = self.game.spritesheet.get_image(568, 1534, 122, 135)
        self.image_down.set_colorkey(black)
        self.image =  self.image_up
        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice([-100, width +100])
        self.vx = random.randrange(1,4)
        if self.rect.centerx > width:
            self.vx *= -1
        self.rect.y = random.randrange(height/2)
        self.vy = 0
        self.dy = 0.5

    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy
        if self.vy > 3 or self.vy < -3:
            self.dy *= -1
        center = self.rect.center
        if self.dy < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = center
        self.rect.y += self.vy
        if  self.rect.left > width + 100 or self.rect.right < - 100:
            self.kill()

#class Platform(pg.sprite.Sprite):
    #def __init__(self, game, x, y):
        #self._layer = cloud_layer
        #self.groups = game.all_sprites, game.clouds
        #pg.sprite.Sprite.__init__(self, self.groups)