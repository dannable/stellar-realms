from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import GameMap, Player, ships
import random
from database import (
    init_db,
    load_players,
    create_player,
    update_player,
    verify_credentials,
    reset_db,
)

app = Flask(__name__)

game_map = GameMap()
init_db()
players = load_players()

# admin route to reset game
@app.route('/admin/reset')
def admin_reset():
    global game_map, players
    game_map = GameMap()
    reset_db()
    players = {}
    return 'Game reset.'

# admin interface simple view
@app.route('/admin')
def admin_view():
    return render_template('admin.html', players=players.values())

# register new player
@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    password = request.form.get('password', '')
    stats = {
        'iron': int(request.form.get('iron', 1)),
        'heart': int(request.form.get('heart', 1)),
        'edge': int(request.form.get('edge', 1)),
        'shadow': int(request.form.get('shadow', 1)),
        'wits': int(request.form.get('wits', 1)),
    }
    ship = ships[0]
    new_id = create_player(name, password, stats, ship_index=0)
    p = Player(id=new_id, name=name, sector_id=0, ship=ship,
               credits=1000, fuel=ship.fuel_capacity,
               iron=stats['iron'], heart=stats['heart'], edge=stats['edge'],
               shadow=stats['shadow'], wits=stats['wits'])
    players[new_id] = p
    return redirect(url_for('index'))

# login existing player
@app.route('/login', methods=['POST'])
def login():
    name = request.form.get('name')
    password = request.form.get('password', '')
    player = verify_credentials(name, password)
    if player:
        players[player.id] = player
        return redirect(url_for('index'))
    return 'Invalid credentials', 401

# move player to sector
@app.route('/move/<int:player_id>/<int:dest>', methods=['POST'])
def move(player_id, dest):
    player = players.get(player_id)
    if not player:
        return 'Player not found', 404
    if dest not in game_map.sectors[player.sector_id].connections:
        return 'Invalid move', 400
    distance = 1
    if player.fuel < distance:
        return 'Out of fuel', 400
    player.fuel -= distance
    player.sector_id = dest
    update_player(player)
    return 'Moved'

@app.route('/')
def index():
    global players
    players = load_players()
    return render_template('index.html', players=players.values(), game_map=game_map)

if __name__ == '__main__':
    app.run(debug=True)
