from flask import Blueprint, render_template, request, make_response
import json
import os
import uuid

from models import Post, Vote
from app import db
import app
predict_game = Blueprint("app",__name__)


# current_image_1 = None
# current_image_2 = None

UUID_NAME = 'guessit_uuid'

@predict_game.route('/record_vote', methods=['POST','GET'])
def record_vote():

    print request.args.get('choice')

    if UUID_NAME in request.cookies.keys():
        user_id = request.cookies[UUID_NAME]
    else:
        user_id = None


    user_choice = request.args.get('choice')

    if app.current_image_1.score >= app.current_image_2.score:
        correct_answer = 1
    else:
        correct_answer = 2

    new_vote = Vote(user_id, app.current_image_1.reddit_id, app.current_image_2.reddit_id, user_choice, correct_answer)
    db.session.add(new_vote)
    db.session.commit()

    if app.current_image_1:
        image_1_score = app.current_image_1.score
    else:
        image_1_score = 0

    if app.current_image_2:
        image_2_score = app.current_image_2.score
    else:
        image_2_score = 0

    return json.dumps({'status':'OK', 'image_1_karma':image_1_score, 'image_2_karma':image_2_score})



@predict_game.route('/get_next_images', methods=['POST','GET'])
def get_next_images():

    update_images()

    next_image_data = {}

    next_image_data['image_1_src'] = app.current_image_1.url
    next_image_data['image_1_title']  = app.current_image_1.title

    next_image_data['image_2_src'] = app.current_image_2.url
    next_image_data['image_2_title'] = app.current_image_2.title

    next_image_data['status'] = 'OK'

    # print request.cookies

    return json.dumps(next_image_data)


@predict_game.route('/log_error', methods=['POST','GET'])
def log_error():

    #Do some stuff to log the error

    update_images()
    return get_next_images()
    # next_image_data = {}

    # next_image_data['image_1_src'] = app.current_image_1.url
    # next_image_data['image_1_title']  = app.current_image_1.title

    # next_image_data['image_2_src'] = app.current_image_2.url
    # next_image_data['image_2_title'] = app.current_image_2.title

    # next_image_data['status'] = 'OK'

    # # print request.cookies

    # return json.dumps(next_image_data)


def update_images():
    [image_1, image_2] = Post.query.order_by(db.func.random()).limit(2).all()
    app.current_image_1 = image_1
    app.current_image_2 = image_2

@predict_game.route('/')
def index():
    update_images()
    response = make_response(render_template('index.html'))

    if (UUID_NAME in request.cookies.keys()) == False:

        user_id = str(uuid.uuid4())
        # user_id = os.urandom(24)
        response.set_cookie(UUID_NAME,user_id)
        print 'NOT HERE BEFORE'
    else:
        print 'HERE BEFORE'
    # print request.remote_addr
    # print request.headers


    return response










