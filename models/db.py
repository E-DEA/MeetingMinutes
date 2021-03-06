# -*- coding: utf-8 -*-
db = DAL('sqlite://storage.db',lazy_tables=True)
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

db.define_table(
    auth.settings.table_user_name,
    Field('Name',length=128,default='',requires=IS_NOT_EMPTY(error_message=auth.messages.is_empty)),
    Field('email', length=128, default='', requires=IS_EMAIL(error_message='Invalid email address'),unique=True),
    Field('Username',default='', requires = IS_ALPHANUMERIC(error_message='Must be alphanumeric') and IS_NOT_EMPTY(error_message='Username cannot be empty') and IS_NOT_IN_DB(db, 'auth_user.Username') ),
    Field('password', 'password', length=512,readable=False,requires = IS_STRONG(min=8, special=1,upper=1),label='Password'),
    Field('Organisation','string',requires=IS_NOT_EMPTY(error_message='Organisation cannot be empty'),length=128),
    Field('abc', 'string',label='State/Union Territory',default='None',requires = IS_IN_SET([('Andaman & Nicobar Islands'),('Andhra Pradesh'),('Arunachal Pradesh'),('Assam'),('Bihar'),('Chandigarh'),('Chattisgarh'),('Dadra & Nagar Haveli'),('New Delhi(NCR)'),('Daman & Diu'),('Goa'),('Gujarat'),('Haryana'),('Himachal Pradesh'),('Jammu & Kashmir'),('Jharkhand'),('Karnataka'),('Kerala'),('Lakshadweep'),('Madhya Pradesh'),('Maharashtra'),('Manipur'),('Meghalaya'),('Mizoram'),('Nagaland'),('Odisha(Orissa)'),('Pondicherry(Puducherry)'),('Punjab'),('Rajashtan'),('Sikkim'),('Tamil Nadu'),('Telangana'),('Tripura'),('Uttar Pradesh'),('Uttarakhand'),('West Bengal')])),
    Field('Phone_number', 'string',requires=IS_LENGTH(10) or IS_LENGTH(7)),
    Field('registration_key', length=512,writable=False, readable=False, default=''),
    Field('reset_password_key', length=512,writable=False, readable=False, default=''),
    Field('registration_id', length=512,writable=False, readable=False, default=''))


def user_bar():
    action = '/MeetingMinutes/default/user'
    if auth.user:
        logout=A('Logout', _href=action+'/logout',_id='id3')
        profile=A('Profile', _href=action+'/profile',_id='id4')
        password=A('Change Password', _href=action+'/change_password',_id='id4')
        bar = A('Hi '+auth.user.Username+' !',profile,password,logout)
    else:
        login=A('Sign In', _href=action+'/login', _id='id4')
        register=A('Sign Up',_href=action+'/register',_id='id3')
        lost_password=EM(A('Lost Password ?', _href=action+'/request_reset_password' ,_id='id2'))
        text = EM(SPAN('New to Meeting Minutes ?'))
        bar = A(text,register,login,lost_password)
    return bar

custom_auth_table = db[auth.settings.table_user_name] # get the custom_auth_table

## create all tables needed by auth if not custom tables
auth.define_tables()

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
if auth.user:
    defname = auth.user.Name
else:
    defname=""
db.define_table('Meetings',
                Field('title','string',requires=IS_NOT_EMPTY(error_message="Meeting title cannot be empty"),label='Title'),
                Field('chair','string',requires=IS_NOT_EMPTY(error_message="Field cannot be empty"),label='Chaired By'),
                Field('tags','string',default='Put up tags here to identify your Meeting.',label='Tags'),
                Field('minutetaker',default=defname,writable=True,requires=IS_NOT_EMPTY(),label='MinuteTaker'),
                Field('organiser','string',requires=IS_NOT_EMPTY(),label='Organiser'),
                Field('organisations','string',requires=IS_NOT_EMPTY(),label='Organisations involved'),
                Field('attendees','string',label='Attendees'),
                Field('loc','string',label='Location'),
                Field('agenda','text',default='Write agenda topics seperated by three fullstops(...)',label='Agenda Topics'),
                Field('templateid','integer',readable=False,writable=True,default='1',requires=IS_IN_SET([1,2,3]),label='Template ID'),
                Field('dt','date',default=request.now,writable=True,label='Date')
               )
db.define_table('Organisation',
                Field('name','string',requires=IS_NOT_EMPTY(),label='Name'),
                Field('meetings','string',default=request.post_vars.title,requires=IS_IN_DB(db,'Meetings.title',multiple=True),label='Meetings'),
                Field('employees','string',requires=IS_NOT_EMPTY() and IS_IN_DB(db,'auth_user.Name',multiple=True)),
                Field('admn',default='None',requires=IS_NOT_EMPTY() and IS_IN_DB(db,'auth_user.Name',multiple=True),label='Administrator')
               )
## after defining tables, uncomment below to enable auditing
auth.enable_record_versioning(db)
