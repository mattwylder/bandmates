# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)


if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')


## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

auth.settings.extra_fields['auth_user']=[
   Field('city')]

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

import string
#Classified listing
db.define_table('listing',
		Field('title',requires=IS_NOT_EMPTY()),
		Field('city',
		    requires=IS_NOT_EMPTY()),
		Field('created_by', 'reference auth_user', default=auth.user_id,readable=False,writable=False),
		Field('date_created','datetime',
		       default=request.now, readable=False,writable=False),
		Field('body', 'text', requires=IS_NOT_EMPTY()))

## An 'application' to a listing
db.define_table('audition',
		Field('parent_ndx', 'reference listing',
		       readable=False, writable=False),
		Field('created_by', 'reference auth_user', 
		       default=auth.user_id, readable=False,writable=False),
		Field('date_created','datetime',
		    default=request.now, readable=False,writable=False),
		Field('body', 'text'), requires=IS_NOT_EMPTY())

## Genres of music 
db.define_table('genre',
		Field('genre_name'))

## Role of a user e.g. guitarist, drummer, bassist
db.define_table('role',
		Field('role_name'))

## Maps listing to roles
db.define_table('listing_role',
		Field('listing_ndx', 'reference listing',
		       readable=False,writable=False),
		Field('role_ndx', 'reference role'))

## Maps listings to genres
db.define_table('listing_genre',
		Field('listing_ndx', 'reference listing',
		       readable=False,writable=False),
		Field('genre_ndx', 'reference genre'))			

## Maps users to genres
db.define_table('user_genre',
		Field('user_ndx', 'reference auth_user',
		       default=auth.user_id, readable=False,writable=False),
		Field('genre_ndx', 'reference genre'))			

## Maps auditions to audio files. Users may not want to include all
#  of their music samples in an audition.

db.define_table('audition_genre',
		Field('audition_ndx','reference audition'),
		Field('genre_ndx','reference genre'))

db.define_table('audition_role',
		Field('audition_ndx','reference audition'),
		Field('role_ndx','reference role'))

db.define_table('city',
		Field('city_name'))
import os
##For some reason <audio> won't play mp3s unless they're in the static folder
db.define_table('audio_file',
		Field('created_by','reference auth_user', default=auth.user_id,
			readable=False,writable=False),
		Field('listing_ndx','reference listing', default=None,
			readable=False,writable=False),
		Field('audition_ndx','reference audition',default=None,
			readable=False,writable=False),
		Field('audio','upload',
			uploadfolder=os.path.join(request.folder,'static/')))
