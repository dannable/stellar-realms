import sqlite3
import hashlib
from typing import Dict

from models import Player, ships

DB_PATH = 'stellar_realms.db'


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            sector_id INTEGER NOT NULL,
            ship_index INTEGER NOT NULL,
            credits INTEGER NOT NULL,
            fuel INTEGER NOT NULL,
            iron INTEGER NOT NULL,
            heart INTEGER NOT NULL,
            edge INTEGER NOT NULL,
            shadow INTEGER NOT NULL,
            wits INTEGER NOT NULL
        )'''
    )
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_player(name: str, password: str, stats: Dict[str, int], ship_index: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        'INSERT INTO players (name, password, sector_id, ship_index, credits, fuel, iron, heart, edge, shadow, wits) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (
            name,
            hash_password(password),
            0,
            ship_index,
            1000,
            ships[ship_index].fuel_capacity,
            stats['iron'],
            stats['heart'],
            stats['edge'],
            stats['shadow'],
            stats['wits'],
        )
    )
    player_id = c.lastrowid
    conn.commit()
    conn.close()
    return player_id


def load_players() -> Dict[int, Player]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, sector_id, ship_index, credits, fuel, iron, heart, edge, shadow, wits FROM players')
    rows = c.fetchall()
    conn.close()
    players: Dict[int, Player] = {}
    for row in rows:
        ship = ships[row[3]]
        p = Player(
            id=row[0],
            name=row[1],
            sector_id=row[2],
            ship=ship,
            credits=row[4],
            fuel=row[5],
            iron=row[6],
            heart=row[7],
            edge=row[8],
            shadow=row[9],
            wits=row[10],
        )
        players[p.id] = p
    return players


def update_player(player: Player):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    ship_index = ships.index(player.ship)
    c.execute(
        'UPDATE players SET sector_id=?, ship_index=?, credits=?, fuel=?, iron=?, heart=?, edge=?, shadow=?, wits=? WHERE id=?',
        (
            player.sector_id,
            ship_index,
            player.credits,
            player.fuel,
            player.iron,
            player.heart,
            player.edge,
            player.shadow,
            player.wits,
            player.id,
        )
    )
    conn.commit()
    conn.close()


def verify_credentials(name: str, password: str) -> Player | None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, sector_id, ship_index, credits, fuel, iron, heart, edge, shadow, wits, password FROM players WHERE name=?', (name,))
    row = c.fetchone()
    conn.close()
    if row and row[-1] == hash_password(password):
        ship = ships[row[3]]
        return Player(
            id=row[0],
            name=row[1],
            sector_id=row[2],
            ship=ship,
            credits=row[4],
            fuel=row[5],
            iron=row[6],
            heart=row[7],
            edge=row[8],
            shadow=row[9],
            wits=row[10],
        )
    return None

def reset_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS players')
    conn.commit()
    conn.close()
    init_db()
