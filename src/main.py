# Pursuit Protocol - a small pygame chase game
# Final project for the University of Helsinki Python Programming MOOC 2025 (Advanced Course)
import os, sys, random, math
import pygame

# Sprite images live in src/assets/, resolved relative to this file so the game runs from any directory
ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

def asset_path(filename):
    return os.path.join(ASSET_DIR, filename)

# Global variables for the main window size
max_window_width = 1280
max_window_height = 720
min_window_width = 0
min_window_height = 0

# The main class that contains all the required information for the game, Pursuit Protocol
class PursuitProtocol:

    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((max_window_width, max_window_height))
        pygame.display.set_caption("Pursuit Protocol")
        self.game_font_1 = pygame.font.SysFont("Times New Roman", 24)
        self.game_font_2 = pygame.font.SysFont("Times New Roman", 24)
        self.game_font_3 = pygame.font.SysFont("Times New Roman", 24) 
        self.game_font_4 = pygame.font.SysFont("Times New Roman", 24) 
        self.game_font_5 = pygame.font.SysFont("Times New Roman", 48)
        self.game_font_6 = pygame.font.SysFont("Times New Roman", 24)

        self.playTutorial = True

        self.challenge_level = 1 
        self.challenge_level_cap = 8

        self.newGame()

        self.clock = pygame.time.Clock()

        self.main_game_loop()

    #A nested class that is used to assign common instance variables like self.x and self.y through inheritance to other classes that are used to make sprites
    class ImageFactory:
        def __init__(self, outerclass, x, y, filename):
            self.x = x
            self.y = y
            self.outerclass = outerclass
            sprite = os.path.basename(filename)
            if "robot" in sprite:
                self.robotImage = pygame.image.load(filename)
                self.name = "robot"
                self.robot_max_x_boundary = max_window_width - self.robotImage.get_width()
                self.robot_max_y_boundary = max_window_height - self.robotImage.get_height()
            if "monster" in sprite:
                self.monsterImage = pygame.image.load(filename)
                self.name = "monster"
                self.monster_max_x_boundary = max_window_width - self.monsterImage.get_width()
                self.monster_max_y_boundary = max_window_height - self.monsterImage.get_height()
                self.outerclass = outerclass
            if "coin" in sprite:
                self.coinImage = pygame.image.load(filename)
                self.name = "coin"
                self.coin_max_x_boundary = max_window_width - self.coinImage.get_width()
                self.coin_max_y_boundary = max_window_height - self.coinImage.get_height()
            if "door" in sprite:
                self.doorImage = pygame.image.load(filename)
                self.name = "door"
                self.door_max_x_boundary = max_window_width - self.doorImage.get_width()
                self.door_max_y_boundary = max_window_height - self.doorImage.get_height()

    # The class for the main robot character
    class RobotClass(ImageFactory):

        def __init__(self, outerclass, x, y, vx, vy, filename):
            super().__init__(outerclass, x, y, filename)
            self.vx = vx
            self.vy = vy
            self.left = False
            self.right = False
            self.up = False
            self.down = False

        # These methods are used to move the robot horizontally/vertically while keeping the robot within the bounds of the game screen
        def horizontalMovement(self):
            if self.right and self.x <= self.robot_max_x_boundary:
                self.x += self.vx
            if self.left and self.x >= 0:
                self.x -= self.vx
        def verticalMovement(self):
            if self.down and self.y <= self.robot_max_y_boundary:
                self.y += self.vy
            if self.up and self.y >= 0:
                self.y -= self.vy

        # This method is used to draw the robot when its called
        def drawRobot(self):
            if self.name == "robot":
                self.outerclass.window.blit(self.robotImage, (self.x, self.y))

    #This class is used to create the monster sprites. Each mmonster has alternate velocities (self.patrolvx/vy and self.chasevx/vy) which changes depending on how close the robot character is to the one of the mosnter sprites
    class MonsterClass(ImageFactory):
        def __init__(self, outerclass, x, y, patrolvx, patrolvy, chasevx, chasevy, filename):
            super().__init__(outerclass, x, y, filename)
            self.left = False
            self.right = False
            self.up = False
            self.down = False
            self.patrolMode = True
            self.chaseMode = False
            self.baseSpeed = patrolvx
            self.patrolvx = patrolvx
            self.patrolvy = patrolvy
            self.chasevx = chasevx
            self.chasevy = chasevy
        
            self.monsterRespawn()

        #This method is used to respawn monsters at a random position when they go outside the bounds of the main game window. The respawn points are bounded to be...
        # ...inside the main game window's vertical boundary, and have a slight offset when spawning near the main window's horizontal boundary. self.startingDirection determines whether the monster starts at the right (1) or the left  (-1) of the screen.
        def monsterRespawn(self):
            self.startingDirection = random.choice([-1, 1])
            if self.startingDirection == 1:
                self.x = random.randint(self.outerclass.window.get_width(), self.outerclass.window.get_width() + 100)
                self.y = random.randint(0, self.monster_max_y_boundary)
                self.patrolvx = self.baseSpeed
            if self.startingDirection == -1:
                self.x = random.randint(-100, 0)
                self.y = random.randint(0, self.monster_max_y_boundary)
                self.patrolvx = self.baseSpeed

        def horizontalMovement(self):
            if self.startingDirection == 1:
                self.x -= self.patrolvx
                
            if self.startingDirection == -1:
                self.x += self.patrolvx

        #Used to draw the monster when its called
        def drawMonster(self):
            if self.name == "monster":
                self.outerclass.window.blit(self.monsterImage, (self.x, self.y))

    #This class is used to create the coin objects
    class CoinClass(ImageFactory):
        def __init__(self, outerclass, x, y, filename):
            super().__init__(outerclass, x, y, filename)

        #Used to draw the coin(s)
        def drawCoin(self):
            if self.name == "coin":
                self.outerclass.window.blit(self.coinImage, (self.x, self.y))

    #This class is used to draw the door and manage the locked/unlocked states
    class DoorClass(ImageFactory):
        def __init__(self, outerclass, x, y, filename):
            super().__init__(outerclass, x, y, filename)
            self.locked = True
            self.arrived = False

        #Draws the door
        def drawDoor(self):
            if self.name == "door":
                self.outerclass.window.blit(self.doorImage, (self.x, self.y))

        # Sets the door to be unlocked when the player gets the required amount of coins
        def doorUnlocked(self):
            self.locked = False

        # Sets the door to be locked until the player gets the required amount of coins
        def doorLocked(self):
            self.locked = True
        
        # Used to determine if robot character made contact with teh door after all the coins are obtained
        def reachedTheDoor(self):
            self.arrived = True
        
        # Resets the door status for each level
        def resetDoor(self):
            self.arrived = False

# This method manages the game winning state. It checks if all the requirements are met for the winning condition. If so, it increases the challenge level and pauses all movement in the game for the robot and the monster(s)
    def gameWon(self):
        if self.points == len(self.coinList) and self.door.locked == False:
            if not self.won:
                self.won = True
                self.lost = False
                if self.challenge_level < self.challenge_level_cap:
                    self.challenge_level += 1
            self.robot.vx = 0
            self.robot.vy = 0
            for i in range(len(self.monsterList)):
                self.monsterList[i].patrolvx = 0
                self.monsterList[i].patrolvy = 0
                self.monsterList[i].chasevx = 0
                self.monsterList[i].chasevy = 0
            self.door.arrived = True

# This method manages the game losing state. It checks if all the requirements are met for the losing condition, decreases the challenge level, and pauses all movement in the game for the robot and the monster(s)    
    def gameLost(self):
        if not self.lost:
            self.lost = True
            self.won = False
            if self.challenge_level > 1:
                self.challenge_level -= 1
            self.robot.vx = 0
            self.robot.vy = 0
            for i in range(len(self.monsterList)):
                self.monsterList[i].patrolvx = 0
                self.monsterList[i].patrolvy = 0
                self.monsterList[i].chasevx = 0
                self.monsterList[i].chasevy = 0
    
    #This method draws the tutorial text and information once at the start of the game
    def drawTutorial(self):
        self.window.fill((0, 225, 70))
        title = self.game_font_5.render("Welcome to Pursuit Protocol", True, (0, 0, 0))
        goal  = self.game_font_6.render("Goal: Collect all coins, unlock the door, avoid monsters.", True, (0, 0, 0))
        ctrl1 = self.game_font_6.render("Controls: Arrow Keys to move", True, (0, 0, 0))
        ctrl2 = self.game_font_6.render("Maximum Level: 8", True, (0, 0, 0))
        ctrl3 = self.game_font_6.render("Press Enter to Start / Continue", True, (0, 0, 0))

        text_center_x = self.window.get_width() // 2

        title_rect = title.get_rect(center=(text_center_x, 200))
        goal_rect  = goal.get_rect(center=(text_center_x, 300))
        ctrl1_rect = ctrl1.get_rect(center=(text_center_x, 350))
        ctrl2_rect = ctrl2.get_rect(center=(text_center_x, 400))
        ctrl3_rect = ctrl3.get_rect(center=(text_center_x, 450))

        self.window.blit(title, title_rect)
        self.window.blit(goal, goal_rect)
        self.window.blit(ctrl1, ctrl1_rect)
        self.window.blit(ctrl2, ctrl2_rect)
        self.window.blit(ctrl3, ctrl3_rect)

        pygame.display.flip()

    #New game state managed using this method, and this is also where the character objects are created. Character traits like monster count/aggression and coin amounts are given base values that scale with the player's current level.
    def newGame(self):
        base_monster_speed_patrol = 0.45
        base_monster_speed_chase = 0.57
        base_detection_radius = 70  
        base_num_coins = 2
        base_num_monsters = 1 

        speed_scale = 0.090               # per level increase
        radius_scale = 2                     # px per level
        coin_scale = 2                     # extra coins per level
        monster_scale = 1

        self.monster_patrol_speed = base_monster_speed_patrol + (self.challenge_level - 1) * speed_scale
        self.monster_chase_speed = base_monster_speed_chase + (self.challenge_level - 1) * speed_scale
        self.detection_radius = base_detection_radius + (self.challenge_level - 1) * radius_scale
        self.num_coins = base_num_coins + (self.challenge_level - 1) * coin_scale
        # One monster per level up to 3, three monsters for levels 4-6, and four from level 7 on
        if self.challenge_level >= 7:
            self.num_monsters = 4
        else:
            self.num_monsters = min(self.challenge_level, 3)

        self.coinBlueprint = pygame.image.load(asset_path("coin.png"))
        self.doorBlueprint = pygame.image.load(asset_path("door.png"))
        self.robotBlueprint = pygame.image.load(asset_path("robot.png"))
        self.monsterBlueprint = pygame.image.load(asset_path("monster.png"))

        self.won = False
        self.lost = False

        self.points = 0

        self.text_1 = self.game_font_1.render(f"Collect the coins. Watch out for monsters!", True, (0, 0, 0))
        self.text_2 = self.game_font_2.render(f"Number of Coins: {self.points}", True, (0, 0, 0))

        monsterStartingChanceLeftORRightValue = [-1, 1]
        if random.choice(monsterStartingChanceLeftORRightValue) > 0:
            monsterStartingSpawn_x_value = random.randint((self.window.get_width() - self.monsterBlueprint.get_width()) + 200, self.window.get_width() + 200)
        else:
            monsterStartingSpawn_x_value = random.randint(-200, 0)


        # Used to spawn the random coins
        self.coinList = [self.CoinClass(self, random.randint(0, max_window_width - self.coinBlueprint.get_width()), random.randint(0, max_window_height - self.coinBlueprint.get_height()), asset_path("coin.png")) for i in range(self.num_coins)]
        self.monsterList = [self.MonsterClass(self, 0, 0, self.monster_patrol_speed, self.monster_patrol_speed, self.monster_chase_speed, self.monster_chase_speed, asset_path("monster.png")) for i in range(self.num_monsters)]
        # Robot main character. Set to always spawn in the center of the screen
        self.robot = self.RobotClass(self, (max_window_width // 2) - (self.robotBlueprint.get_width() // 2), (max_window_height // 2) - (self.robotBlueprint.get_height() / 2), 1.7, 1.7, asset_path("robot.png"))
        self.door = self.DoorClass(self, random.randint(0, max_window_width - self.doorBlueprint.get_width()), random.randint(0, max_window_height - self.doorBlueprint.get_height()), asset_path("door.png"))

    #All the events are managed in this method. The movement for the robot character is turned off and on using its left/right/up/down instance variables. The tutorial is also set to show infinetly until the player presses "Enter"
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if self.playTutorial == True:
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER):
                    self.playTutorial = False
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.robot.right = True
                if event.key == pygame.K_LEFT:
                    self.robot.left = True
                if event.key == pygame.K_UP:
                    self.robot.up = True
                if event.key == pygame.K_DOWN:
                    self.robot.down = True
                if (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER) and (self.won == True or self.lost == True):
                        self.newGame()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    self.robot.right = False
                if event.key == pygame.K_LEFT:
                    self.robot.left = False
                if event.key == pygame.K_UP:
                    self.robot.up = False
                if event.key == pygame.K_DOWN:
                    self.robot.down = False

    #All game updates such as the movement updates of the monsters/robot, object collision boundaries, and the patrol/chase flags for monsters are formally updated in this method. 
    def game_updates(self):
        if self.robot.right or self.robot.left:
            self.robot.horizontalMovement()
        
        if self.robot.up or self.robot.down:
            self.robot.verticalMovement()

        #Robot's collision boundaries
        robotLeftSide = self.robot.x 
        robotRightSide = self.robot.x + self.robot.robotImage.get_width()
        robotBottomSide = self.robot.y + self.robot.robotImage.get_height()
        robotTopSide = self.robot.y 

        #Handles the collision boundaries for each coin and tells if the robot successfully overlaps with one
        for i in range(len(self.coinList)):
            coinLeftSide = self.coinList[i].x 
            coinRightSide = self.coinList[i].x + self.coinList[i].coinImage.get_width()
            coinBottomSide = self.coinList[i].y + self.coinList[i].coinImage.get_height()
            coinTopSide = self.coinList[i].y 

            if robotLeftSide < coinRightSide and robotRightSide > coinLeftSide and robotTopSide < coinBottomSide and robotBottomSide > coinTopSide:
                self.points += 1
                self.text_2 = self.game_font_2.render(f"Number of Coins: {self.points}", True, (0, 0, 0))
                self.coinList[i].y = -10000

        for i in range(len(self.monsterList)):
            monsterLeftSide = self.monsterList[i].x
            monsterRightSide = self.monsterList[i].x + self.monsterList[i].monsterImage.get_width()
            monsterBottomSide = self.monsterList[i].y + self.monsterList[i].monsterImage.get_height()
            monsterTopSide = self.monsterList[i].y

            #The center points for the robot (target) and monster chasers are calculated here for adjusting the monsters' detection radius and tracking

            robot_center_x = self.robot.x + self.robot.robotImage.get_width() / 2
            robot_center_y = self.robot.y + self.robot.robotImage.get_height() / 2

            monster_center_x = self.monsterList[i].x + self.monsterList[i].monsterImage.get_width() / 2
            monster_center_y = self.monsterList[i].y + self.monsterList[i].monsterImage.get_height() / 2

            # This is a detection radius used to determine when to switch between patrol and chase modes for the monsters
            # These are the x and y distance gaps from the robot amd the monster. They serve as legs "a" and "b" in the pythagorean theorem
            dist_x = robot_center_x - monster_center_x
            dist_y = robot_center_y - monster_center_y
            # This is the leg c or hypotenuse which gives the total current distance between the robot and the monster center points. Its using to tell the monster when to patrol and when to chase
            hypotenuse_detection = math.sqrt((dist_x**2) + (dist_y**2))

            if hypotenuse_detection <= self.detection_radius: 
                self.monsterList[i].patrolMode = False
                self.monsterList[i].chaseMode = True
            if hypotenuse_detection >= self.detection_radius + 50:
                self.monsterList[i].patrolMode = True
                self.monsterList[i].chaseMode = False

            if self.monsterList[i].patrolMode == True:
                self.monsterList[i].horizontalMovement()
                # This respawn point matches highest possible random x value generated in the Monsterclass when the monster starts at the left-offscreen and moves right
                # (See MonsterClass instance variables)
                if monsterLeftSide > self.window.get_width() + 100:
                    self.monsterList[i].monsterRespawn()
                # This respawn point matches lowest possible random x value generated in the Monsterclass when the monster starts at the right-offscreen and moves left
                if monsterRightSide < -100:
                    self.monsterList[i].monsterRespawn()
            if self.monsterList[i].chaseMode == True: 
                # Compare the x coordinate for the target's center against the x coordinate for the chasing images center
                if monster_center_x > robot_center_x:
                    # Update the chasing image's x value until it matches the target image's x value
                    self.monsterList[i].x -= self.monsterList[i].chasevx
                if monster_center_x < robot_center_x:
                    self.monsterList[i].x += self.monsterList[i].chasevx
                # Compare the y coordinate for the target's center against the y coordinate for the chasing images center
                if monster_center_y > robot_center_y:
                    # Update the chasing image's y value until it matches the target image's y value
                    self.monsterList[i].y -= self.monsterList[i].chasevy
                if monster_center_y < robot_center_y:
                    self.monsterList[i].y += self.monsterList[i].chasevy
            
            # Calls the losing condition if the robot's boundaries overlap with a monster's.
            # The monster's position is re-read here because it may have just moved this frame.
            monsterLeftSide = self.monsterList[i].x
            monsterRightSide = self.monsterList[i].x + self.monsterList[i].monsterImage.get_width()
            monsterTopSide = self.monsterList[i].y
            monsterBottomSide = self.monsterList[i].y + self.monsterList[i].monsterImage.get_height()
            if robotLeftSide < monsterRightSide and robotRightSide > monsterLeftSide and robotTopSide < monsterBottomSide and robotBottomSide > monsterTopSide:
                self.gameLost()


        #Door collision boundaries, and the win condition if all the coins are collected and the robot reaches the door
        doorLeftSide = self.door.x
        doorRightSide = self.door.x + self.door.doorImage.get_width()
        doorBottomSide = self.door.y + self.door.doorImage.get_height()
        doorTopSide = self.door.y

        if self.points == len(self.coinList):
            self.door.doorUnlocked()
        if robotLeftSide < doorRightSide and robotRightSide > doorLeftSide and robotTopSide < doorBottomSide and robotBottomSide > doorTopSide and self.points == len(self.coinList):
            self.gameWon()


    #The images for the running state of the game are drawn using this method. It shows the HUD for coin collection status, and provides an indicating message if the player wins/losses in addition to the current patrol/chase state of monsters
    def drawWindow(self):
        self.window.fill((0, 225, 70))
        for coin in self.coinList:
            coin.drawCoin()
        self.door.drawDoor()
        for monster in self.monsterList:
            monster.drawMonster()
        self.robot.drawRobot()
        if self.door.arrived == True and self.door.locked == False:
            self.text_1 = self.game_font_1.render(f"You win! Press Enter to continue", True, (0, 0, 0))
            self.window.blit(self.text_1, (0, 0))
        if self.door.locked == True and self.door.arrived == False:
            self.text_1 = self.game_font_1.render(f"Collect the coins. Watch out for monsters!", True, (0, 0, 0))
            self.window.blit(self.text_1, (0, 0))
        if self.door.locked == False and self.door.arrived == False:
            self.text_1 = self.game_font_1.render(f"Door Unlocked. Head to the door to win!", True, (0, 0, 0))
            self.window.blit(self.text_1, (0, 0))
        if self.lost == True:
            self.text_3 = self.game_font_3.render(f"Pursuit Protocol successful. You lose!", True, (255, 0, 0))
            self.window.blit(self.text_3, (0, 50))
        if any(monster for monster in self.monsterList if monster.chaseMode == True) and self.lost == False:
            self.text_3 = self.game_font_3.render(f"Pursuit Protocol Status: Active.", True, (255, 0, 0))
            self.window.blit(self.text_3, (0, 50))
        elif all(monster for monster in self.monsterList if monster.patrolMode == True) and self.lost == False:
            self.text_3 = self.game_font_3.render(f"Pursuit Protocol Status: Inactive.", True, (0, 0, 0))
            self.window.blit(self.text_3, (0, 50))
        self.text_4 = self.game_font_4.render(f"Challenge Level: {self.challenge_level}", True, (0, 0, 0))
        self.window.blit(self.text_4, (0, 75))
        self.window.blit(self.text_2, (0, 25))
        pygame.display.flip() 
        self.clock.tick(60)


# The main game loop is here
    def main_game_loop(self):
        while True:
            self.events()
            if self.playTutorial == True:
                self.drawTutorial()
                self.clock.tick(60)
            else:
                self.game_updates()
                self.drawWindow()
   
#Starts the game as soon as the constructor of Pursuit Protocol is called
def main():
    pursuit_protocol = PursuitProtocol()

if __name__ == "__main__":
    main()
