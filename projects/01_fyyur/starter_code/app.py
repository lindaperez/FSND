# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import datetime
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy import func
from sqlalchemy.event import listen
import datetime

import collections

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

# TODO: connect to a local postgresql database
app.config.from_object('config')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    start_time = db.Column(db.DateTime())
    # relationships with artist and venue
    artist = db.relationship('Artist', back_populates="venues")
    venue = db.relationship('Venue', back_populates="artists")


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    genres = db.Column(db.String(500))
    # relation with association table Show
    artists = db.relationship("Show", back_populates="venue")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    genres = db.Column(db.String(500))
    # relation with association table Show
    venues = db.relationship("Show", back_populates="artist")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# db.create_all()
# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    current_time = datetime.datetime.now()

    sub_query = db.session.query(Show.venue_id, func.coalesce(func.count('*'), 0).label('num_upcoming_shows')). \
        filter(Show.start_time > current_time).group_by(Show.venue_id).subquery()
    result = db.session.query(Venue.city, Venue.state, Venue.id, Venue.name, sub_query.c.num_upcoming_shows). \
        outerjoin(sub_query, Venue.id == sub_query.c.venue_id).order_by(Venue.city, Venue.state)

    venues = collections.defaultdict(list)
    states = collections.defaultdict(str)

    for elem in result:
        venues[elem.city].append({'id': elem.id, 'name': elem.name, 'num_upcoming_shows': elem.num_upcoming_shows})
        states[elem.city] = elem.state

    data = []

    for elem in venues.keys():
        data.append({
            "city": elem,
            "state": states[elem],
            "venues": venues[elem]
        })

    return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    word = request.form['search_term']
    search = "%{}%".format(word)
    current_time = datetime.datetime.now()

    sub_query = db.session.query(Show.venue_id, func.coalesce(func.count('*'), 0).label('num_upcoming_shows')). \
        filter(Show.start_time > current_time).group_by(Show.venue_id).subquery()

    result = db.session.query(Venue.id.label('id'), Venue.name.label('name'), sub_query.c.num_upcoming_shows). \
        outerjoin(sub_query, Venue.id == sub_query.c.venue_id).filter(Venue.name.ilike(search)).order_by(Venue.name)

    data = []
    for elem in result:
        data.append({"id": elem.id, "name": elem.name, "num_upcoming_shows": elem.num_upcoming_shows})

    response = {"count": result.count(), "data": data}

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    current_time = datetime.datetime.now()

    upcoming = db.session.query(Show.venue_id, func.coalesce(func.count('*'), 0).label('num_upcoming_shows')). \
        filter(Show.start_time > current_time).group_by(Show.venue_id).subquery()

    past = db.session.query(Show.venue_id, func.coalesce(func.count('*'), 0).label('past_shows')). \
        filter(Show.start_time < current_time).group_by(Show.venue_id).subquery()

    venues_result = db.session.query(Venue.id, Venue.name, Venue.address, Venue.city, Venue.state,
                                     Venue.phone, Venue.website, Venue.website, Venue.facebook_link,
                                     Venue.seeking_talent,
                                     Venue.seeking_description, Venue.image_link, Venue.genres,
                                     upcoming.c.num_upcoming_shows, past.c.past_shows). \
        outerjoin(upcoming, Venue.id == upcoming.c.venue_id).filter(Venue.id == venue_id). \
        outerjoin(past, Venue.id == past.c.venue_id).filter(Venue.id == venue_id).all()

    data_result = []

    for elem in venues_result:
        upcoming_shows = db.session.query(Artist.id.label('artist_id'),
                                          Artist.name.label('artist_name'),
                                          Artist.image_link.label('artist_image_link'),
                                          Show.start_time). \
            join(Show).filter(Show.artist_id == Artist.id, Show.venue_id == elem.id,
                              Show.start_time > current_time)

        past_shows = db.session.query(Artist.id.label('artist_id'), Artist.name.label('artist_name'),
                                      Artist.image_link.label('artist_image_link'),
                                      Show.start_time). \
            join(Show).filter(Show.artist_id == Artist.id, Show.venue_id == elem.id,
                              Show.start_time < current_time)

        data_result.append({
            "id": elem.id,
            "name": elem.name,
            "genres": elem.genres.split(','),
            "address": elem.address,
            "city": elem.city,
            "state": elem.state,
            "phone": elem.phone,
            "website": elem.website,
            "facebook_link": elem.facebook_link,
            "seeking_talent": elem.seeking_talent,
            "seeking_description": elem.seeking_description,
            "image_link": elem.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": elem.past_shows,
            "upcoming_shows_count": elem.num_upcoming_shows,
        })

    data = list(filter(lambda d: d['id'] == venue_id, data_result))[0]
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form['genres'].join(',')

    image_link = ''
    facebook_link = request.form['facebook_link']
    website = ''
    seeking_talent = False
    seeking_description = ''

    ven = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link,
                facebook_link=facebook_link, genres=genres,
                website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)

    try:
        db.session.add(ven)
        db.session.commit()

    except exc.SQLAlchemyError:
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        form = VenueForm()
        return render_template('forms/new_venue.html', form=form)
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE','GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      if request.method=='DELETE':
          venue = db.session.query(Venue).filter(Venue.id == venue_id).one()
          db.session.delete(venue)
          db.session.commit()
      else:
          return render_template('pages/home.html')
  except exc.SQLAlchemyError:
      db.session.rollback()
      flash('An error occurred. Venue could not be deleted.')
  else:
      flash('Venue  was successfully deleted!')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None


#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    data = db.session.query(Artist).all()

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    word = request.form['search_term']
    search = "%{}%".format(word)

    data = db.session.query(Artist.id, Artist.name).filter(Artist.name.ilike(search)).order_by(Artist.name)

    response = {
        "count": data.count(),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    data_result = []
    current_time = datetime.datetime.now()
    result = db.session.query(Artist)

    for res in result:
        past_shows = db.session.query(Venue.id.label('venue_id'), Venue.name.label('venue_name'),
                                      Show.start_time, Venue.image_link.label('venue_image_link')). \
            join(Show).filter(Show.artist_id == res.id, Venue.id == Show.venue_id,
                              Show.start_time < current_time)
        upcoming_shows = db.session.query(Venue.id.label('venue_id'), Venue.name.label('venue_name'),
                                          Show.start_time, Venue.image_link.label('venue_image_link')). \
            join(Show).filter(Show.artist_id == res.id, Venue.id == Show.venue_id,
                              Show.start_time > current_time)

        data_result.append({
            "id": res.id,
            "name": res.name,
            "genres": res.genres.split(','),
            "city": res.city,
            "state": res.state,
            "phone": res.phone,
            "website": res.website,
            "facebook_link": res.facebook_link,
            "seeking_venue": res.seeking_venue,
            "seeking_description": res.seeking_description,
            "image_link": res.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": past_shows.count(),
            "upcoming_shows_count": upcoming_shows.count(),
        })

    data = list(filter(lambda d: d['id'] == artist_id, data_result))[0]
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(obj=artist)

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        artist = Artist.query.get_or_404(artist_id)
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form['genres']
        artist.facebook_link = request.form['facebook_link']
        db.session.commit()
    except exc.SQLAlchemyError:
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(obj=venue)

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
        venue = Venue.query.get_or_404(venue_id)

        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form['genres']
        venue.facebook_link = request.form['facebook_link']
        venue.address = request.form['address']

        db.session.commit()
    except exc.SQLAlchemyError:
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form

    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        genres = request.form['genres']
        image_link = ''
        facebook_link = request.form['facebook_link']
        website = ''
        seeking_venue = False
        seeking_description = ''

        artist = Artist(name=name, city=city, genres=genres, state=state, phone=phone, image_link=image_link,
                        facebook_link=facebook_link, website=website, seeking_venue=seeking_venue,
                        seeking_description=seeking_description)

        db.session.add(artist)
        db.session.commit()
    except exc.SQLAlchemyError:
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be created.')
    else:

        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully created!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    artist = db.session.query(Artist.id, Artist.name, Artist.image_link).subquery()
    venue = db.session.query(Venue.id, Venue.name.label('name'), Venue.image_link).subquery()
    data = db.session.query(Show.start_time, Show.venue_id, venue.c.name.label('venue_name'),
                            Show.artist_id,
                            artist.c.name.label('artist_name'), artist.c.image_link.label('artist_image_link')). \
        outerjoin(venue, venue.c.id == Show.venue_id). \
        outerjoin(artist, artist.c.id == Show.artist_id).order_by(Show.start_time)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()

    except exc.SQLAlchemyError:
        db.session.rollback()
        flash('An error occurred. Show ' + request.form['name'] + ' could not be created.')
    else:
    # on successful db insert, flash success
        flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
