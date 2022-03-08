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


#####################################################################################################################
# TEAMS #
###########

# get all teams from db, return json
@app.route("/teams/", methods=["GET"])
def teams():
    all_teams = Team.query.all()
    teams_list = []
    for team in all_teams:
        teams_list.append({"id": team.id_, "name": team.name, "country": team.country})
    return make_response({"data": {"teams": teams_list}}, 200)


@app.route("/teams/", methods=["PUT"])
def add_team(team_id):
    if Team.query.filter_by(id_=team_id).first():  # if team is already in our database
        return make_response({"result": "Info!",
                              "detail": "The team already existed in the database.",
                              "api_calls_remaining": None}
                             , 200)
    else:  # look up the team and attempt to add it
        api_response, api_calls_remaining = call_api('teams?id=' + str(team_id))
        status_code = api_response.status_code
        json_response = api_response.json()
        if status_code != 200 or json_response["errors"]:
            if json_response["errors"]:
                status_code = 502
            return make_response({"result": "Failed!",
                                  "detail": "The external API did not respond correctly.",
                                  "api_calls_remaining": api_calls_remaining}
                                 , status_code)
        else:
            team_info = api_response.json()['response'][0]['team']
            team = Team(team_info['id'], team_info['name'], team_info['country'], team_info['logo'])
            db.session.add(team)
            db.session.commit()
            return make_response({"result": "Success!",
                                  "detail": "The team was added.",
                                  "api_calls_remaining": api_calls_remaining}
                                 , 200)


@app.route("/teams/search", methods=["GET"])
def search_for_team():
    name = request.args.get("name")
    api_response, api_calls_remaining = call_api('teams?search=' + name)
    status_code = api_response.status_code
    json_response = api_response.json()
    if status_code != 200 or json_response["errors"]:
        if json_response["errors"]:
            status_code = 502
        return make_response({"result": "Failed!",
                              "detail": "The external API did not respond correctly.",
                              "api_calls_remaining": api_calls_remaining}
                             , status_code)
    else:
        json_data = api_response.json()['response']
        teams_list = []
        for result in json_data:
            teams_list.append({key: result['team'][key] for key in ("id", "name", "country")})
        return make_response({"result": "Success!",
                              "detail": "-",
                              "data": {"teams": teams_list},
                              "api_calls_remaining": api_calls_remaining}
                             , 200)

#####################################################################################################################
# PLAYERS #
###########


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
        player_id_to_add = int(request.json["player_id"])
        team_id_to_add = int(request.json["team_id"])
    except (ValueError, KeyError):
        return make_response({"result": "Failed!",
                              "detail": "Client sent missing or invalid data (player_id, team_id).",
                              "api_calls_remaining": None}
                             , 400)
    response = add_team(team_id_to_add)  # a Flask Response object, not a Requests response object
    if response.status_code != 200 or response.get_json()["result"] not in ["Success!", "Info!"]:
        return response
    else:  # team was successfully added or already existed
        if Player.query.filter_by(id_=player_id_to_add).first():
            return make_response({"result": "Info!",
                                  "detail": "The player already existed in the database.",
                                  "api_calls_remaining": response.get_json()["api_calls_remaining"]}
                                 , 200)
        else:  # team doesn't already exist in our db, look it up on API and attempt to add it
            api_response, api_calls_remaining = call_api('teams/seasons?team=' + str(team_id_to_add))
            current_season = max(api_response.json()['response'])
            api_response, api_calls_remaining = call_api('players?id=' + str(player_id_to_add)
                                                         + '&team=' + str(team_id_to_add)
                                                         + '&season=' + str(current_season))
            status_code = api_response.status_code
            json_response = api_response.json()
            if status_code != 200 or json_response["errors"]:
                if json_response["errors"]:
                    status_code = 502
                return make_response({"result": "Failed!",
                                      "detail": "The external API did not respond correctly.",
                                      "api_calls_remaining": api_calls_remaining}
                                     , status_code)
            else:
                json_response = api_response.json()['response']
                if not json_response:
                    return make_response({"result": "Failed!",
                                         "detail": "The player and his team which the client requested to add are "
                                                   "inconsistent. This player does not play for this team.",
                                          "api_calls_remaining": api_calls_remaining}
                                         , 404)
                else:
                    json_response = json_response[0]  # there's just one result because we uses the player id
                    player_info = json_response['player']
                    id_ = player_info['id']
                    name = player_info['name']
                    birthdate = datetime.datetime.strptime(player_info['birth']['date'], "%Y-%m-%d").date()
                    nationality = player_info['nationality']
                    injured = player_info['injured']
                    photo = player_info['photo']
                    player = Player(id_, name, birthdate, nationality, injured, photo, team_id_to_add)
                    db.session.add(player)
                    db.session.commit()
                    return make_response({"result": "Success!",
                                          "detail": "The player and his team were added.",
                                          "api_calls_remaining": api_calls_remaining}
                                         , 200)


@app.route("/players/<int:player_id>", methods=["DELETE"])
def remove_player(player_id):
    player = Player.query.filter_by(id_=player_id).first()
    if player:
        team = player.team
        db.session.delete(player)
        db.session.commit()
        if not team.players:  # if the player's team has no other players
            db.session.delete(team)
            db.session.commit()
        if Player.query.filter_by(id_=player_id).first():
            return make_response({"result": "Failed!",
                                  "detail": "Could not remove the player due to a server-side issue.",
                                  "data": {"player_id": player_id},
                                  "api_calls_remaining": None}
                                 , 500)
        else:
            return make_response({"result": "Success!",
                                  "detail": "Player was removed.",
                                  "data": {"player_id": player_id},
                                  "api_calls_remaining": None}
                                 , 200)
    else:
        return make_response({"result": "Failed!",
                              "detail": "Attempt by client to remove a player with an id that does not exist. "
                                        "Try to refresh the page.",
                              "data": {"player_id": player_id},
                              "api_calls_remaining": None}
                             , 404)


@app.route("/players/search", methods=["GET"])
def search_for_player():
    team_id = request.args.get("team_id")
    player_name = request.args.get("player_name")
    try:
        team_id = int(team_id)
    except ValueError:
        return make_response({"result": "Failed!",
                              "detail": "Client sent team_id in an incorrect format.",
                              "api_calls_remaining": None}
                             , 400)
    api_response, api_calls_remaining = call_api('players?team=' + str(team_id) + '&search=' + player_name)
    status_code = api_response.status_code
    json_response = api_response.json()
    if status_code != 200 or json_response["errors"]:
        if json_response["errors"]:
            status_code = 502
        return make_response({"result": "Failed!",
                              "detail": "The external API did not respond correctly.",
                              "api_calls_remaining": api_calls_remaining}
                             , status_code)
    else:
        json_data = api_response.json()['response']
        players_list = []
        for result in json_data:
            player = {key: result['player'][key] for key in ("id", "name", "nationality")}
            players_list.append(player)
        return make_response({"result": "Success!",
                              "detail": "-",
                              "data": {"players": players_list},
                              "api_calls_remaining": api_calls_remaining}
                             , 200)


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


#####################################################################################################################


if __name__ == "__main__":
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
