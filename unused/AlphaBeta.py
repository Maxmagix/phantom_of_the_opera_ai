#Init Call Example
# minmax(current_game_state, 4, -666, 666, 1)

def minmax(game_state, depth, alpha, beta, turn_nb):
  if depth == 0:
    return score(game_state)
  

  elif turn_nb % 8 == 1 || turn_nb % 8 == 2 ||  turn_nb % 8 == 4 || turn_nb % 8 == 7: # Fantome
    maxEval = -666
    for child in child_finder(game_state): #It makes sense i swear...
      eval = minmax(child, depth - 1, alpha, beta, turn_nb + 1)
      maxEval = max(maxEval, eval)
      alpha = max(alpha, eval)
      if beta <= alpha:
        break
      return maxEval

  else: # Inspector
    minEval = 666
    for child in child_finder(game_state):
      eval = minmax(child, depth - 1, alpha, beta, turn_nb + 1)
      minEval = min(minEval, eval)
      beta = min(beta, eval)
      if beta <= alpha:
        break
      return minEval
