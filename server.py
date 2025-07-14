import random
import socketserver
from http.server import BaseHTTPRequestHandler
import logic
import urllib.parse
import json

content = ""


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
                player = logic.players[logic.ids.index(ID)]
                contents = urllib.parse.urlparse(self.path).query
                contents = urllib.parse.parse_qs(contents)
                player.request(self.headers.get("Command-type-pirate"), contents)
                self.send_header("Command-type-pirate", "Set-cross-grid")
                current_content = json.dumps(logic.games[logic.game_ids.index(player.game_ID)].grid)
                print(type(current_content))
            print(ID)
        if self.headers.get("Pirate-type") == "Host":
            if ID != -1:
                game = logic.games[logic.game_ids.index(ID)]
                contents = urllib.parse.urlparse(self.path).query
                contents = urllib.parse.parse_qs(contents)
                game.request(self.headers.get("Command-type-pirate"), contents)
            print(ID)
        if self.headers.get("Pirate-type") == "ID-query":
            if ID in logic.game_ids:
                self.send_header("ID-exists", "Yes")
                print("ID EXISTS:", ID)
            else:
                print("ID DOES NOT EXIST")
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