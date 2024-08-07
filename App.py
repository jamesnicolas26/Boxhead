import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PLAYER_SIZE = 50
ENEMY_SIZE = 50
BULLET_SIZE = 5
UPGRADE_SIZE = 20
PLAYER_COLOR = (0, 0, 255)
ENEMY_COLOR = (255, 0, 0)
FAST_ENEMY_COLOR = (255, 165, 0)
STRONG_ENEMY_COLOR = (128, 0, 128)
BULLET_COLOR = (255, 255, 0)
UPGRADE_COLOR = (0, 255, 0)
BACKGROUND_COLOR = (50, 50, 50)
PLAYER_SPEED = 5
ENEMY_SPEED = 2
FAST_ENEMY_SPEED = 4
STRONG_ENEMY_HEALTH = 3
BULLET_SPEED = 10
BULLET_SPEED_UPGRADE = 15
BULLET_FIRE_RATE = 15
BULLET_FIRE_RATE_UPGRADE = 10
ENEMY_SPAWN_RATE = 30
UPGRADE_SPAWN_RATE = 300
UPGRADE_DURATION = 300
FONT_SIZE = 30
FPS = 60

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Enhanced Boxhead")

# Fonts
font = pygame.font.Font(None, FONT_SIZE)


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.health = 100
        self.bullet_speed = BULLET_SPEED
        self.fire_rate = BULLET_FIRE_RATE
        self.fire_timer = 0

    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += PLAYER_SPEED

        # Keep player on screen
        self.rect.x = max(0, min(SCREEN_WIDTH - PLAYER_SIZE, self.rect.x))
        self.rect.y = max(0, min(SCREEN_HEIGHT - PLAYER_SIZE, self.rect.y))

    def draw(self, surface):
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect)

    def shoot(self, mouse_x, mouse_y):
        if self.fire_timer == 0:
            dx, dy = mouse_x - self.rect.centerx, mouse_y - self.rect.centery
            dist = math.hypot(dx, dy)
            dx, dy = dx / dist, dy / dist  # Normalize
            return Bullet(self.rect.centerx, self.rect.centery, dx, dy, self.bullet_speed)
        return None


class Enemy:
    def __init__(self, x, y, enemy_type='normal'):
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.enemy_type = enemy_type
        self.health = STRONG_ENEMY_HEALTH if enemy_type == 'strong' else 1
        self.color = ENEMY_COLOR if enemy_type == 'normal' else (
            FAST_ENEMY_COLOR if enemy_type == 'fast' else STRONG_ENEMY_COLOR
        )
        self.speed = ENEMY_SPEED if enemy_type == 'normal' else (
            FAST_ENEMY_SPEED if enemy_type == 'fast' else ENEMY_SPEED
        )
        self.movement_pattern = random.choice(['straight', 'zigzag', 'circle']) if enemy_type == 'strong' else 'straight'
        self.angle = 0

    def move_towards_player(self, player):
        if self.movement_pattern == 'straight':
            dx, dy = player.rect.x - self.rect.x, player.rect.y - self.rect.y
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx, dy = dx / dist, dy / dist
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
        elif self.movement_pattern == 'zigzag':
            self.rect.x += self.speed * (1 if random.random() > 0.5 else -1)
            self.rect.y += self.speed
            if self.rect.y > SCREEN_HEIGHT:
                self.rect.y = 0
                self.rect.x = random.randint(0, SCREEN_WIDTH)
        elif self.movement_pattern == 'circle':
            center_x, center_y = self.rect.center
            dx = math.cos(math.radians(self.angle)) * self.speed
            dy = math.sin(math.radians(self.angle)) * self.speed
            self.rect.x += dx
            self.rect.y += dy
            self.angle = (self.angle + 5) % 360
            if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH or self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT:
                self.rect.x = random.randint(0, SCREEN_WIDTH)
                self.rect.y = random.randint(0, SCREEN_HEIGHT)
                self.angle = random.randint(0, 360)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


class Bullet:
    def __init__(self, x, y, dx, dy, speed):
        self.rect = pygame.Rect(x, y, BULLET_SIZE, BULLET_SIZE)
        self.dx = dx
        self.dy = dy
        self.speed = speed

    def move(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, BULLET_COLOR, self.rect)


class Upgrade:
    def __init__(self, x, y, upgrade_type):
        self.rect = pygame.Rect(x, y, UPGRADE_SIZE, UPGRADE_SIZE)
        self.upgrade_type = upgrade_type

    def draw(self, surface):
        pygame.draw.rect(surface, UPGRADE_COLOR, self.rect)


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)


def main():
    clock = pygame.time.Clock()

    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    enemies = []
    bullets = []
    upgrades = []

    frame_count = 0
    score = 0
    game_active = True
    upgrade_timer = 0
    active_upgrade = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        bullet = player.shoot(mouse_x, mouse_y)
                        if bullet:
                            bullets.append(bullet)

        keys = pygame.key.get_pressed()
        if game_active:
            player.move(keys)
            if player.fire_timer > 0:
                player.fire_timer -= 1

            # Spawn enemies
            if frame_count % ENEMY_SPAWN_RATE == 0:
                spawn_side = random.choice(['top', 'bottom', 'left', 'right'])
                enemy_type = random.choice(['normal', 'fast', 'strong'])
                if spawn_side == 'top':
                    enemies.append(Enemy(random.randint(0, SCREEN_WIDTH), 0, enemy_type))
                elif spawn_side == 'bottom':
                    enemies.append(Enemy(random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT, enemy_type))
                elif spawn_side == 'left':
                    enemies.append(Enemy(0, random.randint(0, SCREEN_HEIGHT), enemy_type))
                elif spawn_side == 'right':
                    enemies.append(Enemy(SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT), enemy_type))

            # Spawn upgrades
            if frame_count % UPGRADE_SPAWN_RATE == 0:
                upgrade_type = random.choice(['speed', 'fire_rate'])
                upgrades.append(Upgrade(random.randint(0, SCREEN_WIDTH - UPGRADE_SIZE), random.randint(0, SCREEN_HEIGHT - UPGRADE_SIZE), upgrade_type))

            # Move enemies
            for enemy in enemies:
                enemy.move_towards_player(player)

            # Move bullets
            for bullet in bullets:
                bullet.move()

            # Collision detection
            for enemy in enemies:
                if player.rect.colliderect(enemy.rect):
                    player.health -= 10
                    if player.health <= 0:
                        game_active = False
                        break

                for bullet in bullets:
                    if bullet.rect.colliderect(enemy.rect):
                        bullets.remove(bullet)
                        enemy.health -= 1
                        if enemy.health <= 0:
                            enemies.remove(enemy)
                            score += 1
                        break

            # Check for bullet collision with screen edges
            bullets = [bullet for bullet in bullets if 0 < bullet.rect.x < SCREEN_WIDTH and 0 < bullet.rect.y < SCREEN_HEIGHT]

            # Check for upgrade pickup
            for upgrade in upgrades:
                if player.rect.colliderect(upgrade.rect):
                    if upgrade.upgrade_type == 'speed':
                        player.bullet_speed = BULLET_SPEED_UPGRADE
                    elif upgrade.upgrade_type == 'fire_rate':
                        player.fire_rate = BULLET_FIRE_RATE_UPGRADE
                    upgrades.remove(upgrade)
                    active_upgrade = upgrade.upgrade_type
                    upgrade_timer = UPGRADE_DURATION

            if active_upgrade:
                upgrade_timer -= 1
                if upgrade_timer <= 0:
                    if active_upgrade == 'speed':
                        player.bullet_speed = BULLET_SPEED
                    elif active_upgrade == 'fire_rate':
                        player.fire_rate = BULLET_FIRE_RATE
                    active_upgrade = None

            # Draw everything
            screen.fill(BACKGROUND_COLOR)
            player.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            for bullet in bullets:
                bullet.draw(screen)
            for upgrade in upgrades:
                upgrade.draw(screen)
            draw_text(f"Score: {score}", font, (255, 255, 255), screen, SCREEN_WIDTH // 2, 20)
            draw_text(f"Health: {player.health}", font, (255, 255, 255), screen, SCREEN_WIDTH // 2, 60)

            if not game_active:
                draw_text("Game Over", font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                draw_text("Press R to Restart", font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
                if keys[pygame.K_r]:
                    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    enemies.clear()
                    bullets.clear()
                    upgrades.clear()
                    frame_count = 0
                    score = 0
                    game_active = True

            pygame.display.flip()
            clock.tick(FPS)
            frame_count += 1


if __name__ == "__main__":
    main()
