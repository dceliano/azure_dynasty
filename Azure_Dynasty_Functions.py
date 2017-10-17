###########################################################
## After importing all modules and defining the necessary##
## constants, this file only contains non-class function ##
## definitions.                                          ##
###########################################################

#IMPORTS
import pygame, random, time, sys, os, pickle
import pyganim #python module used for animation - the pyganim.py file is included in file and found at http://inventwithpython.com/pyganim/index.html#about
from pygame.locals import *
from Azure_Dynasty_Classes import *

#REDEFINE ALL THE NECESSARY CONSTANTS AND INITIATE PYGAME

WINWIDTH = 640
WINHEIGHT = 480
TILESIZE = 75 #the width and height of each of the rectangular tiles
FILENAME = 'images/world.txt' #the text file with the world map

#           r    g    b
BLACK =   ( 0 ,  0 ,  0 )
WHITE =   (255, 255, 255)
RED =     (255,  0 ,  0 )
PURPLE =  (200,  0 , 150)
ORANGE =  (255, 128,  0 )
GREEN =   ( 0 , 200,  0 )
YELLOW =  (255, 255,  0 )

pygame.init()

#A global dictionary that will hold load and hold all the image surfaces returned by pygame.image.load()
IMAGESDICT = {'game icon': pygame.image.load('images/gameicon.png'),
              'down standing': pygame.image.load('sprites/mainwalkdown.png'),
              'up standing': pygame.image.load('sprites/mainwalkup.png'),
              'left standing': pygame.image.load('sprites/mainwalkleft.png'),
              'right standing': pygame.image.load('sprites/mainwalkright.png'),
              'down wielding': pygame.image.load('sprites/mainattackdown.png'),
              'up wielding': pygame.image.load('sprites/mainattackup.png'),
              'left wielding': pygame.image.load('sprites/mainattackleft.png'),
              'right wielding': pygame.image.load('sprites/mainattackright.png'),
              'grass': pygame.transform.scale(pygame.image.load('images/grass1.png'), (TILESIZE, TILESIZE)),
              'stone tile': pygame.transform.scale(pygame.image.load('images/stone_texture.jpg'), (TILESIZE, TILESIZE)),
              'water': pygame.transform.scale(pygame.image.load('images/water.png'), (TILESIZE, TILESIZE)),
              'lava': pygame.transform.scale(pygame.image.load('images/lava.png'), (TILESIZE, TILESIZE)),
              'text box': pygame.image.load('ui/parchment.png'),
              'button up': pygame.image.load('ui/black.png'),
              'button down': pygame.image.load('ui/black_down.png')}
#Dictionary that links the characters used in the world map data to their images
TILEMAPPING = {'x': IMAGESDICT['grass'],
               'o': IMAGESDICT['stone tile'],
               '~': IMAGESDICT['water'],
               'l': IMAGESDICT['lava'] }

# Creating the display surface to be used by the whole program
DISPSURFACE = pygame.display.get_surface()
pygame.display.set_icon(IMAGESDICT['game icon']) #display the game icon surface object next to the game caption
pygame.display.set_caption('Azure Dynasty')


#NON-CLASS FUNCTIONS:
def terminate():
    """Close up PyGame and exit out of the screen."""
    pygame.quit()
    sys.exit()
        
def loadPygAnimObjs(beginning_of_filenames, num_frames, frame_time):
    """Loads a bunch of PygAnim objects into a list. Each PygAnim object contains a series of frames to be animated, along with the time 
    each of those images will be shown for. frame_time is the amount of time to display each frame, and num_frames is the # of frames to display.
    The list animation indicies are as follows. 0 through 3 are mandatory, the others are not:
    0 - move up            1 - move down            2 - move right            3 - move left
    4 - attack up          5 - attack down          6 - attack right          7 - attack left """
    anim_objs = []
    anim_types = beginning_of_filenames.split() # loads the beginning of the names of the image files into a list
    for anim_type in anim_types:
        images_and_durations = [] #empty list loaded into anim_objs after each frame of the image is loaded
        for num in range(num_frames):
            if os.path.isfile('sprites/{0}{1}.png'.format(anim_type, num)): #make sure the file exists. If it doesn't, don't add it to the object
                images_and_durations.append(('sprites/{0}{1}.png'.format(anim_type, str(num)), frame_time))
        anim_objs.append(pyganim.PygAnimation(images_and_durations)) #load the images and durations into an animObj using PygAnim
    return anim_objs #returns a list

def loadDeathPygAnimObj(num_frames, frame_time, file_beginning):
    """Load the PygAnim death object into a list. This animation is loaded in a separate function than the rest of the animation because every
    time the death animation occurs, we want it to start at the same frame (so it looks the same each time). This is not as important
    with moving or attacking animations. This function takes the same arguments as the loadPygAnimObjs() function."""
    images_and_durations = [] #empty list loaded into anim_objs after each frame of the image is loaded
    for num in range(num_frames):
        images_and_durations.append(('sprites/{0}{1}.png'.format(file_beginning, str(num)), frame_time))
    death_anim_obj = pyganim.PygAnimation(images_and_durations) #load the images and durations into an animObj using PygAnim
    return death_anim_obj

def getMapObj():
    """With FILENAME containing the text representation of the graphical map, this function reads that text file and then loads the
    text representation of each tile into a nested list object, map_obj. For example, map_obj[x][y] will give the tile at point (x, y)
    in the text file. This function also loads water_rects, since it is a convenient spot to do so. water_rects contains the (x, y) text
    coordinates of the rectangles of water."""
    with open(FILENAME, 'r') as map_file:
        map_text_lines = [] #will be a list of every line in the file
        for line in map_file:
            line = line.strip('\n')
            map_text_lines.append(line)
    map_obj = [] #flips the coordinates of map_text_lines, in order to use x and y coordinates to refer to the coordinates of a tile
    for x in range(len(map_text_lines[0])):
        map_obj.append([])
    for y in range(len(map_text_lines)): #for every row
        for x in range(len(map_text_lines[0])): #for every column
            map_obj[x].append(map_text_lines[y][x]) #opposite [y][x] indexing used to switch assignments
    #Storing all the water rectangles into a list here as well
    water_rects = [] #a blank list of all the rectangles with water - this will be used to make sure the character doesn't step on them
    for x in range(len(map_obj)): #for every row
        for y in range(len(map_obj[x])): #for every column
            if map_obj[x][y] == '~': #if water
                water_rects.append(pygame.Rect((x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE))) #store the rectangle in the list
    return map_obj, water_rects
    
def drawMap(map_obj, camera):
    """Given the map_obj containing the (x, y) position of each tile, this function draws each tile sprite onto the surface, 
    but does so if the tile is actually on the screen (to avoid drawing unnecessary things)."""
    for x in range(len(map_obj)): #for every row
        for y in range(len(map_obj[x])): #for every column
            tile_position_x = (x * TILESIZE) - camera.x #multiply x times the TILESIZE so it is in world coordinates, not 'text' coordinates
            tile_position_y = (y * TILESIZE) - camera.y
            if (IsTileOnScreen(tile_position_x, tile_position_y)):
                DISPSURFACE.blit(TILEMAPPING[map_obj[x][y]], (tile_position_x, tile_position_y)) #draw the tile onto the surface

def drawStillChar(move_conductor, char, char_rect):
    """Given the PygAnim move conductor, the character object to draw and its rectangle, draw the character standing still (i.e. no animation)"""
    move_conductor.stop() #calling stop() while the animation objects are already stopped is okay; in that case stop() is a no-op
    if char.direction == 'up':
        if not char.wielding:
            DISPSURFACE.blit(IMAGESDICT['up standing'], char_rect) #blit the image onto the display surface at the location of the main_char_rect
        else:
            DISPSURFACE.blit(IMAGESDICT['up wielding'], char_rect)
    elif char.direction == 'down':
        if not char.wielding:
            DISPSURFACE.blit(IMAGESDICT['down standing'], char_rect)
        else:
            DISPSURFACE.blit(IMAGESDICT['down wielding'], char_rect)
    elif char.direction == 'right':
        if not char.wielding:
            DISPSURFACE.blit(IMAGESDICT['right standing'], char_rect)
        else:
            DISPSURFACE.blit(IMAGESDICT['right wielding'], char_rect)
    elif char.direction == 'left':
        if not char.wielding:
            DISPSURFACE.blit(IMAGESDICT['left standing'], char_rect)
        else:
            DISPSURFACE.blit(IMAGESDICT['left wielding'], char_rect)
            
def performMovement(char, char_rect, move_conductor, anim_objs, camera, water_rects):
    """Given a char object, its rectangle, the PygAnim move conductor to play the animation, and its anim_objs list (containing each individual 
    animation), the camera (to use its position), and the water_rects object (to make sure we don't walk into the water), this 
    large function checks what the state of certain attributes are, then performs the actual movement of the character of monster (that is why
    it is so long). Certain things (such as updating the camera) will only be done for the main character. """
    
    if hasattr(char, 'experience'): #if this variable is defined, we must be dealing with the main character.
        is_main_char = True #this variable is used later
    else:
        is_main_char = False
    
    if char.moving_up or char.moving_down or char.moving_right or char.moving_left:
        # Drawing the movement or attacking - drawing the correct sprites from the animation objects, consequently performing the animation:
        if IsOnScreen(char):
            move_conductor.play() #calling play() while the animation objects are already playing is okay; in that case play() is a no-op
            if char.direction == 'up':
                if char.attacking:
                    anim_objs[4].blit(DISPSURFACE, char_rect) #blit the animation onto the display surface at the location of the main_char_rect
                else:
                    anim_objs[0].blit(DISPSURFACE, char_rect)
            elif char.direction == 'down':
                if char.attacking:
                    anim_objs[5].blit(DISPSURFACE, char_rect)
                else:
                    anim_objs[1].blit(DISPSURFACE, char_rect)
            elif char.direction == 'right':
                if char.attacking:
                    anim_objs[6].blit(DISPSURFACE, char_rect)
                else:
                    anim_objs[2].blit(DISPSURFACE, char_rect)
            elif char.direction == 'left':
                if char.attacking:
                    anim_objs[7].blit(DISPSURFACE, char_rect)
                else:
                    anim_objs[3].blit(DISPSURFACE, char_rect)

        # Actually moving the position of the character or monster:
        if char.moving_right: #we do the same thing for every direction
            #moving in the actual world coordinates below
            char.would_be_in_water = False #reset this variable every time we iterate through, since we are no longer in the water
            char.world_x += char.walkrate # Change the coordinate to see if there will be a collision between the rectangles.
            # The line above is done before the loop so it is done before the rectangle is updated
            for water_rect in water_rects:
                char_rect = char.createRectangle() #redraw it to reflect position changes, so we can test if the char would be in the water
                if char_rect.colliderect(water_rect): # If we would be in the water (collision with water_rect), let the movement be performed.
                    char.would_be_in_water = True
            if char.would_be_in_water:
                char.world_x -= char.walkrate * 3 # If we are about to go into the drink, reverse the operation to get off the wall a little bit more so we are no longer colliding
                if is_main_char:
                    camera.x -= char.walkrate * 3 #make the camera move exactly with the movements of the character, so the character remains in the screen's center
                else: #is not the main character (is a monster instead)
                    #char.world_x is currently in relation to world coordinates, but we need it with respect to the camera's origin to draw it properly on the screen.
                    #To do this, we use the char.cam_y variable
                    char.world_x -= char.walkrate * 5 #get off the wall a little more
                    char.cam_y = char.world_y - camera.y
                    char.cam_x = char.world_x - camera.x #update both character cameras since the character might be moving in only 1 direction
                    char.stopMovement() #reset all movement
                    char.direction = 'left' #set the new direction of the monster to stop it from attempting to keep going into the wall
                    char.moving_left = True
            # if it is the main character, the camera will be moved along with the character
            elif is_main_char: #continue as normal
                camera.x += char.walkrate
            else: #monster moving
                char.cam_y = char.world_y - camera.y
                char.cam_x = char.world_x - camera.x
        #Same code repeated below for the up, down, and left directions
        if char.moving_up:
            char.would_be_in_water = False
            char.world_y -= char.walkrate
            for water_rect in water_rects:
                char_rect = char.createRectangle()
                if char_rect.colliderect(water_rect):
                    char.would_be_in_water = True
            if char.would_be_in_water:
                char.world_y += char.walkrate * 3
                if is_main_char:
                    camera.y += char.walkrate * 3
                else:
                    char.world_y += char.walkrate * 5
                    char.cam_y = char.world_y - camera.y
                    char.cam_x = char.world_x - camera.x
                    char.stopMovement()
                    char.direction = 'down'
                    char.moving_down = True
            elif is_main_char:
                camera.y -= char.walkrate
            else:
                char.cam_y = char.world_y - camera.y
                char.cam_x = char.world_x - camera.x
        if char.moving_down:
            char.would_be_in_water = False
            char.world_y += char.walkrate
            for water_rect in water_rects:
                char_rect = char.createRectangle()
                if char_rect.colliderect(water_rect):
                    char.would_be_in_water = True
            if char.would_be_in_water:
                char.world_y -= char.walkrate * 3
                if is_main_char:
                    camera.y -= char.walkrate * 3
                else:
                    char.world_y -= char.walkrate * 5
                    char.cam_y = char.world_y - camera.y
                    char.cam_x = char.world_x - camera.x
                    char.stopMovement()
                    char.direction = 'up'
                    char.moving_up = True
            elif is_main_char:
                camera.y += char.walkrate
            else:
                char.cam_y = char.world_y - camera.y
                char.cam_x = char.world_x - camera.x
        if char.moving_left:
            char.would_be_in_water = False
            char.world_x -= char.walkrate
            for water_rect in water_rects:
                char_rect = char.createRectangle()
                if char_rect.colliderect(water_rect):
                    char.would_be_in_water = True
            if char.would_be_in_water:
                char.world_x += char.walkrate * 3
                if is_main_char:
                    camera.x += char.walkrate * 3
                else:
                    char.world_x += char.walkrate * 5
                    char.cam_y = char.world_y - camera.y
                    char.cam_x = char.world_x - camera.x
                    char.stopMovement()
                    char.direction = 'right'
                    char.moving_right = True
            elif is_main_char:
                camera.x -= char.walkrate
            else:
                char.cam_y = char.world_y - camera.y
                char.cam_x = char.world_x - camera.x
                
    # Handling events if the character or monster is attacking and not moving:
    elif char.attacking:
        #main character is attacking, but standing still
        if IsOnScreen(char):
            move_conductor.play()
            if char.direction == 'up':
                anim_objs[4].blit(DISPSURFACE, char_rect)
                #update the camera variables of the monster so it stays in the correct spot on the screen
                char.cam_y = char.world_y - camera.y
                char.cam_x = char.world_x - camera.x
            elif char.direction == 'down':
                anim_objs[5].blit(DISPSURFACE, char_rect)
                char.cam_y = char.world_y - camera.y
                char.cam_x = char.world_x - camera.x
            elif char.direction == 'right':
                anim_objs[6].blit(DISPSURFACE, char_rect)
                char.cam_y = char.world_y - camera.y
                char.cam_x = char.world_x - camera.x
            elif char.direction == 'left':
                anim_objs[7].blit(DISPSURFACE, char_rect)
                char.cam_y = char.world_y - camera.y
                char.cam_x = char.world_x - camera.x
            
    else:
        #the character is standing still, doing nothing
        if IsOnScreen(char):
            drawStillChar(move_conductor, char, char_rect)

def getTextSurfAndRect(given_font, text, x, y, color):
    """Loads a text surface and the rectangle that the text surface will be blitted onto. The arguments are the font of the text, the text
    to actually write to the surface, the color of the text, and the x y world coordinates of where to center the text."""
    text_surf = given_font.render('{0}'.format(text), True, color) #text surface to be blitted onto the screen later
    text_rect = text_surf.get_rect() #rectangle the text will be blitted onto
    text_rect.center = (x, y) #the center of where the text will appear
    return text_surf, text_rect

def drawCharState(main_char, text_box, text_box_rect, text_box_surf, status_box, text_font, level_font):
    """This function actually draws the user interface. It is passed all the different text surfaces and rectangles to draw, as well as
    main_char (to get certain attributes from that will be drawn to the screen). All the text surfaces and rectangles are only defined once
    (outside of the game loop)."""
    # All the boxes based on attributes must be redrawn every time to reflect changes in certain attributes of main_char:
    health_box_surf, health_box_rect = getTextSurfAndRect(text_font, '{0}%'.format(main_char.getPercentHealth()), WINWIDTH // 2 + 15, WINHEIGHT - 40, WHITE)
    level_text_surf, level_text_rect = getTextSurfAndRect(level_font, 'Level:{0}'.format(main_char.level), 100, WINHEIGHT - 40, BLACK)
    exp_text_surf, exp_text_rect = getTextSurfAndRect(text_font, 'Level Completion: {0}%  '.format(main_char.getPercentExp()), WINWIDTH - 130, WINHEIGHT - 75, BLACK)
    stam_text_surf, stam_text_rect = getTextSurfAndRect(text_font, 'Max Health: {0}'.format(main_char.full_health), WINWIDTH - 125, WINHEIGHT - 50, BLACK)
    attack_text_surf, attack_text_rect = getTextSurfAndRect(text_font, 'Attack Power: {0}'.format(main_char.attack_power), WINWIDTH - 125, WINHEIGHT - 25, BLACK)
    #level_box image is redefined here because box dimensions may change based on # of digits(i.e. lvl 1 vs. lvl 10)
    level_box = pygame.transform.scale(IMAGESDICT['text box'], (level_text_rect.width, level_text_rect.height))
    # Actually draw the text/box images to the screen:
    DISPSURFACE.blit(level_box, level_text_rect)
    DISPSURFACE.blit(level_text_surf, level_text_rect)
    DISPSURFACE.blit(text_box, text_box_rect)
    DISPSURFACE.blit(text_box_surf, text_box_rect)
    #the status box on the right side of the screen being drawn:
    DISPSURFACE.blit(status_box, exp_text_rect)
    DISPSURFACE.blit(exp_text_surf, exp_text_rect)
    DISPSURFACE.blit(stam_text_surf, stam_text_rect)
    DISPSURFACE.blit(attack_text_surf, attack_text_rect)
    #drawing the background for the health box - green if high health, yellow if low, red if extremely low
    if main_char.getPercentHealth() > 50:
        pygame.draw.rect(DISPSURFACE, GREEN, health_box_rect)
    elif main_char.getPercentHealth() <= 50 and main_char.getPercentHealth() > 20:
        pygame.draw.rect(DISPSURFACE, ORANGE, health_box_rect)
    else: #health below or at 20%
        pygame.draw.rect(DISPSURFACE, RED, health_box_rect)
    DISPSURFACE.blit(health_box_surf, health_box_rect)
    
def drawButtons(save_box_surf, save_box_rect, return_box_surf, return_box_rect, over_save_button, over_return_button):
    """This function draws the 'main menu' and 'save game' buttons to the display surface, depending on whether we are moused over
    the surface or not. It is passed all the different surfaces and rectangles to draw, and the variables telling us whether or not
    we are moused over the different buttons, so we know which image to draw onto the surface."""
    if over_save_button: #if moused over
        save_box = pygame.transform.scale(IMAGESDICT['button down'], (save_box_rect.width, save_box_rect.height))
    else: #not moused over
        save_box = pygame.transform.scale(IMAGESDICT['button up'], (save_box_rect.width, save_box_rect.height))
    if over_return_button:
        return_box = pygame.transform.scale(IMAGESDICT['button down'], (return_box_rect.width, return_box_rect.height))
    else:
        return_box = pygame.transform.scale(IMAGESDICT['button up'], (return_box_rect.width, return_box_rect.height))
    DISPSURFACE.blit(save_box, save_box_rect)
    DISPSURFACE.blit(save_box_surf, save_box_rect)
    DISPSURFACE.blit(return_box, return_box_rect)
    DISPSURFACE.blit(return_box_surf, return_box_rect)
    
def setSpawnPosition(char, camera, x, y):
    """Change the camera variables and world coordinates to spawn the main character at the given location (x, y)."""
    camera.x += x
    camera.y += y
    char.world_x += x
    char.world_y += y
    
def IsOnScreen(char):
    """Returns true if the character is on the screen."""
    return char.cam_x <= WINWIDTH and char.cam_x >= -50 and char.cam_y <= WINHEIGHT and char.cam_y >= -50

def IsTileOnScreen(x, y):
    """Returns true if the tile is on the screen."""
    return x <= WINWIDTH and x >= -TILESIZE or y <= WINHEIGHT and y >= -TILESIZE #use a slight buffer so we draw a little more than the actual screen size

def saveGame(char, camera):
    """Saves the game by writing the char and camera objects (the state of the game objects) to pickle files."""
    with open("saved_char.pickle", "wb") as file:
        pickle.dump(char, file)
    with open("saved_camera.pickle", "wb") as file:
        pickle.dump(camera, file)

def loadGame():
    """Loads the game by loading the char and camera pickle objects. Then returns those objects."""
    with open("saved_char.pickle", "rb") as file:
        char = pickle.load(file)
    with open("saved_camera.pickle", "rb") as file:
        camera = pickle.load(file)
    return char, camera