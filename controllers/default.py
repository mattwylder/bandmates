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
    listings = db(db.listing.id > 0).select();
    return dict(listings=listings)

@auth.requires_login()
def listing():
    """
    listing_id = form.get_parameter("id")

    SELECT *
    FROM listing
    WHERE listing.id = listing_id 

    CURSOR roles IS
	SELECT role.role_name
        FROM listing_role JOIN role
	ON listing_role.role_ndx = role.id
	WHERE listing_role.listing_idx = listing_id 
    
    CURSOR audio IS
	SELECT *
	FROM listing_audio JOIN audio
	ON listing_audio.audio_ndx = audio.id
	WHERE listing_audio.listing_idx = listing_id
    """
    genre_str="""SELECT *
	FROM listing_genre JOIN genre
	ON listing_genre.genre_ndx = genre.id
	WHERE listing_genre.listing_ndx =
    """
    listing = db.listing(request.args(0,cast=int)) or redirect(URL('index'))
    '''genres = db(db.listing_genre.listing_ndx == listing.id).select(
	    db.genre.ALL,
	    left=db.listing_genre.on(listing == db.listing_genre.listing_ndx))'''
    genres=db(db.listing_genre.listing_ndx == listing.id).select()
    roles = db().select(
	    db.role.ALL,
	    left=db.listing_role.on(db.listing.id == db.listing_role.listing_ndx))
    audio = None 
    return dict(listing=listing, genres=genres,roles=roles, audio=audio)

@auth.requires_login()
def audition():
    '''
    if auth.user() = thisAudition.parent.created_by
    '''
    created_by = "usernameexample"
    roles = ['guitar', 'bass']
    body = 'i like this this and that'
    return dict(created_by=created_by, roles=roles, body=body)

@auth.requires_login()
def listingform():
    form = SQLFORM.factory(
		Field('title','title',requires=IS_NOT_EMPTY()),
		Field('city','City', requires=IS_NOT_EMPTY()),
		Field('desc','description', requires=IS_NOT_EMPTY()),
		Field('roles','Roles needed (Separated by commas)'),
		Field('genres','Genres (Separated by commas)'))
    if form.process().accepted:    
        title = form.vars.title
	city = form.vars.city
        desc = form.vars.desc
	genres = form.vars.genres
        roles = form.vars.roles
	listing_ndx = db.listing.insert(title=title, city=city,body=desc,
					created_by=auth.user.id)
    
	for cur_genre in genres.split(','):
	    genre_ndx = db(db.genre.genre_name==cur_genre).select(db.genre.id).first()
	    if genre_ndx == None:
		genre_ndx = db.genre.insert(genre_name=cur_genre)
	    db.listing_genre.insert(listing_ndx=listing_ndx,genre_ndx=genre_ndx)

	for cur_role in roles.split(','):
	    role_ndx = db(db.role.role_name==cur_role).select(db.role.id).first()
	    if role_ndx == None:
		role_ndx = db.role.insert(role_name=cur_role)
	    db.listing_role.insert(listing_ndx=listing_ndx,role_ndx=role_ndx)
    elif form.errors:
	response.flash = 'errors' 

    return dict(form=form)

@auth.requires_login()
def auditionform():
    parent_ndx = request.args(0,cast=int)
    form = SQLFORM.factory(
		Field('desc','description', requires=IS_NOT_EMPTY()),
		Field('roles','Roles needed (Separated by commas)'),
		Field('genres','Genres (Separated by commas)'))
    if form.process().accepted:    
        desc = form.vars.desc
	genres = form.vars.genres
        roles = form.vars.roles
	audition_ndx = db.audition.insert(parent_ndx=parent_ndx,body=desc)
    
	for cur_genre in genres.split(','):
	    genre_ndx = db(db.genre.genre_name==cur_genre).select(db.genre.id).first()
	    if genre_ndx == None:
		genre_ndx = db.genre.insert(genre_name=cur_genre)
	db.audition_genre.insert(listing_ndx=audition_ndx,genre_ndx=genre_ndx)

	for cur_role in roles.split(','):
	    role_ndx = db(db.role.role_name==cur_role).select(db.role.id).first()
	    if role_ndx == None:
		role_ndx = db.role.insert(role_name=role)
	db.audition_role.insert(listing_ndx=audition_ndx,role_ndx=role_ndx)
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
    return dict(form=auth())

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


