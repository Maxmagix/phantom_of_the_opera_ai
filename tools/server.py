import cProfile
import random
import sys

from src.Game import Game
from src.Player import Player
from src.globals import logger, clients, link

"""
    The order of connexion of the sockets is important.
    inspector is player 0, it must be represented by the first socket.
    fantom is player 1, it must be representer by the second socket.
"""


def init_connexion():
    while len(clients) != 2:
        link.listen(2)
        (clientsocket, addr) = link.accept()
        logger.info("Received client !")
        clients.append(clientsocket)
        clientsocket.settimeout(10)

def startServer():
    logger.info("no client yet")
    init_connexion()
    logger.info("received all clients")

    # profiling
    pr = cProfile.Profile()
    pr.enable()

    return pr

def endServer(pr):
    link.close()

    # profiling
    pr.disable()
    # stats_file = open("{}.txt".format(os.path.basename(__file__)), 'w')
    stats_file = open("./logs/profiling.txt", 'w')
    sys.stdout = stats_file
    pr.print_stats(sort='time')

    sys.stdout = sys.__stdout__

def play():
    players = [Player(0), Player(1)]
    game = Game(players)
    return game.lancer()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        random.seed(float(sys.argv[1]))
    pr = startServer()
    play()
    endServer(pr)
