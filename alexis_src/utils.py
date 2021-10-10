def get_char_from_color(game_state, color):
    for c in game_state["characters"]:
        if c["color"] == color:
            return c
