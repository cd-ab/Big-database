



import pygame
import sys
import random

# Initialize Pygame and mixer for sound
pygame.init()
pygame.mixer.init()

# Screen settings
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arcade Dragon Jump")

# Load images
dragon_img = pygame.image.load("dragon.png").convert_alpha()
hurdle_img = pygame.image.load("hurdle.png").convert_alpha()
background = pygame.image.load("day.png").convert_alpha()
dragon_img = pygame.transform.scale(dragon_img, (80, 60))
hurdle_img = pygame.transform.scale(hurdle_img, (40, 60))
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Background scrolling variables
bg_x1 = 0
bg_x2 = WIDTH
scroll_speed = 9 # Match this with hurdle speed

# Load and play sounds
pygame.mixer.music.load("arcade.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  # Loop background music

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)

# FPS
clock = pygame.time.Clock()
FPS = 60

# Game variables
gravity = 0.8
jump_strength = -15
score = 0
high_score = 0
game_over = False

# Font
font = pygame.font.Font(None, 36)

# Dragon sprite class
class Dragon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = dragon_img
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = HEIGHT - self.rect.height - 50
        self.velocity_y = 0
        self.speed=10
        self.is_jumping = False
        self.velocity_x=self.speed

    def update(self):
        self.velocity_y += gravity
        self.rect.y += self.velocity_y
        
        # Ground collision
        if self.rect.bottom >= HEIGHT - 50:
            self.rect.bottom = HEIGHT - 50
            self.velocity_y = 0
            self.is_jumping = False

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = jump_strength
            self.is_jumping = True


    def laser_shooting(self):
       pos_x=self.rect.x +22
       pos_y=0
       laser =[]
       laser_img=pygame.image.load('laser-bolts3.png').convert()
       laser_img=pygame.transform.scale(laser_img, (40, 40))
       laser.append(laser_img)



# Hurdle sprite class
class Hurdle(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = hurdle_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = HEIGHT - self.rect.height - 50
        self.speed = scroll_speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

# Sprite groups
dragon = Dragon()
all_sprites = pygame.sprite.Group()
all_sprites.add(dragon)
hurdles = pygame.sprite.Group()

def create_hurdle():
    x = WIDTH + random.randint(200, 400)
    hurdle = Hurdle(x)
    hurdles.add(hurdle)
    all_sprites.add(hurdle)


# Start with one hurdle
create_hurdle()

# Main game loop
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    dragon.jump()
                    dragon.laser_shooting()
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                game_over = False
                score = 0
                hurdles.empty()
                all_sprites.empty()
                dragon = Dragon()
                all_sprites.add(dragon)
                create_hurdle()
                # Reset background for fresh start
                bg_x1 = 0
                bg_x2 = WIDTH

    if not game_over:
        all_sprites.update()
        # Add hurdles as needed
        if len(hurdles) == 0 or (hurdles.sprites()[-1].rect.x < WIDTH - 300):
            create_hurdle()
        # Check for collision
        if pygame.sprite.spritecollideany(dragon, hurdles):
            
            game_over = True
            
            if score > high_score:
                high_score = score
        # Update score
        for hurdle in hurdles:
            if hurdle.rect.right < dragon.rect.left and not hasattr(hurdle, 'passed'):
                hurdle.passed = True
                score += 5

        # Background scroll update
        bg_x1 -= scroll_speed
        bg_x2 -= scroll_speed
        if bg_x1 <= -WIDTH:
            bg_x1 = bg_x2 + WIDTH
        if bg_x2 <= -WIDTH:
            bg_x2 = bg_x1 + WIDTH

    # Draw background
    screen.blit(background, (bg_x1, 0))
    screen.blit(background, (bg_x2, 0))

    # Draw ground
    pygame.draw.line(screen, BLACK, (0, HEIGHT - 50), (WIDTH, HEIGHT - 50), 3)

    # Draw sprites
    all_sprites.draw(screen)

    # Display score and high score
    score_text = font.render(f"Score: {score}", True, BLACK)
    high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (10, 40))

    if game_over:
        go_text = font.render("DAMN LOSER! Press Enter to Restart", True, BLACK)
        screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()

pygame.quit()
sys.exit()
