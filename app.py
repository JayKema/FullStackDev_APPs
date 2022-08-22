#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import os
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
import logging
import sys
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  place = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
    
  for city in place:
    ven_list = []
    venues = Venue.query\
                  .filter_by(state=city.state)\
                  .filter_by(city=city.city).all()
    for ven in venues:
        get_ven = {
            'id': ven.id,
            'name': ven.name,
            'num_upcoming_shows': len(Show.query.join(Venue)\
                                      .filter(Show.venue_id==ven.id)\
                                      .filter(Show.start_time > datetime.now())\
                                      .all())
        }
        ven_list.append(get_ven)
    
    place_data = {
         "city": city.city,
         "state": city.state,
         "venues": ven_list
        }
    data.append(place_data)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    string = request.form.get('search_term', '')
    items = Venue.query.filter(Venue.name.ilike(f"%{string}%")).all()
    response={
        "count": len(items),
        "data": []
      }
    data = None
    for item in items:
        data= {
            "id": item.id,
            "name": item.name,
            "num_upcoming_shows":len(Show.query\
                                         .filter_by(venue_id=item.id)\
                                         .filter(Show.start_time > datetime.now())\
                                         .all()),
            }
        if data == None:
            reponse = reponse
        else:
            response['data'].append(data)
    return render_template('pages/search_venues.html', results=response, search_term=string)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  # functions to get show details
  def get_show(shows):
    show_detials = []
    for show in shows:
        get_details = {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")}
        show_detials.append(get_details)
    return show_detials
        
    
  venue = db.session.query(Venue).get(venue_id)

  past_shows = Show.query.join(Venue).filter(Show.venue_id == venue_id)\
                                    .filter(Show.start_time <= datetime.now()).all()
   
  upcoming_shows = Show.query.join(Venue).filter(Show.venue_id == venue_id)\
                                    .filter(Show.start_time > datetime.now()).all()
      
            
  data ={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": get_show(past_shows) if len(past_shows) > 0  else [],
    "upcoming_shows": get_show(upcoming_shows) if len(upcoming_shows) > 0 else [],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
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
  error = False
  form = VenueForm()
  try:
    venue = Venue(name=form.name.data,
                  genres= form.genres.data,
                  address=form.address.data,
                  city=form.city.data,
                  state=form.state.data,
                  phone=form.phone.data,
                  website=form.website_link.data,
                  facebook_link=form.facebook_link.data,
                  seeking_talent=form.seeking_talent.data,
                  seeking_description=form.seeking_description.data,
                  image_link=form.image_link.data
                 )
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + form.name.data + ' was successfully listed!')
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('Venue ' + form.name.data + ' could not be listed!')
  finally:
    db.session.close()
  if error==True:
    abort(500)
  else:
    return render_template('pages/home.html')

  
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.query.get(venue_id)
    name = venue.name
    db.session.delete(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + venue_id + ' was successfully deleted!')
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('Venue ' + venue_id + ' could not be deleted!')
  finally:
    db.session.close()
  if error==True:
    abort(500)
  else:
    return render_template('pages/home.html')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    string = request.form.get('search_term', '')
    print(Artist.name.ilike(f"%{string}%"))
    artists = Artist.query.filter(Artist.name.ilike(f"%{string}%")).all()
    response={
        "count": len(items),
        "data": []
      }
    
    data = None
    for artist in artists:
         data= {"id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": len(Show.query.join(Artist)\
                                          .filter(Artist.id==artist.id)\
                                         .filter(Show.start_time>datetime.now()).all())
            }
         response['data'].append(data)
    return render_template('pages/search_artists.html', results=response, search_term=string)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
    def get_show(show_list):
        show_detials = []
        for show in show_list:
            get_details = {
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")}
            show_detials.append(get_details)
            return show_detials
    
    artist = db.session.query(Artist).get(artist_id)
    
    past_shows = Show.query.join(Artist)\
                            .filter(Show.artist_id == artist_id )\
                            .filter(Show.start_time<=datetime.now()).all()
    upcoming_shows = Show.query.join(Artist)\
                            .filter(Show.artist_id == artist_id )\
                            .filter(Show.start_time>datetime.now()).all()
    
    data ={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": get_show(past_shows) if len(past_shows) > 0  else [],
    "upcoming_shows": get_show(upcoming_shows) if len(upcoming_shows) > 0 else [],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist =  Artist.query.get(artist_id)
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data =  artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link
    
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  form = ArtistForm()
  try:
    artist =  Artist.query.get(artist_id)
    artist.name = form.name.data  
    artist.genres = form.genres.data  
    artist.city = form.city.data  
    artist.state = form.state.data  
    artist.phone = form.phone.data  
    artist.website = form.website_link.data  
    artist.facebook_link = form.facebook_link.data  
    artist.seeking_venue = form.seeking_venue.data  
    artist.seeking_description = form.seeking_description.data  
    artist.image_link = form.image_link.data  

    db.session.commit()
    flash('Update Sucessful!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('Update Unsucessful!')
  finally:
    db.session.close()
  if error == True:
    abort(500)
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue =  Venue.query.get(venue_id)
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.city.data =  venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.website_link.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue .seeking_description
  form.image_link.data = venue .image_link  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  form = VenueForm()
  try:
    venue =  Venue.query.get(venue_id)
    venue.name = form.name.data  
    venue.genres = form.genres.data  
    venue.city = form.city.data  
    venue.state = form.state.data 
    venue.address = form.address.data
    venue.phone = form.phone.data  
    venue.website = form.website_link.data  
    venue.facebook_link = form.facebook_link.data  
    venue.seeking_talent = form.seeking_talent.data  
    venue.seeking_description = form.seeking_description.data  
    venue.image_link = form.image_link.data  

    db.session.commit()
    flash('Update Sucessful!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('Update Unsucessful!')
  finally:
    db.session.close()
  if error == True:
    abort(500)
  else:
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
    # TODO: modify data to be the data object returned from db insertio
    error = False
    form = ArtistForm()
    try:
        artist = Artist(name=form.name.data,
                  genres= form.genres.data,
                  city=form.city.data,
                  state=form.state.data,
                  phone=form.phone.data,
                  website=form.website_link.data,
                  facebook_link=form.facebook_link.data,
                  seeking_venue=form.seeking_venue.data,
                  seeking_description=form.seeking_description.data,
                  image_link=form.image_link.data
                 )
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + form.name.data + ' was successfully listed!')
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('Artist ' + form.name.data + ' could not be listed!')
    finally:
        db.session.close()
    if error==True:
        abort(500)
    else:
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  Shows = Show.query.join(Artist).join(Venue).all()
  
  data = []
  
  for show in Shows:
    info = {"venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")}
#     for artist in show.artist:
#        try:
#          info["artist_id"] = artist.id
#          info["artist_name"] = artist.name
#          info["artist_image_link"] = artist.image_link          
#        except:
#             data = data
#        finally:
    data.append(info.copy())
            
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
  form = ShowForm()
  error = False
  try:
    venue = db.session.get(Venue, form.venue_id.data)
    artist = db.session.get(Artist, form.artist_id.data)
    newShow = Show(start_time=form.start_time.data, venue=venue, artist=artist)
    db.session.add(newShow)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
    
    if venue == None and artist == None:
        flash(f'Venue and Artist are not listed')
    elif artist == None:
        flash(f'Artist with ID: {form.artist_id.data} is not listed')
    elif venue == None:
        flash(f'Venue with ID: {form.venue_id.data} is not listed')
    else:
        flash('An error occurred. Show could not be listed.')
  finally:
     db.session.close()
  if error == True:
    abort(500)
  else:
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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# # Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)

