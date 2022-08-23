from entities.entity import Entity
from math import ceil
from tiles import tile_hotbar_order, tile_inventory_order
from timer import Cooldown
from container import trade_containers, get_trade


class Player(Entity):
    def __init__(self, server, pos=(0, 0), user=None):
        super().__init__( server, pos=(0, 0))
        assert user
        self.user = user
        self.iq = float('inf')

        # I stole the names from minceraft, so what?
        self.mode = "survival"

        self.spawn()

    def spawn(self):
        self.health = 10
        self.jump_power = 7
        self.move_power = 5
        self.collider = [
            (0.2, -1),
            (-0.2, -1),
            (-1, 0),
            (1, 0),
            (0.2, 1),
            (-0.2, 1),
        ]

        self.reach = 4
        self.attack_cooldown_length = 1
        self.attack_cooldown = Cooldown(self.attack_cooldown_length)
        self.attack_damage = 1
        
        self.inventory = {}
        self.selected = 0

        self.ground_pounding = False
        self.ground_pound_speed = -10

        self.break_cooldown = Cooldown()

    def destroy(self):
        self.spawn()
        self.x, self.y = self.server.get_world_spawn()
        self.xv = self.yv = 0

    def damage(self, amount):
        if self.mode in ["survival"]:
            super().damage(amount)

    def get_health(self):
        if self.mode in ["creative"]:
            return 0
        else:
            return ceil(self.health * 2)

    def tick(self):
        if not super().tick():
            return False

        self.user.proccess_input()
        
        press_ground_pound = 83 in self.user.keys_just_down
        press_jump = 87 in self.user.keys_down
        up_and_down = press_ground_pound and press_jump

        if 32 in self.user.keys_just_down:
            if self.user.container == 0:
                self.user.container = 1
            else:
                self.user.container = 0
        elif 27 in self.user.keys_just_down:
            self.user.container = 0
            
        mouse_buttons = self.user.mouse_buttons
        mouse_buttons_just_down = self.user.mouse_buttons_just_down

        lmb = 1 in mouse_buttons
        lmbjd = 1 in mouse_buttons_just_down
        rmb = 3 in mouse_buttons or (
            lmb and 16 in self.user.keys_down
        )
        if rmb:
            lmb = False
        rmbjs = 3 in mouse_buttons_just_down or (lmbjd and 16 in self.user.keys_down)
        if rmbjs:
            lmbjd = False

        if (self.user.container in trade_containers and self.user.cell >= 0
            and lmbjd):
            cell = self.user.cell
            i = 0
            while cell > 3:
                cell -= 4
                if i % 2 == 0:
                    cell -= 1
                i += 1
            trade = get_trade(self.user.container, i)
            if trade is not None:
                if self.try_trade(trade):
                    # Close the container if you can't make the same trade again
                    if not self.can_trade(trade):
                        self.user.container = 0
                        # mouse is still in same place as when clicked on trader
                        # as far as game knows, so if we don't remove the mouse input
                        # the container will immediatly reopen
                        lmb = False
                        lmbjd = False
                        rmb = False
                        rmbjd = False
        
        if (self.user.container == 1 and self.user.cell >= 0
            and lmbjd):
                inventory = self.sorted_inventory()
                if self.user.cell < len(inventory):
                    inventory[self.user.cell].select(self)
            
        
        if self.user.container:
            return

        time_delta = self.state.timer.time_delta

        if self.grounded:
            self.ground_pounding = False

        if self.ground_pounding:
            self.yv = self.ground_pound_speed
        else:
            if self.grounded and (press_jump and not up_and_down):
                self.yv = self.jump_power
    
            if 65 in self.user.keys_down:
                self.xv -= self.move_power * time_delta
    
            if 68 in self.user.keys_down:
                self.xv += self.move_power * time_delta

        if press_ground_pound and not up_and_down:
            self.ground_pounding = not self.ground_pounding
            if self.ground_pounding:
                self.xv = 0
        
        mouse_x = round(self.user.mouse_x)
        mouse_y = round(self.user.mouse_y)
        
        if lmb:
            if self.can_place(mouse_x, mouse_y):
                self.place(mouse_x, mouse_y, self.selected_item())
            elif lmbjd and self.can_interact(mouse_x, mouse_y):
                self.interact(mouse_x, mouse_y)

        if rmb:
            if self.can_break(mouse_x, mouse_y):
                self.break_(mouse_x, mouse_y)
            elif self.can_attack(mouse_x, mouse_y):
                self.attack(mouse_x, mouse_y)

        self.selected += self.user.scroll
        if 81 in self.user.keys_just_down:
            self.selected -= 1
        elif 69 in self.user.keys_just_down:
            self.selected += 1
        self.user.scroll = 0
        if self.selected > max(tile_hotbar_order):
            self.selected = 0
        elif self.selected < 0:
            self.selected = max(tile_hotbar_order)

    def can_attack(self, mouse_x, mouse_y):
        entities = self.server.entities_at((mouse_x, mouse_y))
        return entities and entities[0] != self and self.attack_cooldown.expired() and self.within_range(entities[0], self.reach)

    def attack(self, mouse_x, mouse_y):
        entities = self.server.entities_at((mouse_x, mouse_y))
        self.attack_cooldown.start(self.attack_cooldown_length)
        entities[0].damage(self.attack_damage * self.get_speed())

    def get_speed(self):
        return max([
            item.BREAK_SPEED
            for item in self.inventory
        ], default=1)

    def can_trade(self, trade):
        take, _ = trade
        for item, amount in take:
            if not self.has_n_items(item, amount):
                return False
        return True

    def try_trade(self, trade):
        if not self.can_trade(trade):
            return False
        take, give = trade
        for item, amount in take:
            self.remove_n_items(item, amount)
        item, amount = give
        self.add_n_items(item, amount)
        return True

    def can_interact(self, x, y):
        tile = self.server.get_tile((x, y))
        if tile:
            return tile.INTERACTABLE

    def interact(self, x, y):
        tile = self.server.get_tile((x, y))
        if tile:
            tile.interact(self)

    def can_place(self, x, y):
        can_reach = self.can_reach(x, y)
        creative = self.mode in ["creative"]
        selected = self.selected_item() or creative
        is_empty = not self.server.is_full((x, y))
        return can_reach and selected and is_empty

    def can_break(self, x, y):
        can_reach = self.can_reach(x, y)
        creative = self.mode in ["creative"]
        break_cooled_down = self.break_cooldown.expired() or creative
        return self.server.collides((x, y)) and can_reach and break_cooled_down

    def sorted_inventory(self):
        return sorted(
            self.inventory,
            key=lambda k: tile_inventory_order.inverse[k]
        )

    def remove_n_items(self, item, n):
        assert self.has_n_items(item, n)
        curr_num = self.inventory[item]
        if curr_num - n > 0:
            self.inventory[item] = curr_num - n
        else:
            del self.inventory[item]

    def has_n_items(self, item, n):
        return self.inventory.get(item, 0) >= n

    def add_n_items(self, item, n):
        if item not in self.inventory:
            self.inventory[item] = n
        else:
            self.inventory[item] += n

    def collect_item(self, item):
        self.add_n_items(item, 1)
    
    def break_(self, x, y):
        if self.server.get_tile((x, y)) is not None:
            tile = self.server.get_tile((x, y))
            self.server.set_tile((x, y), None)
            self.break_cooldown.start(
                tile.BREAK_COOLDOWN / self.get_speed()
            )
            survival = self.mode in ["survival"]
            if survival:
                becomes = tile.break_becomes()
                if becomes is not None:
                    self.collect_item(becomes)

    def can_reach(self, x, y):
        creative = self.mode in ["creative"]
        return creative or self.within_range((x, y), self.reach)

    def selected_item(self):
        if self.inventory:
            item = tile_hotbar_order[self.selected]
            return item if item in self.inventory else None
        return None

    def place(self, x, y, item):
        if self.server.get_tile((x, y)) is None:
            survival = self.mode in ["survival"]
            if survival:
                self.inventory[item] -= 1
                if self.inventory[item] == 0:
                    del self.inventory[item]
            self.server.set_tile((x, y), item.place_becomes()())
    
    def get_type(self):
        return 1
    