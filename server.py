from worldgen import WorldGen
from entities.player import Player
from entities.zombie import Zombie
from math import ceil
from random import randint, random, choice
from timer import Cooldown, Stopwatch


class Server:
    def __init__(self, state):
        self.state = state
        self.entities = []
        self.tilemap = {}
        self.ticker_tiles = {}
        self.worldgen = WorldGen(self.tilemap, self)
        self.worldgen.start()
        self.monster_time_scale = 1
        self.mob_cap = 10
        self.monster_cooldown = Cooldown(60 * 5 * self.monster_time_scale)
        self.age = Stopwatch()

    def get_world_spawn(self):
        x = randint(-10, 10)
        y = self.get_highest(x)
        return (x, y)

    def spawn(self, entity_type, x):
        same_type = len([
            entity
            for entity in self.entities
            if isinstance(entity, entity_type)
        ])
        if same_type < self.mob_cap:
            y = self.get_highest(x)
            entity = entity_type(self, (x, y))
            self.entities.append(entity)
            return entity, True

    def get_tile(self, pos):
        if pos not in self.tilemap:
            self.worldgen.generate(pos)
        return self.tilemap[pos]

    def get_highest(self, x, stop_clip=True):
        y = -15
        while True:
            if (x, y) in self.tilemap:
                y -= 1
            else:
                break
        tile = self.get_tile((x, y))
        while tile and tile.COLLISION:
            y += 1
            tile = self.get_tile((x, y))
        return y + 0.01 if stop_clip else 0

    def set_tile(self, pos, tile):
        if tile and tile.TICKER:
            self.ticker_tiles[pos] = tile
        elif pos in self.tilemap:  # Check the old tile
            old_tile = self.tilemap[pos]
            if old_tile and old_tile.TICKER:
                del self.ticker_tiles[pos]
        self.tilemap[pos] = tile

    def tick(self):
        self.monsters()
        to_delete = []
        for entity in self.entities:
            if entity.enabled:
                entity.tick()
            if entity.destroyed:
                to_delete.append(entity)
        for entity in to_delete:
            self.entities.remove(entity)
        for pos, tile in list(self.ticker_tiles.items()):
            tile.tick(pos, self)

    def monsters(self):
        if self.monster_cooldown.expired():
            self.monster_cooldown.start(
                (60 + (random() - 0.5) * 30) * self.monster_time_scale
            )
            monster_num = ceil(self.age.time() / (60 * 10) * random())
            for i in range(monster_num):
                player = [
                    entity
                    for entity in self.entities
                    if isinstance(entity, Player)
                ]
                if player:
                    x_pos = choice(player).x + choice([-30, 30])
                    self.spawn(choice([Zombie]), x_pos)

    def collides(self, pos):
        x, y = pos
        return self.get_tile((round(x), round(y)))

    def entities_at(self, pos):
        return [
            entity
            for entity in self.entities
            if entity.collides(pos)
        ]

    def is_full(self, pos):
        return self.collides(pos) or len(self.entities_at(pos))
