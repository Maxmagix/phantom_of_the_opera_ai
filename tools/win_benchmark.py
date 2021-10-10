#!/bin/env python3

import subprocess
import threading
import time
import os
import random
import sys
from queue import Queue

# Disables logging on stdout; see the logs/ folder to find them
os.environ["DONT_LOG_STDOUT"] = "NO"

from server import startServer, endServer, play

class LoadingBar():
	def __init__(self, nbUpdates, displaySize=30):
		self.nbUpdates = nbUpdates
		self.displaySize = displaySize

		if nbUpdates == displaySize:
			self.bar = ["="] * displaySize
		elif nbUpdates < displaySize:
			self.bar = ["=" * (displaySize // nbUpdates)] * nbUpdates
			for i in range(0, displaySize % nbUpdates):
				self.bar[i * displaySize % nbUpdates] += "="
		else:
			self.bar = [""] * nbUpdates
			for i in range(0, displaySize):
				self.bar[i * (nbUpdates // displaySize)] = "="

	def increment(self):
		if len(self.bar) != 0:
			return self.bar.pop()


class SubprocessThread(threading.Thread):
	def __init__(self, command):
		threading.Thread.__init__(self)
		self.command = command
	def run(self):
		subprocess.run(self.command, capture_output=True, shell=True)


class ServerThread(threading.Thread):
	def __init__(self, resQueue):
		threading.Thread.__init__(self)
		self.resQueue = resQueue

	def run(self):
		seed = time.time()
		random.seed(seed)
		pr = startServer()
		try:
			score = play()
			self.resQueue.put(["ok", score])
		except:
			self.resQueue.put(["crash", seed])
		endServer(pr)


def runWinBench(comFan, comInsp, nbGames):
	q = Queue()
	scores = []

	bar = LoadingBar(nbGames)

	firstLoop = True

	for i in range(nbGames):
		serverThread = ServerThread(q)
		inspThread = SubprocessThread(comInsp)
		fantomThread = SubprocessThread(comFan)

		serverThread.start()

		# Leaves time for the server to start up
		if firstLoop:
			time.sleep(0.5) # First loop takes more time
			firstLoop = False
		else:
			time.sleep(0.1)

		inspThread.start()
		time.sleep(0.1) # Inspector must connect first
		fantomThread.start()

		serverThread.join()

		res = q.get()
		if res[0] == "ok":
			scores.append(res[1])
		elif res[0] == "crash":
			print("!")
			print("An error occured while playing")
			print(f"This is the server seed, use it to reproduce the error (won't always work): {res[1]}")
			return scores

		print(bar.increment(), end="", file=sys.stderr)
		sys.stderr.flush()

	print()
	return scores


def printWinStats(scores):
	nbGames = len(scores)
	fantomWins = len(list(filter(lambda x: x <= 0, scores)))
	inspWins = nbGames - fantomWins

	print(f"played {nbGames} games")
	print("fantom win rate: {:.2f}%".format(fantomWins / nbGames * 100))
	print("inspector win rate: {:.2f}%".format(inspWins / nbGames * 100))


def main(argv):
	comFan = argv[0]
	comInsp = argv[1]
	nbGames = int(argv[2])

	scores = runWinBench(comFan, comInsp, nbGames)
	if scores != []:
		printWinStats(scores)
	else:
		print("No results to display")
	os._exit(0) # This is dirty, the subprocesses don't seem exit so we forcefully exit


if __name__ == '__main__':
	if len(sys.argv[1:]) == 3:
		main(sys.argv[1:])
	else:
		print("USAGE")
		print("\t./win_benchmark.py command_run_fantom_IA command_run_inspector_IA nb_games")

# try it with:
# $ ./win_benchmark.py "python3 random_fantom.py" "python3 random_inspector.py" "50"
