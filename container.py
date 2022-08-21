from tiles import Wood, Stone, Iron, Drill1, Drill2, Planks, Trader1Stall, Leaves
from utils import pad_list
from tiles import Tile, Empty, Arrow
from shortsocket import Array


all_trades = {
    1: [
        (((Wood, 3), (Stone, 1)), (Drill1, 1)),
        (((Drill1, 1), (Iron, 3)), (Drill2, 1)),
        (((Wood, 5),), (Planks, 2)),
        (((Leaves, 3), (Planks, 5)), (Trader1Stall, 1),)
    ]
}
trade_containers = [2]


def get_trade(container, num):
    if container not in trade_containers:
        return None
    trades = all_trades[{2: 1}[container]]
    if len(trades) <= num:
        return None
    return trades[num]


def inventory_container(player):
    items = player.sorted_inventory()
    amounts = [player.inventory[item] for item in items]
    return make_container(
        1,
        [
            item
            for item in items
        ],
        amounts,
        8, 4
    )

def trader1_container(player):
    trades = all_trades[1]
    return make_container(
        2,
        *zip(*[
            item
            for trade in [
                [
                    *pad_list(take, 2, (Empty(), 1)),
                    (Arrow(), 1),
                    give,
                    *([(Empty(), 1)] if i % 2 == 0 else [])
                ]
                for i, (take, give) in enumerate(trades)
            ]
            for item in trade
        ]), 9, 5, Empty
    )

def make_container(container, items, amounts, width, height, otherwise=Tile,
             slots=None):
    items = list(items[::-1])
    amounts = list(amounts[::-1])
    return Array([
        Array([container], dtype="int8"),
        Array([
            (items.pop().TYPE if items else otherwise.TYPE)
            if slots is None or (x, y) in slots else 
            otherwise.TYPE
            for x in range(width)
            for y in range(height)
        ], dtype="int8"),
        Array([
            (amounts.pop() if amounts else 1)
            if slots is None or (x, y) in slots else
            1
            for x in range(width)
            for y in range(height)
        ], dtype="int8")
    ])


containers = {
    1: inventory_container,
    2: trader1_container
}
