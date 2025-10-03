import pygame
import random
import sys
import os
import json

# SETTINGS AND CONSTANTS
WIDTH, HEIGHT = 1280, 720
FPS = 60
ROBOT_SIZE = 64
VILLAIN_SIZE = 56
BULLET_SIZE = 16
BG_LAYERS = 2
LEVELS = 4
VILLAIN_WAVES = [10, 18, 30, 40]
VILLAIN_SPEEDS = [3, 4, 5, 6]
ROBOT_HEALTH = 12
ROBOT_SHIELD = 0
BOSS_HEALTH = [40, 70]
SCORE_PER_VILLAIN = 15
SCORE_PER_BOSS = 250
POWERUP_TYPES = ["health", "shield", "double_shot", "rapid_fire"]
ASSET_DIR = "assets"
BG_FILES = [os.path.join(ASSET_DIR, "stage-preview", f"bg{i+1}.png") for i in range(BG_LAYERS)]
ROBOT_IMG = os.path.join(ASSET_DIR, "observer.png")
VILLAIN_BASIC_IMG = os.path.join(ASSET_DIR, "Sentinel.png")
VILLAIN_FAST_IMG = os.path.join(ASSET_DIR, "Drone.png")
VILLAIN_TANK_IMG = os.path.join(ASSET_DIR, "Metal-Slug.png")
BOSS_IMG = os.path.join(ASSET_DIR, "steel-eagle.png")
BULLET_IMG = os.path.join(ASSET_DIR, "laserbolts3.png")
POWERUP_IMG = os.path.join(ASSET_DIR, "powerup.png")
BG_MUSIC = os.path.join(ASSET_DIR, "BEAT this week.ogg")
SHOOT_SOUND = os.path.join(ASSET_DIR, "shoot.wav")
EXPLOSION_SOUND = os.path.join(ASSET_DIR, "explosion.wav")
POWERUP_SOUND = os.path.join(ASSET_DIR, "shoot.wav")



def load_image(filename, size=None):
    try:
        img = pygame.image.load(filename).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        return None

def play_sound(filename):
    try:
        s = pygame.mixer.Sound(filename)
        s.play()
    except Exception:
        pass

def play_music(filename, loop=True):
    try:
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(-1 if loop else 0)
    except Exception:
        pass


    
        

def play_music(filename, volume=1.0, loop=True):
    try:
        pygame.mixer.music.load(filename)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1 if loop else 0)
    except Exception:
        pass

def clamp(val, minv, maxv):
    return max(minv, min(val, maxv))

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robot vs Villains Deluxe")
clock = pygame.time.Clock()

robot_img = load_image(ROBOT_IMG, (ROBOT_SIZE, ROBOT_SIZE))
villain_basic_img = load_image(VILLAIN_BASIC_IMG, (VILLAIN_SIZE, VILLAIN_SIZE))
villain_fast_img = load_image(VILLAIN_FAST_IMG, (VILLAIN_SIZE, VILLAIN_SIZE))
villain_tank_img = load_image(VILLAIN_TANK_IMG, (VILLAIN_SIZE, VILLAIN_SIZE))
boss_img = load_image(BOSS_IMG, (ROBOT_SIZE * 2, ROBOT_SIZE * 2))
bullet_img = load_image(BULLET_IMG, (BULLET_SIZE, BULLET_SIZE))
powerup_img = load_image(POWERUP_IMG, (32, 32))
bg_imgs = [load_image(bg, (WIDTH, HEIGHT)) for bg in BG_FILES]

font_large = pygame.font.SysFont("arial", 72)
font_medium = pygame.font.SysFont("arial", 40)
font_small = pygame.font.SysFont("arial", 28)

def load_high_scores():
    try:
        with open("high_scores.json", "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_high_scores(scores):
    try:
        with open("high_scores.json", "w") as f:
            json.dump(scores, f)
    except Exception:
        pass

def load_profile():
    try:
        with open("profile.json", "r") as f:
            return json.load(f)
    except Exception:
        return {"max_level": 1, "settings": {}}

def save_profile(profile):
    try:
        with open("profile.json", "w") as f:
            json.dump(profile, f)
    except Exception:
        pass

high_scores = load_high_scores()
profile = load_profile()
global_volume = 1.0

# Sprite and entity classes

class Robot(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = robot_img
        
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT - ROBOT_SIZE * 2))
        self.health = ROBOT_HEALTH
        self.shield = ROBOT_SHIELD
        self.speed = 9
        self.fire_rate = 13
        self.cooldown = 0
        self.double_shot = False
        self.rapid_fire = False
        self.score = 0
        self.powerups = {"double_shot": 0, "rapid_fire": 0}

    def move(self, keys):
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        self.rect.x = clamp(self.rect.x, 0, WIDTH - self.rect.width)
        self.rect.y = clamp(self.rect.y, 0, HEIGHT - self.rect.height)

    def shoot(self, bullets_group):
        if self.cooldown == 0:
            bullets_group.add(Bullet((self.rect.centerx, self.rect.top)))
            if self.double_shot:
                bullets_group.add(Bullet((self.rect.left + 16, self.rect.top)))
                bullets_group.add(Bullet((self.rect.right - 16, self.rect.top)))
            play_sound(SHOOT_SOUND, global_volume)
            self.cooldown = self.fire_rate // (2 if self.rapid_fire else 1)

    def update(self, keys):
        self.move(keys)
        if self.cooldown > 0:
            self.cooldown -= 1
        for p in ["double_shot", "rapid_fire"]:
            if self.powerups[p] > 0:
                self.powerups[p] -= 1
                setattr(self, p, True)
            else:
                setattr(self, p, False)

    def add_powerup(self, ptype, frames):
        if ptype in self.powerups:
            self.powerups[ptype] = frames
            setattr(self, ptype, True)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x, self.rect.y - 16, int(ROBOT_SIZE * (self.health / ROBOT_HEALTH)), 8))
        if self.shield > 0:
            pygame.draw.ellipse(surface, (0, 200, 255), self.rect.inflate(12, 12), 2)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, speed=-18):
        super().__init__()
        self.image = bullet_img

        self.rect = self.image.get_rect(center=pos)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

class Villain(pygame.sprite.Sprite):
    def __init__(self, villain_type="basic", speed=3):
        super().__init__()
        self.type = villain_type
        if villain_type == "basic":
            self.image = villain_basic_img
            if not villain_basic_img:
                self.image = pygame.Surface((VILLAIN_SIZE, VILLAIN_SIZE))
                self.image.fill((200, 30, 50))
            self.health = 3
        elif villain_type == "fast":
            self.image = villain_fast_img
            if not villain_fast_img:
                self.image = pygame.Surface((VILLAIN_SIZE, VILLAIN_SIZE))
                self.image.fill((255, 100, 10))
            self.health = 2
        elif villain_type == "tank":
            self.image = villain_tank_img
            if not villain_tank_img:
                self.image = pygame.Surface((VILLAIN_SIZE, VILLAIN_SIZE))
                self.image.fill((90, 90, 90))
            self.health = 7
        self.rect = self.image.get_rect(topleft=(random.randint(0, WIDTH - VILLAIN_SIZE), -VILLAIN_SIZE))
        self.speed = speed

    def update(self, robot_pos):
        dx = robot_pos[0] - self.rect.centerx
        dy = robot_pos[1] - self.rect.centery
        dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        self.rect.x += int(self.speed * dx / dist)
        self.rect.y += int(self.speed * dy / dist)
        if self.rect.top > HEIGHT:
            self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self, health=40):
        super().__init__()
        self.max_health = health
        self.image = boss_img
        if not boss_img:
            self.image = pygame.Surface((ROBOT_SIZE * 2, ROBOT_SIZE * 2))
            self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(center=(random.randint(ROBOT_SIZE * 2, WIDTH - ROBOT_SIZE * 2), -ROBOT_SIZE * 2))
        self.health = health
        self.speed = 2
        self.shoot_timer = 0

    def update(self, robot_pos):
        dx = robot_pos[0] - self.rect.centerx
        dy = robot_pos[1] - self.rect.centery
        dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        self.rect.x += int(self.speed * dx / dist)
        self.rect.y += int(self.speed * dy / dist)
        if self.rect.top > HEIGHT:
            self.rect.top = -ROBOT_SIZE * 2

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        pygame.draw.rect(surface, (255, 0, 0), (self.rect.x, self.rect.y - 24, self.rect.width, 12))
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x, self.rect.y - 24, int(self.rect.width * (self.health / self.max_health)), 12))

class Powerup(pygame.sprite.Sprite):
    def __init__(self, ptype, pos):
        super().__init__()
        self.ptype = ptype
        self.image = powerup_img
        if not powerup_img:
            self.image = pygame.Surface((32, 32))
            color = {"health":(0,255,0), "shield":(0,200,255), "double_shot":(255,255,0), "rapid_fire":(255,100,255)}
            self.image.fill(color.get(ptype, (255,255,255)))
        self.rect = self.image.get_rect(center=pos)
        self.speed = 4
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Background:
    def __init__(self, bg_imgs):
        self.layers = bg_imgs
        self.offsets = [0 for _ in self.layers]

    def update(self, speed=1):
        for i in range(len(self.offsets)):
            self.offsets[i] = (self.offsets[i] + speed * (i + 1)) % HEIGHT

    def draw(self, surface):
        for i, img in enumerate(self.layers):
            if img:
                y = self.offsets[i]
                surface.blit(img, (0, y - HEIGHT))
                surface.blit(img, (0, y))

def draw_text(surface, text, size, color, x, y, center=True):
    font = pygame.font.SysFont('arial', size)
    txt = font.render(text, True, color)
    rect = txt.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(txt, rect)

def draw_hud(surface, robot, level, paused=False):
    pygame.draw.rect(surface, (0, 0, 0), (0, 0, WIDTH, 48))
    draw_text(surface, f"Score: {robot.score}", 32, (255, 255, 0), 20, 10, center=False)
    draw_text(surface, f"Health: {robot.health}", 32, (255, 0, 0), 220, 10, center=False)
    draw_text(surface, f"Shield: {robot.shield}", 32, (0, 200, 255), 400, 10, center=False)
    draw_text(surface, f"Level: {level}", 32, (255, 255, 255), WIDTH - 180, 10, center=False)
    if paused:
        draw_text(surface, "PAUSED", 60, (255, 255, 255), WIDTH // 2, HEIGHT // 2)

def draw_tutorial(surface):
    lines = [
        "ROBOT VS VILLAINS DELUXE - HELP",
        "Move: WASD or Arrow Keys",
        "Shoot: Space",
        "Pause: ESC",
        "Collect powerups for upgrades!",
        "Defeat all villains and bosses to win.",
        "Press any key to return."
    ]
    surface.fill((15, 15, 50))
    for i, line in enumerate(lines):
        draw_text(surface, line, 42 if i == 0 else 32, (255, 255, 200), WIDTH // 2, 120 + i * 60)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def start_menu(high_scores):
    menu = True
    selected = 0
    options = ["PLAY", "HELP", "SETTINGS", "QUIT"]
    while menu:
        screen.fill((30, 30, 60))
        draw_text(screen, "ROBOT VS VILLAINS DELUXE", 72, (255, 255, 0), WIDTH // 2, HEIGHT // 4)
        for i, opt in enumerate(options):
            color = (0, 255, 0) if selected == i else (180, 180, 180)
            draw_text(screen, opt, 48, color, WIDTH // 2, HEIGHT // 2 + i * 64)
        if high_scores:
            draw_text(screen, f"High Score: {max(high_scores)}", 36, (255, 180, 0), WIDTH // 2, HEIGHT - 80)
        else:
            draw_text(screen, f"High Score: 0", 36, (255, 180, 0), WIDTH // 2, HEIGHT - 80)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if selected == 0:
                        menu = False
                    elif selected == 1:
                        draw_tutorial(screen)
                    elif selected == 2:
                        settings_menu()
                    elif selected == 3:
                        pygame.quit()
                        sys.exit()

def settings_menu():
    global global_volume
    options = ["Music: On", "Volume: 100%", "Back"]
    selected = 0
    music_on = True
    volume = global_volume
    while True:
        screen.fill((15, 15, 40))
        draw_text(screen, "SETTINGS", 60, (130, 255, 255), WIDTH // 2, HEIGHT // 4)
        for i, opt in enumerate(options):
            c = (0, 255, 255) if selected == i else (180, 180, 180)
            if i == 0:
                opt = f"Music: {'On' if music_on else 'Off'}"
            if i == 1:
                opt = f"Volume: {int(volume * 100)}%"
            draw_text(screen, opt, 44, c, WIDTH // 2, HEIGHT // 2 + i * 60)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_LEFT and selected == 1:
                    volume = clamp(volume - 0.1, 0, 1)
                if event.key == pygame.K_RIGHT and selected == 1:
                    volume = clamp(volume + 0.1, 0, 1)
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if selected == 0:
                        music_on = not music_on
                        if music_on:
                            play_music(BG_MUSIC, volume)
                        else:
                            pygame.mixer.music.stop()
                    elif selected == 2:
                        global_volume = volume
                        pygame.mixer.music.set_volume(volume)
                        return

def game_over_screen(score, high_scores):
    pygame.mixer.music.stop()
    screen.fill((60, 0, 0))
    draw_text(screen, "GAME OVER!", 72, (255, 255, 255), WIDTH // 2, HEIGHT // 3)
    draw_text(screen, f"Score: {score}", 44, (255, 180, 0), WIDTH // 2, HEIGHT // 2)
    draw_text(screen, "Press Enter to return to menu", 36, (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 80)
    high_scores.append(score)
    high_scores.sort(reverse=True)
    save_high_scores(high_scores)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False

def victory_screen(score, high_scores):
    pygame.mixer.music.stop()
    screen.fill((0, 60, 0))
    draw_text(screen, "VICTORY!", 72, (255, 255, 255), WIDTH // 2, HEIGHT // 3)
    draw_text(screen, f"Score: {score}", 44, (255, 255, 0), WIDTH // 2, HEIGHT // 2)
    draw_text(screen, "Press Enter to return to menu", 36, (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 80)
    high_scores.append(score)
    high_scores.sort(reverse=True)
    save_high_scores(high_scores)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False

def play_game(level=1):
    global global_volume
    play_music(BG_MUSIC, global_volume)
    robot = Robot()
    bullets = pygame.sprite.Group()
    villains = pygame.sprite.Group()
    bosses = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    bg = Background(bg_imgs)
    wave = 0
    paused = False
    boss_spawned = False
    next_wave_timer = 0
    frames = 0

    # Initial spawn basic villains
    for _ in range(VILLAIN_WAVES[level - 1]):
        villains.add(Villain("basic", VILLAIN_SPEEDS[level - 1]))

    running = True
    while running:
        frames += 1
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    robot.shoot(bullets)
                if event.key == pygame.K_ESCAPE:
                    paused = not paused

        if paused:
            draw_hud(screen, robot, level, paused=True)
            pygame.display.flip()
            clock.tick(FPS)
            continue

        # Updates
        bg.update(speed=1 + level)
        robot.update(keys)
        bullets.update()
        for villain in villains.sprites():
            villain.update(robot.rect.center)
        for boss in bosses.sprites():
            boss.update(robot.rect.center)
        powerups.update()

        # Collisions: bullets vs villains
        for bullet in bullets.sprites():
            hit_villains = pygame.sprite.spritecollide(bullet, villains, False)
            for villain in hit_villains:
                villain.health -= 1
                bullet.kill()
                if villain.health <= 0:
                    robot.score += SCORE_PER_VILLAIN
                    play_sound(EXPLOSION_SOUND, global_volume)
                    villain.kill()
                    if random.random() < 0.14:
                        ptype = random.choice(POWERUP_TYPES)
                        powerups.add(Powerup(ptype, villain.rect.center))

        # bullets vs bosses
        for bullet in bullets.sprites():
            hit_bosses = pygame.sprite.spritecollide(bullet, bosses, False)
            for boss in hit_bosses:
                boss.health -= 2
                bullet.kill()
                robot.score += 3
                play_sound(EXPLOSION_SOUND, global_volume)
                if boss.health <= 0:
                    robot.score += SCORE_PER_BOSS
                    boss.kill()
                    play_sound(EXPLOSION_SOUND, global_volume)
                    if len(bosses) == 0:
                        victory_screen(robot.score, high_scores)
                        return

        # villains/bosses vs robot
        for villain in villains.sprites():
            if robot.rect.colliderect(villain.rect):
                if robot.shield > 0:
                    robot.shield -= 1
                else:
                    robot.health -= 2 if villain.type == "tank" else 1
                villain.kill()
                play_sound(EXPLOSION_SOUND, global_volume)
                if robot.health <= 0:
                    game_over_screen(robot.score, high_scores)
                    return

        for boss in bosses.sprites():
            if robot.rect.colliderect(boss.rect):
                if robot.shield > 0:
                    robot.shield -= 2
                else:
                    robot.health -= 4
                play_sound(EXPLOSION_SOUND, global_volume)
                if robot.health <= 0:
                    game_over_screen(robot.score, high_scores)
                    return

        # powerups vs robot
        for powerup in powerups.sprites():
            if robot.rect.colliderect(powerup.rect):
                if powerup.ptype == "health":
                    robot.health = clamp(robot.health + 4, 0, ROBOT_HEALTH)
                elif powerup.ptype == "shield":
                    robot.shield = clamp(robot.shield + 5, 0, 20)
                elif powerup.ptype == "double_shot":
                    robot.add_powerup("double_shot", FPS * 10)
                elif powerup.ptype == "rapid_fire":
                    robot.add_powerup("rapid_fire", FPS * 10)
                play_sound(POWERUP_SOUND, global_volume)
                powerup.kill()

        # Level progression & spawning
        if len(villains) == 0 and not boss_spawned:
            next_wave_timer += 1
            if next_wave_timer > FPS * 2:
                wave += 1
                next_wave_timer = 0
                if wave < 3:
                    # Spawn mixed waves of villains
                    for _ in range(VILLAIN_WAVES[level - 1] // 3):
                        villains.add(Villain("fast", VILLAIN_SPEEDS[level - 1] + 2))
                        villains.add(Villain("tank", max(2, VILLAIN_SPEEDS[level - 1] - 1)))
                    for _ in range(VILLAIN_WAVES[level - 1] // 2):
                        villains.add(Villain("basic", VILLAIN_SPEEDS[level - 1]))
                else:
                    boss_spawned = True
                    base_health = BOSS_HEALTH[(level-1) % len(BOSS_HEALTH)]
                    bosses.add(Boss(health=base_health + 15 * level))

        # Remove expired powerups (falling off screen)
        for powerup in powerups.sprites():
            if powerup.rect.top > HEIGHT:
                powerup.kill()

        # DRAW
        bg.draw(screen)
        robot.draw(screen)
        bullets.draw(screen)
        villains.draw(screen)
        for boss in bosses:
            boss.draw(screen)
        powerups.draw(screen)
        draw_hud(screen, robot, level, paused=False)

        # Minimap
        minimap_rect = pygame.Rect(WIDTH - 140, HEIGHT - 140, 120, 120)
        pygame.draw.rect(screen, (10, 10, 30), minimap_rect)
        rx = minimap_rect.x + int((robot.rect.centerx / WIDTH) * 120)
        ry = minimap_rect.y + int((robot.rect.centery / HEIGHT) * 120)
        pygame.draw.circle(screen, (0, 200, 255), (rx, ry), 6)
        for villain in villains:
            vx = minimap_rect.x + int((villain.rect.centerx / WIDTH) * 120)
            vy = minimap_rect.y + int((villain.rect.centery / HEIGHT) * 120)
            pygame.draw.circle(screen, (255, 60, 60), (vx, vy), 4)
        for boss in bosses:
            bx = minimap_rect.x + int((boss.rect.centerx / WIDTH) * 120)
            by = minimap_rect.y + int((boss.rect.centery / HEIGHT) * 120)
            pygame.draw.circle(screen, (255, 0, 255), (bx, by), 8)
        for powerup in powerups:
            px = minimap_rect.x + int((powerup.rect.centerx / WIDTH) * 120)
            py = minimap_rect.y + int((powerup.rect.centery / HEIGHT) * 120)
            pygame.draw.circle(screen, (255, 255, 0), (px, py), 3)
        pygame.draw.rect(screen, (200, 200, 200), minimap_rect, 2)

        # Powerup status display
        px = 20
        if robot.double_shot:
            draw_text(screen, "Double Shot", 24, (255, 255, 0), px, HEIGHT - 40, center=False)
            px += 140
        if robot.rapid_fire:
            draw_text(screen, "Rapid Fire", 24, (255, 100, 255), px, HEIGHT - 40, center=False)
            px += 140

        # End game check
        if robot.health <= 0:
            game_over_screen(robot.score, high_scores)
            return

        pygame.display.flip()
        clock.tick(FPS)

        # Boss attacks: shoot downwards bullets
        for boss in bosses.sprites():
            boss.shoot_timer += 1
            if boss.shoot_timer > FPS // 2:
                boss.shoot_timer = 0
                bx = boss.rect.centerx
                by = boss.rect.bottom
                for i in [-40, 0, 40]:
                    bullets.add(Bullet((bx + i, by), speed=10))

def main():
    while True:
        start_menu(high_scores)
        play_game(level=1)

if __name__ == "__main__":
    main()
