def get_fantom_from_color(game_state, fantom_color):
    for c in game_state["characters"]:
        if c["color"] == fantom_color:
            return c


def predict_carlotta_move(game_state, fantom_position):
    partition = [[p for p in game_state["characters"] if p["position"] == i] for i in range(10)]
    move = 0

    if len(partition[fantom_position]) == 1 \
            or fantom_position == game_state["shadow"]:
        move += 1
        for room, chars in enumerate(partition):
            if len(chars) == 1 or room == game_state["shadow"]:
                for p in chars:
                    move += 1
    else:
        for room, chars in enumerate(partition):
            if len(chars) > 1 and room != game_state["shadow"]:
                for p in chars:
                    move += 1

    return move


def predict_carlotta_move_inspector(game_state):
    partition = [[p for p in game_state["characters"] if p["position"] == i] for i in range(10)]
    move_scream = 1
    move_no_scream = 0

    for room, chars in enumerate(partition):
        if len(chars) == 1 or room == game_state["shadow"]:
            for p in chars:
                move_scream += 1

    for room, chars in enumerate(partition):
        if len(chars) > 1 and room != game_state["shadow"]:
            for p in chars:
                move_no_scream += 1

    return move_scream, move_no_scream
