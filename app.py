import os
import random
from functools import wraps
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from models import GameMap, Player, ships
from database import (
    create_player,
    init_db,
    load_players,
    reset_db,
    update_player,
    verify_admin_credentials,
    verify_credentials,
)


def create_app() -> Flask:
    """Application factory for Flask."""
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "change-me")

    # Initialize game state and database
    app.game_map = GameMap()
    init_db()
    app.players = load_players()

    register_routes(app)
    return app


def admin_required(func):
    """Decorator to restrict routes to logged-in admin users."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return func(*args, **kwargs)

    return wrapper

def register_routes(app: Flask) -> None:
    """Register all routes on the given app."""

    @app.route("/admin/reset")
    @admin_required
    def admin_reset():
        app.game_map = GameMap()
        reset_db()
        app.players = {}
        return "Game reset."

    @app.route("/admin")
    @admin_required
    def admin_view():
        return render_template("admin.html", players=app.players.values())

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "POST":
            name = request.form.get("name")
            password = request.form.get("password", "")
            if verify_admin_credentials(name, password):
                session["admin"] = name
                return redirect(url_for("admin_view"))
            return "Invalid credentials", 401
        return render_template("admin_login.html")

    @app.route("/admin/logout")
    def admin_logout():
        session.pop("admin", None)
        return redirect(url_for("index"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name = request.form.get("name")
            password = request.form.get("password", "")
            stats = {
                "iron": int(request.form.get("iron", 1)),
                "heart": int(request.form.get("heart", 1)),
                "edge": int(request.form.get("edge", 1)),
                "shadow": int(request.form.get("shadow", 1)),
                "wits": int(request.form.get("wits", 1)),
            }
            ship = ships[0]
            start_sector = random.choice(list(app.game_map.sectors.keys()))
            new_id = create_player(name, password, stats, ship_index=0, sector_id=start_sector)
            p = Player(
                id=new_id,
                name=name,
                sector_id=start_sector,
                ship=ship,
                credits=1000,
                fuel=ship.fuel_capacity,
                upgrades=[],
                cargo={},
                iron=stats["iron"],
                heart=stats["heart"],
                edge=stats["edge"],
                shadow=stats["shadow"],
                wits=stats["wits"],
            )
            app.players[new_id] = p
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            name = request.form.get("name")
            password = request.form.get("password", "")
            player = verify_credentials(name, password)
            if player:
                app.players[player.id] = player
                session["player_id"] = player.id
                return redirect(url_for("index"))
            return "Invalid credentials", 401
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.pop("player_id", None)
        return redirect(url_for("index"))

    @app.route("/move/<int:player_id>/<int:dest>", methods=["POST"])
    def move(player_id: int, dest: int):
        player = app.players.get(player_id)
        if not player:
            return "Player not found", 404
        if dest not in app.game_map.sectors[player.sector_id].connections:
            return "Invalid move", 400
        distance = 1
        if player.fuel < distance:
            return "Out of fuel", 400
        player.fuel -= distance
        player.sector_id = dest
        update_player(player)
        return "Moved"

    @app.route("/")
    def index():
        app.players = load_players()
        return render_template(
            "index.html", players=app.players.values(), game_map=app.game_map
        )


if __name__ == "__main__":
    create_app().run(debug=True)
