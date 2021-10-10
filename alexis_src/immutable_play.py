#!/bin/python3

import copy
import json

permanents = {"pink"}
before = {"purple", "brown"}
after = {"black", "white", "red", "blue", "grey"}

colors = {"pink",
          "blue",
          "purple",
          "grey",
          "white",
          "black",
          "red",
          "brown"}

passages = [{1, 4}, {0, 2}, {1, 3}, {2, 7}, {0, 5, 8},
            {4, 6}, {5, 7}, {3, 6, 9}, {4, 9}, {7, 8}]
pink_passages = [{1, 4}, {0, 2, 5, 7}, {1, 3, 6}, {2, 7}, {0, 5, 8, 9},
                 {4, 6, 1, 8}, {5, 7, 2, 9}, {3, 6, 9, 1}, {4, 9, 5},
                 {7, 8, 4, 6}]

mandatory_powers = ["red", "blue", "grey"]

char_needs_arg = {"white", "purple", "brown", "grey", "blue"}

def game_state_deep_copy(game_state):
    # Copying characters dict's references around to:
    # 1 - Save memory (2 to 2.5 less space used by character dicts)
    # 2 - Update all instances of character cards easily and avoid inconsistencies
    chars = copy.deepcopy(game_state["characters"])
    chars_dict = {char["color"]: char for char in chars}
    char_cards = [chars_dict[card["color"]] for card in game_state["character_cards"]]
    active_char_card = [chars_dict[card["color"]] for card in game_state["active character_cards"]]

    new_game_state = {
        "position_carlotta": game_state["position_carlotta"],
        "exit": game_state["exit"],
        "num_tour": game_state["num_tour"],
        "shadow": game_state["shadow"],
        "blocked": game_state["blocked"].copy(),
        "characters": chars,
        "character_cards": char_cards,
        "active character_cards": active_char_card,
    }

    if "fantom" in game_state:
        new_game_state["fantom"] = game_state["fantom"]

    return new_game_state


def get_char_from_color(game_state, color):
    for c in game_state["characters"]:
        if c["color"] == color:
            return c


def get_adjacent_positions(game_state, charact):
    if charact["color"] == "pink":
        active_passages = pink_passages
    else:
        active_passages = passages
    return [room for room in active_passages[charact["position"]] if set([room, charact["position"]]) != set(game_state["blocked"])]


def get_adjacent_positions_from_position(game_state, position, color):
    if color == "pink":
        active_passages = pink_passages
    else:
        active_passages = passages
    return [room for room in active_passages[position] if set([room, position]) != set(game_state["blocked"])]


def select(game_state, play):
    selected_character = play.pop(0)
    perso = game_state["active character_cards"][selected_character]

    del game_state["active character_cards"][selected_character]
    return perso


def activate_power(game_state, charact, activables, play):
    if charact["color"] not in activables:
        return None

    if charact["color"] in mandatory_powers:
        power_activation = 1
    else:
        power_activation = play.pop(0)
        if power_activation == 0:
            return None

    charact["power"] = True

    if charact["color"] == "red":
        # This part is random and cannot be determined!
        # You also have to take into account the fact the inspector does not
        # know who the fantom is and what card has already been drawn.
        # Todo: try to simulate this power somewhat, by picking a random card maybe ?
        pass
    elif charact["color"] == "black":
        for c in game_state["characters"]:
            if c["position"] in get_adjacent_positions(game_state, charact):
                c["position"] = charact["position"]
    elif charact["color"] == "white":
        for moved_character in game_state["characters"]:
            if moved_character["position"] != charact["position"] \
                or charact == moved_character:
                continue
            moved_character["position"] = play.pop(0)
    elif charact["color"] == "purple":
        selected_char = get_char_from_color(game_state, play.pop(0))
        charact["position"], selected_char["position"] = selected_char["position"], charact["position"]
        return selected_char
    elif charact["color"] == "brown":
        available_characters = [c for c in game_state["characters"] if
                                charact["position"] == c["position"] if
                                c["color"] != "brown"]

        if len(available_characters) == 0:
            return None
        selected_char = get_char_from_color(game_state, play.pop(0))
        return selected_char
    elif charact["color"] == "grey":
        selected_room = play.pop(0)
        game_state["shadow"] = selected_room
    elif charact["color"] == "blue":
        first_room = play.pop(0)
        second_room = play.pop(0)
        game_state["blocked"] = [first_room, second_room]
    return None


def move(game_state, charact, moved_character, play):
    if charact["color"] == "purple" and moved_character != None:
        return

    dest = play.pop(0)
    charact["position"] = dest

    if charact["color"] == "brown" and moved_character != None:
        moved_character["position"] = dest


def immutable_play(game_state, play):
    orig_game_state = game_state
    game_state = game_state_deep_copy(game_state)
    orig_play = play
    play = play.copy()

    charact = select(game_state, play)
    moved_character = activate_power(game_state, charact, before, play)
    move(game_state, charact, moved_character, play)
    activate_power(game_state, charact, after, play)

    return game_state

# from evaluate_game_state import predict_carlotta_move
# from get_all_possible_plays import get_all_possible_plays

if __name__ == "__main__":
    f = open('test_game_state.json', 'r')
    content = f.read()
    question = json.loads(content)

    # new_game_state = immutable_play(question, [])
    # print(json.dumps(new_game_state, indent=2))

    plays = get_all_possible_plays(question)

    fantom_position = get_char_from_color(question["game state"], question["game state"]["fantom"])["position"]
    max_play = None
    max_carlotta_move = None
    for play in plays:
        new_game_state = immutable_play(question["game state"], play)
        new_max_carlotta_move = predict_carlotta_move(new_game_state, fantom_position)

        print(play, " => ", new_max_carlotta_move)
        if max_play == None or new_max_carlotta_move > max_carlotta_move:
            max_play = play
            max_carlotta_move = new_max_carlotta_move

    print("==================")
    print(max_play)
    print(max_carlotta_move)
    print(json.dumps(new_game_state["blocked"], indent=2))
