from flask import Blueprint, render_template, request, make_response
import json
import os
import uuid

from models import Post, Vote, User
from app import db
import app
predict_game = Blueprint("app",__name__)


# current_image_1 = None
# current_image_2 = None

UUID_NAME = 'guessit_uuid'

@predict_game.route('/record_vote', methods=['POST','GET'])
def record_vote():

    print request.args.get('choice')

  
    current_uuid = get_uuid_from_cookie(request.cookies)
    current_user = get_current_user(current_uuid)
    user_choice = request.args.get('choice')


    image_1 = current_user.current_image_1
    image_2 = current_user.current_image_2

    if image_1.score >= image_2.score:
        correct_answer = 1
    else:
        correct_answer = 2

    new_vote = Vote(current_uuid, image_1.reddit_id, image_2.reddit_id, user_choice, correct_answer)
    db.session.add(new_vote)
    db.session.commit()

    if image_1:
        image_1_score = image_1.score
    else:
        image_1_score = 0

    if image_2:
        image_2_score = image_2.score
    else:
        image_2_score = 0

    return json.dumps({'status':'OK', 'image_1_karma':image_1_score, 'image_2_karma':image_2_score})


def check_valid_picture_source(subreddit):
    accepted_sources = ['pics','aww']
    return subreddit in accepted_sources

@predict_game.route('/get_next_images', methods=['POST','GET'])
def get_next_images():

    current_uuid =  get_uuid_from_cookie(request.cookies)
    update_images(current_uuid)

    current_user = get_current_user(current_uuid)

    next_image_data = {}

    next_image_data['image_1_src'] = current_user.current_image_1.url
    next_image_data['image_1_title']  = current_user.current_image_1.title

    next_image_data['image_2_src'] = current_user.current_image_2.url
    next_image_data['image_2_title']  = current_user.current_image_2.title



    # next_image_data['image_1_src'] = app.current_image_1.url
    # next_image_data['image_1_title']  = app.current_image_1.title

    # next_image_data['image_2_src'] = app.current_image_2.url
    # next_image_data['image_2_title'] = app.current_image_2.title

    next_image_data['status'] = 'OK'

    # print request.cookies

    return json.dumps(next_image_data)


@predict_game.route('/log_error', methods=['POST','GET'])
def log_error():

    #Do some stuff to log the error

    # update_images(request.cookies)
    return get_next_images()


@predict_game.route('/render_game')
def start_game():
    subreddit = request.args.get('article_source')
    
    if subreddit == 'aww':
        pic_source_url = "http://www.reddit.com/r/aww"
        pic_source_name = 'r/aww'
    if subreddit == 'pics':
        pic_source_url = "http://www.reddit.com/r/pics"
        pic_source_name = 'r/pics'

    if subreddit is None:
        pic_source_url = "http://www.reddit.com/r/aww"
        pic_source_name = 'r/aww'
        subreddit = 'aww'

    #We should first check that the game is actually there


    current_uuid = get_uuid_from_cookie(request.cookies)
    update_article_source(current_uuid, subreddit)
    update_images(current_uuid)
    current_user = get_current_user(current_uuid)

    response = make_response( render_template('pic_game.html', 
        pic_source_url = pic_source_url,
        pic_source_name = pic_source_name,
        image_1_title = current_user.current_image_1.title,
        image_1_src = current_user.current_image_1.url,
        image_2_title = current_user.current_image_2.title,
        image_2_src = current_user.current_image_2.url
        )
    )
    response.set_cookie(UUID_NAME, current_uuid)
    return response


def get_current_user(cookie_uuid):
    current_user = User.query.get(cookie_uuid)
    if current_user is None:
        new_user = User(uuid=cookie_uuid)
        db.session.add(new_user)
        db.session.commit()    
        print 'NEW USER'
        return new_user
    return current_user


def get_uuid_from_cookie(cookie):
    if (UUID_NAME in cookie.keys()) == False:
        user_id = str(uuid.uuid4())
        print 'NOT HERE BEFORE'
    else:
        user_id = request.cookies.get(UUID_NAME)
        print 'HERE BEFORE'
    return user_id


def update_article_source(current_uuid, article_source):
    current_user = get_current_user(current_uuid)
    current_user.current_image_source = article_source
    db.session.commit()


def update_images(current_uuid):
    print 'update_images called'
    current_user = get_current_user(current_uuid)

    if current_user.current_image_source is not None:
        [image_1, image_2] = Post.query.filter_by(subreddit=current_user.current_image_source).order_by(db.func.random()).limit(2).all()
    else:
        [image_1, image_2] = Post.query.order_by(db.func.random()).limit(2).all()

    current_user.current_image_1_id = image_1.id
    current_user.current_image_2_id = image_2.id

    db.session.commit()



@predict_game.route('/')
def index():
    response = make_response(render_template('introduction.html'))
    
    current_uuid = get_uuid_from_cookie(request.cookies)
    response.set_cookie(UUID_NAME, current_uuid)
    current_user = get_current_user(current_uuid)
    update_images(current_uuid)
    return response


    # print request.cookies
    # if (UUID_NAME in request.cookies.keys()) == False:

    #     user_id = str(uuid.uuid4())
    #     response.set_cookie(UUID_NAME,user_id)
    #     print 'NOT HERE BEFORE'
    # else:
    #     user_id = request.cookies.get(UUID_NAME)
    #     print 'HERE BEFORE'
    

    # print request.remote_addr
    # print request.headers


    # current_user = User.query.get(user_id)
    # if current_user is None:
    #     new_user = User(uuid=user_id)
    #     db.session.add(new_user)
    #     db.session.commit()











