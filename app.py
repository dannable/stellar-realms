from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import GameMap, Player, ships
import random

app = Flask(__name__)
app.secret_key = 'change-me'

ADMIN_PASSWORD = 'admin'

game_map = GameMap()
players = {}
next_player_id = 1

# admin login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_view'))
        return 'Invalid password', 403
    return render_template('admin_login.html')

# admin route to reset game
@app.route('/admin/reset')
def admin_reset():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    global game_map, players, next_player_id
    game_map = GameMap()
    players = {}
    next_player_id = 1
    return 'Game reset.'

# admin interface simple view
@app.route('/admin')
def admin_view():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin.html', players=players.values())

# register new player
@app.route('/register', methods=['POST'])
def register():
    global next_player_id
    name = request.form.get('name')
    password = request.form.get('password')
    stats = {
        'iron': int(request.form.get('iron', 1)),
        'heart': int(request.form.get('heart', 1)),
        'edge': int(request.form.get('edge', 1)),
        'shadow': int(request.form.get('shadow', 1)),
        'wits': int(request.form.get('wits', 1)),
    }
    ship = ships[0]
    p = Player(id=next_player_id, name=name, sector_id=0, ship=ship,
               password_hash=generate_password_hash(password),
               credits=1000, fuel=ship.fuel_capacity,
               iron=stats['iron'], heart=stats['heart'], edge=stats['edge'],
               shadow=stats['shadow'], wits=stats['wits'])
    players[next_player_id] = p
    session['player_id'] = next_player_id
    next_player_id += 1
    return redirect(url_for('index'))

# player login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        for p in players.values():
            if p.name == name and check_password_hash(p.password_hash, password):
                session['player_id'] = p.id
                return redirect(url_for('index'))
        return 'Invalid credentials', 403
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('player_id', None)
    session.pop('admin', None)
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
    current = players.get(session.get('player_id'))
    return render_template('index.html', players=players.values(),
                           game_map=game_map, current_player=current)

if __name__ == '__main__':
    app.run(debug=True)
