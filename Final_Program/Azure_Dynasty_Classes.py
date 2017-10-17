###########################################################
## After importing all modules and defining the necessary##
## constants, this file only contains the Monster,       ##
## Character, and Camera classes.                        ##
###########################################################

#IMPORTS
import pygame, random
#from pygame.locals import *

#INITIATE PYGAME AND DEFINE CERTAIN CONSTANTS NEEDED
WINWIDTH = 640
WINHEIGHT = 480
RED = (255,  0 ,  0 )
DISPSURFACE = pygame.display.set_mode((WINWIDTH, WINHEIGHT)) #create the screen object with its height and width

pygame.init()

#THE CLASSES:
class Monster:
    """This class holds all the attributes and methods of each individual monster and the main character (Character inherits from this
    class). When a new monster is created, it needs to pass certain values to the Monster class, such as the position of the monster
    to spawn at, its width, height, walkrate, attack power, health, and also the camera object, which is in a separate class."""
    def __init__(self, x, y, width, height, walkrate, camera, attack_pow, health):
        """Instantiates certain attributes of the monster or character. Everything is self-explanatory, except camera, which is an object
        passed in that holds the x and y coordinates of the 'camera' - this essentially tells us where to draw the monster or character
        on the screen. Also necessary to note is that (x, y) is the spawn point of the skeleton, while height and width are the dimensions
        of the image file for the monster/character."""
        self.full_health = health
        self.health = self.full_health #health is originally equal to full health
        self.attack_power = attack_pow #how much damage the attacks will do
        self.direction = 'down' #the default direction the character/monster will start facing
        self.walkrate = walkrate #how fast the object will move
        self.world_x = x #the top left coordinates of the rectangle to be created (w.r.t. the top left of the screen) - this value WILL NOT change
        self.world_y = y
        self.cam_x = self.world_x - camera.x #the coordinates with respect to the top left coordinates of the camera. Initially, the same as the world coordinates
        self.cam_y = self.world_y - camera.y
        self.width = width
        self.height = height
        #Setting up a bunch of initial conditions:
        self.moving_up = self.attacking = self.would_be_in_water = self.wielding = self.moving_down = self.moving_left = False
        self.moving_right = self.aggroed = self.chasing = self.dying = self.dead = False
        
    def createRectangle(self):
        """Creates (or recreates/updates) the rectangle that will be used to detect collisions, and then returns it.
        This rectangle will be directly under the monster/character image - the animation/image will be blitted (copied) onto this rectangle."""
        self.rectangle = pygame.Rect(self.cam_x, self.cam_y, self.width, self.height)
        return self.rectangle

    def stopMovement(self):
        """Stops all movement of the character."""
        self.moving_down = self.moving_left = self.moving_right = self.moving_up = False

    def facePlayer(self, main_char):
        """This method only applies to a monster. Given the main_char object to face, the monster object faces the main character
        depending on the monster's position relative to the main character. """
        if main_char.cam_x < self.cam_x:
            self.direction = 'left'
        elif main_char.cam_x > self.cam_x:
            self.direction = 'right'
        elif main_char.cam_y < self.cam_y:
            self.direction = 'up'
        elif main_char.cam_y > self.cam_y:
            self.direction = 'down'
            
    def changeDirectionRandom(self):
        """Change the direction of the object (in this case, a monster) randomly so it goes in a direction it wasn't going before. 
        Used for monsters changing their directions periodically. This method only applies to monsters."""
        rand_num = random.randint(1, 4) #get random direction
        if rand_num == 1 and self.direction != 'up': #must be a direction change
            self.direction = 'up'
            self.stopMovement() #stop movement in every other direction
            self.moving_up = True
        elif rand_num == 2 and self.direction != 'down':
            self.direction = 'down'
            self.stopMovement()
            self.moving_down = True
        elif rand_num == 3 and self.direction != 'right':
            self.direction = 'right'
            self.stopMovement()
            self.moving_right = True
        elif rand_num == 4 and self.direction != 'left':
            self.direction = 'left'
            self.stopMovement()
            self.moving_left = True

    def chaseMainChar(self, char, char_rect):
        """This method only applies to a monster. When the main character is running away, this method is passed the main character object
        and its rectangle to determine which direction to go in to chase the monster. As soon as a collision occurs between the monster's
        rectangle and the main_char's rectangle, the method will stop all movement of the character and stop chasing it.
        This method can make the monster move diagonal, but won't if it doesn't need to."""
        self.attacking = False
        if char.cam_x < self.cam_x:
            self.direction = 'left'
            self.stopMovement() #stop movement in all other directions
            self.moving_left = True
            if char.cam_y < self.cam_y: #moving up as well (for diagonal movement)
                self.moving_up = True
            elif char.cam_y > self.cam_y:
                self.moving_down = True
        elif char.cam_x > self.cam_x:
            self.direction = 'right'
            self.stopMovement()
            self.moving_right = True
            if char.cam_y < self.cam_y:
                self.moving_up = True
            elif char.cam_y > self.cam_y:
                self.moving_down = True
        elif char.cam_y < self.cam_y: #only happens if moving straight up or straight down
            self.direction = 'up'
            self.stopMovement()
            self.moving_up = True
        elif char.cam_y > self.cam_y:
            self.direction = 'down'
            self.stopMovement()
            self.moving_down = True
        if self.rectangle.colliderect(char_rect):
            self.stopMovement()
            self.attacking = True
            self.chasing = False

    def attack(self, enemy):
        """Given an enemy object, change the health of the enemy an amount dependent on the attack power of the self object."""
        enemy.health -= (self.attack_power / 10)
        
    def performDeathAnimation(self, death_anim_obj, camera):
        """Perform the death animation for the monster given the death animation object. This function uses PygAnim to play the animation
        and blit it to the screen. It also updates the position of the skeleton relative to the camera."""
        #update the monster's position relative to the camera so it stays in the correct spot on the screen
        self.cam_y = self.world_y - camera.y
        self.cam_x = self.world_x - camera.x   
        self.dying = True #this variable will remain True while the death animation is occurring
        death_anim_obj.play()
        death_anim_obj.blit(DISPSURFACE, self.rectangle)

    def performMonsterBattle(self, enemy):
        """This method only applies to monsters. It determines whether the monster has successfully landed an attack, then calls the attack
        function if necessary. This method is similar to the 'perform battle' method for the main character, but this method doesn't affect 
        what any other character is doing - it only affects the monster"""
        if self.direction == 'right' and self.cam_x < enemy.cam_x: #successful right-facing attack by monster
            self.attack(enemy)
        elif self.direction == 'left' and self.cam_x > enemy.cam_x:
            self.attack(enemy)
        elif self.direction == 'up' and self.cam_y > enemy.cam_y:
            self.attack(enemy)
        elif self.direction == 'right' and self.cam_y < enemy.cam_y:
            self.attack(enemy)
        
class Character(Monster):
    """This class contains all the attributes and methods of the main character, as well as those of a monster (since it inherits from
    the Monster class). It contains attributes and methods the monster class does not need, such as experience and leveling up.
    Only one object is created using this class since there is only one main character."""
    def __init__(self, x, y, width, height, walkrate, camera):
        """Initiates all the attributes of the main character, and calls the initiate method of the super class. This class
        does not take as many arguments since the start attack and start health of the character is always the same."""
        super().__init__(x, y, width, height, walkrate, camera, 1, 100) #main character starts with 1 attack and 100 health
        self.level = 1 #start at level 1
        self.experience = 0
        self.full_health = self.health #full_health is what the health should be if we are full
        self.exp_to_level = 20 * 2 ** self.level
        
    def levelUp(self):
        """This method is called whenever the main character 'levels up'. Whenever it levels up, it gains attack power and maximum possible
        health. The level is also of course increased by one, and the experience counter changes to reflect the new level."""
        self.level += 1
        self.experience -= self.exp_to_level #get rid of all the experience from the last level
        self.exp_to_level = 20 * 2 ** self.level #calculate the experience needed for the next level - it requires more exp. with higher lvl
        self.full_health = 80 + (40 * self.level) #calculate the new amount of health points - the number increases by 20 each level
        self.health = self.full_health #reset the character's health to full
        self.attack_power = int(2 ** self.level / 2)
        
    def performBattle(self, monst, monst_rect):
        """Given a monster and its rectangle, this method is called whenever the character is close to a monster and might be attacking it.
        It determines if a successful attack has been landed on the monster, and calls the attack method if that is the case. It also sets the 
        'aggroed' attribute of the monster to True, making the monster chase the character. A red rectangle will show up behind the monster if 
        it is attacked."""
        if not monst.aggroed:
            monst.aggroed = True # The monster has been encountered ('aggroed') - it will start chasing the main_char if necessary
        if self.attacking: # may have successfully landed an attack
            #successful right-facing attack by character, and monster not dying/dead:
            if self.direction == 'right' and self.cam_x < monst.cam_x and not monst.dying and not monst.dead:
                monst.attacking = True
                monst.chasing = False #stop the monster's chasing, since it is now in direct combat
                monst.stopMovement() #make sure all movement with the monster is stopped
                self.attack(monst) #actually attack the monster
                pygame.draw.rect(DISPSURFACE, RED, monst_rect) #blit a red background on the monster so the user knows they're attacking it
            elif self.direction == 'left' and self.cam_x > monst.cam_x and not monst.dying and not monst.dead:
                monst.attacking = True
                monst.chasing = False
                monst.stopMovement()
                self.attack(monst)
                pygame.draw.rect(DISPSURFACE, RED, monst_rect)
            elif self.direction == 'up' and self.cam_y > monst.cam_y and not monst.dying and not monst.dead:
                monst.attacking = True
                monst.chasing = False
                monst.stopMovement()
                self.attack(monst)
                pygame.draw.rect(DISPSURFACE, RED, monst_rect)
            elif self.direction == 'down' and self.cam_y < monst.cam_y and not monst.dying and not monst.dead:
                monst.attacking = True
                monst.chasing = False
                monst.stopMovement()
                self.attack(monst)
                pygame.draw.rect(DISPSURFACE, RED, monst_rect)
                
    def getPercentHealth(self):
        """Returns how much health the main character has, as a percentage, which is then blitted onto the user interface."""
        return int(100 * (self.health / self.full_health))
    
    def getPercentExp(self):
        """Returns far into the current level a character is, as a percentage, which is then blitted onto the user interface."""
        return int(100 * (self.experience / self.exp_to_level))
        
class Camera:
    """Camera's coordinates represents the top left corner of the screen, which moves around the world. The camera can see to the 
    right a distance of WINWIDTH and down a distance of WINHEIGHT. The camera changes depending on how the player moves. 
    Camera is set as a class so it can be easily used and modified."""
    def __init__(self, x, y):
        self.x = x
        self.y = y