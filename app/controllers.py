import numpy as np

from flask import Blueprint, render_template, request, make_response
import json
import os
import uuid

from models import Post, Vote, User, SurveyResult
from forms import SurveyForm
from app import db
from app import app
# import app
predict_game = Blueprint("app",__name__)


UUID_NAME = 'guessit_uuid'

@predict_game.route('/record_vote', methods=['POST','GET'])
def record_vote():

    print request.args.get('choice')

  
    current_uuid = get_uuid_from_cookie(request.cookies)
    current_user = get_current_user(current_uuid)
    user_choice = int(request.args.get('choice'))

    print type(user_choice)

    image_1 = current_user.current_image_1
    image_2 = current_user.current_image_2

    if image_1.score > image_2.score:
        correct_answer = 1
    elif image_2.score > image_1.score:
        correct_answer = 2
    else:
        correct_answer = 0 

    if user_choice == correct_answer:
        user_correct = 1
    else:
        user_correct = 0

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

    return json.dumps({'status':'OK', 'image_1_karma':image_1_score, 'image_2_karma':image_2_score, 'correct':user_correct})


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

    next_image_data['status'] = 'OK'


    return json.dumps(next_image_data)

@predict_game.route('/get_next_images_validation', methods=['POST','GET'])
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


@predict_game.route('/log_error', methods=['POST','GET'])
def log_error():

    #Do some stuff to log the error

    # update_images(request.cookies)
    return get_next_images()

@predict_game.route('/remove_image', methods=['POST','GET'])
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


@predict_game.route('/check_images')
def check_images():
    
    if app.config['ENABLE_IMAGE_MODERATION'] == False:
        return index()

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
    current_user = get_current_user(current_uuid)
    query_kwargs = {}

    if app.config['APPROVED_IMAGES_ONLY'] == True:
        query_kwargs['show_to_users'] = 't'

    if current_user.current_image_source is not None:
        query_kwargs['subreddit'] = current_user.current_image_source


    query_kwargs['year_posted'] = 2014

    # month = np.random.random_integers(1,12)
    # query_kwargs['month_posted'] = month

    [image_1, image_2] = Post.query.filter_by(**query_kwargs).order_by(db.func.random()).limit(2).all()

    current_user.current_image_1_id = image_1.id
    current_user.current_image_2_id = image_2.id

    db.session.commit()

def update_images_validation(current_uuid):
    current_user = get_current_user(current_uuid)
    query_kwargs = {}
    query_kwargs['hand_validated'] = None
    query_kwargs['year_posted'] = 2014

    # [image_1, image_2] = Post.query.filter(Post.hand_validated == None).order_by(db.func.random()).limit(2).all()
    [image_1, image_2] = Post.query.filter_by(**query_kwargs).order_by(db.func.random()).limit(2).all()

    current_user.current_image_1_id = image_1.id
    current_user.current_image_2_id = image_2.id

    db.session.commit()



@predict_game.route('/survey', methods=['GET', 'POST'])
def login():
    form = SurveyForm()

    if request.method == 'POST':
        s = SurveyResult(type_of_use = str(form.type_of_use.data),
                        frequency_of_use = str(form.use_frequency.data),
                        length_of_use = str(form.length_of_use.data)
                        )
        db.session.add(s)
        db.session.commit()
        return render_template('survey_thanks.html')


    if request.method == 'GET':
        return render_template('survey.html', 
                               title='Reddit Use',
                               form=form)


@predict_game.route('/')
def index():
    response = make_response(render_template('introduction.html'))
    
    current_uuid = get_uuid_from_cookie(request.cookies)
    response.set_cookie(UUID_NAME, current_uuid)
    current_user = get_current_user(current_uuid)
    update_images(current_uuid)
    return response











