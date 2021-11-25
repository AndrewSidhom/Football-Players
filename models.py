from db import db


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=False)
    team = db.relationship("Team", backref=db.backref("players", lazy=True))

    def __init__(self, id, name, team_id):
        self.id = id
        self.name = name
        self.team_id = team_id


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __init__(self, id, name):
        self.id = id
        self.name = name


class Fixture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=False)
    team = db.relationship("Team", primaryjoin="or_(Fixture.home_team_id==Team.id, Fixture.away_team_id==Team.id)",
                           backref=db.backref("fixtures", lazy=True))
    date = db.Column(db.String(25))
    time = db.Column(db.String(25))
    status = db.Column(db.String(25))  # "BeforeLineups , "LineupsIn", "FT"

    def __init__(self, id, home_team_id, away_team_id, date, time, status):
        self.id = id
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        self.date = date
        self.time = time
        self.status = status


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fixture_id = db.Column(db.Integer, db.ForeignKey("fixture.id"), nullable=False)
    fixture = db.relationship("Fixture", backref=db.backref("events", lazy=True))
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    player = db.relationship("Player")
    minute = db.Column(db.Integer)
    event_type = db.Column(db.String(10))  # "LineupsIn" (added manually), "Goal", "Card",
                                           # "Subst"(substs out added manually), "Var"
    event_detail = db.Column(db.String(50))  # For LineupsIn: "XI", "Bench", "Out", "Unknown"
                                             # For Subst (detail overwritten manually): "In: player1, Out: player2"

    def __init__(self, id, fixture_id, player_id, minute, event_type, event_detail):
        self.id = id
        self.fixture_id = fixture_id
        self.player_id = player_id
        self.minute = minute
        self.event_type = event_type
        self.event_detail = event_detail
