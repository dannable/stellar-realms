import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Ship:
    name: str
    cost: int
    cargo: int
    fuel_capacity: int
    attack: int
    defense: int

@dataclass
class TradePort:
    prices: Dict[str, int]  # commodity -> price

@dataclass
class Sector:
    id: int
    connections: List[int] = field(default_factory=list)
    planet: bool = False
    trade_port: Optional[TradePort] = None

@dataclass
class Player:
    id: int
    name: str
    sector_id: int
    ship: Ship
    credits: int = 0
    fuel: int = 0
    iron: int = 1
    heart: int = 1
    edge: int = 1
    shadow: int = 1
    wits: int = 1

class GameMap:
    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height
        self.sectors: Dict[int, Sector] = {}

        # Delay importing to avoid circular dependency with database module
        from database import load_sectors, save_sectors

        # Attempt to load sectors from the database; generate a new map if none exist
        self.sectors = load_sectors()
        if not self.sectors:
            self.generate_map()
            save_sectors(self.sectors)

    def generate_map(self):
        total = self.width * self.height
        self.sectors = {i: Sector(id=i) for i in range(total)}
        ids = list(self.sectors.keys())
        for sector in self.sectors.values():
            connect_count = random.randint(1, 4)
            while len(sector.connections) < connect_count:
                dest = random.choice(ids)
                if dest == sector.id:
                    continue
                if len(self.sectors[dest].connections) >= 4:
                    continue
                if dest not in sector.connections:
                    sector.connections.append(dest)
                    self.sectors[dest].connections.append(sector.id)

        # assign planets and trade ports
        commodities = ["Ore", "Food", "Technology"]
        for sector in self.sectors.values():
            if random.random() < 0.1:
                sector.planet = True
            if random.random() < 0.1:
                prices = {c: random.randint(5, 15) for c in commodities}
                sector.trade_port = TradePort(prices=prices)

ships = [
    Ship("Trade Freighter", 0, cargo=50, fuel_capacity=100, attack=5, defense=5),
    Ship("Scout", 1000, cargo=20, fuel_capacity=80, attack=4, defense=4),
    Ship("Light Fighter", 2000, cargo=10, fuel_capacity=90, attack=7, defense=5),
    Ship("Heavy Fighter", 4000, cargo=15, fuel_capacity=100, attack=10, defense=8),
    Ship("Interceptor", 6000, cargo=10, fuel_capacity=110, attack=12, defense=6),
    Ship("Destroyer", 10000, cargo=30, fuel_capacity=120, attack=15, defense=12),
    Ship("Cruiser", 15000, cargo=40, fuel_capacity=150, attack=18, defense=15),
    Ship("Battleship", 20000, cargo=50, fuel_capacity=170, attack=22, defense=18),
    Ship("Carrier", 25000, cargo=60, fuel_capacity=180, attack=20, defense=20),
    Ship("Dreadnought", 30000, cargo=70, fuel_capacity=200, attack=25, defense=25),
    Ship("Science Vessel", 12000, cargo=35, fuel_capacity=140, attack=8, defense=10),
    Ship("Miner", 8000, cargo=80, fuel_capacity=130, attack=5, defense=7),
]

