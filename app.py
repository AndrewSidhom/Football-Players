from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, jsonify
from db import db
from models import Player, Team, Fixture, Event
from utilities import call_api


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///footballPlayers.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route("/")
def home():
    return render_template("matches_dashboard.html")


@app.route("/players/", methods=["GET"])
def players():
    all_players = Player.query.all()  # get all players from db, pass them to template
                                        # (just player name, id & team name, id)
    data = []
    for player in all_players:
        data.append({"id": player.id, "name": player.name, "team_name": player.team.name})
    return render_template("players.html", players=data)


@app.route("/players/", methods=["POST"])
def add_player():
    team_id = request.json["team_id"]
    player_id = request.json["player_id"]
    # call api to get team info, add to db, call api to get player info, add to db, return json


@app.route("/players/<player_id>", methods=["DELETE"])
def remove_player(player_id):
    player = Player.query.filter_by(id=player_id)
    if player:
        player.delete()
        db.session.commit()
        if Player.query.filter_by(id=player_id).first():
            return jsonify({"status": 1, "message": "Player was not successfully removed",
                            "data": {"player_id": player_id}})
        else:
            return jsonify({"status": 2, "message": "Player was successfully removed",
                            "data": {"player_id": player_id}})
    else:
        return jsonify({"status": 3, "message": "No player with this id",
                        "data": {"player_id": player_id}})
    # TODO: update status codes, and in js the afterRemovePlayer function


@app.route("/test_add_player/", methods=["GET"])  # args: id, name
def test_add_player():
    player_id = int(request.args.get("id"))
    player_name = request.args.get("name")
    team_id = 1
    team_name = "Liverpool"
    if not Team.query.filter_by(id=team_id).first():
        team = Team(team_id, team_name)
        db.session.add(team)
    if not Player.query.filter_by(id=player_id).first():
        player = Player(player_id, player_name, team_id)
        db.session.add(player)
    db.session.commit()
    return render_template("message.html", message="Done")


if __name__ == "__main__":
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run()
