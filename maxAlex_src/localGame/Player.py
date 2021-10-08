import json
from typing import Tuple
from random import randint, choice
from src.globals import passages, colors, pink_passages, before, after, logger, mandatory_powers
from src.utils import ask_question_json


class Player:
    """
        Class representing the players, either the inspector (player 0)
        or the fantom (player 1)
    """
    num: int

    def __init__(self, n: int):
        self.num = n
        # Todo: Should not be a str, enum instead.
        self.role: str = "inspector" if n == 0 else "fantom"

    def get_moves(self, game):

    def play(self, game):
        logger.info("--\n" + self.role + " plays\n--")

        logger.debug(json.dumps(game.update_game_state(""), indent=4))
        charact = self.select(
            game.active_cards, game.update_game_state(self.role))

        # purple and brown power choose to activate or not before moving
        moved_character = self.activate_power(charact,
                                              game,
                                              before,
                                              game.update_game_state(self.role))

        self.move(charact,
                  moved_character,
                  game.blocked,
                  game.update_game_state(self.role),
                  game)

        self.activate_power(charact,
                            game,
                            after,
                            game.update_game_state(self.role))


    def possible_selected_cards(active_cards):
        """
            Choose the character to activate whithin
            the given choices.
        """
        available_characters = [character.display()
                                for character in active_cards]
        return available_characters

    def select(active_cards, selected_character):
        """
            Choose the character to activate whithin
            the given choices.
        """
        if selected_character not in range(len(active_cards)):
            selected_character = randint(0, len(active_cards) - 1)

        perso = active_cards[selected_character]

        del active_cards[selected_character]
        return perso


    def get_adjacent_positions(self, charact, game):
        if charact.color == "pink":
            active_passages = pink_passages
        else:
            active_passages = passages
        return [room for room in active_passages[charact.position] if set([room, charact.position]) != set(game.blocked)]


    def get_adjacent_positions_from_position(self, position, charact, game):
        if charact.color == "pink":
            active_passages = pink_passages
        else:
            active_passages = passages
        return [room for room in active_passages[position] if set([room, position]) != set(game.blocked)]

    def choose_activate_power_and_action(self, charact, game, activables, game_state):
        """
            Use the special power of the character.
        """

        possible_actions = {
            "activate": [],
            "choices": []
        }
        # check if the power should be used before of after moving
        # this depends on the "activables" variable, which is a set.
        if not charact.power_activated and charact.color in activables:
            # check if special power is mandatory
            if charact.color in mandatory_powers:
                possible_actions["activate"].append(1)

            # special power is not mandatory
            else:
                possible_actions["activate"].append(0)
                possible_actions["activate"].append(1)
        
        # the power will be used
        # charact.power represents the fact that
        # the power is still available
        
        # red character
        if charact.color == "red":
            return possible_actions

        # black character
        if charact.color == "black":
            return possible_actions

        # white character
        if charact.color == "white":
            for moved_character in game.characters:
                if moved_character.position == charact.position and charact != moved_character:
                    available_positions = self.get_adjacent_positions(charact, game)
                    possible_actions["choices"].append(available_positions)

        # purple character
        if charact.color == "purple":
            available_characters = [q for q in game.characters if q.color != "purple"]

            # the socket can not take an object
            available_colors = [q.color for q in available_characters]
            possible_actions["choices"].append(available_colors)

        # brown character
        if charact.color == "brown":
            # the brown character can take one other character with him
            # when moving.
            available_characters = [q for q in game.characters if
                                    charact.position == q.position if
                                    q.color != "brown"]

            # the socket can not take an object
            available_colors = [q.color for q in available_characters]
            if len(available_colors) > 0:
                possible_actions["choices"].append(available_colors)
            else:
                return None

        # grey character
        if charact.color == "grey":
            available_rooms = [room for room in range(10) if room is not game.shadow]
            possible_actions["choices"].append(available_rooms)

        # blue character
        if charact.color == "blue":

            # choose room
            available_rooms = [room for room in range(10)]
            possible_actions["choices"].append(available_rooms)
            passages_connections = {}
            for selected_room in available_rooms:
                passages_work = passages[selected_room].copy()
                passages_connections[selected_room] = passages_work
            possible_actions["choices"].append(passages_connections)

        return possible_actions



    def activate_power(self, charact, game, activables, game_state, chosen_actions):
        """
            Use the special power of the character.
        """
        # check if the power should be used before of after moving
        # this depends on the "activables" variable, which is a set.
        if not charact.power_activated and charact.color in activables:

            # check if special power is mandatory
            if charact.color in mandatory_powers:
                power_activation = 1

            # special power is not mandatory
            else:
                power_activation = chosen_actions["activate"]

            # the power will be used
            # charact.power represents the fact that
            # the power is still available
            if power_activation:
                charact.power_activated = True

                # red character
                if charact.color == "red":
                    draw = choice(game.alibi_cards)
                    game.alibi_cards.remove(draw)
                    if draw == "fantom":
                        game.position_carlotta += -1 if self.num == 0 else 1
                    elif self.num == 0:
                        draw.suspect = False

                # black character
                if charact.color == "black":
                    for q in game.characters:
                        if q.position in self.get_adjacent_positions(charact, game):
                            q.position = charact.position

                # white character
                if charact.color == "white":
                    index_character = 0
                    for moved_character in game.characters:
                        if moved_character.position == charact.position and charact != moved_character:
                            available_positions = self.get_adjacent_positions(
                                charact, game)
                            selected_index = chosen_actions["choices"][index_character]
                            index_character += 1

                            # test
                            if selected_index not in range(len(available_positions)):
                                selected_position = choice(available_positions)

                            else:
                                selected_position = available_positions[selected_index]

                            moved_character.position = selected_position

                # purple character
                if charact.color == "purple":
                    # logger.debug("Rappel des positions :\n" + str(game))

                    available_characters = [q for q in game.characters if
                                            q.color != "purple"]

                    # the socket can not take an object
                    selected_index = chosen_actions["choices"]

                    # test
                    if selected_index not in range(len(colors)):
                        selected_character = choice(colors)

                    else:
                        selected_character = available_characters[selected_index]


                    # swap positions
                    charact.position, selected_character.position = selected_character.position, charact.position


                    return selected_character

                # brown character
                if charact.color == "brown":
                    # the brown character can take one other character with him
                    # when moving.
                    available_characters = [q for q in game.characters if
                                            charact.position == q.position if
                                            q.color != "brown"]

                    # the socket can not take an object
                    available_colors = [q.color for q in available_characters]
                    if len(available_colors) > 0:
                        selected_index = chosen_actions["choices"]

                        # test
                        if selected_index not in range(len(colors)):
                            selected_character = choice(colors)
                        else:
                            selected_character = available_characters[selected_index]
                        return selected_character
                    else:
                        return None

                # grey character
                if charact.color == "grey":

                    available_rooms = [room for room in range(10) if room is
                                       not game.shadow]
                    selected_index = chosen_actions["choices"]

                    # test
                    if selected_index not in range(len(available_rooms)):
                        selected_index = randint(0, len(available_rooms) - 1)
                        selected_room = available_rooms[selected_index]

                    else:
                        selected_room = available_rooms[selected_index]

                    game.shadow = selected_room

                # blue character
                if charact.color == "blue":

                    # choose room
                    available_rooms = [room for room in range(10)]
                    selected_index = chosen_actions["choices"][0]

                    # test
                    if selected_index not in range(len(available_rooms)):
                        selected_index = randint(0, len(available_rooms) - 1)
                        selected_room = available_rooms[selected_index]

                    else:
                        selected_room = available_rooms[selected_index]

                    # choose exit
                    passages_work = passages[selected_room].copy()
                    available_exits = list(passages_work)
                    selected_index = chosen_actions["choices"][1]

                    # test
                    if selected_index not in range(len(available_exits)):
                        selected_exit = choice(passages_work)

                    else:
                        selected_exit = available_exits[selected_index]

                    game.blocked = tuple((selected_room, selected_exit))
            else:
                # if the power was not used
                return None

    def move(self, charact, moved_character, blocked, game_state, game, selected_index):
        """
            Select a new position for the character.
        """

        # get the number of characters in the same room
        characters_in_room = [
            q for q in game.characters if q.position == charact.position]
        number_of_characters_in_room = len(characters_in_room)

        # get the available rooms from a given position
        available_rooms = list()
        available_rooms.append(self.get_adjacent_positions(charact, game))
        for step in range(1, number_of_characters_in_room):
            # build rooms that are a distance equal to step+1
            next_rooms = list()
            for room in available_rooms[step-1]:
                next_rooms += self.get_adjacent_positions_from_position(room,
                                                                        charact,
                                                                        game)
            available_rooms.append(next_rooms)

        # flatten the obtained list
        temp = list()
        for sublist in available_rooms:
            for room in sublist:
                temp.append(room)


        # filter the list in order to keep an unique occurrence of each room
        temp = set(temp)
        available_positions = list(temp)

        # ensure the character changes room
        if charact.position in available_positions:
            available_positions.remove(charact.position)

        # if the character is purple and the power has
        # already been used, we pass since it was already moved
        # (the positions were swapped)
        if charact.color == "purple" and charact.power_activated:
            pass
        else:
            # test
            if selected_index not in range(len(available_positions)):
                selected_position = choice(available_positions)

            else:
                selected_position = available_positions[selected_index]

            # it the character is brown and the power has been activated
            # we move several characters with him
            if charact.color == "brown" and charact.power_activated:
                charact.position = selected_position
                if moved_character:
                    moved_character.position = selected_position
            else:
                charact.position = selected_position
