from bidict import bidict
import random


# Tiles are ordered as such:
# * First default Tile (TYPE=0) class
# * Then tiles with <0 TYPE are ordered alphabetically
# * Finally tiles with >0 TYPE are ordered alphabetically

class Tile:
    COLLISION = True
    BREAK_COOLDOWN = 0
    INTERACTABLE = False
    TYPE = 0
    PLACEABLE = True
    BREAK_SPEED = 1
    TICKER = False

    def interact(self, player):
        name = type(self).__name__
        raise AttributeError(f"Tile {name} cannot be interacted with")

    @staticmethod
    def select(player):
        pass
    
    @classmethod
    def break_becomes(cls):
        return cls
    
    @classmethod
    def place_becomes(cls):
        return cls

    def tick(self, pos, server):
        pass


class Empty(Tile):
    TYPE = -1
    PLACEABLE = False


class Arrow(Tile):
    TYPE = -2
    PLACEABLE = False


class Drill1(Tile):
    TYPE = -3
    PLACEABLE = False
    BREAK_SPEED = 2


class Drill2(Tile):
    TYPE = -4
    PLACEABLE = False
    BREAK_SPEED = 4


class Iron(Tile):
    TYPE = -3
    PLACEABLE = False


class Flowers(Tile):
    COLLISION = False
    BREAK_COOLDOWN = 0
    TYPE = 6


class Grass(Tile):
    BREAK_COOLDOWN = 0.2
    TYPE = 1


class Hatch(Tile):
    BREAK_COOLDOWN = 0.2
    Type = 12


class IronOre(Tile):
    BREAK_COOLDOWN = 4
    TYPE = 9
    
    @classmethod
    def break_becomes(cls):
        return Iron


class Mango(Tile):
    TYPE = 7

    @classmethod
    def place_becomes(cls):
        return Sapling
    
    @staticmethod
    def select(player):
        player.remove_n_items(Mango, 1)
        player.health = player.health + 2


class Leaves(Tile): # Add decorative leaves for broken leaves
    BREAK_COOLDOWN = 0.1
    TYPE = 4
    
    @classmethod
    def break_becomes(cls):
        return random.choice([
            *([Mango] * 1),
            *([Leaves] * 3)
        ])


class Planks(Tile):
    BREAK_COOLDOWN = 0.1
    TYPE = 5


class Sapling(Tile):
    BREAK_COOLDOWN = 0.05
    TYPE = 10
    COLLISION = False
    TICKER = True
    
    @classmethod
    def break_becomes(cls):
        return None

    def tick(self, pos, server):
        if random.random() / server.state.timer.time_delta < 1/300:
            server.worldgen.gen_tree(pos)


class Stone(Tile):
    BREAK_COOLDOWN = 2
    TYPE = 2


class Trader1(Tile):
    COLLISION = False
    BREAK_COOLDOWN = 5
    INTERACTABLE = True
    TYPE = 8
    
    @classmethod
    def break_becomes(cls):
        return Trader1Stall

    def interact(self, player):
        player.user.container = 2


class Trader1Stall(Tile):
    TYPE = 11

    @classmethod
    def place_becomes(cls):
        return Trader1


class Wood(Tile):
    COLLISION = False
    BREAK_COOLDOWN = 0.5
    TYPE = 3


tiles = [
    Tile, Arrow, Mango, Drill1, Drill2, Iron, IronOre, Grass, Wood,
    Leaves, Stone, Flowers, Planks, Sapling, Trader1, Trader1Stall
]

tile_inventory_order = bidict({i: item for i, item in enumerate([
    Tile, Arrow, Drill1, Drill2, Iron, IronOre, Grass,
    Stone, Wood, Planks, Mango, Sapling, Leaves, Flowers, Trader1, Trader1Stall
])})

tile_hotbar_order = bidict({i: item for i, item in enumerate([
    Grass, Stone, Wood, Planks, Mango, Leaves, Flowers, Trader1Stall
])})
