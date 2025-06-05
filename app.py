from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import GameMap, Player, ships
import random

app = Flask(__name__)

game_map = GameMap()
players = {}
next_player_id = 1

# admin route to reset game
@app.route('/admin/reset')
def admin_reset():
    global game_map, players, next_player_id
    game_map = GameMap()
    players = {}
    next_player_id = 1
    return 'Game reset.'

# admin interface simple view
@app.route('/admin')
def admin_view():
    return render_template('admin.html', players=players.values())

# register new player
@app.route('/register', methods=['POST'])
def register():
    global next_player_id
    name = request.form.get('name')
    stats = {
        'iron': int(request.form.get('iron', 1)),
        'heart': int(request.form.get('heart', 1)),
        'edge': int(request.form.get('edge', 1)),
        'shadow': int(request.form.get('shadow', 1)),
        'wits': int(request.form.get('wits', 1)),
    }
    ship = ships[0]
    p = Player(id=next_player_id, name=name, sector_id=0, ship=ship,
               credits=1000, fuel=ship.fuel_capacity,
               iron=stats['iron'], heart=stats['heart'], edge=stats['edge'],
               shadow=stats['shadow'], wits=stats['wits'])
    players[next_player_id] = p
    next_player_id += 1
    return redirect(url_for('index'))

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
    return 'Moved'

@app.route('/')
def index():
    return render_template('index.html', players=players.values(), game_map=game_map)

if __name__ == '__main__':
    app.run(debug=True)
