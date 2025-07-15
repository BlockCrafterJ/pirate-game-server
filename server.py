import random
import socketserver
from http.server import BaseHTTPRequestHandler
import logic
import urllib.parse
import json
from enum import Enum

content = ""


class action_types (Enum):
    ROB = 0
    KILL = 1
    PRESENT = 2
    WIPE_OUT = 3
    SWAP = 4
    CHOOSE_NEXT_SQUARE = 5
    SHIELD = 6
    MIRROR = 7
    BOMB = 8
    DOUBLE = 9
    BANK = 10
    M_5000 = 11
    M_3000 = 12
    M_1000 = 13
    M_200 = 14


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        current_content = content
        #if self.path == "/":
        #    print(current_content)
        self.send_response(200, "OK")
        if self.headers.get("ID") == "-1" and self.headers.get("Pirate-type") == "Player":
            self.send_header("Command-type-pirate", "New-ID")
            next_id = logic.next_id
            logic.next_id += 1
            current_content = str(next_id)
            logic.ids.append(next_id)
            game_id = int(self.headers.get("Game-ID"))
            player_name = self.headers.get("Name")
            logic.players.append(logic.PlayerInstance(next_id, game_id, player_name))
        elif self.headers.get("ID") == "-1" and self.headers.get("Pirate-type") == "Host":
            self.send_header("Command-type-pirate", "New-ID")
            host_id = logic.available_game_ids[random.randint(0, len(logic.available_game_ids)-1)]
            logic.available_game_ids.remove(host_id)
            logic.game_ids.append(host_id)
            logic.games.append(logic.GameInstance(host_id))
            current_content = str(host_id)
        self.send_header('Content-type', 'text/html')
        self.send_header("Connection", "Keep-alive")
        ID = int(self.headers.get("ID"))
        if self.headers.get("Pirate-type") == "Player":
            if ID != -1:
                print("Got request from player")
                player = logic.players[logic.ids.index(ID)]
                contents = urllib.parse.urlparse(self.path).query
                contents = urllib.parse.parse_qs(contents)
                player.request(self.headers.get("Command-type-pirate"), self.headers, contents)
                self.send_header("Command-type-pirate", "Set-cross-grid")
                if self.headers.get("Player-action") != "-1":
                    action = int(self.headers.get("Player-action"))
                    print(action)
                    player_names = []
                    player_ids = []
                    for loop_player in logic.players:
                        if loop_player != player:
                            player_names.append(loop_player.name)
                            player_ids.append(loop_player.ID)
                    print(player_names)
                    self.send_header("Player-name-list", json.dumps(player_names))
                    self.send_header("Player-ID-list", json.dumps(player_ids))
                    '''match action:
                        case action_types.ROB:
                            self.send_header("")'''

                self.send_header("Cash", str(player.money))
                current_content = json.dumps(logic.games[logic.game_ids.index(player.game_ID)].grid)
        if self.headers.get("Pirate-type") == "Host":
            if ID != -1:
                game = logic.games[logic.game_ids.index(ID)]
                contents = urllib.parse.urlparse(self.path).query
                contents = urllib.parse.parse_qs(contents)
                game.request(self.headers.get("Command-type-pirate"), contents)
                self.send_header("Command-type-pirate", "Set-cross-grid")
                current_content = json.dumps(game.grid)
        if self.headers.get("Pirate-type") == "ID-query":
            if ID in logic.game_ids:
                self.send_header("ID-exists", "Yes")
        self.send_header("Content-length", str(len(current_content)))
        self.end_headers()
        self.wfile.write(current_content.encode("utf-8"))


def set_content(content_input):
    global content
    content = content_input


class Server:
    def __init__(self):
        self.httpd = socketserver.TCPServer(("", 8080), Handler)
        self.client_number = 0

    def serve(self):
        #self.client_number += 1
        self.httpd.handle_request()
        #self.client_number -= 1