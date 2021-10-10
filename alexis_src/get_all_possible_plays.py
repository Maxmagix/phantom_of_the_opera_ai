#!/bin/python3

import json
import time
import itertools
from functools import reduce

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


def get_power_available_args(game_state, play):
    color = play[0]
    if color == "purple":
        available_characters = [c for c in game_state["characters"] if
                                c["color"] != "purple"]

        available_colors = [c["color"] for c in available_characters]
        return available_colors
    elif color == "grey":
        return [room for room in range(10) if room is not game_state["shadow"]]
    elif color == "brown":
        char = get_char_from_color(game_state, color)
        available_characters = [c for c in game_state["characters"] if
                                char["position"] == c["position"] if
                                c["color"] != "brown"]
        available_colors = [c["color"] for c in available_characters]
        return available_colors
    elif color == "blue":
        available_rooms = [room for room in range(10)]
        args = set() # Using a set to remove redundant choices
        for entrance in range(10):
            passages_work = passages[entrance].copy()
            available_exits = list(passages_work)
            for exit in available_exits:
                if entrance < exit:
                    args.add((entrance, exit))
                else:
                    args.add((exit, entrance))
        return list(args)
    elif color == "white":
        char = get_char_from_color(game_state, color)
        char["position"] = play[1]
        args = []
        for moved_character in game_state["characters"]:
            if moved_character["position"] != char["position"] or color == moved_character["color"]:
                continue
            available_positions = get_adjacent_positions(game_state, char)
            args.append(available_positions)
        return args


def get_available_colors(question):
    return [char["color"] for char in question["data"]]


def add_power(game_state, plays, char_set):
    new_plays = []
    for play in plays:
        if play[0] not in char_set or play[0] in mandatory_powers:
            new_plays.append(play)
            continue
        elif play[0] == "white":
            # Optimization: no point in using the power if there are no characters in the room
            nb_chars_room = len([c for c in game_state["characters"] if c["position"] == play[1]])
            if nb_chars_room == 0:
                new_plays.append(play + [0])
                continue
        elif play[0] == "brown":
            char = get_char_from_color(game_state, "brown")
            available_characters = [c for c in game_state["characters"] if
                                    char["position"] == c["position"] if
                                    c["color"] != "brown"]
            if len(available_characters) == 0:
                new_plays.append(play + [0])
                continue
        for x in [0, 1]:
            new_plays.append(play + [x])

    return new_plays


def flat_map(f, xs):
    return sum(map(f, xs), [])


def add_power_arg(game_state, plays, char_set):
    new_plays = []
    for play in plays:
        if play[0] not in char_needs_arg \
            or play[0] not in char_set \
            or (play[0] not in mandatory_powers and ( \
                (play[0] in before and play[1] == 0) \
                or (play[0] in after and play[2] == 0))):
            new_plays.append(play)
            continue
        available_args = get_power_available_args(game_state, play)
        if available_args == []:
            new_plays.append(play)
            continue
        if play[0] == "white":
            # foldl (\acc xs3 -> concat(map (\y -> map (++ [y]) acc) xs3)) xs1 xs2
            arg_plays = reduce(
                lambda acc, arg: flat_map(
                    lambda arg_val: list(map(
                        lambda x: x + [arg_val],
                        acc)),
                    arg),
                available_args,
                [play])
            new_plays += arg_plays
            continue
        if play[0] == "blue":
            for (arg1, arg2) in available_args:
                new_plays.append(play + [arg1, arg2])
            continue
        for arg in available_args: # For all characters whose power takes 1 arg
            new_plays.append(play + [arg])

    return new_plays


def get_available_moves(game_state, color):
    char = get_char_from_color(game_state, color)
    nb_chars_room = len([c for c in game_state["characters"] if c["position"] == char["position"]])

    # mini-dijkstra
    available_rooms = [get_adjacent_positions(game_state, char)]
    for step in range(1, nb_chars_room):
        next_rooms = []
        for room in available_rooms[step-1]:
            next_rooms += get_adjacent_positions_from_position(game_state, room, char)
        available_rooms.append(next_rooms)

    # flat
    temp = []
    for sublist in available_rooms:
        for room in sublist:
            temp.append(room)

    # Remove duplicates
    temp = set(temp)
    available_positions = list(temp)

    # Remove initial position
    if char["position"] in available_positions:
        available_positions.remove(char["position"])

    return available_positions


def add_move(game_state, plays):
    new_plays = []
    for play in plays:
        if play[0] == "purple" and play[1] == 1:
            new_plays.append(play)
            continue
        for move in get_available_moves(game_state, play[0]):
            new_plays.append(play + [move])
    return new_plays


def get_all_possible_plays(question):
    game_state = question["game state"]

    plays = get_available_colors(question)
    plays = [[c] for c in plays]
    plays = add_power(game_state, plays, before)
    plays = add_power_arg(game_state, plays, before)
    plays = add_move(game_state, plays)
    plays = add_power(game_state, plays, after)
    plays = add_power_arg(game_state, plays, after)

    for play in plays:
        for (i, char) in enumerate(question["data"]):
            if play[0] == char["color"]:
                play[0] = i

    return plays

if __name__ == "__main__":
    f = open('test_game_state3.json', 'r')
    content = f.read()
    question = json.loads(content)

    # print(json.dumps(question["data"], indent=2))
    # choice = copy.deepcopy(question["data"][2])
    # print(question["data"].index(choice))

    plays = get_all_possible_plays(question)

    for play in plays:
        print(play)

    # print(json.dumps(question, indent=2))
