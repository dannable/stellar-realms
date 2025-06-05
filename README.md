# Stellar Realms

This is a simple prototype for a browser based multiplayer space trading game inspired by the classic Trade Wars 2002.

## Running

Install dependencies and start the development server:

```bash
pip install flask
python app.py
```

Then open `http://localhost:5000` in your browser.

Players are stored in an SQLite database `stellar_realms.db`. New players
register with a password and can log in using the form on the front page.

An administrator account is created automatically with username `admin` and
password `admin`. Access the admin interface via `/admin/login` and use those
credentials to log in. Only authenticated admin users can view the admin
dashboard or reset the game.
