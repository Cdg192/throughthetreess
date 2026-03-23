#!/usr/bin/env python3
"""
ASTHENIA - A standalone RPG adventure game
Rescue your cat Ptouneigh from the evil sorceress Tracey
"""

import pygame
import sys
import random
import math
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
TILE_SIZE = 40

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 53, 69)
GREEN = (0, 214, 128)
BLUE = (10, 148, 218)
DARK_BLUE = (15, 52, 96)
BROWN = (139, 69, 19)
DARK_RED = (139, 26, 26)
ORANGE = (255, 165, 0)
GOLD = (255, 215, 0)
GRAY = (128, 128, 128)

class GameState(Enum):
    MENU = 1
    EXPLORING = 2
    COMBAT = 3
    DIALOGUE = 4
    VICTORY = 5
    GAME_OVER = 6

@dataclass
class Character:
    name: str
    x: int
    y: int
    hp: int
    max_hp: int
    attack: int
    defense: int
    color: Tuple[int, int, int]
    size: int = 30

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("⚔️ ASTHENIA - Rescue the Cat ⚔️")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        self.state = GameState.MENU
        self.init_game()
        self.log_messages = []
        self.animation_counter = 0
        
    def init_game(self):
        """Initialize game state"""
        self.player = Character("Caleb", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 100, 100, 8, 5, BROWN)
        self.enemy = None
        self.current_location = "cottage"
        self.gold = 0
        self.level = 1
        self.xp = 0
        self.enemies_defeated = set()
        self.game_over = False
        self.victory = False
        self.in_combat = False
        self.combat_log = []
        self.player_turn = True
        self.wait_timer = 0
        
    def add_log(self, message: str, color: Tuple[int, int, int] = WHITE):
        """Add message to log"""
        self.log_messages.append((message, color, pygame.time.get_ticks()))
        if len(self.log_messages) > 10:
            self.log_messages.pop(0)
    
    def draw_menu(self):
        """Draw main menu"""
        self.screen.fill(BLACK)
        
        title = self.font_large.render("⚔️ ASTHENIA ⚔️", True, RED)
        subtitle = self.font_medium.render("Rescue Ptouneigh from the Sorceress", True, BLUE)
        
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 200))
        
        start_text = self.font_medium.render("Press SPACE to Start", True, GREEN)
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 400))
        
        story = [
            "Your beloved cat Ptouneigh has been captured!",
            "The evil sorceress Tracey and her Sionist cult hold him captive.",
            "Armed with your Gibson Guitar and sidekick Chazz,",
            "you must battle through cultists and defeat Tracey.",
            "Can you rescue your furry friend?"
        ]
        
        y = 500
        for line in story:
            text = self.font_small.render(line, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 40
    
    def draw_character(self, char: Character, x: int, y: int, selected: bool = False):
        """Draw a character"""
        # Draw shadow
        pygame.draw.ellipse(self.screen, (50, 50, 50), (x - 25, y + 20, 50, 15))
        
        # Draw body
        pygame.draw.rect(self.screen, char.color, (x - 15, y - 10, 30, 35))
        
        # Draw head
        pygame.draw.circle(self.screen, (255, 200, 150), (x, y - 20), 12)
        
        # Draw eyes
        pygame.draw.circle(self.screen, BLACK, (x - 5, y - 22), 3)
        pygame.draw.circle(self.screen, BLACK, (x + 5, y - 22), 3)
        
        # Draw selection glow
        if selected:
            pygame.draw.circle(self.screen, GREEN, (x, y), 45, 3)
        
        # Draw name
        name_text = self.font_small.render(char.name, True, WHITE)
        self.screen.blit(name_text, (x - name_text.get_width() // 2, y + 40))
    
    def draw_hud(self):
        """Draw heads-up display"""
        # Player HP bar
        bar_width = 200
        bar_height = 20
        hp_ratio = max(0, self.player.hp / self.player.max_hp)
        
        pygame.draw.rect(self.screen, RED, (10, 10, bar_width, bar_height))
        pygame.draw.rect(self.screen, GREEN, (10, 10, bar_width * hp_ratio, bar_height))
        pygame.draw.rect(self.screen, WHITE, (10, 10, bar_width, bar_height), 2)
        
        hp_text = self.font_small.render(f"❤️ HP: {max(0, self.player.hp)}/{self.player.max_hp}", True, WHITE)
        self.screen.blit(hp_text, (15, 35))
        
        # Player stats
        stats_text = f"⚔️ ATK: {self.player.attack} | 🛡️ DEF: {self.player.defense} | 💰 Gold: {self.gold}"
        stats_surface = self.font_small.render(stats_text, True, BLUE)
        self.screen.blit(stats_surface, (10, 65))
        
        # Location name
        location_text = self.font_medium.render(f"📍 {self.current_location.upper()}", True, ORANGE)
        self.screen.blit(location_text, (SCREEN_WIDTH - 300, 10))
    
    def draw_combat_hud(self):
        """Draw combat interface"""
        if not self.enemy:
            return
        
        # Enemy info
        enemy_name = self.font_medium.render(f"⚠️ {self.enemy.name}", True, RED)
        self.screen.blit(enemy_name, (SCREEN_WIDTH - 300, 50))
        
        # Enemy HP bar
        bar_width = 250
        hp_ratio = max(0, self.enemy.hp / self.enemy.max_hp)
        pygame.draw.rect(self.screen, RED, (SCREEN_WIDTH - 260, 90, bar_width, 20))
        pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH - 260, 90, bar_width * hp_ratio, 20))
        pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH - 260, 90, bar_width, 20), 2)
        
        enemy_hp = self.font_small.render(f"HP: {max(0, self.enemy.hp)}/{self.enemy.max_hp}", True, WHITE)
        self.screen.blit(enemy_hp, (SCREEN_WIDTH - 250, 95))
        
        # Action buttons
        action_y = SCREEN_HEIGHT - 100
        actions = [
            ("SPACE - Attack", BLUE),
            ("D - Defend", BLUE),
            ("R - Run", BLUE)
        ]
        
        for i, (action, color) in enumerate(actions):
            action_text = self.font_small.render(action, True, color)
            self.screen.blit(action_text, (20 + i * 300, action_y))
    
    def draw_log(self):
        """Draw game log messages"""
        current_time = pygame.time.get_ticks()
        y_pos = SCREEN_HEIGHT - 200
        
        for message, color, timestamp in self.log_messages:
            if current_time - timestamp < 5000:  # Show for 5 seconds
                text = self.font_small.render(message, True, color)
                self.screen.blit(text, (20, y_pos))
                y_pos -= 30
    
    def start_combat(self, enemy_name: str):
        """Start a combat encounter"""
        enemies = {
            "cultist": Character("Cultist Minion", SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2, 25, 25, 5, 2, DARK_RED),
            "priest": Character("Sionist Priest", SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2, 40, 40, 8, 3, RED),
            "golem": Character("Tower Guardian", SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2, 60, 60, 10, 4, GRAY),
            "tracey": Character("Tracey the Sorceress", SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2, 80, 80, 12, 5, (100, 0, 100)),
        }
        
        self.enemy = enemies.get(enemy_name)
        if not self.enemy:
            self.enemy = enemies["cultist"]
        
        self.in_combat = True
        self.state = GameState.COMBAT
        self.combat_log = []
        self.player_turn = True
        self.player.x = SCREEN_WIDTH // 2 - 150
        self.player.y = SCREEN_HEIGHT // 2
        self.add_log(f"⚔️ {self.enemy.name} appears!", RED)
    
    def player_attack(self):
        """Player attacks enemy"""
        damage = self.player.attack + random.randint(-1, 3)
        self.enemy.hp -= damage
        
        messages = [
            f"Caleb swings his Gibson Guitar for {damage} damage!",
            f"Caleb riffs and hits {self.enemy.name} for {damage} damage!",
            f"The Gibson Guitar strikes for {damage} damage!",
        ]
        
        self.add_log(random.choice(messages), GREEN)
        
        if self.enemy.hp <= 0:
            self.handle_victory()
        else:
            self.wait_timer = 60
            self.player_turn = False
    
    def player_defend(self):
        """Player defends"""
        self.add_log("Caleb takes a defensive stance!", BLUE)
        damage = max(1, self.enemy.attack // 2)
        self.player.hp -= damage
        self.add_log(f"Enemy attacks for {damage} damage (reduced)!", ORANGE)
        
        if self.player.hp <= 0:
            self.game_over = True
            self.state = GameState.GAME_OVER
            self.add_log("💀 You have been defeated!", RED)
        
        self.wait_timer = 60
        self.player_turn = False
    
    def enemy_attack(self):
        """Enemy attacks player"""
        if self.enemy.name == "Tracey the Sorceress":
            messages = [
                '"Where are you?! I can\'t see!"',
                '"Stupid eyes! Why can\'t I see properly?!"',
                '"I\'m attacking where I think you are!"'
            ]
            self.add_log(f"{self.enemy.name} shouts: {random.choice(messages)}", RED)
        
        damage = max(1, self.enemy.attack - self.player.defense + random.randint(-1, 2))
        self.player.hp -= damage
        self.add_log(f"Enemy deals {damage} damage!", RED)
        
        if self.player.hp <= 0:
            self.game_over = True
            self.state = GameState.GAME_OVER
            self.add_log("💀 You have been defeated!", RED)
    
    def handle_victory(self):
        """Handle combat victory"""
        self.add_log(f"✨ Victory! {self.enemy.name} defeated!", GREEN)
        
        # Determine rewards
        rewards = {
            "cultist": (20, 10),
            "priest": (50, 25),
            "golem": (100, 50),
            "tracey": (300, 200),
        }
        
        enemy_type = self.enemy.name.lower().split()[0]
        if "cultist" in self.enemy.name.lower():
            xp_gain, gold_gain = rewards["cultist"]
        elif "priest" in self.enemy.name.lower():
            xp_gain, gold_gain = rewards["priest"]
        elif "golem" in self.enemy.name.lower():
            xp_gain, gold_gain = rewards["golem"]
        elif "tracey" in self.enemy.name.lower():
            xp_gain, gold_gain = rewards["tracey"]
        else:
            xp_gain, gold_gain = 10, 5
        
        self.xp += xp_gain
        self.gold += gold_gain
        self.add_log(f"+{xp_gain} XP, +{gold_gain} Gold!", GREEN)
        
        if "tracey" in self.enemy.name.lower():
            self.victory = True
            self.state = GameState.VICTORY
            self.add_log("🏆 VICTORY! Ptouneigh is rescued!", GREEN)
            self.add_log("The Sionist cult crumbles without their leader!", GREEN)
        else:
            self.in_combat = False
            self.enemy = None
            self.player.x = SCREEN_WIDTH // 2 - 100
            self.player.y = SCREEN_HEIGHT // 2
            self.state = GameState.EXPLORING
    
    def draw_exploring(self):
        """Draw exploring state"""
        self.screen.fill((30, 40, 50))
        
        # Draw location description
        locations = {
            "cottage": "Your cozy home. Chazz stands ready to help.",
            "village": "A peaceful village. Strange Sionist symbols mark the buildings.",
            "forest": "Dark woods. You sense danger here...",
            "temple": "A massive temple with bizarre Sionist symbols.",
            "tower": "Tracey's dark tower crackles with purple lightning!",
        }
        
        location_desc = locations.get(self.current_location, "Unknown location")
        desc_text = self.font_medium.render(f"📍 {self.current_location.upper()}", True, ORANGE)
        desc_text2 = self.font_small.render(location_desc, True, WHITE)
        
        self.screen.blit(desc_text, (20, 20))
        self.screen.blit(desc_text2, (20, 60))
        
        # Draw player
        self.draw_character(self.player, self.player.x, self.player.y, selected=True)
        
        # Draw Chazz (sidekick)
        chazz = Character("Chazz", SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2, 50, 50, 5, 2, (0, 128, 255))
        self.draw_character(chazz, chazz.x, chazz.y)
        
        # Draw action hints
        actions_y = SCREEN_HEIGHT - 80
        actions = [
            "A - Search Area",
            "E - Explore Next Location",
            "C - Check Status",
            "Space - Start Battle"
        ]
        
        for i, action in enumerate(actions):
            action_text = self.font_small.render(action, True, BLUE)
            self.screen.blit(action_text, (20 + (i % 2) * 400, actions_y + (i // 2) * 30))
    
    def draw_combat(self):
        """Draw combat state"""
        self.screen.fill(BLACK)
        
        combat_title = self.font_large.render("⚔️ BATTLE ⚔️", True, RED)
        self.screen.blit(combat_title, (SCREEN_WIDTH // 2 - combat_title.get_width() // 2, 20))
        
        # Draw player
        self.draw_character(self.player, self.player.x, self.player.y, selected=self.player_turn)
        
        # Draw enemy
        if self.enemy:
            self.draw_character(self.enemy, self.enemy.x, self.enemy.y, selected=not self.player_turn)
        
        # Draw HUDs
        self.draw_hud()
        self.draw_combat_hud()
    
    def draw_victory(self):
        """Draw victory screen"""
        self.screen.fill(BLACK)
        
        victory_text = self.font_large.render("🏆 VICTORY! 🏆", True, GOLD)
        self.screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, 150))
        
        victory_msgs = [
            "You have defeated Tracey!",
            "Ptouneigh leaps into your arms, purring loudly!",
            "Your brave boy is safe!",
            "The Sionist cult crumbles.",
            "Peace returns to the land."
        ]
        
        y = 300
        for msg in victory_msgs:
            text = self.font_small.render(msg, True, GREEN)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 50
        
        restart_text = self.font_medium.render("Press R to Restart", True, BLUE)
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT - 100))
    
    def draw_game_over(self):
        """Draw game over screen"""
        self.screen.fill(BLACK)
        
        gameover_text = self.font_large.render("💀 GAME OVER 💀", True, RED)
        self.screen.blit(gameover_text, (SCREEN_WIDTH // 2 - gameover_text.get_width() // 2, 150))
        
        msg1 = self.font_medium.render("You have been defeated!", True, RED)
        msg2 = self.font_small.render("Ptouneigh remains captured...", True, WHITE)
        
        self.screen.blit(msg1, (SCREEN_WIDTH // 2 - msg1.get_width() // 2, 300))
        self.screen.blit(msg2, (SCREEN_WIDTH // 2 - msg2.get_width() // 2, 380))
        
        restart_text = self.font_medium.render("Press R to Restart", True, BLUE)
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT - 100))
    
    def handle_input(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.EXPLORING
                        self.add_log("🎮 Welcome to ASTHENIA!", BLUE)
                        self.add_log("Rescue Ptouneigh from Tracey!", ORANGE)
                
                elif self.state == GameState.EXPLORING:
                    if event.key == pygame.K_SPACE:
                        self.start_combat("cultist")
                    elif event.key == pygame.K_e:
                        locations = ["cottage", "village", "forest", "temple", "tower"]
                        idx = locations.index(self.current_location)
                        self.current_location = locations[(idx + 1) % len(locations)]
                        self.add_log(f"You travel to {self.current_location}!", BLUE)
                        if self.current_location == "tower":
                            self.add_log("You face Tracey in her tower!", RED)
                    elif event.key == pygame.K_c:
                        self.add_log(f"Level {self.level} | HP: {self.player.hp}/{self.player.max_hp} | XP: {self.xp}", WHITE)
                    elif event.key == pygame.K_a:
                        self.add_log("You search the area but find nothing.", GRAY)
                
                elif self.state == GameState.COMBAT:
                    if self.player_turn and self.wait_timer == 0:
                        if event.key == pygame.K_SPACE:
                            self.player_attack()
                        elif event.key == pygame.K_d:
                            self.player_defend()
                        elif event.key == pygame.K_r:
                            self.in_combat = False
                            self.enemy = None
                            self.state = GameState.EXPLORING
                            self.add_log("You fled from combat!", ORANGE)
                    
                    if not self.player_turn and self.wait_timer == 0:
                        self.enemy_attack()
                        if not self.game_over:
                            self.player_turn = True
                
                elif self.state == GameState.VICTORY or self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.init_game()
                        self.state = GameState.MENU
        
        return True
    
    def update(self):
        """Update game state"""
        if self.wait_timer > 0:
            self.wait_timer -= 1
        
        # Gentle animation
        self.animation_counter += 1
        if self.player and self.state == GameState.EXPLORING:
            self.player.y += math.sin(self.animation_counter * 0.02) * 0.5
    
    def draw(self):
        """Draw current state"""
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.EXPLORING:
            self.draw_exploring()
            self.draw_hud()
        elif self.state == GameState.COMBAT:
            self.draw_combat()
            self.draw_log()
        elif self.state == GameState.VICTORY:
            self.draw_victory()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        
        if self.state in [GameState.EXPLORING, GameState.COMBAT]:
            self.draw_log()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
