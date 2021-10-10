from localgame.game import Game
from localgame.globals import passages, colors, pink_passages, before, after, mandatory_powers

myfile = open("logfilechoices.log", "w")

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

def get_new_possibilities(action, game_state, turns_left, action_description, moved_character=[""]):
    # action affect game state
    # if turn end we end turn (turns_left.pop(0)) otherwise we stay on same person's turn
    #  return possible actions
    
    simulated_game = Game()
    simulated_game.set_game_state(game_state)
    nb_player = 0 if turns_left[0] == "inspector" else 1
    color = ""
    
    if action_description[0] == "select_color":
      color = action["color"]
      charact = simulated_game.get_character_from_color(color, simulated_game.characters)
      simulated_game.players[nb_player].select(simulated_game.active_cards, charact) ## select the color of the card to play
      game_state = simulated_game.get_game_state()
      optional_activation = simulated_game.players[nb_player].choose_activate_power(color, before) #if power is activable before move choose if activate
      if (optional_activation):
        return optional_activation, game_state, turns_left, ["choose_activate_before", color]
      moves = simulated_game.players[nb_player].get_possible_moves(charact, simulated_game)
      return moves, game_state, turns_left, ["move", color]
    else:
      color = action_description[1]
      charact = simulated_game.get_character_from_color(color, simulated_game.characters)

    if action_description[0] == "choose_activate_before":
      if (action == 1):

        choices = simulated_game.players[nb_player].get_power_choices(charact, simulated_game, before) 
        return choices, game_state, turns_left, ["before_power", color]
      moves = simulated_game.players[nb_player].get_possible_moves(charact, simulated_game)
      return moves, game_state, turns_left, ["move", color]

    if (action_description[0] == "before_power"):
      moved_character[0] = simulated_game.players[nb_player].activate_power(charact, simulated_game, before, action) #power got activated before move
      game_state = simulated_game.get_game_state() #get new game_state
      if (color == "purple"):
        colors = simulated_game.players[nb_player].possible_selected_cards(simulated_game.active_cards) #if purple end turn
        turns_left.pop()
        return colors, game_state, turns_left, ["select_color"]
      moves = simulated_game.players[nb_player].get_possible_moves(charact, simulated_game) #give move possibilities
      return moves, game_state, turns_left, ["move", color]

    if (action_description[0] == "move"):
      simulated_game.players[nb_player].move(charact, moved_character[0], simulated_game, action) #move the player
      game_state = simulated_game.get_game_state()#get new game_state
      optional_activation = simulated_game.players[nb_player].choose_activate_power(charact, after) #get if power activation is optional
      if (optional_activation):
        return optional_activation, game_state, turns_left, ["choose_activate_after", color]
      power_possibilities = simulated_game.players[nb_player].get_power_choices(charact, after) #otherwise return the power possibilities
      return power_possibilities, game_state, turns_left, ["after_power", color]
    
    if action_description[0] == "choose_activate_after":
      if (action == 1):
        choices = simulated_game.players[nb_player].get_power_choices(charact, simulated_game, after) #if power got activated give power options
        return choices, game_state, turns_left, ["after_power", color]
      colors = simulated_game.players[nb_player].possible_selected_cards(simulated_game.active_cards) #end turn
      turns_left.pop()
      return colors, game_state, turns_left, ["select_color"]

    if action_description[0] == "after_power":
      simulated_game.players[nb_player].activate_power(charact, simulated_game, before, action) #activate the power in game state
      game_state = simulated_game.get_game_state() #get new game_state
      colors = simulated_game.players[nb_player].possible_selected_cards(simulated_game.active_cards) #end turn
      turns_left.pop()
      return colors, game_state, turns_left, ["select_color"]

    # select 
    # activate power for purple and brown
    # move
    # activate power
    return 

class SkyRoot:
  alpha: 10000
  beta = -10000

_Skyroot = SkyRoot()

class Tree:
    """
        Class representing the possibility tree and adding Alplha Beta to optimise it
    """
    score: float
    maxScore: float
    minScore: float
    answer: str
    branches = []
    mother_branch = None

    def __init__(self, answer, possibilities, game_state, turns_left, action_description, trunk):
        self.answer = answer
        self.mother_branch = trunk
        # Case if End Of Branch
        if len(turns_left) == 0:
          self.score = self.calculate_score(game_state) # TODO
        # Case if Phantom turn
        elif turns_left[0] == "phantom": # TODO : TOCHECK
          self.maxScore = -10000
          
          ## log
          myfile.write("\n" + str(action_description[0]))
          myfile.write(str(possibilities))
          ##

          for possibility in possibilities: 
            # Calculate possibilities of the branch and create it
              new_possible_actions, new_game_state, turns_to_play, new_action_description = get_new_possibilities(possibility, game_state, turns_left, action_description) # TODO
              branch = Tree(possibility, new_possible_actions, new_game_state, turns_to_play, new_action_description, self)
              self.branches.append(branch)
              # Get best score & Alpha/Beta Pruning
              maxScore = max(maxScore, branch.score)
              _Skyroot.alpha = max(_Skyroot.alpha, branch.score)
              if SkyRoot.beta <= SkyRoot.alpha:
                break
          self.score = maxScore
        # Case if Inspector turn
        else:
          self.minScore = 10000
          for possibility in possibilities:
            ## log
            myfile.write(str(possibility))
            ##

            # Calculate possibilities of the branch and create it
            new_possible_actions, new_game_state, turns_to_play, new_action_description = get_new_possibilities(possibility, game_state, turns_left, action_description) # TODO
            branch = Tree(possibility, new_possible_actions, new_game_state, turns_to_play, new_action_description, self)
            self.branches.append(branch)
            # Get best score & Alpha/Beta Pruning
            minScore = min(minScore, branch.score)
            _Skyroot.beta = min(_Skyroot.beta, branch.score)
            if SkyRoot.beta <= SkyRoot.alpha:
              break
          self.score = minScore
        
        
    
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
