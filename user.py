from entities.player import Player
from math import floor, ceil
from shortsocket import Array
from timer import Stopwatch
from functools import lru_cache
from container import containers
from tiles import tile_hotbar_order
from werkzeug.security import generate_password_hash, check_password_hash


class User:
    def __init__(self, server, username, password):
        self.password = generate_password_hash(password)
        
        self.player = Player(server, (0, 0), user=self)
        self.server = None
        self.user_positions = {}
        self.change_server(server)
        self.username = username

        self.keys_down = set()
        self._keys_just_down = set()
        self.keys_just_down = set()
        
        self.mouse_buttons = set()
        self._mouse_buttons_just_down = set()
        self.mouse_buttons_just_down = set()

        self._mouse_x = 0
        self._mouse_y = 0
        
        self.mouse_x = 0
        self.mouse_y = 0

        self.cell = 0

        self._scroll = []
        self.scroll = 0
        
        self.remembered_tilemap = {}
        self.remembered_selected = 0
        self.remembered_health = 0
        self.remembered_player_index = 0
        
        self.max_ratio = 3
        self.veiw_height = 7
        self.veiw_width = self.max_ratio * self.veiw_height
        self.veiw_buffer = 1
        self.timer = Stopwatch()
        self.used_ids = []

        self.container = 0

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def reset(self):
        self.remembered_tilemap = {}
        self.remembered_selected = 0
        self.remembered_health = 0
        self.remembered_player_index = 0

    @lru_cache(maxsize=255)
    def get_entity_id(self, entity):
        new_id = entity.get_type() * 16 - 126
        return new_id

    def change_server(self, server):
        if self.server: # Store position in old server
            self.user_positions[self.server] = (
                self.player.x, 
                self.player.y
            )
            self.server.entities.remove(self.player)
        if server in self.user_positions:
            self.player.x, self.player.y = self.user_positions[server]
        else:
            self.player.x, self.player.y = server.get_world_spawn()
        server.entities.append(self.player)
        self.server = server
        self.remembered_tilemap = {}
    
    def render_frame(self):
        self.timer.start()
        
        if self.container:
            return containers[self.container](self.player)

        # self.check_entity_ids()
        entities = {
            id(entity): (entity.x, entity.y,
                         self.get_entity_id(entity))
            for entity in self.server.entities
            if entity.enabled
        }

        if id(self.player) not in entities:
            return None
        player_x, player_y, _ = entities[id(self.player)]
        
        x_min = (floor(player_x - self.veiw_width) 
                - self.veiw_buffer)
        x_max = (ceil(player_x + self.veiw_width) 
                + 1 + self.veiw_buffer)
        y_min = (floor(player_y - self.veiw_height) 
                - self.veiw_buffer)
        y_max = (ceil(player_y + self.veiw_height) 
                + 1 + self.veiw_buffer)
        
        seen_tiles = [
            (x, y)
            for x in range(x_min, x_max)
            for y in range(y_min, y_max)
        ]
        
        send_tiles = []
        for tile_pos in seen_tiles:
            if (tile_pos not in self.remembered_tilemap or
                    self.remembered_tilemap[tile_pos]
                    != self.server.get_tile(tile_pos)):
                real_tile = self.server.get_tile(tile_pos)
                self.remembered_tilemap[tile_pos] = real_tile
                send_tiles.append((
                    tile_pos,
                    real_tile.TYPE if real_tile else 0
                ))
                
        entities = {
            eid: (x, y, etype)
            for eid, (x, y, etype) in entities.items()
            if x_min <= x <= x_max
            if y_min <= y <= y_max
        }
        
        extra_data = []
        before = False
        
        health = self.player.get_health()
        if health != self.remembered_health or before:
            before = True
            extra_data.insert(0, max(health, 0))
            self.remembered_health = health
        
        if self.player.selected != self.remembered_selected or before:
            before = True
            extra_data.insert(0, tile_hotbar_order[self.player.selected].TYPE)
            self.remembered_selected = self.player.selected
        
        player_index = None
        for i, (entity_id, _) in enumerate(entities.items()):
            if entity_id == id(self.player):
                player_index = i
        
        if self.remembered_player_index != player_index or before:
            before = True
            extra_data.insert(0, player_index)
            self.remembered_player_index = player_index
        
        entities = entities.values()
        
        return Array([
            Array(
                [tile[0][0] for tile in send_tiles],
                dtype="int32"
            ),
            Array(
                [tile[0][1] for tile in send_tiles],
                dtype="int32"
            ),
            Array(
                [tile[1] for tile in send_tiles],
                dtype="int8"
            ),
            Array(
                [entity[0] for entity in entities], 
                dtype="float32"
            ),
            Array(
                [entity[1] for entity in entities],
                dtype="float32"
            ),
            Array(
                [entity[2] for entity in entities],
                dtype="int8"
            ),
            Array(extra_data, dtype="int8")
        ])

    def proccess_input(self):
        self.scroll = sum([1 if input > 0 else -1 for input in self._scroll])
        self._scroll = []
        
        self.keys_just_down = self._keys_just_down
        self._keys_just_down = set()

        self.mouse_buttons_just_down = self._mouse_buttons_just_down
        self._mouse_buttons_just_down = set()
        
        self.mouse_x = self.player.x + self._mouse_x
        self.mouse_y = self.player.y + self._mouse_y
    
    def client_frame(self, keys, mouse_buttons, mouse_x, mouse_y, cell, mouse_wheel):
        self._mouse_x = mouse_x
        self._mouse_y = mouse_y

        self.cell = cell
        
        self._keys_just_down.update(keys - self.keys_down)
        self.keys_down = keys
        
        self._mouse_buttons_just_down.update(mouse_buttons - self.mouse_buttons)
        self.mouse_buttons = mouse_buttons
        
        if mouse_wheel:
            self._scroll.append(mouse_wheel)
    
    def state_frame(self):
        self.player.enabled = self.timer.time() < 10
