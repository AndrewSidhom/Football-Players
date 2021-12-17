import datetime
import requests

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, make_response, url_for
from db import db
from models import Player, Team, Fixture, Event
from utilities import call_api


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///footballPlayers.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route("/")
def home():
    return render_template("matches_dashboard.html")


# get all teams from db, return json
@app.route("/teams/", methods=["GET"])
def teams():
    all_teams = Team.query.all()
    teams_list = []
    for team in all_teams:
        teams_list.append({"id": team.id_, "name": team.name, "country": team.country})
    return make_response({"data": {"teams": teams_list}}, 200)


@app.route("/teams/search", methods=["GET"])
def search_for_team():
    name = request.args.get("name")
    api_response, api_calls_remaining = call_api('teams?search=' + name)
    status_code = api_response.status_code
    if status_code == 200:
        json_data = api_response.json()['response']
        payload = []
        for result in json_data:
            payload.append({key: result['team'][key] for key in ("id", "name", "country")})
        return make_response({"result": "Success!",
                              "detail": "-",
                              "data": payload}
                             , 200)
    else:
        return make_response({"result": "Failed!",
                              "detail": "The external API did not respond correctly.",
                              "api_calls_remaining": api_calls_remaining}
                             , status_code)


# get all players from db, pass them to template
@app.route("/players/", methods=["GET"])
def players():
    all_players = Player.query.all()
    players_list = []
    for player in all_players:
        players_list.append({"id": player.id_, "name": player.name, "team_name": player.team.name, "photo": player.photo})
    return render_template("players.html", players=players_list)


# adds the player and his team
# expected data: player_id, team_id
@app.route("/players/", methods=["PUT"])
def add_player():
    try:
        player_id_to_add = request.json["player_id"]
        team_id_to_add = request.json["team_id"]
        player_id_to_add = int(player_id_to_add)
        team_id_to_add = int(team_id_to_add)
    except (ValueError, KeyError):
        return make_response({"result": "Failed!",
                              "detail": "Client sent missing or invalid data (player_id, team_id)."}
                             , 400)
    if not Team.query.filter_by(id_=team_id_to_add).first():
        api_response, api_calls_remaining = call_api('teams?id=' + str(team_id_to_add))
        status_code = api_response.status_code
        if status_code == 200:
            team_info = api_response.json()['response'][0]['team']
            team = Team(team_info['id'], team_info['name'], team_info['country'], team_info['logo'])
            db.session.add(team)
        else:
            return make_response({"result": "Failed!",
                                  "detail": "The external API did not respond correctly.",
                                  "api_calls_remaining": api_calls_remaining}
                                 , status_code)
    if not Player.query.filter_by(id_=player_id_to_add).first():
        api_response, api_calls_remaining = call_api('players?id=' + str(player_id_to_add)
                                                     + '&season=' + str(datetime.date.today().year))
        status_code = api_response.status_code
        if status_code == 200:
            json_response = api_response.json()['response'][0]
            player_info = json_response['player']
            player_stats = json_response['statistics'][0]
            id_ = player_info['id']
            name = player_info['name']
            birthdate = datetime.datetime.strptime(player_info['birth']['date'], "%Y-%m-%d").date()
            nationality = player_info['nationality']
            injured = player_info['injured']
            photo = player_info['photo']
            team_id = player_stats['team']['id']
            if team_id != team_id_to_add:
                return make_response({"result": "Failed!",
                                     "detail": "The player and his team which the client requested to add are "
                                               "inconsistent. This player does not play for this team.",
                                      "api_calls_remaining": api_calls_remaining}
                                     , 404)
            player = Player(id_, name, birthdate, nationality, injured, photo, team_id)
            db.session.add(player)
        else:
            return make_response({"result": "Failed!",
                                  "detail": "The external API did not respond correctly.",
                                  "api_calls_remaining": api_calls_remaining}
                                 , status_code)
    db.session.commit()
    return make_response({"result": "Success!",
                          "detail": "The player and his team were added.",
                          "api_calls_remaining": api_calls_remaining}
                         , 200)


@app.route("/players/<int:player_id>", methods=["DELETE"])
def remove_player(player_id):
    player = Player.query.filter_by(id_=player_id).first()
    if player:
        db.session.delete(player)
        db.session.commit()
        if Player.query.filter_by(id_=player_id).first():
            return make_response({"result": "Failed!",
                                  "detail": "Could not remove the player due to a server-side issue.",
                                  "data": {"player_id": player_id}}, 500)
        else:
            return make_response({"result": "Success!",
                                  "detail": "Player was removed.",
                                  "data": {"player_id": player_id}}, 200)
    else:
        return make_response({"result": "Failed!",
                              "detail": "Attempt by client to remove a player with an id that does not exist. "
                                        "Try to refresh the page.",
                              "data": {"player_id": player_id}}, 404)


@app.route("/players/search", methods=["GET"])
def search_for_player():
    team_id = request.args.get("team_id")
    player_name = request.args.get("player_name")
    try:
        team_id = int(team_id)
    except ValueError:
        return make_response({"result": "Failed!",
                              "detail": "Client sent team_id in an incorrect format."}
                             , 400)
    api_response, api_calls_remaining = call_api('players?team=' + team_id + '&search=' + player_name)
    status_code = api_response.status_code
    if status_code == 200:
        json_data = api_response.json()['response']
        payload = []
        for result in json_data:
            payload.append({key: result['player'][key] for key in ("id", "name", "nationality")})
        return make_response({"result": "Success!",
                              "detail": "-",
                              "data": payload}
                             , 200)
    else:
        return make_response({"result": "Failed!",
                              "detail": "The external API did not respond correctly.",
                              "api_calls_remaining": api_calls_remaining}
                             , status_code)

@app.route("/test_add_player_to_db/", methods=["GET"])  # args: id, name
def test_add_player_to_db():
    player_id = int(request.args.get("id"))
    player_name = request.args.get("name")
    team_id = 1
    team_name = "Liverpool"
    if not Team.query.filter_by(id_=team_id).first():
        team = Team(team_id, team_name, "England", "...")
        db.session.add(team)
    if not Player.query.filter_by(id_=player_id).first():
        player = Player(player_id, player_name, datetime.date(year=1990, month=7, day=26), "Egypt", False, "...", team_id)
        db.session.add(player)
    db.session.commit()
    return render_template("message.html", message="Done")


@app.route("/test_add_player_from_api/", methods=["GET"])  # args: player_id, team_id
def test_add_player_from_api():
    player_id = request.args.get("player_id")
    team_id = request.args.get("team_id")
    response = requests.request("PUT", url_for("add_player", _external=True),
                                json={"player_id": player_id, "team_id": team_id})
    message = "Status Code: " + str(response.status_code) + "\nResult: " + response.json()['result'] + "\nDetail: " \
              + response.json()['detail']
    return render_template("message.html", message=message)


if __name__ == "__main__":
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
