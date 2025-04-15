import pygame
import random
import os
import sys
import threading
import pylsl
from pylsl import StreamInlet
import csv

# Initialize pygame
pygame.init()

# Set up the screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Where's Waldo")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 200, 0)

# Global variables
waldo_size = 50
font = pygame.font.Font(None, 36)
tbr_value = [2.0]  # Default TBR, shared with EEG thread

# Load sprites (simple version, no __file__ mangling)
waldo_sprite = pygame.image.load("sprites/waldo_sprite.png").convert_alpha()
waldo_sprite = pygame.transform.scale(waldo_sprite, (waldo_size, waldo_size))

other_sprite = pygame.image.load("sprites/other_sprite.png").convert_alpha()
other_sprite = pygame.transform.scale(other_sprite, (waldo_size, waldo_size))

other_sprite1 = pygame.image.load("sprites/other_sprite1.png").convert_alpha()
other_sprite1 = pygame.transform.scale(other_sprite1, (waldo_size, waldo_size))

other_sprite2 = pygame.image.load("sprites/other_sprite2.png").convert_alpha()
other_sprite2 = pygame.transform.scale(other_sprite2, (waldo_size, waldo_size))

other_sprite3 = pygame.image.load("sprites/other_sprite3.png").convert_alpha()
other_sprite3 = pygame.transform.scale(other_sprite3, (waldo_size, waldo_size))

background_sprite = pygame.image.load("sprites/background_sprite.png").convert_alpha()
background_sprite = pygame.transform.scale(background_sprite, (WIDTH, HEIGHT))

# EEG Thread
file_path = "C:/Users/Ryan/Desktop/OpenBCI1.csv"
def update_data():
    print("Looking for EEG stream...")
    streams = pylsl.resolve_streams()
    stream = streams[0]
    inlet = StreamInlet(stream)
    while True:
        chunks, timestamps = inlet.pull_chunk()
        if timestamps and chunks and chunks[0][0] == 0:
            tbrt = 0
            count = 0
            for chunk in chunks:
                if chunk[0] in [7, 8, 9]:
                    if chunk[4] != 0:
                        tbri = (chunk[2] / chunk[4]) * 100
                        tbrt += tbri
                        count += 1
            if count > 0:
                tbr = tbrt / count
                tbr_value[0] = tbr
                with open(file_path, "a+", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([timestamps[0], tbr])

# Game variables
level = 1
sprites = []
waldo_pos = (0, 0)

def get_difficulty_counts():
    tbr = tbr_value[0]
    if tbr < 2:
        return 5, 5, 5, 5
    elif tbr < 4:
        return 10, 10, 10, 10
    else:
        return 15, 15, 15, 15

def get_difficulty_label():
    tbr = tbr_value[0]
    if tbr < 2:
        return "Easy"
    elif tbr < 4:
        return "Medium"
    else:
        return "Hard"

def shuffle_sprites():
    global sprites, waldo_pos
    sprites = []
    occupied_positions = set()

    # Place Waldo
    while True:
        waldo_x, waldo_y = random.randint(0, WIDTH - waldo_size), random.randint(0, HEIGHT - waldo_size)
        grid_x, grid_y = waldo_x // waldo_size, waldo_y // waldo_size
        if (grid_x, grid_y) not in occupied_positions:
            occupied_positions.add((grid_x, grid_y))
            break
    waldo_pos = (waldo_x, waldo_y)
    sprites.append((waldo_sprite, waldo_x, waldo_y, True))

    # Place other sprites based on difficulty (TBR)
    counts = get_difficulty_counts()
    for count, sprite_img in zip(counts, [other_sprite, other_sprite1, other_sprite2, other_sprite3]):
        for _ in range(count):
            while True:
                x, y = random.randint(0, WIDTH - waldo_size), random.randint(0, HEIGHT - waldo_size)
                grid_x, grid_y = x // waldo_size, y // waldo_size
                if (grid_x, grid_y) not in occupied_positions:
                    occupied_positions.add((grid_x, grid_y))
                    sprites.append((sprite_img, x, y, False))
                    break

def start_screen():
    screen.fill((0, 0, 0))
    title_font = pygame.font.Font(None, 50)
    text = title_font.render("Press any key to start", True, WHITE)
    screen.blit(text, text.get_rect(center=(400, 300)))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return

def game_body():
    global level
    shuffle_sprites()
    while True:
        screen.fill(WHITE)
        screen.blit(background_sprite, (0, 0))
        for img, x, y, is_waldo in sprites:
            screen.blit(img, (x, y))

        # HUD
        level_text = font.render(f"Level: {level}", True, BLACK)
        tbr_text = font.render(f"TBR: {tbr_value[0]:.2f}", True, BLUE)
        diff_text = font.render(f"Difficulty: {get_difficulty_label()}", True, GREEN)
        screen.blit(level_text, (10, 10))
        screen.blit(tbr_text, (10, 50))
        screen.blit(diff_text, (10, 90))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if waldo_pos[0] <= mx <= waldo_pos[0] + waldo_size and waldo_pos[1] <= my <= waldo_pos[1] + waldo_size:
                    level += 1
                    shuffle_sprites()

if __name__ == "__main__":
    threading.Thread(target=update_data, daemon=True).start()
    start_screen()
    game_body()
