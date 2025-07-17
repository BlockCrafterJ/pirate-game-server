from server import Server
import time
import threading
from typing import List
import json
import random


class PlayerInstance:
    def __init__(self, ID, game_ID = -1, name = ""):
        self.ID = ID
        self.game_ID = game_ID
        self.last_check_time = time.time()
        self.name = name
        self.money = 0
        self.bank = 0
        self.skip_next = 0
        self.money_set = 0
        self.money_change = 0
        self.set_money = False

    def request(self, command_type, headers, contents = {}):
        self.last_check_time = time.time()
        self.money = int(headers.get("Cash"))
        if self.set_money:
            print(self.set_money)
            self.money = self.money_set
            self.set_money = False
        self.money += self.money_change
        self.money_change = 0
        self.bank = int(headers.get("Bank"))

    def check_timeout(self):
        if time.time() - self.last_check_time >= TIMEOUT:
            print("timeout after " + str(time.time() - self.last_check_time))
            ids.remove(self.ID)
            players.remove(self)

class GameInstance:
    def __init__(self, ID):
        self.ID = ID
        self.player_ids = []
        self.last_check_time = time.time()
        self.grid = []
        for x in range(7):
            self.grid.append([])
            for y in range(7):
                self.grid[x].append(0)
        self.available_squares = []
        for x in range(7):
            for y in range(7):
                self.available_squares.append([x,y])
        self.next_square_list = []
        self.last_cross_place_time = time.time()
        self.cross_place_time = 5

    def request(self, command_type = "", contents = {}):
        self.last_check_time = time.time()
        #self.grid = json.loads(contents.get("Cross-grid"))

    def check_timeout(self):
        if time.time() - self.last_check_time >= TIMEOUT:
            game_ids.remove(self.ID)
            available_game_ids.append(self.ID)
            games.remove(self)

    def tick(self):
        if time.time() - self.last_cross_place_time >= self.cross_place_time:
            self.last_cross_place_time = time.time()
            err = self.place_cross_at_random()

    def place_cross_at_random(self):
        if len(self.available_squares) > 0:
            available_selection = random.randint(0, len(self.available_squares) - 1)
            current_square = self.available_squares[available_selection]
            self.grid[current_square[0]][current_square[1]] = 1
            self.available_squares.pop(available_selection)
            return 0
        else:
            return 1

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
        game.tick()
    if threads <= len(players) + len(games):
        thread = threading.Thread(target=serve_thread)
        thread.start()
        threads += 1
    #print(len(threads))