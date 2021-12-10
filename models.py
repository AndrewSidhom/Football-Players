from db import db


class Player(db.Model):
    id_ = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    birthdate = db.Column(db.Date)
    nationality = db.Column(db.String(50))
    injured = db.Column(db.Boolean)
    photo = db.Column(db.String(100))
    team_id = db.Column(db.Integer, db.ForeignKey("team.id_"), nullable=False)
    team = db.relationship("Team", backref=db.backref("players", lazy=True))

    def __init__(self, id_, name, birthdate, nationality, injured, photo, team_id):
        self.id_ = id_
        self.name = name
        self.birthdate = birthdate
        self.nationality = nationality
        self.injured = injured
        self.photo = photo
        self.team_id = team_id


class Team(db.Model):
    id_ = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    country = db.Column(db.String(50))
    logo = db.Column(db.String(100))

    def __init__(self, id_, name, country, logo):
        self.id_ = id_
        self.name = name
        self.country = country
        self.logo = logo


class Fixture(db.Model):
    id_ = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey("team.id_"), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey("team.id_"), nullable=False)
    team = db.relationship("Team", primaryjoin="or_(Fixture.home_team_id==Team.id_, Fixture.away_team_id==Team.id_)",
                           backref=db.backref("fixtures", lazy=True))
    datetime = db.Column(db.DateTime)
    status = db.Column(db.String(25))  # "BeforeLineups , "LineupsIn", "FT"

    def __init__(self, id_, home_team_id, away_team_id, datetime, status):
        self.id_ = id_
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        self.datetime = datetime
        self.status = status


class Event(db.Model):
    id_ = db.Column(db.Integer, primary_key=True)
    fixture_id = db.Column(db.Integer, db.ForeignKey("fixture.id_"), nullable=False)
    fixture = db.relationship("Fixture", backref=db.backref("events", lazy=True))
    player_id = db.Column(db.Integer, db.ForeignKey("player.id_"), nullable=False)
    player = db.relationship("Player")
    minute = db.Column(db.Integer)
    event_type = db.Column(db.String(10))  # "LineupsIn" (added manually), "Goal", "Card",
                                           # "Subst"(substs out added manually), "Var"
    event_detail = db.Column(db.String(50))  # For LineupsIn: "XI", "Bench", "Out", "Unknown"
                                             # For Subst (detail overwritten manually): "In: player1, Out: player2"

    def __init__(self, id_, fixture_id, player_id, minute, event_type, event_detail):
        self.id_ = id_
        self.fixture_id = fixture_id
        self.player_id = player_id
        self.minute = minute
        self.event_type = event_type
        self.event_detail = event_detail
