# Imports
#----------------------------------------------------------------------------#
import os
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)


# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# artist_shows = db.Table('artist_shows', db.Model.metadata,
#     db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id', ondelete="CASCADE"), primary_key=True),
#     db.Column('show_id', db.Integer, db.ForeignKey('Show.id', ondelete="CASCADE"), primary_key=True)
# )

# venue_shows = db.Table('venue_shows', db.Model.metadata,
#     db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id', ondelete="CASCADE"), primary_key=True),
#     db.Column('show_id', db.Integer, db.ForeignKey('Show.id', ondelete="CASCADE"), primary_key=True)
# )

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(), nullable=True)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    website = db.Column(db.String(120))
    
     # setting up show to backpopulate artists for many-to-many 
    #shows = db.relationship("Show", secondary=venue_shows, back_populates="venues", cascade="all, delete")
    shows = db.relationship('Show', backref='venue', lazy=True)
    
    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(), nullable=False)
    phone = db.Column(db.String(120), nullable=False )
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(), nullable=True)
    website = db.Column(db.String(120))
    
    # setting up show to backpopulate artists for many-to-many 
    #shows = db.relationship("Show", secondary=artist_shows, backref=db.backref("artists", lazy="dynamic"), cascade="all, delete")
    #shows = db.relationship("Show", secondary=artist_shows, back_populates="artists", cascade="all, delete")
    
    shows = db.relationship('Show', backref='artist', lazy=True)
    
    
    
    
    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime(), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    
    # setting up show to backpopulate artists for many-to-many
#     venues = db.relationship("Venue", secondary=venue_shows, back_populates="shows", passive_deletes=True)
#     artists = db.relationship("Artist", secondary=artist_shows, back_populates="shows", passive_deletes=True)
    
    def __repr__(self):
        return f'<Show {self.id} {self.start_time}>'
