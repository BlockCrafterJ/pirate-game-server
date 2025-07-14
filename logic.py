from server import Server
import time
import threading
from typing import List
import json


class PlayerInstance:
    def __init__(self, ID, game_ID = -1, name = ""):
        self.ID = ID
        self.game_ID = game_ID
        self.last_check_time = time.time()
        self.name = name

    def request(self, command_type = "", contents = {}):
        self.last_check_time = time.time()

    def check_timeout(self):
        if time.time() - self.last_check_time >= TIMEOUT:
            ids.remove(self.ID)
            players.remove(self)

class GameInstance:
    def __init__(self, ID):
        self.ID = ID
        self.player_ids = []
        self.last_check_time = time.time()
        self.grid = []
        self.next_square_list = []

    def request(self, command_type = "", contents = {}):
        self.last_check_time = time.time()
        self.grid = json.loads(contents.get("cross-grid")[0])

    def check_timeout(self):
        if time.time() - self.last_check_time >= TIMEOUT:
            game_ids.remove(self.ID)
            available_game_ids.append(self.ID)
            games.remove(self)

counter = 0
content = ""
ids = []
next_id = 0
game_ids = []
players: List[PlayerInstance] = []
games: List[GameInstance] = []
available_game_ids = []

TIMEOUT = 15

game_server = Server()

def serve_thread():
    global threads
    game_server.serve()
    print("exit")
    threads -= 1

threads = 0

print("Generating game IDs... ", end="")
for i in range(9999):
    available_game_ids.append(i)
print("- Done")

while True:
    counter += 1
    for player in players:
        player.check_timeout()
    for game in games:
        game.check_timeout()
    if threads <= len(players) + len(games):
        thread = threading.Thread(target=serve_thread)
        thread.start()
        threads += 1
    #print(len(threads))