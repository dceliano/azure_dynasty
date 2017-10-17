#Azure Dynasty
#Dominic Celiano, C3C
#CS 210 - Section T1A
#
# Azure dynasty is a role-playing game in which a character (a knight/duke) spawns, and is able to kill monsters (i.e. skeletons) to level up. The character
# can save their progress to return to the game at a later time, and load that game through the main menu/splash screen.
#
#Documentation Statement: Dr. Bower ensured me to keep my program in separate files and not use getter/setter methods.
#                         http://inventwithpython.com/makinggames.pdf was referenced
#                         As well as  http://inventwithpython.com/pyganim/tutorial.html   and    http://usingpython.com/pygame/
#Images/spites/icons found from websites:Icon: http://icons.iconarchive.com/icons/iconmuseo/gardening/32/Castle-icon.png
#                     Splash Background Image: http://static.desktopnexus.com/wallpaper/1888649-1680x1050-[DesktopNexus.com].jpg?st=AVLsVbL5BJg6fKlLavzJ7g&e=1417041356
#                     Splash Background Music: http://opengameart.org/content/distant-plains  from Yubatake
#              All sprites were taken from the open-source websites of http://www.spriters-resource.com/ or http://opengameart.org/
###################################################################################################################
# The file only contains functions which contain game loops (i.e. the showSplashScreen() and runGame() functions) #
###################################################################################################################

import pygame, pickle
import pyganim #python module used for animation - the pyganim.py file is included in file and found at http://inventwithpython.com/pyganim/index.html#about
from pygame.locals import *
from Azure_Dynasty_Classes import * # The DISPSURFACE is created here since it is called before anything else is done
from Azure_Dynasty_Functions import *

#Adjust these constants as desired to change how the game is played:
FPS = 30 # Number of frames updated to the screen per second
WINWIDTH = 640
WINHEIGHT = 480
MAIN_CHAR_WALKRATE = 6 #how fast the main character moves
NUM_SKELS = 10
SKEL_ATTK_POW = 1.4
SKEL_HEALTH = 8
SKEL_WALKRATE = 2

#           r    g    b
BLACK =   ( 0 ,  0 ,  0 )
WHITE =   (255, 255, 255)
RED =     (255,  0 ,  0 )
PURPLE =  (200,  0 , 150)
ORANGE =  (255, 128,  0 )
GREEN =   ( 0 , 200,  0 )
YELLOW =  (255, 255,  0 )
        

def main():
    global FPSCLOCK, DISPSURFACE, IMAGESDICT # These global variables must be defined here because they can be defined only after PyGame is initialized
    
    pygame.init() # initialize PyGame - this must be done before things like FPSCLOCK are defined.
    FPSCLOCK = pygame.time.Clock() #create a clock object used to control the FPS of the game
    DISPSURFACE = pygame.display.get_surface()
    
    #A global dictionary that will hold load and hold all the image surfaces returned by pygame.image.load()
    IMAGESDICT = {'splash bkgd': pygame.image.load('images/splash_background.jpg'),
                  'down standing': pygame.image.load('sprites/mainwalkdown.png'),
                  'up standing': pygame.image.load('sprites/mainwalkup.png'),
                  'left standing': pygame.image.load('sprites/mainwalkleft.png'),
                  'right standing': pygame.image.load('sprites/mainwalkright.png'),
                  'down wielding': pygame.image.load('sprites/mainattackdown.png'),
                  'up wielding': pygame.image.load('sprites/mainattackup.png'),
                  'left wielding': pygame.image.load('sprites/mainattackleft.png'),
                  'right wielding': pygame.image.load('sprites/mainattackright.png'),
                  'text box': pygame.image.load('ui/parchment.png')}
    
    action = showSplashScreen() #show the splash screen until the user either loads or runs a game
    while True: #loop the interaction between the splash screen so it goes on forever.
        if action == 'load':
            main_char, camera = loadGame()
            action = runGame(main_char, camera)
        else: #if we don't need to load, run the main game loop
            main_char = None # make sure the main_char object is not defined (since it is a new game)
            action = runGame()
                
        
def runGame(main_char = None, camera = None):
    """main_char is optional parameter that is only passed if we just loaded a game."""
    mouse_x, mouse_y = (0,0) #define these here to clear whatever happened on the splash screen
    char_just_died = False #used later to break out of game loop
    
    # Setting up the variables for main character:   
    main_anim_objs = loadPygAnimObjs('mainwalkup mainwalkdown mainwalkright mainwalkleft mainattackup mainattackdown mainattackright mainattackleft', 3, 0.1) #load all the animation objects to be drawn onto the screen
    # The move conductor will either play or stop the animation
    # Have the animation objects managed by a conductor.
    # With the conductor, we can call play() and stop() on all the animation
    # objects at the same time, so that way they'll always be in sync with each other.
    main_move_conductor = pyganim.PygConductor(main_anim_objs)
    
    main_width = IMAGESDICT['up standing'].get_rect().size[0] #width of image
    main_height = IMAGESDICT['up standing'].get_rect().size[1] #height
    #Actually create the main character object, but only if it is a new game. Also create the camera object.
    if not main_char and not camera: #if these variables are not defined
        camera = Camera(0, 0) #create a camera object
        main_char = Character(WINWIDTH // 2 - (main_width // 2), WINHEIGHT // 2 - (main_height // 2), main_width, main_height, MAIN_CHAR_WALKRATE, camera)
        setSpawnPosition(main_char, camera, 150, 200) #spawn the character at (150,200)
    
    #Setting up the variables for 'skeleton' monsters:
    skel_anim_objs = loadPygAnimObjs('skelwalkup skelwalkdown skelwalkright skelwalkleft skelattackup skelattackdown skelattackright skelattackleft', 8, 0.2)
    skel_move_conductor = pyganim.PygConductor(skel_anim_objs)
    
    skel_width = pygame.image.load('sprites/skelwalkup.png').get_rect().size[0]
    skel_height = pygame.image.load('sprites/skelwalkup.png').get_rect().size[1]

    skels = [] #blank list to hold skeleton objects
    skel_rects = [] #blank list to hold skeleton rectangle objects

    # Object used for drawing the map:
    map_obj, water_rects = getMapObj() #contains the x, y coordinates of each tile, while water_rects holds the world coordinates of all the tiles with water
    
    # Surfaces, fonts, and rectangles for drawing the UI (level box, etc.). Some are also defined inside the game loop as well, to reflect attribute changes
    level_font = pygame.font.SysFont('bookmanoldstyle', 40) #the font used for displaying the level of the character
    text_font = pygame.font.SysFont('bookmanoldstyle', 20) #the font used for everything else
    #some surfaces/rectangles must be defined here, even though they are redefined later, only to use the dimensions of their rectangles
    #the first text box
    text_box_surf, text_box_rect = getTextSurfAndRect(text_font, 'Health:    ', WINWIDTH // 2 - 37, WINHEIGHT - 40, BLACK)
    text_box = pygame.transform.scale(IMAGESDICT['text box'], (text_box_rect.width, text_box_rect.height))
    #status_box, which keeps track of total health, exp to level, and attack power is defined here
    exp_text_rect = getTextSurfAndRect(text_font, 'Level Completion: {0}%  '.format(main_char.getPercentExp()), WINWIDTH - 130, WINHEIGHT - 75, BLACK)[1]
    status_box = pygame.transform.scale(IMAGESDICT['text box'], (exp_text_rect.width, exp_text_rect.height * 3))
    #buttons to save game or return to the main menu
    save_box_surf, save_box_rect = getTextSurfAndRect(text_font, '  Save Game  ', 70, 50, WHITE)
    return_box_surf, return_box_rect = getTextSurfAndRect(text_font, '  Main Menu  ', 70, 20, WHITE)
    
    #play the background music for the game
    pygame.mixer.music.load('the_kings_crowning.mp3')
    pygame.mixer.music.play(-1, 0) #start the music at 0 - it will loop until stopped 
    
        
    while True: #main game loop 
        # Resetting a couple variables that should by default by False:
        mouse_clicked = False
        main_char.just_leveled = False
        
        # Updating the water rectangles so that their coordinates depend on the camera's position
        moving_water_rects = [] #water rects that stay in the same world position
        for water_rect in water_rects:
            moving_water_rects.append(pygame.Rect(water_rect.x - camera.x, water_rect.y - camera.y, TILESIZE, TILESIZE))
        
        # Drawing the map:
        drawMap(map_obj, camera)
        
        # Spawn all of the necessary skeletons so there are always NUM_SKELS of them on the map
        if len(skels) < NUM_SKELS:
            for i in range(len(skels), NUM_SKELS): #add however many skel/skel_rect objects we need
                x_spawn = random.randint(500, 5000) #spawn each skeleton in a random spot
                y_spawn = random.randint(500, 1000)
                skels.append(Monster(x_spawn, y_spawn, skel_width, skel_height, SKEL_WALKRATE, camera, SKEL_ATTK_POW, SKEL_HEALTH)) #add a skeleton object
                skel_rects.append(skels[i].createRectangle()) #create the rectangle objects for each skeleton
                skels[i].moving_down = True #the initial direction of the skeleton
        for i in range(NUM_SKELS):
            skel_rects[i] = skels[i].createRectangle() #update the rectangle the skeleton will be blitted onto
        
        main_char_rect = main_char.createRectangle() # the rectangle that the main character animation will be blitted onto
        
        for event in pygame.event.get(): # event handling loop for user input
            
            if event.type == QUIT:
                terminate()
                
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                
                if event.key == K_a and main_char.wielding:
                    main_char.attacking = True
                if event.key == K_r and main_char.dead:
                    char_just_died = True #variable used later
                if event.key == K_LEFT:
                    main_char.moving_left = True
                    main_char.moving_right = False
                    if not main_char.moving_up and not main_char.moving_down:
                        # only change the direction to up if the player wasn't moving up/down
                        main_char.direction = 'left'
                elif event.key == K_RIGHT:
                    main_char.moving_right = True
                    main_char.moving_left = False
                    if not main_char.moving_up and not main_char.moving_down:
                        main_char.direction = 'right'
                elif event.key == K_UP:
                    main_char.moving_up = True
                    main_char.moving_down = False
                    if not main_char.moving_left and not main_char.moving_right:
                        # only change the direction to up if the player wasn't moving left/right
                        main_char.direction = 'up'
                elif event.key == K_DOWN:
                    main_char.moving_down = True
                    main_char.moving_up = False
                    if not main_char.moving_left and not main_char.moving_right:
                        main_char.direction = 'down'
                
            elif event.type == KEYUP:
                if event.key == K_w: #wielding or unwielding weapon
                    if main_char.wielding:
                        main_char.wielding = False
                    else:
                        main_char.wielding = True
                if event.key == K_a and main_char.wielding:
                    main_char.attacking = False
                #Stopping the player's movement in a certain direction(s)
                if event.key == K_UP:
                    main_char.moving_up = False
                    #If the player was moving in a sideways direction before, change the direction the player is facing.
                    if main_char.moving_left:
                        main_char.direction = 'left'
                    if main_char.moving_right:
                        main_char.direction = 'right'
                elif event.key == K_LEFT:
                    main_char. moving_left = False
                    if main_char.moving_up:
                        main_char.direction = 'up'
                    if main_char.moving_down:
                        main_char.direction = 'down'
                elif event.key == K_RIGHT:
                    main_char.moving_right = False
                    if main_char.moving_up:
                        main_char.direction = 'up'
                    if main_char.moving_down:
                        main_char.direction = 'down'
                elif event.key == K_UP:
                    main_char.moving_up = False
                elif event.key == K_DOWN:
                    main_char.moving_down = False
                    if main_char.moving_left:
                        main_char.direction = 'left'
                    if main_char.moving_right:
                        main_char.direction = 'right'
            elif event.type == MOUSEMOTION:
                mouse_x, mouse_y = event.pos
            elif event.type == MOUSEBUTTONUP:
                mouse_x, mouse_y = event.pos
                mouse_clicked = True
        
        # Handling possible game reset:
        if char_just_died: # If the main_char just died and we returned to the main menu - show the splash screen and then break out of the game loop so the game resets
            action = showSplashScreen() #show the splash screen until the user either loads or runs a game                    
            char_just_died = False
            pygame.mixer.music.stop() #stop the background music
            return action #exit this game loop and return the action of whether we need to load a game or not.
        
        # Handling each skeleton's battle, movement, etc. - only do this stuff if the main character is alive
        if main_char.dead == False:
            for i in range(len(skels) - 1, -1, -1): #For every skeleton object, perform all the code below.
                                                    #It is necessary to iterate over the list in reverse, so deleting items from it works.
                rand_num = random.randint(1, 60)
                if rand_num == 1 and not skels[i].attacking: # this will happen, on average, once every 2 seconds(since 30 FPS * 2 = 60)
                    skels[i].changeDirectionRandom() #change the direction the monster is moving
                
                # Player attacking monster:
                if main_char_rect.colliderect(skel_rects[i]): #an attack may not have been successfully landed, but we have definitely 'aggroed' the monster
                    main_char.performBattle(skels[i], skel_rects[i])
                if skels[i].aggroed and not skels[i].chasing: # Face the player
                    skels[i].facePlayer(main_char) 
                    
                # Monster chasing player
                if skels[i].aggroed and not main_char_rect.colliderect(skel_rects[i]):
                    # If the monster is out of attack range but aggroed, it will chase the main_char until its rectangle collides with the character's - combat then starts again
                    skels[i].chasing = True
                if skels[i].chasing:
                    skels[i].chaseMainChar(main_char, main_char_rect)
                           
                # Monster attacking player:
                if skels[i].attacking and skel_rects[i].colliderect(main_char_rect):
                    skels[i].performMonsterBattle(main_char)
    
                # Seeing whether monster is dead
                if skels[i].health <= 0:
                    skels[i].dying = True #it will be dying before it is actually dead and deleted
                    death_anim_frames = 6 #the number of image files used for the animation
                    death_frame_time = 0.2 #arbitrary value
                    
                    if not hasattr(skels[i], 'start_death_time'): #this code will only happen once
                        skels[i].start_death_time = time.time() #mark the start time of when the monster starts dying
                        #Recreate the anim_objs object for dying to reset the frame at 0 - this is done so the dying animation looks the same each time.
                        death_anim_obj = loadDeathPygAnimObj(death_anim_frames, death_frame_time, 'skeldie')
                        
                    elapsed_dying_time = time.time() - skels[i].start_death_time #the time the dying animation has been going on for
                    if elapsed_dying_time <= (death_anim_frames * death_frame_time): #if the skeleton dying animation is still going on
                        skels[i].performDeathAnimation(death_anim_obj, camera)
                    else: #The dying animation is over - the monster is now officially dead
                        skels[i].dead = True
                        main_char.experience += skels[i].full_health #add experience to the character
                        del skels[i]
                        del skel_rects[i]
                    
                else: #if monster is still alive, draw/animate it
                    performMovement(skels[i], skel_rects[i], skel_move_conductor, skel_anim_objs, camera, moving_water_rects)
            
        # Drawing the main character, or playing its death animation:
        if main_char.health <= 0: #if dying or dead - this does essentially the same stuff as when a monster dies, but plays a 'game over' screen as well
            main_char.dead = True
            #The big 'game over' text
            game_over_font = pygame.font.SysFont('realvirtue', 125)
            game_over_surf, game_over_rect = getTextSurfAndRect(game_over_font, 'Game Over', WINWIDTH // 2, WINHEIGHT // 2, RED)
            pygame.draw.rect(DISPSURFACE, BLACK, game_over_rect)
            DISPSURFACE.blit(game_over_surf, game_over_rect)
            #The text telling you to go back to the home screen - drawn right below the game over text
            return_font = pygame.font.SysFont('realvirtue', 35)
            return_surf, return_rect = getTextSurfAndRect(return_font, "Press 'r' to return to the Main Menu.", WINWIDTH // 2, WINHEIGHT // 2 + (game_over_rect.height // 2) + 25, RED)
            pygame.draw.rect(DISPSURFACE, BLACK, return_rect)
            DISPSURFACE.blit(return_surf, return_rect)
            
            
        else: #main_char is alive
            performMovement(main_char, main_char_rect, main_move_conductor, main_anim_objs, camera, moving_water_rects) #draw/animate the main char
            if main_char.experience >= main_char.exp_to_level: #check if the character has leveled up
                main_char.levelUp()
                pygame.draw.rect(DISPSURFACE, YELLOW, main_char_rect) #blink the character yellow if so
                congrats_font = pygame.font.SysFont('realvirtue', 125)
                congrats_surf, congrats_rect = getTextSurfAndRect(congrats_font, 'LEVELED UP!', WINWIDTH // 2, WINHEIGHT // 2, YELLOW)
                DISPSURFACE.blit(congrats_surf, congrats_rect)
                main_char.just_leveled = True
            # Drawing the user interface with the function. The function is only passed the values not defined inside the game loop.
            drawCharState(main_char, text_box, text_box_rect, text_box_surf, status_box, text_font, level_font)
            drawButtons(save_box_surf, save_box_rect, return_box_surf, return_box_rect, False, False)
        
        # Handle mouse-clicking or motion - this is done after drawing the buttons incase they need to be redrawn.
        if mouse_clicked:
            if save_box_rect.collidepoint(mouse_x, mouse_y): #if we are over (and clicked on) the 'save game' text rectangle
                saveGame(main_char, camera)
            elif return_box_rect.collidepoint(mouse_x, mouse_y): #clicked on 'main menu'
                saveGame(main_char, camera)
                action = showSplashScreen()
                pygame.mixer.music.stop() #stop the background music
                return action #exit the game loop and return the action of whether we need to load a game or not.
        else: #must be a mouse over event
            if save_box_rect.collidepoint(mouse_x, mouse_y): #if we are over the 'save game' text rectangle
                drawButtons(save_box_surf, save_box_rect, return_box_surf, return_box_rect, True, False)
            elif return_box_rect.collidepoint(mouse_x, mouse_y):
                drawButtons(save_box_surf, save_box_rect, return_box_surf, return_box_rect, False, True)
        
        pygame.display.update() #update/redraw the screen
        FPSCLOCK.tick(FPS) # make sure the FPS stays at the value FPS
        
        if main_char.just_leveled: #if we just leveled up, freeze the screen for a second so it shows the congratulations text for longer
            time.sleep(1)
        
        
        
def showSplashScreen():
    mouse_x, mouse_y = (0,0) #define these here to clear whatever happened earlier
    """Show the splash screen until the user either pressed 'load game' or 'new game'."""
    splash_bgd = pygame.transform.scale(IMAGESDICT['splash bkgd'], (WINWIDTH, WINHEIGHT)) #background image resized according to screen size
    title_font = pygame.font.SysFont('nightclubbtn', 72) #set up the font for the title in the splash screen
    other_font = pygame.font.SysFont('swtxt', 45) #the other text used for the rest of the splash screen
    
    # create the surfaces to hold the game text in the splash screen
    game_title_surf, game_title_rect = getTextSurfAndRect(title_font, 'Azure Dynasty', WINWIDTH // 2, WINHEIGHT // 5, WHITE)
    new_game_surf, new_game_rect = getTextSurfAndRect(other_font, 'New Game', WINWIDTH // 2, 4 * WINHEIGHT // 7, WHITE)
    load_game_surf, load_game_rect = getTextSurfAndRect(other_font, 'Load Game', WINWIDTH // 2, 5 * WINHEIGHT // 7, WHITE)
    
    #play some background music for the splash screen
    pygame.mixer.music.load('DistantPlains.ogg')
    pygame.mixer.music.play(-1, 0.6) #start the music at 0.6 - it will loop until stopped 
    
    while True: #the 'game loop' for the splash screen
        mouse_clicked = False
        #display the background image and all of the text on the splash page
        DISPSURFACE.blit(splash_bgd, (0, 0))
        DISPSURFACE.blit(game_title_surf, game_title_rect)
        DISPSURFACE.blit(new_game_surf, new_game_rect)
        DISPSURFACE.blit(load_game_surf, load_game_rect)
        
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == MOUSEMOTION:
                mouse_x, mouse_y = event.pos
            elif event.type == MOUSEBUTTONUP:
                mouse_x, mouse_y = event.pos
                mouse_clicked = True
                
        if mouse_clicked:
            if new_game_rect.collidepoint(mouse_x, mouse_y):
                pygame.mixer.music.stop() #stop the background music
                break #an option has been selected, so break out of this game loop
            elif load_game_rect.collidepoint(mouse_x, mouse_y):
                pygame.mixer.music.stop() #stop the background music
                #break
                return 'load' #an option has been selected, so return to the main function
        else: #must be a mouse over event
            if new_game_rect.collidepoint(mouse_x, mouse_y): #if we are over the 'new game' text rectangle
                new_game_surf = other_font.render('New Game', True, PURPLE) #recreate the text surface with a new color
                load_game_surf = other_font.render('Load Game', True, WHITE)
            elif load_game_rect.collidepoint(mouse_x, mouse_y):
                load_game_surf = other_font.render('Load Game', True, PURPLE)
                new_game_surf = other_font.render('New Game', True, WHITE)
            else: #none of the text is being moused over, so make sure all the text is reset to its default color.
                new_game_surf = other_font.render('New Game', True, WHITE)
                load_game_surf = other_font.render('Load Game', True, WHITE) 
                 
        pygame.display.update() #update/redraw the screen
        FPSCLOCK.tick(FPS)
    

if __name__ == '__main__':
    main()