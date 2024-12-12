import pygame
import random
import sys
import math
import os
from pygame import mixer
from PIL import Image
import io

# Initialisation de Pygame
pygame.init()
mixer.init()

# Constantes
WINDOW_SIZE = 800
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE

# Couleurs
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 20, 147)
NEON_GREEN = (57, 255, 20)
DARK_PURPLE = (25, 0, 51)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Phrases moqueuses
MOCKING_PHRASES = [
    "Tu appelles ça jouer ?",
    "Même mon grand-père fait mieux !",
    "T'as les doigts carrés ou quoi ?",
    "C'est tout ce que tu peux faire ?",
    "Retourne jouer à Pong...",
    "LOL, même pas niveau 1 !",
    "Un escargot irait plus vite !",
    "Tu devrais peut-être essayer Tetris...",
    "Pas terrible ton high score...",
    "Mon chat joue mieux que ça !",
    "C'était... intéressant ?",
    "Essaie avec les yeux ouverts !",
    "Faut appuyer sur les touches, tu sais ?",
    "On dirait un bug qui joue !",
    "404 : Talent non trouvé"
]

# Configuration de l'écran
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Cyberpunk Snake")
clock = pygame.time.Clock()

class GridEffect:
    def __init__(self):
        self.lines = []
        self.line_spacing = 40
        self.scroll_speed = 1
        self.offset = 0
        self.alpha = 128

    def update(self):
        self.offset = (self.offset + self.scroll_speed) % self.line_spacing

    def draw(self, screen):
        # Lignes horizontales
        for y in range(-self.line_spacing + int(self.offset), WINDOW_SIZE + self.line_spacing, self.line_spacing):
            surface = pygame.Surface((WINDOW_SIZE, 2), pygame.SRCALPHA)
            color = (*NEON_BLUE[:3], self.alpha)
            pygame.draw.line(surface, color, (0, 0), (WINDOW_SIZE, 0), 1)
            screen.blit(surface, (0, y))

        # Lignes verticales
        for x in range(-self.line_spacing + int(self.offset), WINDOW_SIZE + self.line_spacing, self.line_spacing):
            surface = pygame.Surface((2, WINDOW_SIZE), pygame.SRCALPHA)
            color = (*NEON_BLUE[:3], self.alpha)
            pygame.draw.line(surface, color, (0, 0), (0, WINDOW_SIZE), 1)
            screen.blit(surface, (x, 0))

class GlowEffect:
    def __init__(self, color, radius):
        self.color = color
        self.radius = radius
        self.surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        self.create_glow()

    def create_glow(self):
        center = self.radius
        for i in range(self.radius, 0, -1):
            alpha = int((1 - (i / self.radius)) * 100)
            pygame.draw.circle(self.surface, (*self.color[:3], alpha), (center, center), i)

    def draw(self, screen, pos):
        screen.blit(self.surface, (pos[0] - self.radius, pos[1] - self.radius), special_flags=pygame.BLEND_ALPHA_SDL2)

class SnakeHead:
    def __init__(self):
        self.mouth_open = False
        self.animation_counter = 0
        self.animation_speed = 5
        self.glow = GlowEffect(NEON_PINK, 15)

    def update(self):
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.mouth_open = not self.mouth_open
            self.animation_counter = 0

    def draw(self, screen, x, y, direction):
        # Dessiner l'effet de lueur
        self.glow.draw(screen, (x*GRID_SIZE + GRID_SIZE//2, y*GRID_SIZE + GRID_SIZE//2))
        
        # Dessiner la tête principale
        pygame.draw.rect(screen, NEON_PINK, (x*GRID_SIZE+1, y*GRID_SIZE+1, GRID_SIZE-2, GRID_SIZE-2))
        
        # Effet de brillance métallique
        highlight = pygame.Surface((GRID_SIZE-2, GRID_SIZE-2), pygame.SRCALPHA)
        pygame.draw.line(highlight, (255, 255, 255, 100), (0, 0), (GRID_SIZE-2, 0), 2)
        pygame.draw.line(highlight, (255, 255, 255, 50), (0, 2), (GRID_SIZE-2, 2), 1)
        screen.blit(highlight, (x*GRID_SIZE+1, y*GRID_SIZE+1))
        
        # Position des yeux en fonction de la direction
        eye_size = 4
        eye_offset = 5
        eye_color = WHITE
        pupil_color = BLACK
        pupil_size = 2

        # Position de base des yeux avec effet de lueur
        left_eye_pos = [x*GRID_SIZE + eye_offset, y*GRID_SIZE + eye_offset]
        right_eye_pos = [x*GRID_SIZE + GRID_SIZE - eye_offset - eye_size, y*GRID_SIZE + eye_offset]

        # Ajuster la position des yeux selon la direction
        if direction == (0, -1):  # Haut
            left_eye_pos = [x*GRID_SIZE + eye_offset, y*GRID_SIZE + eye_offset]
            right_eye_pos = [x*GRID_SIZE + GRID_SIZE - eye_offset - eye_size, y*GRID_SIZE + eye_offset]
        elif direction == (0, 1):  # Bas
            left_eye_pos = [x*GRID_SIZE + eye_offset, y*GRID_SIZE + GRID_SIZE - eye_offset - eye_size]
            right_eye_pos = [x*GRID_SIZE + GRID_SIZE - eye_offset - eye_size, y*GRID_SIZE + GRID_SIZE - eye_offset - eye_size]
        elif direction == (-1, 0):  # Gauche
            left_eye_pos = [x*GRID_SIZE + eye_offset, y*GRID_SIZE + eye_offset]
            right_eye_pos = [x*GRID_SIZE + eye_offset, y*GRID_SIZE + GRID_SIZE - eye_offset - eye_size]
        elif direction == (1, 0):  # Droite
            left_eye_pos = [x*GRID_SIZE + GRID_SIZE - eye_offset - eye_size, y*GRID_SIZE + eye_offset]
            right_eye_pos = [x*GRID_SIZE + GRID_SIZE - eye_offset - eye_size, y*GRID_SIZE + GRID_SIZE - eye_offset - eye_size]

        # Dessiner les yeux avec effet de lueur
        for eye_pos in [left_eye_pos, right_eye_pos]:
            # Lueur des yeux
            eye_glow = GlowEffect(WHITE, 6)
            eye_glow.draw(screen, (eye_pos[0] + eye_size//2, eye_pos[1] + eye_size//2))
            # Œil
            pygame.draw.rect(screen, eye_color, (eye_pos[0], eye_pos[1], eye_size, eye_size))
            # Pupille
            pygame.draw.rect(screen, pupil_color, (eye_pos[0] + 1, eye_pos[1] + 1, pupil_size, pupil_size))

        # Dessiner la bouche avec effet de lueur
        mouth_color = WHITE
        mouth_width = 8
        mouth_height = 4 if self.mouth_open else 2

        # Position de la bouche selon la direction
        if direction == (0, -1):  # Haut
            mouth_pos = [x*GRID_SIZE + (GRID_SIZE - mouth_width)//2, y*GRID_SIZE + eye_offset + eye_size + 2]
        elif direction == (0, 1):  # Bas
            mouth_pos = [x*GRID_SIZE + (GRID_SIZE - mouth_width)//2, y*GRID_SIZE + GRID_SIZE - eye_offset - mouth_height - 2]
        elif direction == (-1, 0):  # Gauche
            mouth_pos = [x*GRID_SIZE + eye_offset + eye_size + 2, y*GRID_SIZE + (GRID_SIZE - mouth_width)//2]
            mouth_width, mouth_height = mouth_height, mouth_width
        elif direction == (1, 0):  # Droite
            mouth_pos = [x*GRID_SIZE + GRID_SIZE - eye_offset - mouth_height - 2, y*GRID_SIZE + (GRID_SIZE - mouth_width)//2]
            mouth_width, mouth_height = mouth_height, mouth_width

        # Lueur de la bouche
        mouth_glow = GlowEffect(WHITE, 6)
        mouth_glow.draw(screen, (mouth_pos[0] + mouth_width//2, mouth_pos[1] + mouth_height//2))
        pygame.draw.rect(screen, mouth_color, (mouth_pos[0], mouth_pos[1], mouth_width, mouth_height))

class LoserGif:
    def __init__(self):
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 8  
        self.position_change_speed = 25  
        self.position_counter = 0
        self.counter = 0
        self.position = (0, 0)
        self.size = (400, 200)  
        self.mocking_phrase = random.choice(MOCKING_PHRASES)
        
        # Création d'un GIF "LOOSER" en utilisant du texte
        font_large = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 36)
        colors = [(255, 0, 0), (255, 128, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255)]
        
        for color in colors:
            # Surface pour contenir le texte "LOOSER" et la phrase moqueuse
            text_surface = pygame.Surface(self.size, pygame.SRCALPHA)
            
            # Rendu du texte "LOOSER"
            looser_text = font_large.render("LOOSER!", True, color)
            # Rendu de la phrase moqueuse avec vérification de la longueur
            mocking_text = font_small.render(self.mocking_phrase, True, color)
            
            # S'assurer que la phrase moqueuse ne dépasse pas la surface
            if mocking_text.get_width() > self.size[0] - 20:
                # Réduire la taille de la police si le texte est trop long
                font_smaller = pygame.font.Font(None, 30)
                mocking_text = font_smaller.render(self.mocking_phrase, True, color)
            
            # Ajouter un effet de brillance pour "LOOSER"
            glow_surface = pygame.Surface(self.size, pygame.SRCALPHA)
            for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
                glow = font_large.render("LOOSER!", True, (*color[:3], 128))
                glow_rect = glow.get_rect(center=(self.size[0]//2 + offset[0], self.size[1]//2 - 20 + offset[1]))
                glow_surface.blit(glow, glow_rect)
            
            # Position du texte "LOOSER"
            looser_rect = looser_text.get_rect(center=(self.size[0]//2, self.size[1]//2 - 20))
            # Position de la phrase moqueuse
            mocking_rect = mocking_text.get_rect(center=(self.size[0]//2, self.size[1]//2 + 30))
            
            # Ajouter un fond semi-transparent pour améliorer la lisibilité
            background = pygame.Surface(self.size, pygame.SRCALPHA)
            background.fill((0, 0, 0, 128))  
            text_surface.blit(background, (0, 0))
            
            # Assembler tous les éléments
            text_surface.blit(glow_surface, (0, 0))
            text_surface.blit(looser_text, looser_rect)
            text_surface.blit(mocking_text, mocking_rect)
            
            self.frames.append(text_surface)

    def update(self):
        self.counter += 1
        self.position_counter += 1

        # Mise à jour de l'animation des couleurs
        if self.counter >= self.animation_speed:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.counter = 0

        # Mise à jour de la position et de la phrase moqueuse
        if self.position_counter >= self.position_change_speed:
            self.position_counter = 0
            # Mettre à jour la position aléatoire en s'assurant que le texte reste dans l'écran
            self.position = (
                random.randint(10, max(10, WINDOW_SIZE - self.size[0] - 10)),
                random.randint(10, max(10, WINDOW_SIZE - self.size[1] - 10))
            )
            # Changer la phrase moqueuse occasionnellement
            if random.random() < 0.2:  
                self.mocking_phrase = random.choice(MOCKING_PHRASES)
                # Recréer les frames avec la nouvelle phrase
                self.__init__()

    def draw(self, screen):
        screen.blit(self.frames[self.current_frame], self.position)

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.lifetime = 255
        self.color = random.choice([NEON_BLUE, NEON_PINK, NEON_GREEN])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 5
        return self.lifetime > 0

    def draw(self, screen):
        alpha = max(0, min(255, self.lifetime))
        color = (*self.color[:3], alpha)
        surface = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (2, 2), 2)
        screen.blit(surface, (int(self.x), int(self.y)))

class Game:
    def __init__(self):
        self.reset()
        self.particles = []
        self.difficulty = "normal"
        self.speeds = {"easy": 10, "normal": 15, "hard": 20}
        self.menu_active = True
        self.font = pygame.font.Font(None, 36)
        self.snake_head = SnakeHead()
        self.loser_gif = LoserGif()
        self.grid_effect = GridEffect()
        self.food_glow = GlowEffect(NEON_GREEN, 15)
        self.body_glow = GlowEffect(NEON_BLUE, 12)

    def reset(self):
        self.snake = [(GRID_COUNT//2, GRID_COUNT//2)]
        self.direction = (1, 0)
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        self.particles = []
        self.snake_head = SnakeHead()
        self.loser_gif = LoserGif()

    def spawn_food(self):
        while True:
            pos = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))
            if pos not in self.snake:
                return pos

    def create_particles(self, x, y):
        for _ in range(20):
            self.particles.append(Particle(x * GRID_SIZE, y * GRID_SIZE))

    def update(self):
        self.grid_effect.update()
        if self.game_over:
            self.loser_gif.update()
            return

        # Mise à jour de l'animation de la tête
        self.snake_head.update()

        # Mise à jour de la position du serpent
        new_head = (
            (self.snake[0][0] + self.direction[0]) % GRID_COUNT,
            (self.snake[0][1] + self.direction[1]) % GRID_COUNT
        )

        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
            self.create_particles(new_head[0], new_head[1])
        else:
            self.snake.pop()

        self.particles = [p for p in self.particles if p.update()]

    def draw(self):
        screen.fill(DARK_PURPLE)

        # Dessiner l'effet de grille
        self.grid_effect.draw(screen)

        # Dessin des particules
        for particle in self.particles:
            particle.draw(screen)

        # Dessin du serpent
        for i, (x, y) in enumerate(self.snake):
            if i == 0:
                self.snake_head.draw(screen, x, y, self.direction)
            else:
                # Effet de lueur pour le corps
                self.body_glow.draw(screen, (x*GRID_SIZE + GRID_SIZE//2, y*GRID_SIZE + GRID_SIZE//2))
                # Corps du serpent
                pygame.draw.rect(screen, NEON_BLUE, (x*GRID_SIZE+1, y*GRID_SIZE+1, GRID_SIZE-2, GRID_SIZE-2))
                # Effet métallique
                highlight = pygame.Surface((GRID_SIZE-2, GRID_SIZE-2), pygame.SRCALPHA)
                pygame.draw.line(highlight, (255, 255, 255, 100), (0, 0), (GRID_SIZE-2, 0), 2)
                pygame.draw.line(highlight, (255, 255, 255, 50), (0, 2), (GRID_SIZE-2, 2), 1)
                screen.blit(highlight, (x*GRID_SIZE+1, y*GRID_SIZE+1))

        # Dessin de la nourriture avec effet de lueur
        self.food_glow.draw(screen, (self.food[0]*GRID_SIZE + GRID_SIZE//2, self.food[1]*GRID_SIZE + GRID_SIZE//2))
        pygame.draw.rect(screen, NEON_GREEN,
                        (self.food[0]*GRID_SIZE+1, self.food[1]*GRID_SIZE+1, GRID_SIZE-2, GRID_SIZE-2))

        # Effet métallique sur la nourriture
        highlight = pygame.Surface((GRID_SIZE-2, GRID_SIZE-2), pygame.SRCALPHA)
        pygame.draw.line(highlight, (255, 255, 255, 100), (0, 0), (GRID_SIZE-2, 0), 2)
        pygame.draw.line(highlight, (255, 255, 255, 50), (0, 2), (GRID_SIZE-2, 2), 1)
        screen.blit(highlight, (self.food[0]*GRID_SIZE+1, self.food[1]*GRID_SIZE+1))

        # Score avec effet de lueur
        score_text = self.font.render(f"Score: {self.score}", True, NEON_PINK)
        score_glow = GlowEffect(NEON_PINK, 20)
        score_glow.draw(screen, (80, 25))
        screen.blit(score_text, (10, 10))

        if self.game_over:
            self.loser_gif.draw(screen)
            game_over_text = self.font.render("Press R to Restart", True, NEON_PINK)
            screen.blit(game_over_text, 
                       (WINDOW_SIZE//2 - game_over_text.get_width()//2, WINDOW_SIZE//2))

    def draw_menu(self):
        screen.fill(DARK_PURPLE)
        title = self.font.render("CYBERPUNK SNAKE", True, NEON_PINK)
        screen.blit(title, (WINDOW_SIZE//2 - title.get_width()//2, 200))

        difficulties = ["easy", "normal", "hard"]
        for i, diff in enumerate(difficulties):
            color = NEON_GREEN if self.difficulty == diff else NEON_BLUE
            text = self.font.render(diff.upper(), True, color)
            pos = (WINDOW_SIZE//2 - text.get_width()//2, 300 + i*50)
            screen.blit(text, pos)

        start_text = self.font.render("Press SPACE to start", True, NEON_PINK)
        screen.blit(start_text, (WINDOW_SIZE//2 - start_text.get_width()//2, 500))

    def handle_menu_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                difficulties = ["easy", "normal", "hard"]
                current_index = difficulties.index(self.difficulty)
                self.difficulty = difficulties[(current_index - 1) % 3]
            elif event.key == pygame.K_DOWN:
                difficulties = ["easy", "normal", "hard"]
                current_index = difficulties.index(self.difficulty)
                self.difficulty = difficulties[(current_index + 1) % 3]
            elif event.key == pygame.K_SPACE:
                self.menu_active = False
                self.reset()

def main():
    game = Game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game.menu_active:
                game.handle_menu_input(event)
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and game.direction != (0, 1):
                        game.direction = (0, -1)
                    elif event.key == pygame.K_DOWN and game.direction != (0, -1):
                        game.direction = (0, 1)
                    elif event.key == pygame.K_LEFT and game.direction != (1, 0):
                        game.direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and game.direction != (-1, 0):
                        game.direction = (1, 0)
                    elif event.key == pygame.K_r and game.game_over:
                        game.reset()
                    elif event.key == pygame.K_ESCAPE:
                        game.menu_active = True

        if game.menu_active:
            game.draw_menu()
        else:
            game.update()
            game.draw()

        pygame.display.flip()
        clock.tick(game.speeds[game.difficulty])

if __name__ == "__main__":
    main()
