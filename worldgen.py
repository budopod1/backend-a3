import random
from wave import Wave
from tiles import Grass, Wood, Leaves, Stone, Flowers, Trader1, IronOre
from math import ceil


class WorldGen: # https://www.desmos.com/calculator/xy1dflbuac
    def __init__(self, tilemap, server, seed=0):
        self.seed = seed
        random.seed(seed)
        self.tilemap = tilemap
        self.server = server
        
        self.grass_wave = Wave(100, 15, 100, 0)

        self.stone_wave = Wave(100, 10, 100, -3)

        self.tree_wave = Wave(100, 1, 100, 0.1)

        self.flower_wave = Wave(100, 10, 100, -0.5)

    def start(self):
        pos = (0, self.server.get_highest(0, False) + 1)
        self.server.set_tile(pos, Trader1())

    def gen_tree(self, pos):
        x, y = pos
        set_tile = self.server.set_tile
        for o in range(random.randint(3, 7)):
            set_tile((x, y + o), Wood())
        set_tile((x + 1, y + o), Leaves())
        set_tile((x - 1, y + o), Leaves())
        set_tile((x, y + o + 1), Leaves())

    def generate(self, pos):
        x, y = pos
        random.seed(f"{self.seed}{x}{y}")
        grass_height = self.grass_wave.generate(x)
        stone_height = self.stone_wave.generate(x)
        tree_prob = self.tree_wave.generate(x)
        flower_prob = self.flower_wave.generate(x)
        block = None
        if y < grass_height:
            if y < stone_height:
                if random.random() < 0.05:
                    block = IronOre()
                else:
                    block = Stone()
            else:
                block = Grass()
        if ceil(grass_height - y) == 0 and\
                isinstance(self.server.get_tile((x, y - 1)), Grass):
            if random.random() < tree_prob:
                block = Wood()
                self.gen_tree((x, y))
            elif random.random() < flower_prob:
                block = Flowers()
        self.server.set_tile(pos, block)
        