#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from sqlalchemy.sql.expression import distinct
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from dateutil import parser
import pytz
# from django.utils import timezone

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# DONE: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user1:1234@localhost:5432/fyyurapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'false'

migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # missing fields: genres(array), website(string), seeking_talent(boolean), seeking_description(string)
    # past_shows(array of objects), upcoming_shows(array of objects), past_shows_count(integer), upcoming_shows_count(integer)
    genres = db.Column(db.String(500))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(120))  # default false
    seeking_description = db.Column(db.String(500))  # nullable
    past_shows = db.Column(db.String(500))  # nullable
    upcoming_shows = db.Column(db.String(500))  # nullable
    past_shows_count = db.Column(db.Integer)  # default 0
    upcoming_shows_count = db.Column(db.Integer)  # default 0
    # DEVELOPER NOTE: uncertain how to implement arrays and arrays of objects so defined as strings until time for further research
    # parent to show table
    shows = db.relationship('Show', backref='Venue', lazy=True)
    # DONE: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # missing fields: genres(array), website(string), seeking_venue(boolean), seeking_description(string),
    # past_shows(array of objects), upcoming_shows(array of objects), past_shows_count(integer), upcoming_shows_count(integer)
    genres = db.Column(db.String(500))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(120))  # default false
    seeking_description = db.Column(db.String(500))  # nullable
    past_shows = db.Column(db.String(500))  # nullable
    upcoming_shows = db.Column(db.String(500))  # nullable
    past_shows_count = db.Column(db.Integer)  # default 0
    upcoming_shows_count = db.Column(db.Integer)  # default 0
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
    start_time = db.Column(db.String)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # DONE: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    # data required: venue.city, venue.state, venue.id, venue.name, venue.upcoming shows

    data = []
    try:
        venue_areas = db.session.query(distinct(Venue.city), Venue.state).all()
        # print(venue_areas)

        for area in venue_areas:
            venue_list_data = db.session.query(Venue.id, Venue.name, Venue.upcoming_shows_count).filter(
                Venue.city == area[0], Venue.state == area[1])

            data.append({
                "city": area[0],
                "state": area[1],
                "venues": venue_list_data
            })

    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        return render_template('pages/venues.html', areas=data)


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    # case-insensitive - ilike
    response = {}
    data = []
    search_item = request.form.get("search_term")
    # print(search_item)
    try:
        venue_query_results = db.session.query(Venue.name, Venue.id, Venue.upcoming_shows_count).filter(
            Venue.name.ilike('%' + search_item + '%')).all()
        count_upcoming_venues = len(venue_query_results)
        # print('count', count_upcoming_shows)
        # print(venue_query_results)

        for venue in venue_query_results:

            # Acquire num upcoming shows
            past_shows_list = db.session.query(
                Show).filter(venue.id == Show.venue_id)
            show_list = []
            upcoming_shows = []
            for past_show in past_shows_list:
                if (parser.parse(past_show.start_time) > pytz.utc.localize(datetime.now())):
                    upcoming_shows.append(show_list)

            # print(venue.id)
            # print(venue.name)
            data.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(upcoming_shows)
            })

            response = {
                "count": count_upcoming_venues,
                "data": data
            }
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id
    # chosen_venue = db.session.query(Venue).filter(Venue.id == venue_id).all()
    chosen_venue = db.session.query(Venue).filter(Venue.id == venue_id)
    # print(chosen_venue)
    try:
        for venue_attribute in chosen_venue:
            # print(venue_attribute)
            past_shows_list = db.session.query(
                Show).filter(venue_id == Show.venue_id)

            past_shows = []
            upcoming_shows = []
            for past_show in past_shows_list:
                # print('id', past_show.artist_id)
                past_show_artist = db.session.query(Artist.name, Artist.image_link).filter(
                    past_show.artist_id == Artist.id).first()
                # print(past_show_artist.name)

                show_list = {
                    "artist_id": past_show.artist_id,
                    "artist_name": past_show_artist.name,
                    "artist_image_link": past_show_artist.image_link,
                    "start_time": past_show.start_time
                }

                if (parser.parse(past_show.start_time) < pytz.utc.localize(datetime.now())):
                    past_shows.append(show_list)
                    # print(past_shows)
                else:
                    upcoming_shows.append(show_list)
                    # print(upcoming_shows)

            data = {
                "id": venue_attribute.id,
                "name": venue_attribute.name,
                "genres": venue_attribute.genres,
                "address": venue_attribute.address,
                "city": venue_attribute.city,
                "state": venue_attribute.state,
                "phone": venue_attribute.phone,
                "website": venue_attribute.website,
                "facebook_link": venue_attribute.facebook_link,
                "seeking_talent": venue_attribute.seeking_talent,
                "seeking_description": venue_attribute.seeking_description,
                "image_link": venue_attribute.image_link,
                "past_shows": past_shows,
                "upcoming_shows": upcoming_shows,
                "past_shows_count": len(past_shows),
                "upcoming_shows_count": len(upcoming_shows),
            }
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        address = request.form.get('address')
        phone = request.form.get('phone')
        image_link = request.form.get('image_link')
        facebook_link = request.form.get('facebook_link')
        genres = request.form.getlist('genres')
        website = request.form.get('website')
        seeking_talent = request.form.get('seeking_talent')
        seeking_description = request.form.get('seeking_description')

        new_venue_listing = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            image_link=image_link,
            facebook_link=facebook_link,
            genres=', '.join(genres),
            website=website,
            seeking_talent=bool(seeking_talent),
            seeking_description=seeking_description,
        )
        print(new_venue_listing.name)
        print(new_venue_listing.genres)
        print(new_venue_listing)
        # then 'try' to add to sessions and 'flash' success
        db.session.add(new_venue_listing)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        # then 'except' rollback
        # DONE: on unsuccessful db insert, flash an error instead. - modify 'flash' for unsuccessful
    except:
        db.session.rollback()
        print(sys.exc_info())
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Venue ' +
              request.form['name'] + ' unfortuntely could not be listed.')
    # then finally close session
    finally:
        db.session.close()
        # the return
        return render_template('pages/home.html')


@ app.route('/venues/<int:venue_id>/delete', methods=['GET', 'DELETE'])
def delete_venue(venue_id):
    # DONE: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    # query = Task.query.filter_by(category='Archived')
    # query.delete()

    try:
        venue_to_delete = db.session.query(
            Venue).filter(Venue.id == venue_id)
        venue_to_delete.delete()
        db.session.commit()
        flash('Venue was successfully deleted!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue unfortuntely could not be listed.')
    finally:
        db.session.close()
        return render_template('pages/home.html')
# BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
# clicking that button delete it from the db then redirect the user to the homepage
#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    # DONE: replace with real data returned from querying the database
    data = []
    try:
        artists_listed = db.session.query(Artist).all()
        print(artists_listed)

        for artists in artists_listed:
            data.append({
                "id": artists.id,
                "name": artists.name
            })
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {}
    data = []
    search_item = request.form.get("search_term")
    # print(search_item)
    try:
        artist_query_results = db.session.query(Artist.name, Artist.id, Artist.upcoming_shows_count).filter(
            Artist.name.ilike('%' + search_item + '%')).all()
        count_upcoming_artist = len(artist_query_results)
        # print('count', count_upcoming_shows)
        # print(artist_query_results)
        for artist in artist_query_results:

            # Acquire num upcoming shows
            past_shows_list = db.session.query(
                Show).filter(artist.id == Show.artist_id)
            show_list = []
            upcoming_shows = []
            for past_show in past_shows_list:
                if (parser.parse(past_show.start_time) > pytz.utc.localize(datetime.now())):
                    upcoming_shows.append(show_list)

            # print(len(upcoming_shows))
            data.append({
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": len(upcoming_shows)
            })

            response = {
                "count": count_upcoming_artist,
                "data": data
            }
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # DONE: replace with real artist data from the artist table, using artist_id

    chosen_artist = db.session.query(Artist).filter(Artist.id == artist_id)
    # print(chosen_venue)
    try:
        for artist_attribute in chosen_artist:
            # print(venue_attribute)
            past_shows_list = db.session.query(
                Show).filter(artist_id == Show.artist_id)

            past_shows = []
            upcoming_shows = []
            for past_show in past_shows_list:
                # print('id', past_show.artist_id)
                past_show_venue = db.session.query(Venue.name, Venue.image_link).filter(
                    past_show.venue_id == Venue.id).first()
                # print(past_show_artist.name)

                show_list = {
                    "venue_id": past_show.venue_id,
                    "venue_name": past_show_venue.name,
                    "venue_image_link": past_show_venue.image_link,
                    "start_time": past_show.start_time
                }

                if (parser.parse(past_show.start_time) < pytz.utc.localize(datetime.now())):
                    past_shows.append(show_list)
                    # print(past_shows)
                else:
                    upcoming_shows.append(show_list)
                    # print(upcoming_shows)

            data = {
                "id": artist_attribute.id,
                "name": artist_attribute.name,
                "genres": artist_attribute.genres,
                "city": artist_attribute.city,
                "state": artist_attribute.state,
                "phone": artist_attribute.phone,
                "website": artist_attribute.website,
                "facebook_link": artist_attribute.facebook_link,
                "seeking_venue": artist_attribute.seeking_venue,
                "seeking_description": artist_attribute.seeking_description,
                "image_link": artist_attribute.image_link,
                "past_shows": past_shows,
                "upcoming_shows": upcoming_shows,
                "past_shows_count": len(past_shows),
                "upcoming_shows_count": len(upcoming_shows),
            }
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {}
    try:
        artist_selected = Artist.query.get(artist_id)
        # print(artist_selected)
        # print(artist_selected.name)

        artist = {
            "id": artist_selected.id,
            "name": artist_selected.name,
            "genres": artist_selected.genres,
            "city": artist_selected.city,
            "state": artist_selected.state,
            "phone": artist_selected.phone,
            "website": artist_selected.website,
            "facebook_link": artist_selected.facebook_link,
            "seeking_venue": artist_selected.seeking_venue,
            "seeking_description": artist_selected.seeking_description,
            "image_link": artist_selected.image_link,
        }

        form.name.data = artist_selected.name
        form.genres.data = artist_selected.genres
        form.city.data = artist_selected.city
        form.state.data = artist_selected.state
        form.phone.data = artist_selected.phone
        form.website_link.data = artist_selected.website
        form.facebook_link.data = artist_selected.facebook_link
        form.seeking_venue.data = artist_selected.seeking_venue
        form.seeking_description.data = artist_selected.seeking_description
        form.image_link.data = artist_selected.image_link

    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        return render_template('forms/edit_artist.html', form=form, artist=artist)

    #  DONE: populate form with fields from artist with ID <artist_id>
    # https://python-adv-web-apps.readthedocs.io/en/latest/flask_forms.html


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # DONE: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    artist_selected = Artist.query.get(artist_id)
    try:
        artist_selected.name = request.form.get('name')
        artist_selected.city = request.form.get('city')
        artist_selected.state = request.form.get('state')
        artist_selected.phone = request.form.get('phone')
        artist_selected.image_link = request.form.get('image_link')
        artist_selected.facebook_link = request.form.get('facebook_link')
        artist_selected.genres = request.form.getlist('genres')
        artist_selected.website = request.form.get('website_link')
        artist_selected.seeking_talent = request.form.get('seeking_talent')
        artist_selected.seeking_description = request.form.get(
            'seeking_description')
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        return redirect(url_for('show_artist', artist_id=artist_id))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {}
    try:
        venue_selected = Venue.query.get(venue_id)
        # print(venue_selected)
        # print(venue_selected.name)

        venue = {
            "id": venue_selected.id,
            "name": venue_selected.name,
            "genres": venue_selected.genres,
            "address": venue_selected.address,
            "city": venue_selected.city,
            "state": venue_selected.state,
            "phone": venue_selected.phone,
            "website": venue_selected.website,
            "facebook_link": venue_selected.facebook_link,
            "seeking_talent": venue_selected.seeking_talent,
            "seeking_description": venue_selected.seeking_description,
            "image_link": venue_selected.image_link,
        }

        form.name.data = venue_selected.name
        form.genres.data = venue_selected.genres
        form.address.data = venue_selected.address
        form.city.data = venue_selected.city
        form.state.data = venue_selected.state
        form.phone.data = venue_selected.phone
        form.website_link.data = venue_selected.website
        form.facebook_link.data = venue_selected.facebook_link
        form.seeking_talent.data = venue_selected.seeking_talent
        form.seeking_description.data = venue_selected.seeking_description
        form.image_link.data = venue_selected.image_link

    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    # DONE: populate form with values from venue with ID <venue_id>


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # DONE: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    venue_selected = Venue.query.get(venue_id)
    try:
        venue_selected.name = request.form.get('name')
        venue_selected.city = request.form.get('city')
        venue_selected.state = request.form.get('state')
        venue_selected.phone = request.form.get('phone')
        venue_selected.image_link = request.form.get('image_link')
        venue_selected.facebook_link = request.form.get('facebook_link')
        venue_selected.genres = request.form.getlist('genres')
        venue_selected.website = request.form.get('website_link')
        venue_selected.seeking_talent = bool(
            request.form.get('seeking_talent'))
        venue_selected.seeking_description = request.form.get(
            'seeking_description')
        print(venue_selected)
        print(venue_selected.name)

        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion

    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = request.form.get('phone')
        image_link = request.form.get('image_link')
        facebook_link = request.form.get('facebook_link')
        genres = request.form.getlist('genres')
        website = request.form.get('website_link')
        seeking_venue = request.form.get('seeking_venue')
        seeking_description = request.form.get('seeking_description')

        new_artist_listing = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            image_link=image_link,
            facebook_link=facebook_link,
            genres=', '.join(genres),
            website=website,
            seeking_venue=bool(seeking_venue),
            seeking_description=seeking_description,
        )
        print(new_artist_listing.name)
        print(new_artist_listing.genres)
        print(new_artist_listing)
        # then 'try' to add to sessions and 'flash' success
        db.session.add(new_artist_listing)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        # then 'except' rollback
        # DONE: on unsuccessful db insert, flash an error instead. - modify 'flash' for unsuccessful
    except:
        db.session.rollback()
        print(sys.exc_info())
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Artist ' +
              request.form['name'] + ' unfortuntely could not be listed.')
    # then finally close session
    finally:
        db.session.close()
        # the return
        return render_template('pages/home.html')

    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    # DONE: replace with real venues data.
    shows_list = Show.query.order_by(db.desc(Show.start_time)).all()
    print(shows_list)
    data = []
    try:
        for show in shows_list:
            # venue_name = Venue.query.get(Venue.name).filter(
            #     show.venue_id == Venue.id)
            # artist_name = Artist.query.get(
            #     Artist.name).filter(show.venue_id == Artist.id)
            venue_name = Venue.query.get(show.venue_id).name
            artist_name = Artist.query.get(show.artist_id).name
            artist_image_link = Artist.query.get(show.artist_id).image_link
            print(venue_name)
            print(artist_name)

            data.append({
                "venue_id": show.venue_id,
                "venue_name": venue_name,
                "artist_id": show.artist_id,
                "artist_name": artist_name,
                "artist_image_link": artist_image_link,
                "start_time": str(show.start_time)
            })
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
