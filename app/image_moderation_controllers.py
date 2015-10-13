import numpy as np

from flask import Blueprint, render_template, request, make_response
import json
import os
import uuid

from models import Post, Vote, User, SurveyResult, UserScore
from controllers import get_current_user, get_uuid_from_cookie, update_article_source
from forms import SurveyForm
from app import db
from app import app
# import app
image_moderation = Blueprint("moderation",__name__)


UUID_NAME = 'guessit_uuid'

@image_moderation.route('/get_next_images_validation', methods=['POST','GET'])
def get_next_images_validation():

    current_uuid =  get_uuid_from_cookie(request.cookies)
    current_user = get_current_user(current_uuid)

    current_user.current_image_1.hand_validated = True
    current_user.current_image_2.hand_validated = True

    if current_user.current_image_1.show_to_users is None:
        current_user.current_image_1.show_to_users = True

    if current_user.current_image_2.show_to_users is None:
        current_user.current_image_2.show_to_users = True

    db.session.commit()


    update_images_validation(current_uuid)

    next_image_data = {}

    next_image_data['image_1_src'] = current_user.current_image_1.url
    next_image_data['image_1_id']  = current_user.current_image_1.reddit_id
    next_image_data['image_1_title']  = current_user.current_image_1.title




    next_image_data['image_2_src'] = current_user.current_image_2.url
    next_image_data['image_2_id']  = current_user.current_image_2.reddit_id
    next_image_data['image_2_title']  = current_user.current_image_2.title


    next_image_data['status'] = 'OK'


    return json.dumps(next_image_data)



@image_moderation.route('/remove_image', methods=['POST','GET'])
def remove_image():
    print 'remove image called'
    print request.args.get('id')

    image_id = int(request.args.get('id'))

    current_uuid =  get_uuid_from_cookie(request.cookies)
    current_user = get_current_user(current_uuid)

    if image_id == 1:
        temp = current_user.current_image_1

    if image_id == 2:
        temp = current_user.current_image_2
        
    temp.show_to_users = False
    db.session.commit()

    return json.dumps({'status':'OK'})



@image_moderation.route('/check_images')
def check_images():
    
    if app.config['ENABLE_IMAGE_MODERATION'] == False:
        return index()

    subreddit = request.args.get('article_source')
    pic_source_url = "http://www.reddit.com"
    pic_source_name = 'reddit'
    
    #We should first check that the game is actually there


    current_uuid = get_uuid_from_cookie(request.cookies)
    update_article_source(current_uuid, subreddit)
    update_images_validation(current_uuid)
    current_user = get_current_user(current_uuid)

    response = make_response( render_template('validate_images.html', 
        pic_source_url = pic_source_url,
        pic_source_name = pic_source_name,
        image_1_id = current_user.current_image_1.id,
        image_1_title = current_user.current_image_1.title,
        image_1_src = current_user.current_image_1.url,
        image_2_id = current_user.current_image_2.id,
        image_2_src = current_user.current_image_2.url,
        image_2_title = current_user.current_image_2.title
        )
    )
    response.set_cookie(UUID_NAME, current_uuid)
    return response


def update_images_validation(current_uuid):
    current_user = get_current_user(current_uuid)
    query_kwargs = {}
    query_kwargs['hand_validated'] = None
    query_kwargs['year_posted'] = 2014
    if current_user.current_image_source is not None:
        query_kwargs['subreddit'] = current_user.current_image_source


    # [image_1, image_2] = Post.query.filter(Post.hand_validated == None).order_by(db.func.random()).limit(2).all()
    [image_1, image_2] = Post.query.filter_by(**query_kwargs).order_by(db.func.random()).limit(2).all()

    current_user.current_image_1_id = image_1.id
    current_user.current_image_2_id = image_2.id

    db.session.commit()













