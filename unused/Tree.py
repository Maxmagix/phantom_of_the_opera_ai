class Parrallal_Game:
    final_score = 16
    remaining_suspects = 8
    screaming_people = 0

    ghost_color = 'blue'
    num_tour = 0
    action_tour = 0
    shadow = 0
    blocked = [0, 1]
    characters = []
    remaining_powers = []
    responses_index = []

    def __init__(self, game_state):
        self.final_score = int(game_state['exit']) - int(game_state['position_carlotta'])
        self.num_tour = int(game_state['num_tour'])
        self.shadow = int(game_state['shadow'])
        self.blocked = game_state['blocked']
        self.characters = game_state['characters']
        for card in game_state['active character_cards']:
            self.remaining_powers.append(card['color'])

def get_new_possibilities(action, game_state, turns_left):
    # action affect game state
    # if turn end we end turn (turns_left.pop(0)) otherwise we stay on same person's turn
    #  return possible actions
    
    new_game_state = Parrallal_Game(game_state)
    
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