#!/bin/env python3

import subprocess
import threading
import time
import os
import sys
from queue import Queue

# Disables logging on stdout; see the logs/ folder to find them
os.environ["DONT_LOG_STDOUT"] = "NO"

from server import startServer, endServer, play

class SubprocessThread(threading.Thread):
	def __init__(self, command):
		threading.Thread.__init__(self)
		self.command = command
	def run(self):
		subprocess.run(self.command, capture_output=True, shell=True)


class ServerThread(threading.Thread):
	def __init__(self, resQueue, nbGames):
		threading.Thread.__init__(self)
		self.resQueue = resQueue
		self.nbGames = nbGames

	def run(self):
		print("Starting server", file=sys.stderr)
		pr = startServer()
		print("Clients connected", file=sys.stderr)

		# scores = []
		scores = []

		print("Running tests", file=sys.stderr)
		sizeLoadingBar = 30
		loading = 0
		for i in range(self.nbGames):
			if self.nbGames <= sizeLoadingBar:
				print("=" * (sizeLoadingBar // self.nbGames), file=sys.stderr, end='')
				sys.stderr.flush()
				loading += 1
			elif self.nbGames > sizeLoadingBar and i / (self.nbGames / sizeLoadingBar) > loading:
				print("=", file=sys.stderr, end='')
				sys.stderr.flush()
				loading += 1

			scores.append(play())
		print(file=sys.stderr)

		endServer(pr)
		self.resQueue.put(scores)


def runWinBench(comFan, comInsp, nbGames):
	q = Queue()

	serverThread = ServerThread(q, nbGames)
	fantomThread = SubprocessThread(comFan)
	inspThread = SubprocessThread(comInsp)

	serverThread.start()

	time.sleep(1)

	fantomThread.start()
	inspThread.start()

	serverThread.join()
	return q.get()

def printWinStats(scores):
	nbGames = len(scores)
	fantomWins = len(list(filter(lambda x: x <= 0, scores)))
	inspWins = nbGames - fantomWins

	print("played {} games".format(nbGames))
	print("fantom win rate: {:.2f}%".format(fantomWins / nbGames * 100))
	print("inspector win rate: {:.2f}%".format(inspWins / nbGames * 100))

def main(argv):
	comFan = argv[0]
	comInsp = argv[1]
	nbGames = int(argv[2])

	scores = runWinBench(comFan, comInsp, nbGames)
	printWinStats(scores)
	os._exit(0) # This is dirty, the subprocesses don't seem exit so we forcefully exit

if __name__ == '__main__':
	if len(sys.argv[1:]) == 3:
		main(sys.argv[1:])
	else:
		print("USAGE")
		print("\t./win_benchmark.py command_run_fantom_IA command_run_inspector_IA nb_games")

# try it with:
# $ ./win_benchmark.py "python3 random_fantom.py" "python3 random_inspector.py" "50"
