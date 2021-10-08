def parse_game_state(text_state):
    game_state = {
        "position_carlotta": text_state.position_carlotta,
        "exit": text_state.exit,
        "num_tour": text_state.num_tour,
        "shadow": text_state.shadow,
        "blocked": text_state.blocked,
        "characters": text_state.characters_display,
        # Todo: should be removed
        "character_cards": text_state.character_cards_display,
        "active character_cards": text_state.active_cards_display,
    }

    return game_state

def get_new_possibilities(action, game_state, turns_left):
    # action affect game state
    # if turn end we end turn (turns_left.pop(0)) otherwise we stay on same person's turn
    #  return possible actions
    
    # select 
    # activate power for purple and brown
    # move
    # activate power

    new_game_state = (game_state)
    
    return []

class Tree:
    """
        Class representing the possibility tree and adding Alplha Beta to optimise it
    """
    alpha: float
    beta: float
    answer: str
    possibilities = []
    mother_branch = None

    def __init__(self, answer, possibilities, game_state, turns_left, trunk):
        self.answer = answer
        self.beta = -10000
        self.mother_branch = trunk
        for possibility in possibilities:
            new_possible_actions, new_game_state, turns_to_play = get_new_possibilities(possibility, game_state, turns_left)
            branch = Tree(possibility, new_possible_actions, new_game_state, turns_to_play, self)
            branch.alpha = branch.calculate_alpha(new_game_state)
            self.possibilities.append(branch)
    
    def calculate_alpha(game_state):
        # look at game state and outcome of action
        final_score = 16
        remaining_suspects = 8
        screaming_people = 0
        alpha = 0
        return alpha
    
    def propagate_beta(alpha, beta):
        if (alpha > beta):
            return alpha
        return beta