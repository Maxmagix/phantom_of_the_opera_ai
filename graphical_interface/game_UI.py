import pygame
import sys
import os
import json
from pygame_classes import *
import math
import numpy as np
import tkinter
import tkinter.filedialog

dirname = os.path.dirname(__file__)
resources_folder = os.path.join(dirname, "..", "ressources")
characters_folder = os.path.join(resources_folder, "Characters")
opera_background = os.path.join(resources_folder, "opera_bck.jpg")
game_background = os.path.join(resources_folder, "backgroundOpera.png")
cutains_background = os.path.join(resources_folder, "opera_curtains.jpg")
turn_reminder_1 = os.path.join(resources_folder, "turn_reminder_1.png")
turn_reminder_2 = os.path.join(resources_folder, "turn_reminder_2.png")
lock_icon = os.path.join(resources_folder, "lock.png")
shadow_icon = os.path.join(resources_folder, "light.png")
singer_icon = os.path.join(resources_folder, "singer.png")
phantom_icon = os.path.join(resources_folder, "phantom_icon.png")
inspector_icon = os.path.join(resources_folder, "inspector_icon.png")
power_back_card = os.path.join(characters_folder, "back_power.png")
character_back_card = os.path.join(characters_folder, "back_character.png")

file_name = ""
turn_order = ["inspector", "phantom", "phantom", "inspector", "phantom", "inspector", "inspector", "phantom"]

rooms_positions = [(850, 460), (675, 465), (450, 490), (190, 475), (865, 325), (675, 330), (430, 320), (190, 290), (675, 150), (425, 140)]

locks_positions = {"9-8": (560, 180), "9-7": (295, 220), "8-4": (790, 245), "7-6": (300, 328), "6-5": (555, 390), "5-4": (782, 368), "7-3": (262, 395), "3-2": (315, 515), "2-1": (568, 500), "1-0": (770, 500), "4-0": (940, 430)}


##changing game infos
turn_data = []
players_positions = {}
suspect_players = ["red", "white", "black", "brown", "purple", "pink", "blue", "grey"]
active_powers = []
shadow_in_room = 3
lock_between_rooms = [0, 2]
carlotta_position = 0

ratio = (1240, 600)
screen_size = (1240, 600)
turn = 0
max_turn = 0

def prompt_file():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    saved_dir_path = os.path.join(dir_path, "..")
    """Create a Tk file dialog and cleanup when finished"""
    top = tkinter.Tk()
    top.withdraw()
    file_name = tkinter.filedialog.askopenfilename(parent=top, title="Select game to view", initialdir=saved_dir_path, multiple=True)
    top.destroy()
    return file_name

def display_room_players(room_nb, players):
    players_img = []

    nb_players = len(players)
    step = 2 * math.pi / nb_players
    pos = rooms_positions[room_nb]
    radius = 10 + (10 * (nb_players / 2))
    if (nb_players == 1):
        radius = 0
    for i, player in enumerate(players):
        path = os.path.join(characters_folder, player)
        if (player in suspect_players):
            path = os.path.join(path, "pawn.png")
        else:
            path = os.path.join(path, "pawn_innocent.png")
        img_pos = (pos[0] + (radius * np.cos(step * i)), pos[1] + (radius * np.sin(step * i)))
        players_img.append(pygame_img(img_pos, (40, 40), path))
    return players_img

def display_players(display):
    room_population = {}
    room_players_img = []
    people_screaming = 0
    for player in players_positions:
        room_index = players_positions[player]
        if (room_index not in room_population):
            room_population[room_index] = []
        room_population[room_index].append(player)
    for room in room_population:
        if (len(room_population[room]) == 1):
            people_screaming += 1
        elif (shadow_in_room == room):
            people_screaming += len(room_population[room])
        room_players_img.append(display_room_players(int(room), room_population[room]))
    for players_img in room_players_img:
        for player_img in players_img:
            player_img.draw(display.get_screen())
    return people_screaming

def gameEventManager(button_list, phantom_card):
    # stores the (x,y) coordinates into
    # the variable as a tuple

    for ev in pygame.event.get():
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if ev.button == 1:
                pos = pygame.mouse.get_pos()
                for b in button_list:
                    if b.mouse_over(pos):
                        return_value = b.call_back()
                        if return_value:
                            read_file(return_value[0], phantom_card)
        if ev.type == pygame.QUIT:
            pygame.quit()
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                pygame.quit()

def increase_turn():
    global turn
    global max_turn
    if (turn < max_turn):
        turn += 1
        set_turn_data_global(turn)

def decrease_turn():
    global turn
    if (turn > 0):
        turn -= 1
        set_turn_data_global(turn)

def get_lock_position():
    selected_key = {key: value for key, value in locks_positions.items() if str(lock_between_rooms[0]) in key and str(lock_between_rooms[1]) in key}
    pos_list = list(selected_key.values())
    pos = locks_positions["1-0"]
    if (pos_list):
        pos = pos_list[0]
    return pos

def parse_all_turns_data(filename):
    f = open(filename, "r")
    game_data = json.loads(f.read())
    all_turns = len(game_data["turns"])
    for i in range(int(all_turns / 5) - 1, 0, -1):
        game_data["turns"].pop((i * 5) + 1)
    return game_data

def set_turn_data_global(actual_turn):
    global suspect_players, carlotta_position, shadow_in_room, lock_between_rooms, active_powers, players_positions
    suspect_players = []
    temp_players_pos = {}
    active_powers = []
    if (actual_turn >= len(turn_data)):
        return
    carlotta_position = turn_data[actual_turn]["exit"] - turn_data[actual_turn]["position_carlotta"]
    shadow_in_room = turn_data[actual_turn]["shadow"]
    blocked = turn_data[actual_turn]["blocked"]
    lock_between_rooms = (blocked[0], blocked[0])
    for character in turn_data[actual_turn]["characters"]:
        temp_players_pos[character["color"]] = character["position"]
        if (character["suspect"] and character["color"] not in suspect_players):
            suspect_players.append(character["color"])
        if (character["power"]):
            active_powers.append(character["color"])
    players_positions = temp_players_pos

def read_file(file_path, phantom_card):
    global file_name, turn, turn_data, max_turn
    file_name = file_path.split("/")[-1]
    turn = 0
    max_turn = 0
    game_data = parse_all_turns_data(file_path)
    path = os.path.join(characters_folder, game_data["fantom"])
    file_guilty_card = os.path.join(path, "innocent.png")
    phantom_card.set_img(file_guilty_card)
    turn_data = game_data["turns"]
    max_turn = len(turn_data)
    set_turn_data_global(0)

def startScreen(title):
    # initializing the constructor
    pygame.init()

    # screen resolution
    color = (0,0,0)
    color_transparent = (50, 50, 50, 150)
    color_light = (250,250,170)
    color_white = (255,255,255)
    color_pink = (255,0,100)

    clock = pygame.time.Clock()
    display = pygame_screen(screen_size, color, game_background, title)

    rooms_text = []

    file_text = pygame_text("No file selected", (960, 40), color_white)
    button_start = pygame_button((1100, 85), (220, 30), prompt_file, "Select saved game to view")
    for i, pos_text in enumerate(rooms_positions):
        rooms_text.append(pygame_text(str(i), (int(pos_text[0] * screen_size[0] / ratio[0]), int(pos_text[1] * screen_size[1] / ratio[1])), color_transparent, "Segoe Print", 120, True))
    debug_text = pygame_text("", (0, 0), color_light, "Segoe Print", 20)
    button_previous = pygame_button((1000, 560), (75, 25), decrease_turn, "Previous")
    button_next = pygame_button((1080, 560), (75, 25), increase_turn, "Next")
    text_title = pygame_text("The Phantom of the Opera", (955, 10), color_light, "Segoe Print", 20)
    turn_reminder = pygame_img((980, 520), (50, 50), inspector_icon)
    singer_state = pygame_img((1200, 520), (50, 100), singer_icon, 255, "6", color_pink, "Segoe Print", 30)
    lock_img = pygame_img((1200, 520), (50, 50), lock_icon)
    shadow_img = pygame_img((1200, 520), (120, 120), shadow_icon, 200)
    turn_text = pygame_text("Turn ", (1000, 520), color_white, "Segoe Print", 20)
    innocent_text = pygame_text("Suspects remaining", (960, 350), color_white, "Segoe Print", 20)
    screaming_text = pygame_text("People screaming", (960, 400), color_white, "Segoe Print", 20)
    shadow_text = pygame_text("shadow in room", (960, 450), color_white, "Segoe Print", 20)

    power_pos = (990, 160)
    power1 = pygame_img((power_pos[0], power_pos[1]), (70, 100), power_back_card)
    power2 = pygame_img((power_pos[0] + 70, power_pos[1]), (70, 100), power_back_card)
    power3 = pygame_img((power_pos[0] + 140, power_pos[1]), (70, 100), power_back_card)
    power4 = pygame_img((power_pos[0] + 210, power_pos[1]), (70, 100), power_back_card)
    
    character_cards = pygame_img((power_pos[0], power_pos[1] + 120), (70, 100), character_back_card, 255, "11", color_white, "Segoe Print", 30)
    phantom_card = pygame_img((power_pos[0] + 140, power_pos[1] + 120), (70, 100), character_back_card)
    phantom_card_icon = pygame_img((power_pos[0] + 140, power_pos[1] + 120), (60, 60), phantom_icon)


    all_buttons = [button_previous, button_next, button_start]
    all_images = [turn_reminder, singer_state, power1, power2, power3, power4, character_cards, shadow_img, lock_img, phantom_card, phantom_card_icon]
    all_texts = [text_title, turn_text, screaming_text, innocent_text, shadow_text, file_text]

    while True:
        display.draw()
        shadow_img.set_position(rooms_positions[shadow_in_room])
        debug_text.text(f"{pygame.mouse.get_pos()}")
        if (turn == 0):
            turn_text.text(f"Initial state")
        else:
            turn_text.text(f"Turn {turn}")
        if (len(file_name) > 0):
            file_text.text(file_name)
        else:
            file_text.text("No file selected")
        innocent_text.text(f"Suspects remaining: {len(suspect_players)}")
        shadow_text.text(f"shadow in room: {shadow_in_room}")
        lock_img.set_position(get_lock_position())
        singer_state.set_text(str(carlotta_position))
        if (turn_order[(turn % len(turn_order)) - 1] == "inspector"):
            turn_reminder.set_img(inspector_icon)
        else:
            turn_reminder.set_img(phantom_icon)
        for img in all_images:
            img.draw(display.get_screen())
        for text in all_texts:
            text.draw(display.get_screen())
        for button in all_buttons:
            button.draw(display.get_screen())
        for text in rooms_text:
            text.draw(display.get_screen())
        nb_people_screaming = display_players(display)
        screaming_text.text(f"People who can scream: {nb_people_screaming}")
        gameEventManager(all_buttons, phantom_card)
        # updates the frames of the game
        pygame.display.update()
        clock.tick(60)


def main():
    startScreen("09-27-2021_11-22")

if __name__ == "__main__":
    main()