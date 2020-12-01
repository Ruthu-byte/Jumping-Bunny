#Settings
width, height = 400, 600
title = "Bunny Chow"
highscore = "highscore.txt"

#Colour settings
black = (0,0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
pink = (255, 0, 255)
blue = (0, 0, 255)
red = (255, 0, 0)
lightblue = (53, 153, 255)
gold = (212, 175, 55)
fps = 60
font_name = "Arial"

#Game properties
boost_power = 60
pow_spawn_prob = 7
mob_freq = 5000
player_layer = 2
platform_layer = 1
pow_layer = 1
mob_layer = 2
cloud_layer = 0

#Player settings
player_acc = 0.5
player_sprint = 0.8
player_frition = -0.12
player_grav = 0.98
jump_power = 20
jump_down_power = 25
#Platform list
platform_list = [
    (0, height - 60 ),
    (width/2 - 50, height*(3/4)),
    #(width/2 - 70, height*(1/4) ),
   # (width/2 +60, height*(1/2)),
    #(0, height*(4/5) - 450),
    (100, height*(4/5) - 150),
    (width/2 - 170, height*(1/4) + 110),
    (width-100, height*(4/5) - 350),
    (width/2 + 70, height*(0.10))
    ]