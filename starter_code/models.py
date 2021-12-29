from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
# https://www.pythonpool.com/python-circular-import/ - circular import issue fix

# ----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    # missing fields: genres(array), website(string), seeking_talent(boolean), seeking_description(string)
    # past_shows(array of objects), upcoming_shows(array of objects), past_shows_count(integer), upcoming_shows_count(integer)
    genres = db.Column(db.String(500), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean(
        120), nullable=True, default=False)  # default false
    seeking_description = db.Column(db.String(500), nullable=True)  # nullable
    past_shows = db.Column(db.String(500), nullable=True)  # nullable
    upcoming_shows = db.Column(db.String(500), nullable=True)  # nullable
    past_shows_count = db.Column(db.Integer, nullable=True)
    upcoming_shows_count = db.Column(db.Integer, nullable=True)
    # DEVELOPER NOTE: uncertain how to implement arrays and arrays of objects so defined as strings until time for further research
    # parent to show table
    shows = db.relationship('Show', backref='Venue', lazy=True)
    # DONE: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    # missing fields: genres(array), website(string), seeking_venue(boolean), seeking_description(string),
    # past_shows(array of objects), upcoming_shows(array of objects), past_shows_count(integer), upcoming_shows_count(integer)
    genres = db.Column(db.String(500), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean(
        120), nullable=True, default=False)  # default false
    seeking_description = db.Column(db.String(500), nullable=True)  # nullable
    past_shows = db.Column(db.String(500), nullable=True)  # nullable
    upcoming_shows = db.Column(db.String(500), nullable=True)  # nullable
    past_shows_count = db.Column(db.Integer, nullable=True)
    upcoming_shows_count = db.Column(db.Integer, nullable=True)
    # parent to show table
    shows = db.relationship('Show', backref='Artist', lazy=True)
    # DONE: implement any missing fields, as a database migration using Flask-Migrate

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'Show'
    # fields: id (primary key), venue.id(foreign key), artist.id(foriegn key), start time(string)
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    start_time = db.Column(db.String, nullable=False)
