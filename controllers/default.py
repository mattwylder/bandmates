# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
@auth.requires_login()
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    import string
    city_msg = ''
    if request.vars.city and request.vars.roles:
	city = string.capitalize(request.vars.city)
	roles = request.vars.roles.replace(' ', '').split(',') 
	city_msg = 'Showing results in ' + city
	listings= None
	for role in roles:
	    listing = db((db.listing.id == db.listing_role.listing_ndx) &
		(db.listing.city == city) &
		(db.listing_role.role_ndx == db.role.id) &
		(db.role.role_name == role)).select(
		    db.listing.id,
		    db.listing.created_by,
		    db.listing.title,
		    db.listing.city,
		    db.listing.date_created,
		    orderby=~db.listing.date_created)
	    if listing and listings:
		listings = listings |listing
	    elif listing:
		listings=listing
    elif request.vars.city and not request.vars.roles:
	city = string.capitalize(request.vars.city)
	city_msg = 'Showing results in ' + city
	listings = db(db.listing.city == city).select(orderby=~db.listing.date_created)
    elif request.vars.roles:
	roles = request.vars.roles.replace(' ', '').split(',') 
	listings= None
	for role in roles:
	    listing = db((db.listing.id == db.listing_role.listing_ndx) &
		(db.listing_role.role_ndx == db.role.id) &
		(db.role.role_name == role)).select(
		    db.listing.id,
		    db.listing.created_by,
		    db.listing.title,
		    db.listing.city,
		    db.listing.date_created,
		    orderby=~db.listing.date_created)
	    if listing and listings:
		listings = listings |listing
	    elif listing:
		listings = listing
	city_msg = 'Showing results in all cities'
    elif not request.vars.roles and not request.vars.city:
        listings=db(db.listing).select(orderby=~db.listing.date_created)
	city_msg = 'Showing listings in all cities'
    return dict(listings=listings,user=auth.user,city_msg=city_msg)

@auth.requires_login()
def listing():
    listing = db.listing(request.args(0,cast=int)) or redirect(URL('index'))
    user_authorized =auth.user.id == listing.created_by
    genres=db((db.listing_genre.genre_ndx== db.genre.id) & 
	     (db.listing_genre.listing_ndx == listing.id)).select(
	    db.genre.genre_name)
    roles = db((db.listing_role.role_ndx == db.role.id) &
	       (db.listing_role.listing_ndx == listing.id)).select(
	    db.role.role_name)
    audio = db(db.audio_file.listing_ndx == listing.id).select(
	    db.audio_file.audio)
    auditions = None
    if user_authorized:
	auditions = db((db.audition.created_by == db.auth_user.id) &
		    (db.audition.parent_ndx == listing.id)).select(db.audition.id,db.auth_user.first_name, db.auth_user.last_name)
    return dict(user_authorized=user_authorized,listing=listing, genres=genres,roles=roles, audio=audio, auditions=auditions)

#TODO: for some reason the auth requirement below affects every page
#@auth.requires(auth.user_id == db.listing(db.audition(request.args(0,cast=int)).parent_ndx).created_by or auth.user_id == db.audition(request.args(0,cast=int)).created_by)
@auth.requires_login()
def audition():
    audition = db.audition(request.args(0,cast=int)) or redirect(URL('index')) 
    parent = db.listing(audition.parent_ndx)
    if auth.user_id != audition.created_by and auth.user_id != parent.created_by:
	redirect(URL('index'))
    author = db(db.auth_user.id==audition.created_by).select().first()
    genres = db((db.audition_genre.genre_ndx== db.genre.id) & 
	     (db.audition_genre.audition_ndx == audition.id)).select(
	    db.genre.genre_name)
    roles = db((db.audition_role.role_ndx == db.role.id) &
	       (db.audition_role.audition_ndx == audition.id)).select(
	    db.role.role_name)
    audio = db(db.audio_file.audition_ndx == audition.id).select(
	    db.audio_file.audio)
    return dict(author=author,audition=audition, genres=genres,roles=roles, audio=audio)


@auth.requires_login()
def listingform():
    form = SQLFORM.factory(db.listing,
			   Field('role','list:string'),
			   Field('genre','list:string'), 
			   db.audio_file)
    if form.process().accepted:
	import string
	form.vars.city = string.capitalize(form.vars.city)
	listing_ndx = db.listing.insert(**db.listing._filter_fields(form.vars))
	form.vars.listing_ndx=listing_ndx
	if form.vars.audio:
	    db.audio_file.insert(**db.audio_file._filter_fields(form.vars))
	roles = form.vars.role
	genres=form.vars.genre
	#TODO: Single entries are broken into single characters for some reason
	#TODO: Double entries on a single form get double added to listing
	for role in roles:
	    if role:
		role_ndx = db(db.role.role_name==role).select(db.role.id).first()
		if(role_ndx==None):
		   role_ndx=db.role.insert(role_name=role)
		db.listing_role.insert(listing_ndx=listing_ndx, role_ndx=role_ndx)
	
	for genre in genres:
	    if genre:
		genre_ndx = db(db.genre.genre_name==role).select(db.genre.id).first()
		if(genre_ndx==None):
		   genre_ndx=db.genre.insert(genre_name=genre)
		db.listing_genre.insert(listing_ndx=listing_ndx, genre_ndx=genre_ndx)
	redirect(URL('listing',args=listing_ndx))
    return dict(form=form)

@auth.requires_login()
def auditionform():
    parent_ndx = request.args(0,cast=int)
    rows = db((db.role.id == db.listing_role.role_ndx) &	
	    (db.listing_role.listing_ndx == parent_ndx)).select(db.role.role_name)
    roles = []
    for role in rows:
	roles.append(role.role_name)
    form = SQLFORM.factory(
		db.audition,
		Field('roles','list:reference', requires=IS_IN_SET(roles, multiple=True), widget = SQLFORM.widgets.checkboxes.widget),
		Field('genre','list:string'),
		db.audio_file)
    if form.process().accepted:    
	form.vars.parent_ndx = parent_ndx
	audition_ndx = db.audition.insert(**db.audition._filter_fields(form.vars))
	form.vars.audition_ndx=audition_ndx
	if form.vars.audio:
	    db.audio_file.insert(**db.audio_file._filter_fields(form.vars))
	genres = form.vars.genre
        roles = form.vars.roles
    
	for role in roles:
	    if role:
		role_ndx = db(db.role.role_name==role).select(db.role.id).first()
		if(role_ndx==None):
		   role_ndx=db.role.insert(role_name=role)
		db.audition_role.insert(audition_ndx=audition_ndx, role_ndx=role_ndx)
	
	for genre in genres:
	    if genre:
		genre_ndx = db(db.genre.genre_name==role).select(db.genre.id).first()
		if(genre_ndx==None):
		   genre_ndx=db.genre.insert(genre_name=genre)
		db.audition_genre.insert(audition_ndx=audition_ndx, genre_ndx=genre_ndx)
	
	redirect(URL('audition', args=audition_ndx))
    elif form.errors:
	response.flash = 'errors' 
    return dict(form=form)

@auth.requires_login()
## All of a user's audio files
def audio():
    """
    SELECT *
    FROM AUDIO
    WHERE AUDIO.CREATED_BY = auth.user
    """
    audio_ndx = request.args(0,cast=int)
    audio = db(db.audio_file.id == audio_ndx).select(db.audio_file.audio).first()
    return dict(audio=audio)

@auth.requires_login()
def audioform():
    form = SQLFORM(db.audio_file)
    return dict(form=form)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


