import math
import time
from pygame import Rect

WIDTH = 1200
HEIGHT = 600
TITLE = "Jogo do astronautinha!"

TILE_SIZE = 18

SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
DIRT_BROWN = (139, 69, 19)
STONE_GRAY = (120, 120, 120)
LAVA_RED = (220, 60, 60)
WOOD_BROWN = (120, 80, 30)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_BLUE = (40, 100, 240)
ENEMY_RED = (200, 50, 50)

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_WON = "won"

TILE_EMPTY = 0
TILE_GRASS = 1
TILE_DIRT = 2
TILE_STONE = 3
TILE_LAVA = 4
TILE_WOOD = 5

MAP_W = WIDTH // TILE_SIZE
MAP_H = HEIGHT // TILE_SIZE

TILE_ASSETS = {
    TILE_GRASS: "tile_0102",
    TILE_DIRT: "tile_0104",
    TILE_STONE: "tile_0029",
    TILE_LAVA: "tile_0033",
    TILE_WOOD: "tile_0062"
}

start_time = time.time() * 1000
def get_current_time_ms():
    return int((time.time() * 1000) - start_time)

class TileMap:
    def __init__(self, w, h, tile_size):
        self.width = w
        self.height = h
        self.tile_size = tile_size
        self.grid = [[TILE_EMPTY for _ in range(w)] for _ in range(h)]
        self.scaled_images = {}
        self._load_images()
        self._build_classic_level()

    def _load_images(self):
        for t, name in TILE_ASSETS.items():
            try:
                img = images.load(name)
                self.scaled_images[t] = getattr(img, "surface", img)
            except Exception:
                self.scaled_images[t] = None

    def _build_classic_level(self):
        h, w = self.height, self.width

        for y in range(h - 2, h):
            for x in range(w):
                self.grid[y][x] = TILE_GRASS if y == h - 2 else TILE_DIRT

        for hole_start in (30, 90, 140):
            for x in range(hole_start, min(hole_start + 4, w)):
                self.grid[h - 2][x] = TILE_EMPTY
                self.grid[h - 1][x] = TILE_EMPTY

        plat_list = [
            (6, h - 6, 6),
            (18, h - 8, 8),
            (36, h - 5, 5),
            (60, h - 9, 7),
            (85, h - 6, 6),
            (110, h - 7, 5),
            (130, h - 5, 8),
            (150, h - 8, 6)
        ]
        for start_x, y, length in plat_list:
            for x in range(start_x, min(start_x + length, w)):
                self.grid[y][x] = TILE_STONE

        pillar_positions = [(28, h - 3, 3), (52, h - 3, 4), (95, h - 3, 3)]
        for x, base_y, height_p in pillar_positions:
            for offset in range(height_p):
                yy = base_y - offset
                if 0 <= yy < h and 0 <= x < w:
                    self.grid[yy][x] = TILE_STONE

        lava_start = min(w - 30, 145)
        for x in range(lava_start, lava_start + 6):
            self.grid[h - 2][x] = TILE_LAVA
            self.grid[h - 1][x] = TILE_LAVA

    def get_tile(self, x, y):
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.grid[y][x]
        return TILE_EMPTY

    def is_solid(self, x, y):
        t = self.get_tile(x, y)
        return t in (TILE_GRASS, TILE_DIRT, TILE_STONE, TILE_WOOD)

    def draw(self):
        for y in range(self.height):
            for x in range(self.width):
                tile = self.grid[y][x]
                if tile == TILE_EMPTY:
                    continue
                px = x * self.tile_size
                py = y * self.tile_size
                surf = self.scaled_images.get(tile)
                if surf:
                    try:
                        screen.surface.blit(surf, (px, py))
                        continue
                    except Exception:
                        pass
                color = DIRT_BROWN
                if tile == TILE_GRASS:
                    color = GRASS_GREEN
                elif tile == TILE_STONE:
                    color = STONE_GRAY
                elif tile == TILE_LAVA:
                    color = LAVA_RED
                elif tile == TILE_WOOD:
                    color = WOOD_BROWN
                screen.draw.filled_rect(Rect(px, py, self.tile_size, self.tile_size), color)

class Player:
    def __init__(self, tile_x, tile_y, tile_map):
        self.tile_map = tile_map
        self.width = 12
        self.height = 12
        self.rect = Rect(0, 0, self.width, self.height)
        self.rect.centerx = tile_x * TILE_SIZE + TILE_SIZE // 2
        self.rect.bottom = tile_y * TILE_SIZE
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.health = 3
        self.speed = 180.0
        self.jump_strength = 550.0
        self.frames = []
        self.reflection_frames = [] 
        self.facing_right = True

        try:
            f0 = images.load("tile_0000")
            self.frames.append(getattr(f0, "surface", f0))
            f1 = images.load("tile_0001")
            self.frames.append(getattr(f1, "surface", f1))
            
            rf0 = images.load("tile_reflection_0000")
            self.reflection_frames.append(getattr(rf0, "surface", rf0))
            rf1 = images.load("tile_reflection_0001")
            self.reflection_frames.append(getattr(rf1, "surface", rf1))
            
        except Exception:
            self.frames = []
            self.reflection_frames = []

    def update(self, dt, keys):
        if keys.left:
            self.vx = -self.speed
            self.facing_right = False 
        elif keys.right:
            self.vx = self.speed
            self.facing_right = True 
        else:
            self.vx = 0
        if (keys.w or keys.up) and self.on_ground:
            self.vy = -self.jump_strength
            self.on_ground = False

        self.vy += 1200.0 * dt

        self.rect.x += int(self.vx * dt)
        self._collide_x()

        self.rect.y += int(self.vy * dt)
        self.on_ground = False
        self._collide_y()

        if self.rect.top > HEIGHT + 200:
            self.health = 0

    def _collide_x(self, **kwargs):
        r = self.rect
        left_tile = int(r.left // TILE_SIZE)
        right_tile = int((r.right - 1) // TILE_SIZE)
        top_tile = int(r.top // TILE_SIZE)
        bottom_tile = int((r.bottom - 1) // TILE_SIZE)

        if self.vx > 0:
            if self.tile_map.is_solid(right_tile, top_tile) or self.tile_map.is_solid(right_tile, bottom_tile):
                r.right = right_tile * TILE_SIZE
                self.vx = 0
        elif self.vx < 0:
            if self.tile_map.is_solid(left_tile, top_tile) or self.tile_map.is_solid(left_tile, bottom_tile):
                r.left = (left_tile + 1) * TILE_SIZE
                self.vx = 0
                
    def _collide_y(self, **kwargs):
        r = self.rect
        left_tile = int(r.left // TILE_SIZE)
        right_tile = int((r.right - 1) // TILE_SIZE)
        top_tile = int(r.top // TILE_SIZE)
        bottom_tile = int((r.bottom - 1) // TILE_SIZE)

        if self.vy > 0:
            if self.tile_map.is_solid(left_tile, bottom_tile) or self.tile_map.is_solid(right_tile, bottom_tile):
                r.bottom = bottom_tile * TILE_SIZE
                self.vy = 0
                self.on_ground = True
        elif self.vy < 0:
            if self.tile_map.is_solid(left_tile, top_tile) or self.tile_map.is_solid(right_tile, top_tile):
                r.top = (top_tile + 1) * TILE_SIZE
                self.vy = 0

        tile_l = self.tile_map.get_tile(left_tile, bottom_tile)
        tile_r = self.tile_map.get_tile(right_tile, bottom_tile)
        if (tile_l == TILE_LAVA or tile_r == TILE_LAVA) and (r.bottom - bottom_tile * TILE_SIZE) > 4:
            self.health = 0

    def draw(self):
        # Determina qual conjunto de frames usar
        current_frames = self.reflection_frames if self.facing_right else self.frames
        
        if current_frames:
            if abs(self.vx) > 10:
                idx = int(get_current_time_ms() / 150) % len(current_frames)
            else:
                idx = 0
            
            surf = current_frames[idx]
            try:
                rect_img = getattr(surf, "get_rect", None)
                if rect_img:
                    img_rect = surf.get_rect(center=(self.rect.centerx, self.rect.centery))
                    screen.surface.blit(surf, img_rect)
                    return
            except Exception:
                pass
        screen.draw.filled_rect(self.rect, PLAYER_BLUE)

class Enemy:
    def __init__(self, tile_x, tile_y, range_tiles=4, speed=60):
        self.width = 12
        self.height = 12
        self.rect = Rect(0, 0, self.width, self.height)
        self.rect.centerx = tile_x * TILE_SIZE + TILE_SIZE // 2
        self.rect.bottom = tile_y * TILE_SIZE
        self.start_x = self.rect.centerx
        self.range_x = range_tiles * TILE_SIZE
        self.vx = float(speed)
        self.frames = []
        self.reflection_frames = [] # Novo atributo para frames espelhados
        
        try:
            a = images.load("tile_0022")
            b = images.load("tile_0023")
            self.frames = [getattr(a, "surface", a), getattr(b, "surface", b)]
            
            # Carrega frames espelhados
            ra = images.load("tile_reflection_0022")
            rb = images.load("tile_reflection_0023")
            self.reflection_frames = [getattr(ra, "surface", ra), getattr(rb, "surface", rb)]
            
        except Exception:
            self.frames = []
            self.reflection_frames = []

    def update(self, dt):
        self.rect.x += int(self.vx * dt)
        if self.rect.centerx > self.start_x + self.range_x:
            self.vx = -abs(self.vx)
        elif self.rect.centerx < self.start_x:
            self.vx = abs(self.vx)

    def draw(self):
        # O inimigo está olhando para a direita se self.vx > 0
        facing_right = self.vx > 0
        current_frames = self.reflection_frames if facing_right else self.frames
        
        if current_frames:
            idx = int(get_current_time_ms() / 160) % len(current_frames)
            surf = current_frames[idx]
            try:
                img_rect = surf.get_rect(center=(self.rect.centerx, self.rect.centery))
                screen.surface.blit(surf, img_rect)
                return
            except Exception:
                pass
        screen.draw.filled_rect(self.rect, ENEMY_RED)

class Coin:
    def __init__(self, tile_x, tile_y):
        self.rect = Rect(0, 0, 14, 14)
        self.rect.centerx = tile_x * TILE_SIZE + TILE_SIZE // 2
        self.rect.centery = tile_y * TILE_SIZE + TILE_SIZE // 2
        self.collected = False
        self.bob = 0.0
        self.frames = []
        try:
            f0 = images.load("tile_0151")
            f1 = images.load("tile_0152")
            self.frames = [getattr(f0, "surface", f0), getattr(f1, "surface", f1)]
        except Exception:
            self.frames = []

    def update(self, dt):
        self.bob += dt * 6.0

    def draw(self):
        if self.collected:
            return
        offset = math.sin(self.bob) * 4
        center = (self.rect.centerx, self.rect.centery + offset)
        if self.frames:
            idx = int(get_current_time_ms() / 100) % len(self.frames)
            surf = self.frames[idx]
            try:
                img_rect = surf.get_rect(center=center)
                screen.surface.blit(surf, img_rect)
                return
            except Exception:
                pass
        screen.draw.filled_circle(center, 7, GOLD)
        screen.draw.circle(center, 7, WHITE)

tile_map = TileMap(MAP_W, MAP_H, TILE_SIZE)
player = None
enemies = []
coins = []
score = 0
game_state = STATE_MENU

def reset_game():
    global player, enemies, coins, score, game_state, start_time
    start_time = time.time() * 1000
    score = 0
    player = Player(2, MAP_H - 2, tile_map)

    enemies.clear()
    enemies.extend([
        Enemy(6, MAP_H - 6, range_tiles=5, speed=70),
        Enemy(20, MAP_H - 8, range_tiles=6, speed=55), 
        Enemy(36, MAP_H - 5, range_tiles=4, speed=65), 
        Enemy(130, MAP_H - 5, range_tiles=7, speed=60) 
    ])

    coins.clear()
    coin_positions = [(8, MAP_H - 7), (22, MAP_H - 9), (38, MAP_H - 6), (62, MAP_H - 10),
                      (87, MAP_H - 7), (112, MAP_H - 8), (132, MAP_H - 6)]
    for tx, ty in coin_positions:
        if 0 <= tx < tile_map.width and 0 <= ty < tile_map.height:
            coins.append(Coin(tx, ty))

    game_state = STATE_PLAYING

def update(dt):
    global game_state, score
    if game_state == STATE_PLAYING:
        player.update(dt, keyboard)

        remaining = 0
        for coin in coins:
            coin.update(dt)
            if not coin.collected:
                remaining += 1
                if player.rect.colliderect(coin.rect):
                    coin.collected = True
                    score += 10

        for e in enemies:
            e.update(dt)
            if player.rect.colliderect(e.rect):
                player.health -= 1
                player.vy = -220
                if player.rect.centerx < e.rect.centerx:
                    player.rect.x -= 20
                else:
                    player.rect.x += 20

        if player.health <= 0:
            game_state = STATE_GAME_OVER
            return

        if remaining == 0:
            game_state = STATE_WON
            return

def draw():
    screen.clear()
    if game_state == STATE_MENU:
        screen.fill(SKY_BLUE)
        screen.draw.text("PLATFORMER - CLASSIC", center=(WIDTH / 2, HEIGHT / 3), fontsize=54, color=BLACK)
        screen.draw.text("Press SPACE to Start", center=(WIDTH / 2, HEIGHT / 2), fontsize=34, color="white")
        screen.draw.text("Arrows/WASD to move, Up/W to jump", center=(WIDTH / 2, HEIGHT / 2 + 50), fontsize=24, color="black")

    elif game_state == STATE_PLAYING:
        screen.fill(SKY_BLUE)
        tile_map.draw()

        for coin in coins:
            coin.draw()

        for e in enemies:
            e.draw()

        player.draw()

        screen.draw.text(f"Health: {player.health}", (12, 10), fontsize=24, color=BLACK)
        screen.draw.text(f"Score: {score}", (WIDTH - 170, 10), fontsize=24, color=BLACK)

    elif game_state == STATE_GAME_OVER:
        screen.fill(BLACK)
        screen.draw.text("GAME OVER", center=(WIDTH/2, HEIGHT/2 - 20), fontsize=72, color="red")
        screen.draw.text(f"Final Score: {score}", center=(WIDTH/2, HEIGHT/2 + 40), fontsize=40, color="yellow")
        screen.draw.text("Press SPACE to restart", center=(WIDTH/2, HEIGHT/2 + 110), fontsize=28, color="white")

    elif game_state == STATE_WON:
        screen.fill((50, 150, 50))
        screen.draw.text("YOU WIN!", center=(WIDTH/2, HEIGHT/2 - 20), fontsize=72, color="gold")
        screen.draw.text(f"Score Total: {score}", center=(WIDTH/2, HEIGHT/2 + 40), fontsize=40, color="white")
        screen.draw.text("Press SPACE to restart", center=(WIDTH/2, HEIGHT/2 + 110), fontsize=28, color="yellow")

def on_key_down(key):
    global game_state
    if key == keys.SPACE:
        if game_state == STATE_MENU:
            reset_game()
        elif game_state in (STATE_GAME_OVER, STATE_WON):
            reset_game()
