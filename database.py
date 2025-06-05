import sqlite3
import hashlib
from typing import Dict

from models import Player, Sector, ships

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
    c.execute(
        '''CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )'''
    )
    c.execute(
        '''CREATE TABLE IF NOT EXISTS sectors (
            id INTEGER PRIMARY KEY,
            connections TEXT NOT NULL
        )'''
    )
    c.execute('SELECT COUNT(*) FROM admins')
    if c.fetchone()[0] == 0:
        c.execute(
            'INSERT INTO admins (name, password) VALUES (?, ?)',
            ('admin', hash_password('admin')),
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


def save_sectors(sectors: Dict[int, Sector]):
    """Store sectors and their connections in the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM sectors')
    for sector in sectors.values():
        conns = ','.join(str(n) for n in sector.connections)
        c.execute('INSERT INTO sectors (id, connections) VALUES (?, ?)', (sector.id, conns))
    conn.commit()
    conn.close()


def load_sectors() -> Dict[int, Sector]:
    """Load sectors from the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, connections FROM sectors')
    rows = c.fetchall()
    conn.close()
    sectors: Dict[int, Sector] = {}
    for row in rows:
        connections = [int(x) for x in row[1].split(',')] if row[1] else []
        sectors[row[0]] = Sector(id=row[0], connections=connections)
    return sectors


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


def verify_admin_credentials(name: str, password: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT password FROM admins WHERE name=?', (name,))
    row = c.fetchone()
    conn.close()
    return bool(row) and row[0] == hash_password(password)

def reset_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS players')
    c.execute('DROP TABLE IF EXISTS admins')
    c.execute('DROP TABLE IF EXISTS sectors')
    conn.commit()
    conn.close()
    init_db()
