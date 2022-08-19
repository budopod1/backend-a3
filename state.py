from server import Server
# from client import Client
from user import User
from timer import Timer
# from time import sleep


class State:
    def __init__(self):
        self.server_started = False
        self.users = {}
        self.servers = []
        self.main_server = self.add_server()

        self.timer = Timer()

    def add_server(self):
        new_server = Server(self)
        self.servers.append(new_server)
        return new_server

    def create_user(self, username, password):
        if username in self.users:
            return None, {"success": False, "message": "That username is taken"}
        new_user = User(self.main_server, username, password)
        self.users[username] = new_user
        return new_user, {"success": True, "message": ""}

    def authorize(self, username, password):
        if username not in self.users:
            return None, {"success": False, "message": "A user with that name does not exist"}
        user = self.users[username]
        if user.check_password(password):
            return user, {"success": True, "message": ""}
        return None, {"success": False, "message": "Incorrect password"}

    def ticking(self):
        while True:
            self.tick()

    def tick(self):
        self.timer.tick()
        
        for server in self.servers:
            server.tick()
            
        for user in list(self.users.values()):
            user.state_frame()
