import pygame
from pygame.locals import *
import random
from menu import Menu
import os # MODIFICATION: Import os to check for file existence

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 500
screen_height = 936

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

#define font
font = pygame.font.SysFont('Bauhaus 93', 60)
small_font = pygame.font.SysFont('Bauhaus 93', 30) # MODIFICATION: Smaller font for high score

menu_font = pygame.font.SysFont('Bauhaus 93', 40)

#define colours
white = (255, 255, 255)
gold = (255, 215, 0) # MODIFICATION: Added gold color for high score

#define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
in_menu = True
game_over = False
pipe_gap = 150
pipe_frequency = 1500 #milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
high_score = 0 # MODIFICATION: High score variable

# MODIFICATION: Load high score from file
score_file_path = 'high_score.txt'
if os.path.exists(score_file_path):
    with open(score_file_path, 'r') as file:
        try:
            high_score = int(file.read())
        except ValueError:
            high_score = 0 # Handle case where file is empty or corrupted


#load images
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')


#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score

class Bird(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range (1, 4):
            img = pygame.image.load(f"img/bird{num}.png")
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):

        if flying == True:
            #apply gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if game_over == False:
            #jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            #handle the animation
            flap_cooldown = 5
            self.counter += 1
            
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]


            #rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            #point the bird at the ground
            self.image = pygame.transform.rotate(self.images[self.index], -90)



class Pipe(pygame.sprite.Sprite):

    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/pipe.png")
        self.rect = self.image.get_rect()
        #position variable determines if the pipe is coming from the bottom or top
        #position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        elif position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]


    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()



class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        #draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action



pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))

menu = Menu(screen_width, screen_height, menu_font)

bird_group.add(flappy)

#create restart button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)


run = True
while run:

    clock.tick(fps)

    #draw background
    screen.blit(bg, (0,0))

    pipe_group.draw(screen)
    bird_group.draw(screen)
    bird_group.update()

    #draw and scroll the ground
    screen.blit(ground_img, (ground_scroll, 768))

    #check the score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
    
    # Draw scores
    draw_text(f'Score: {score}', small_font, white, 20, 10)
    # MODIFICATION: Draw the high score in the top right
    draw_text(f'High Score: {high_score}', small_font, gold, screen_width - 200, 10)


    # MODIFICATION: Consolidated collision check and high score update
    # This block now runs only ONCE when the game ends.
    if game_over == False:
        # Check for collisions with pipes, ceiling, or ground
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0 or flappy.rect.bottom >= 768:
            game_over = True
            # Check for new high score and save it
            if score > high_score:
                high_score = score
                with open(score_file_path, 'w') as file:
                    file.write(str(high_score))
    
    # Original ground collision check to stop the bird from flying
    if flappy.rect.bottom >= 768:
        flying = False


    if flying == True and game_over == False:
        #generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        pipe_group.update()

        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0
    

    #check for game over and reset
    if game_over == True:
        if button.draw():
            game_over = False
            score = reset_game()
    
    if in_menu:
        menu.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if in_menu:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    menu.navigate(-1)
                elif event.key == pygame.K_DOWN:
                    menu.navigate(1)
                elif event.key == pygame.K_RETURN:
                    selected_option = menu.get_selected_option()
                    if selected_option == "Start Game":
                        in_menu = False
                        flying = True
                    elif selected_option == "High Score":
                        # In a real game, you'd display the high score here.
                        print(f"High Score: {high_score}")
                        # For now, let's just go back to the menu.
                        in_menu = True  # This line ensures you go back to the menu
                    elif selected_option == "Quit Game":
                        run = False
        elif event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True
        elif event.type == pygame.KEYDOWN and game_over and event.key == pygame.K_RETURN:
            game_over = False
            score = reset_game()

    if not in_menu and not game_over:
        # Check for game over during the game
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0 or flappy.rect.bottom >= 768:
            game_over = True


    pygame.display.update()
pygame.quit()