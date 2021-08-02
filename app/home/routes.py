# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from sqlalchemy.sql.functions import func, user
from app.home import blueprint
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
from app.base.models import User, Media, MediaLog, MediaType, db
from sqlalchemy.sql import text
from config import Admin, ProductionConfig

@blueprint.route('/index')
@login_required
def index():
    if(current_user.username == Admin) :
        # Get Dashboard info
        mediaRentList = MediaLog.query.join(Media, MediaLog.mediaid == Media.id).add_columns(Media.mediatype, Media.medianame, MediaLog.mediarenter, MediaLog.mediarenttime)
        mediaCountList = [];
        with db.engine.connect() as connection:
            result = connection.execute(text("""SELECT
                                                    t2.mediatype,
                                                    IFNULL( t1.count, 0 ) as count
                                                FROM
                                                    MediaType t2
                                                    LEFT JOIN ( SELECT Count( * ) AS count, mediatype FROM Media GROUP BY mediatype ) t1 ON t2.mediatype = t1.mediatype"""))
            for row in result:
                mediaCountList.append(row)

        userList = User.query.all()
        mediaList = Media.query.all()
        mediaRentList = Media.query.filter_by(mediastatus=2).all()
        mediaTypeList = MediaType.query.all()

        dashinfo = {
            "user_count":len(userList),
            "media_count":len(mediaList),
            "media_rented_count":len(mediaRentList),
            "media_rented": mediaRentList,
            "media_type_list": mediaTypeList,
            "media_count_list": mediaCountList
        }
        print(dashinfo)
        return render_template('index.html', segment='index', dashinfo=dashinfo, admin=True)
    else :
         return redirect(url_for('home_blueprint.medias'), code=302)


@blueprint.route('/Medias')
def medias():

    mediaRentList = Media.query.filter_by(mediastatus=2).all()
    mediaLeftList = Media.query.filter_by(mediastatus=1).all()
    mediaList = Media.query.all()
    mediasinfo = {
        "media_count":len(Media.query.all()),
        "media_rented_count":len(Media.query.filter_by(mediastatus=2).all()),
        "media_rented": mediaRentList,
        "media_left": mediaLeftList,
        "media_list": mediaList
    }
    return render_template('medias.html', segment='Medias', mediasinfo=mediasinfo, admin=(current_user.username == Admin))
    
@blueprint.route('/media_admin/check', methods=['POST'])
def admin_check():
    json = request.form["mediaId"]
    print(json)
    media = Media.query.filter_by(id=json).first()
    media.mediastatus = 1
    media.mediarenter = ""
    db.session.commit()
    return "SUCCESS"

@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith( '.html' ):
            template += '.html'

        # Detect the current page
        segment = get_segment( request )
        
        # Serve the file (if exists) from app/templates/FILE.html
        return render_template( template, segment=segment )

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500

# Helper - Extract current page name from request 
def get_segment( request ): 

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment    

    except:
        return None  
