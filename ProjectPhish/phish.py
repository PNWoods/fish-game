import pygame
import random
import sys
import os
import math
import pickle  # For saving and loading game data

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer module for audio

# Screen dimensions
WIDTH, HEIGHT = 1920, 1080  # Updated resolution

# Create game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fish Collector")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Fonts
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

# Load the generic fish image
fish_base_image = pygame.image.load(os.path.join('images', 'fish.png')).convert_alpha()
fish_base_image = pygame.transform.scale(fish_base_image, (60, 30))

# Load gold coin image
coin_image = pygame.image.load(os.path.join('images', 'gold_coin.png')).convert_alpha()
coin_image = pygame.transform.scale(coin_image, (30, 30))

# Load world map image
world_map_image = pygame.image.load(os.path.join('images', 'main_menu.png')).convert()
world_map_image = pygame.transform.scale(world_map_image, (220, 220))

# Load cosmetic items (e.g., hats)
hat_image = pygame.image.load(os.path.join('images', 'hat.png')).convert_alpha()
hat_image = pygame.transform.scale(hat_image, (30, 30))

def colorize(image, new_color):
    """Colorize an image while preserving its transparency."""
    image = image.copy()  # Copy the original image
    # Zero out RGB values
    image.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    # Add the new color
    image.fill(new_color[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
    return image

# Load background images for each area
background_images = {
    "Pond": pygame.image.load(os.path.join('images', 'pond.png')).convert(),
    "Lake": pygame.image.load(os.path.join('images', 'lake.png')).convert(),
    "Stream": pygame.image.load(os.path.join('images', 'stream.png')).convert(),
    "River": pygame.image.load(os.path.join('images', 'river.png')).convert(),
    "Ocean": pygame.image.load(os.path.join('images', 'ocean.png')).convert(),
    "Tank": pygame.image.load(os.path.join('images', 'tank.png')).convert(),  # Add Tank background
}

# Scale background images to fit the screen
for key in background_images:
    background_images[key] = pygame.transform.scale(background_images[key], (WIDTH, HEIGHT))

# Load sounds
background_music_path = os.path.join('images', 'sounds', 'background_music.mp3')
coin_sound_path = os.path.join('images', 'sounds', 'coin_sound.mp3')

# Load background music
pygame.mixer.music.load(background_music_path)
pygame.mixer.music.play(-1)  # Play indefinitely

# Load coin sound effect
coin_sound = pygame.mixer.Sound(coin_sound_path)

# Fish base values based on pattern
fish_base_values = {
    "plain": 1,
    "striped": 2,
    "spotted": 3,
    "glowing": 4,
    "rainbow": 5,
}

# Define Upgrade class
class Upgrade:
    def __init__(self, name, cost, level=0, max_level=5):
        self.name = name
        self.cost = cost
        self.level = level
        self.max_level = max_level

# Define Fish class
class Fish(pygame.sprite.Sprite):
    def __init__(self, color, pattern, cosmetics=None, size_multiplier=1.0):
        super().__init__()
        self.color = color
        self.pattern = pattern
        self.base_value = fish_base_values.get(pattern, 1)  # Base value of the fish
        self.cosmetics = cosmetics if cosmetics else []

        # Colorize the base fish image
        self.base_image = colorize(fish_base_image, color)

        # Add patterns
        self.add_pattern()

        # Apply size multiplier
        self.base_image = pygame.transform.scale(
            self.base_image,
            (int(self.base_image.get_width() * size_multiplier),
             int(self.base_image.get_height() * size_multiplier))
        )

        # Set initial position
        self.rect = self.base_image.get_rect()
        self.rect.x = random.randint(220, WIDTH - 320)  # Adjusted for sidebars
        self.rect.y = random.randint(0, HEIGHT - self.rect.height)

        # Set velocity
        self.dx = random.uniform(-3, 3)
        self.dy = random.uniform(-3, 3)
        # Ensure fish has some movement
        if self.dx == 0 and self.dy == 0:
            self.dx = 1

        # Set initial image and angle
        self.update_image()

    def add_pattern(self):
        # Create a surface to draw patterns on
        pattern_surface = pygame.Surface(self.base_image.get_size(), pygame.SRCALPHA)

        if self.pattern == "striped":
            # Draw stripes
            for x in range(0, self.base_image.get_width(), 10):
                pygame.draw.line(pattern_surface, BLACK, (x, 0), (x, self.base_image.get_height()), 2)
        elif self.pattern == "spotted":
            # Draw spots
            for _ in range(5):
                x = random.randint(0, self.base_image.get_width())
                y = random.randint(0, self.base_image.get_height())
                pygame.draw.circle(pattern_surface, BLACK, (x, y), 3)
        elif self.pattern == "glowing":
            # Draw a glow effect (simple representation)
            glow = pygame.Surface(self.base_image.get_size(), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255, 255, 0, 100), glow.get_rect().inflate(10, 10))
            pattern_surface.blit(glow, (-5, -5))
        elif self.pattern == "rainbow":
            # Draw rainbow stripes
            colors = [pygame.Color("red"), pygame.Color("orange"), pygame.Color("yellow"),
                      pygame.Color("green"), pygame.Color("blue"), pygame.Color("indigo"),
                      pygame.Color("violet")]
            stripe_height = self.base_image.get_height() // len(colors)
            for i, color in enumerate(colors):
                rect = pygame.Rect(0, i * stripe_height, self.base_image.get_width(), stripe_height)
                pygame.draw.rect(pattern_surface, color, rect)

        # Blit the pattern onto the fish image
        self.base_image.blit(pattern_surface, (0, 0))

    def update(self):
        # Update position
        self.rect.x += self.dx
        self.rect.y += self.dy

        # Define movement boundaries (excluding sidebars)
        left_boundary = 220
        right_boundary = WIDTH - 320
        top_boundary = 0
        bottom_boundary = HEIGHT - self.rect.height

        # Bounce off walls
        if self.rect.left <= left_boundary or self.rect.right >= right_boundary:
            self.dx *= -1
            self.rect.x += self.dx  # Move fish away from the wall
        if self.rect.top <= top_boundary or self.rect.bottom >= bottom_boundary:
            self.dy *= -1
            self.rect.y += self.dy  # Move fish away from the wall

        # Update image
        self.update_image()

    def update_image(self):
        # Recalculate angle and rotate image
        self.angle = math.degrees(math.atan2(self.dy, self.dx)) + 90  # Adjusted angle
        self.image = pygame.transform.rotate(self.base_image, self.angle)

        # Apply cosmetics
        for cosmetic in self.cosmetics:
            self.image.blit(cosmetic['image'], cosmetic['position'])

        # Update rect to new image's rect, keeping the center position
        self.rect = self.image.get_rect(center=self.rect.center)

# Define Player class
class Player:
    def __init__(self):
        self.level = 1
        self.experience = 0
        self.experience_needed = 10  # Experience needed for next level
        self.collected_fish = []
        self.stored_fish = []  # Fish kept in storage
        self.tank_fish = []    # Fish in the tank
        self.coins = 0
        self.messages = []
        self.area_index = 0  # Index of the current area in the areas list
        self.unlocked_areas = ["Pond"]  # Areas the player has unlocked
        self.upgrades = {
            "Auto-Collector": Upgrade("Auto-Collector", cost=100),
            "Bigger Fish": Upgrade("Bigger Fish", cost=50),
            "Increased Storage": Upgrade("Increased Storage", cost=75),
            "Increased Breeding": Upgrade("Increased Breeding", cost=80),
            "Luck Upgrade": Upgrade("Luck Upgrade", cost=60),
        }
        self.cosmetics_inventory = []
        self.auto_collect_timer = pygame.time.get_ticks()
        self.auto_collect_interval = 1000  # 1 second
        self.fish_size_multiplier = 1.0
        self.storage_capacity = 10  # Default storage capacity
        self.breeding_interval = 30000  # 30 seconds, can be decreased with upgrade
        self.luck_multiplier = 1.0  # Multiplier for storage chance

    def add_experience(self, amount):
        self.experience += amount
        while self.experience >= self.experience_needed:
            self.experience -= self.experience_needed
            self.level += 1
            self.add_message(f"You've reached level {self.level}!")
            # Increase experience needed for next level by 10x
            self.experience_needed *= 10

    def add_message(self, message):
        self.messages.append(message)
        # Keep only the last 10 messages
        if len(self.messages) > 10:
            self.messages.pop(0)

    def sell_fish(self, fish):
        sell_value = fish.base_value * 5  # Sell for 5x base value
        self.coins += sell_value
        self.stored_fish.remove(fish)
        self.add_message(f"Sold a {fish.pattern} fish for {sell_value} coins!")
        coin_sound.play()  # Play the coin sound effect when a fish is sold

    def can_upgrade(self, upgrade_name):
        upgrade = self.upgrades[upgrade_name]
        return self.coins >= upgrade.cost and upgrade.level < upgrade.max_level

    def purchase_upgrade(self, upgrade_name):
        if self.can_upgrade(upgrade_name):
            upgrade = self.upgrades[upgrade_name]
            self.coins -= int(upgrade.cost)
            upgrade.level += 1
            self.add_message(f"Purchased {upgrade_name} Upgrade Level {upgrade.level}!")
            # Apply upgrade effects
            if upgrade_name == "Auto-Collector":
                # Reduce interval by multiplying by a random factor between 0.65 and 0.75
                factor = random.uniform(0.65, 0.75)
                self.auto_collect_interval *= factor
                self.auto_collect_interval = max(200, self.auto_collect_interval)
                upgrade.cost *= random.uniform(1.65, 1.75)
            elif upgrade_name == "Bigger Fish":
                self.fish_size_multiplier += 0.1
                upgrade.cost *= random.uniform(1.65, 1.75)
            elif upgrade_name == "Increased Storage":
                self.storage_capacity += 5
                upgrade.cost *= random.uniform(1.65, 1.75)
            elif upgrade_name == "Increased Breeding":
                factor = random.uniform(0.65, 0.75)
                self.breeding_interval *= factor
                self.breeding_interval = max(5000, self.breeding_interval)
                upgrade.cost *= random.uniform(1.65, 1.75)
            elif upgrade_name == "Luck Upgrade":
                self.luck_multiplier += 0.05
                upgrade.cost *= random.uniform(1.65, 1.75)
        else:
            self.add_message("Cannot purchase upgrade.")

# Define Game class
class Game:
    def __init__(self):
        self.player = Player()
        self.all_fish = pygame.sprite.Group()
        self.running = True
        self.areas = ["Pond", "Lake", "Stream", "River", "Ocean", "Tank"]  # Added "Tank"
        self.area = self.areas[self.player.area_index]
        self.load_game()  # Load game data if available
        self.spawn_fish()

        # Right sidebar dimensions
        self.sidebar_width = 220

        # World map button
        self.world_map_rect = pygame.Rect(WIDTH - self.sidebar_width, HEIGHT - 220, self.sidebar_width, 220)

        # Breeding variables
        self.last_breeding_time = pygame.time.get_ticks()

        # Cosmetic items available
        self.cosmetics_shop = [
            {"name": "Hat", "image": hat_image, "cost": 30},
            # Add more cosmetics as needed
        ]

    def spawn_fish(self):
        # Fish patterns available in each area
        area_patterns = {
            "Pond": ["plain"],
            "Lake": ["plain", "striped"],
            "Stream": ["plain", "striped", "spotted"],
            "River": ["plain", "striped", "spotted", "glowing"],
            "Ocean": ["plain", "striped", "spotted", "glowing", "rainbow"],
        }

        # Colors available
        colors = [
            pygame.Color("red"), pygame.Color("green"), pygame.Color("blue"),
            pygame.Color("orange"), pygame.Color("pink"), pygame.Color("cyan"),
            pygame.Color("magenta"), pygame.Color("brown"), pygame.Color("gray"),
            pygame.Color("yellow"), pygame.Color("purple")
        ]

        patterns = area_patterns.get(self.area, ["plain"])

        number_of_fish = 50  # Fish count
        for _ in range(number_of_fish):
            color = random.choice(colors)
            pattern = random.choice(patterns)
            fish = Fish(color, pattern, size_multiplier=self.player.fish_size_multiplier)
            self.all_fish.add(fish)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(60)  # Limit to 60 FPS
            self.handle_events()
            self.update()
            self.draw()
        self.save_game()  # Save game data on exit
        pygame.quit()
        sys.exit()

    def auto_collect_fish(self):
        if len(self.all_fish) > 0:
            fish = random.choice(self.all_fish.sprites())
            self.player.collected_fish.append(fish)
            self.player.add_experience(1)  # Each fish gives 1 experience point
            self.player.coins += 1  # Player gets 1 coin per fish collected
            self.all_fish.remove(fish)
            self.player.add_message("Auto-collected a fish and earned 1 coin!")

            # Chance to store fish
            if random.random() < 0.025 * self.player.luck_multiplier:
                if len(self.player.stored_fish) < self.player.storage_capacity:
                    self.player.stored_fish.append(fish)
                    self.player.add_message(f"Stored a {fish.pattern} fish!")
                else:
                    self.player.add_message("Storage is full!")

            if len(self.all_fish) == 0:
                self.spawn_fish()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                # Check if the world map is clicked
                if self.world_map_rect.collidepoint(pos):
                    self.open_area_shop()

                # Check for cosmetics shop click
                if pos[0] < 220 and pos[1] > HEIGHT - 440 and pos[1] < HEIGHT - 220:
                    self.open_cosmetics_shop()

                # Check for upgrade shop click
                if pos[0] < 220 and pos[1] > HEIGHT - 220:
                    self.open_upgrade_shop()

                if self.area == "Tank":
                    # Move fish from storage to tank
                    for fish in self.player.stored_fish:
                        index = self.player.stored_fish.index(fish)
                        fish_rect = pygame.Rect(
                            WIDTH - self.sidebar_width + 10,
                            150 + index * 40,
                            40,
                            30
                        )
                        if fish_rect.collidepoint(pos):
                            self.player.stored_fish.remove(fish)
                            self.player.tank_fish.append(fish)
                            self.player.add_message(f"Moved {fish.pattern} fish to tank")
                            break

                    # Move fish from tank to storage
                    for fish in self.player.tank_fish:
                        if fish.rect.collidepoint(pos):
                            self.player.tank_fish.remove(fish)
                            if len(self.player.stored_fish) < self.player.storage_capacity:
                                self.player.stored_fish.append(fish)
                                self.player.add_message(f"Moved {fish.pattern} fish to storage")
                            else:
                                self.player.add_message("Storage is full!")
                            break

                    # Apply cosmetics to fish in tank
                    for fish in self.player.tank_fish:
                        if fish.rect.collidepoint(pos):
                            self.apply_cosmetic(fish)
                            break
                else:
                    # Check for fish clicks
                    clicked_sprites = [s for s in self.all_fish if s.rect.collidepoint(pos)]
                    for fish in clicked_sprites:
                        self.player.collected_fish.append(fish)
                        self.player.add_experience(1)  # Each fish gives 1 experience point
                        self.player.coins += 1  # Player gets 1 coin per fish tapped
                        self.all_fish.remove(fish)
                        self.player.add_message(f"Collected a {fish.pattern} fish and earned 1 coin!")

                        # Chance to store fish
                        if random.random() < 0.025 * self.player.luck_multiplier:
                            if len(self.player.stored_fish) < self.player.storage_capacity:
                                self.player.stored_fish.append(fish)
                                self.player.add_message(f"Stored a {fish.pattern} fish!")
                            else:
                                self.player.add_message("Storage is full!")

                        if len(self.all_fish) == 0:
                            self.spawn_fish()

                    # Sell fish from storage
                    for fish in self.player.stored_fish:
                        index = self.player.stored_fish.index(fish)
                        fish_rect = pygame.Rect(
                            WIDTH - self.sidebar_width + 10,
                            150 + index * 40,
                            40,
                            30
                        )
                        if fish_rect.collidepoint(pos):
                            self.player.sell_fish(fish)
                            break

    def open_area_shop(self):
        # Display the area shop using the world map image as background
        shop_running = True
        while shop_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    shop_running = False
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    # Check if player wants to buy a new area or go to Tank
                    for i, area in enumerate(self.areas):
                        area_rect = pygame.Rect(WIDTH // 2 - 100, 100 + i * 60, 200, 50)
                        if area_rect.collidepoint(pos):
                            if area == "Tank":
                                self.player.area_index = i
                                self.area = self.areas[self.player.area_index]
                                self.player.add_message(f"Moved to {self.area}!")
                                shop_running = False
                            elif area not in self.player.unlocked_areas:
                                # Cost to unlock the area
                                cost = (i + 1) * 10  # Example cost formula
                                if self.player.coins >= cost:
                                    self.player.coins -= cost
                                    self.player.unlocked_areas.append(area)
                                    self.player.add_message(f"Unlocked {area}!")
                                else:
                                    self.player.add_message("Not enough coins!")
                            else:
                                self.player.area_index = i
                                self.area = self.areas[self.player.area_index]
                                self.player.add_message(f"Moved to {self.area}!")
                                self.all_fish.empty()
                                self.spawn_fish()
                            shop_running = False
                            break

            # Draw shop interface with world map as background
            shop_background = pygame.transform.scale(world_map_image, (WIDTH, HEIGHT))
            screen.blit(shop_background, (0, 0))

            # Semi-transparent overlay to highlight the shop area
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            title_text = font.render("Area Shop", True, WHITE)
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))

            for i, area in enumerate(self.areas):
                area_rect = pygame.Rect(WIDTH // 2 - 100, 100 + i * 60, 200, 50)
                pygame.draw.rect(screen, (70, 130, 180), area_rect)
                area_text = font.render(area, True, WHITE)
                screen.blit(area_text, (area_rect.x + 10, area_rect.y + 10))

                if area == "Tank":
                    unlocked_text = small_font.render("Unlocked", True, WHITE)
                    screen.blit(unlocked_text, (area_rect.x + 10, area_rect.y + 30))
                elif area not in self.player.unlocked_areas:
                    cost = (i + 1) * 10  # Example cost formula
                    cost_text = small_font.render(f"Cost: {cost} coins", True, WHITE)
                    screen.blit(cost_text, (area_rect.x + 10, area_rect.y + 30))
                else:
                    unlocked_text = small_font.render("Unlocked", True, WHITE)
                    screen.blit(unlocked_text, (area_rect.x + 10, area_rect.y + 30))

            pygame.display.flip()

    def open_upgrade_shop(self):
        # Display the upgrade shop
        shop_running = True
        while shop_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    shop_running = False
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    # Check if player wants to purchase an upgrade
                    for i, upgrade_name in enumerate(self.player.upgrades.keys()):
                        upgrade_rect = pygame.Rect(WIDTH // 2 - 150, 100 + i * 70, 300, 60)
                        if upgrade_rect.collidepoint(pos):
                            self.player.purchase_upgrade(upgrade_name)
                            break
                    else:
                        shop_running = False  # Clicked outside, exit shop

            # Draw shop interface
            screen.fill((50, 50, 50))
            title_text = font.render("Upgrade Shop", True, WHITE)
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))

            for i, (upgrade_name, upgrade) in enumerate(self.player.upgrades.items()):
                upgrade_rect = pygame.Rect(WIDTH // 2 - 150, 100 + i * 70, 300, 60)
                pygame.draw.rect(screen, (70, 130, 180), upgrade_rect)
                upgrade_text = font.render(f"{upgrade_name} (Level {upgrade.level}/{upgrade.max_level})", True, WHITE)
                screen.blit(upgrade_text, (upgrade_rect.x + 10, upgrade_rect.y + 10))
                cost_text = small_font.render(f"Cost: {int(upgrade.cost)} coins", True, WHITE)
                screen.blit(cost_text, (upgrade_rect.x + 10, upgrade_rect.y + 40))

            pygame.display.flip()

    def open_cosmetics_shop(self):
        # Display the cosmetics shop
        shop_running = True
        while shop_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    shop_running = False
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    # Check if player wants to purchase a cosmetic
                    for i, cosmetic in enumerate(self.cosmetics_shop):
                        cosmetic_rect = pygame.Rect(WIDTH // 2 - 150, 100 + i * 70, 300, 60)
                        if cosmetic_rect.collidepoint(pos):
                            if self.player.coins >= cosmetic['cost']:
                                self.player.coins -= cosmetic['cost']
                                self.player.cosmetics_inventory.append(cosmetic)
                                self.player.add_message(f"Purchased {cosmetic['name']}!")
                            else:
                                self.player.add_message("Not enough coins!")
                            break
                    else:
                        shop_running = False  # Clicked outside, exit shop

            # Draw shop interface
            screen.fill((50, 50, 50))
            title_text = font.render("Cosmetics Shop", True, WHITE)
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))

            for i, cosmetic in enumerate(self.cosmetics_shop):
                cosmetic_rect = pygame.Rect(WIDTH // 2 - 150, 100 + i * 70, 300, 60)
                pygame.draw.rect(screen, (70, 130, 180), cosmetic_rect)
                cosmetic_text = font.render(f"{cosmetic['name']}", True, WHITE)
                screen.blit(cosmetic_text, (cosmetic_rect.x + 10, cosmetic_rect.y + 10))
                cost_text = small_font.render(f"Cost: {cosmetic['cost']} coins", True, WHITE)
                screen.blit(cost_text, (cosmetic_rect.x + 10, cosmetic_rect.y + 40))

            pygame.display.flip()

    def apply_cosmetic(self, fish):
        # Apply a cosmetic to a fish
        if self.player.cosmetics_inventory:
            # For simplicity, apply the first cosmetic in the list
            cosmetic = self.player.cosmetics_inventory[0]
            fish.cosmetics.append({
                'image': cosmetic['image'],
                'position': (fish.image.get_width() // 2 - cosmetic['image'].get_width() // 2,
                             -cosmetic['image'].get_height())  # Position above the fish
            })
            self.player.add_message(f"Applied {cosmetic['name']} to a fish!")
            self.player.cosmetics_inventory.remove(cosmetic)
        else:
            self.player.add_message("You have no cosmetics!")

    def breed_fish(self):
        # Breeding logic
        if len(self.player.tank_fish) >= 2:
            # Randomly select two parents
            parent1, parent2 = random.sample(self.player.tank_fish, 2)
            # Create baby fish with combined traits
            baby_fish = self.create_baby_fish(parent1, parent2)
            # Add baby fish to tank
            self.player.tank_fish.append(baby_fish)
            self.player.add_message("A new baby fish was born!")

    def create_baby_fish(self, parent1, parent2):
        # Combine traits
        color = random.choice([parent1.color, parent2.color])
        pattern = random.choice([parent1.pattern, parent2.pattern])
        baby_fish = Fish(color, pattern, size_multiplier=self.player.fish_size_multiplier)
        # Inherit cosmetics from parents (randomly)
        inherited_cosmetics = random.choice([parent1.cosmetics, parent2.cosmetics])
        baby_fish.cosmetics = [cosmetic.copy() for cosmetic in inherited_cosmetics]
        # Position baby fish randomly in tank area
        baby_fish.rect.x = random.randint(220, WIDTH - 320)
        baby_fish.rect.y = random.randint(0, HEIGHT - baby_fish.rect.height)
        return baby_fish

    def update(self):
        # Auto-collector logic
        if self.player.upgrades["Auto-Collector"].level > 0:
            current_time = pygame.time.get_ticks()
            if current_time - self.player.auto_collect_timer >= self.player.auto_collect_interval:
                self.auto_collect_fish()
                self.player.auto_collect_timer = current_time

        if self.area == "Tank":
            # Update tank fish movement
            for fish in self.player.tank_fish:
                fish.update()
            # Implement breeding logic
            current_time = pygame.time.get_ticks()
            if current_time - self.last_breeding_time >= self.player.breeding_interval:
                self.breed_fish()
                self.last_breeding_time = current_time
        else:
            # Update fish movement
            self.all_fish.update()

    def draw(self):
        # Draw the background image for the current area
        screen.blit(background_images[self.area], (0, 0))

        # Draw left sidebar background
        pygame.draw.rect(screen, (30, 30, 30, 180), (0, 0, 220, HEIGHT))

        # Draw right sidebar background
        pygame.draw.rect(screen, (30, 30, 30, 180), (WIDTH - self.sidebar_width, 0, self.sidebar_width, HEIGHT))

        # Display player info on the left sidebar
        level_text = font.render(f"Level: {self.player.level}", True, WHITE)
        exp_text = font.render(f"EXP: {self.player.experience}/{self.player.experience_needed}", True, WHITE)
        area_text = font.render(f"Area: {self.area}", True, WHITE)
        coins_text = font.render(f"Coins: {self.player.coins}", True, WHITE)
        screen.blit(level_text, (10, 10))
        screen.blit(exp_text, (10, 50))
        screen.blit(area_text, (10, 90))
        screen.blit(coins_text, (10, 130))
        screen.blit(coin_image, (150, 125))

        # Display messages
        y_offset = 180
        for message in self.player.messages:
            message_text = small_font.render(message, True, WHITE)
            screen.blit(message_text, (10, y_offset))
            y_offset += 25

        # Draw fish
        if self.area == "Tank":
            for fish in self.player.tank_fish:
                screen.blit(fish.image, fish.rect)
        else:
            self.all_fish.draw(screen)

        # Display stored fish on the right sidebar
        storage_title = font.render(f"Storage ({len(self.player.stored_fish)}/{self.player.storage_capacity})", True, WHITE)
        screen.blit(storage_title, (WIDTH - self.sidebar_width + 10, 10))

        for i, fish in enumerate(self.player.stored_fish):
            # Draw fish image
            fish_pos = (WIDTH - self.sidebar_width + 10, 150 + i * 40)
            screen.blit(fish.image, fish_pos)
            # Draw fish value
            sell_value = fish.base_value * 5  # Sell value is 5x base value
            value_text = small_font.render(f"{sell_value} coins", True, WHITE)
            screen.blit(value_text, (WIDTH - self.sidebar_width + 60, 160 + i * 40))

        # Draw world map at the bottom of the right sidebar
        screen.blit(world_map_image, self.world_map_rect.topleft)

        # Draw cosmetics shop button above the upgrade shop
        pygame.draw.rect(screen, (70, 130, 180), (0, HEIGHT - 440, self.sidebar_width, 220))
        cosmetics_text = font.render("Cosmetics", True, WHITE)
        screen.blit(cosmetics_text, (10, HEIGHT - 430))

        # Draw upgrade shop button at the bottom of the left sidebar
        pygame.draw.rect(screen, (70, 130, 180), (0, HEIGHT - 220, self.sidebar_width, 220))
        upgrade_text = font.render("Upgrades", True, WHITE)
        screen.blit(upgrade_text, (10, HEIGHT - 210))

        pygame.display.flip()

    def save_game(self):
        # Save the game data to a file
        save_data = {
            'player': self.player,
            'area': self.area,
            'areas_unlocked': self.player.unlocked_areas,
        }
        with open('savegame.pkl', 'wb') as f:
            pickle.dump(save_data, f)

    def load_game(self):
        # Load the game data from a file
        if os.path.exists('savegame.pkl') and os.path.getsize('savegame.pkl') > 0:
            try:
                with open('savegame.pkl', 'rb') as f:
                    save_data = pickle.load(f)
                    self.player = save_data['player']
                    self.area = save_data['area']
                    self.player.unlocked_areas = save_data['areas_unlocked']
                    self.player.auto_collect_timer = pygame.time.get_ticks()
                    self.last_breeding_time = pygame.time.get_ticks()
                    self.player.add_message("Game Loaded!")
            except (EOFError, pickle.UnpicklingError):
                # Handle empty or corrupted save file
                self.player.add_message("Save file is corrupted. Starting a new game.")
                self.reset_game_data()
        else:
            self.player.add_message("New Game Started!")

    def reset_game_data(self):
        self.player = Player()
        self.area = self.areas[self.player.area_index]
        self.all_fish.empty()
        self.spawn_fish()


# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()
