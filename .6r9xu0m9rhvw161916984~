import traceback
from entities.player import Player
from time import sleep


def exec_admin(command, state):
    admin_globals = {
        "state": state,
        "users": state.users,
        "servers": state.servers,
        "fps": state.timer.fps()
    }
    if state.servers and state.users:
        players = [
            entity
            for entity in state.servers[0].entities
            if isinstance(entity, Player)
        ]
        admin_globals.update({
            "first_server": state.servers[0],
            "entities": state.servers[0].entities,
            "tilemap": state.servers[0].tilemap,
            "players": players,
            "active_players": [
                player
                for player in players
                if player.enabled
            ],
            "active_users": [
                player.user
                for player in players
                if player.enabled
            ]
        })
        if players:
            admin_globals.update({
                "first_player": players[0]
            })
    try:
        try:
            print(eval(command, admin_globals))
        except Exception:
            exec(command, admin_globals)
    except Exception:
        print("Error in repl code:")
        print(traceback.format_exc())


def console(state):
    while not state.server_started:
        sleep(0.1)
    print("Admin Console")
    print("Type 'help' for help")
    repl_mode = False
    while True:
        if repl_mode:
            print("(repl mode)", end="")
        command = input(" >>> ")
        
        if repl_mode:
            if command == "/exit":
                repl_mode = False
                continue
            exec_admin(command, state)
            continue
        
        if command == "help":
            print("""
Admin Console Help

Start a Python instruction with a '/' to run it globals:
* state
* users
* fps
* servers
* first_server
* entities
* tilemap
* players
* active_players
* active_users
* first_player
(Some may not be present if they do not exist)

repl - Start a Python repl (once in it, type '/exit' to exit)
            """)
        elif command == "repl":
            print("Type '/exit' to exit Python repl")
            repl_mode = True
        elif command.startswith("/"):
            exec_admin(command[1:], state)
        else:
            print("Invalid command")
        