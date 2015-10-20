import numpy as np
from numpy.random import choice

from flask import Blueprint, render_template, request, make_response
import json
import os
import uuid

from models import Post, Vote, User, SurveyResult, UserScore
from forms import SurveyForm
from app import db
from app import app


import pylibmc

from app import MAX_COOKIE_AGE
# import app
predict_game = Blueprint("app",__name__)


UUID_NAME = 'guessit_uuid'

@predict_game.route('/record_vote', methods=['POST','GET'])
def record_vote():

    current_uuid = get_uuid_from_cookie(request.cookies)
    current_user, current_score = get_current_user_and_score(current_uuid)
    user_choice = int(request.args.get('choice'))

    image_1 = current_user.current_image_1
    image_2 = current_user.current_image_2

    if image_1.score > image_2.score:
        correct_answer = 1
    elif image_2.score > image_1.score:
        correct_answer = 2
    else:
        correct_answer = 0 



    if current_score.num_correct is None:
        current_score.num_correct = 0
    if current_score.num_wrong is None:
        current_score.num_wrong = 0


    if user_choice == correct_answer:
        user_correct = 1
        current_score.num_correct = current_score.num_correct + 1
    else:
        user_correct = 0
        current_score.num_wrong = current_score.num_wrong + 1

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


    percent_correct = format_correct_percentage(current_score)
    num_remaining = current_score.num_questions - (current_score.num_correct + current_score.num_wrong)
    ret_vals = {
    'status':'OK',
    'image_1_karma':image_1_score,
    'image_2_karma':image_2_score,
    'correct':user_correct,
    'num_correct':current_score.num_correct,
    'num_wrong':current_score.num_wrong, 
    'num_remaining':num_remaining,
    'user_choice': user_choice
    }

    print current_score.num_correct + current_score.num_wrong

    if current_score.num_correct + current_score.num_wrong >= 10:
        ret_vals['end_of_game'] = 1


    return json.dumps(ret_vals)


def check_valid_picture_source(subreddit):
    accepted_sources = ['pics','aww']
    return subreddit in accepted_sources

@predict_game.route('/get_next_images', methods=['POST','GET'])
def get_next_images():

    current_uuid =  get_uuid_from_cookie(request.cookies)
    update_images(current_uuid)

    current_user, current_score = get_current_user_and_score(current_uuid)
    
    if current_score.num_seen:  
        current_score.num_seen = current_user.num_seen + 1
    else:
        current_score.num_seen = 0 
    next_image_data = {}

    next_image_data['image_1_src'] = current_user.current_image_1.url
    next_image_data['image_1_title']  = current_user.current_image_1.title

    next_image_data['image_2_src'] = current_user.current_image_2.url
    next_image_data['image_2_title']  = current_user.current_image_2.title
    next_image_data['status'] = 'OK'
    db.session.commit()

    return json.dumps(next_image_data)


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
    

    # current_user, current_score = get_current_user_and_score(current_uuid)

    current_user = get_current_user(current_uuid)
    current_score = make_new_score(current_user, subreddit)


    percent_correct = format_correct_percentage(current_score)

    response = make_response( render_template('pic_game_mobile.html', 
        pic_source_url = pic_source_url,
        pic_source_name = pic_source_name,
        image_1_title = current_user.current_image_1.title,
        image_1_src = current_user.current_image_1.url,
        image_2_title = current_user.current_image_2.title,
        image_2_src = current_user.current_image_2.url,
        num_correct = current_score.num_correct,
        num_wrong = current_score.num_wrong,
        num_remaining = current_score.num_questions,
        num_questions = current_score.num_questions
        )
    )
    response.set_cookie(UUID_NAME, current_uuid)
    return response


@predict_game.route('/end_game')
def end_game():
    current_uuid = get_uuid_from_cookie(request.cookies)

    current_user, current_score = get_current_user_and_score(current_uuid)
    response = make_response(render_template('end_game_thanks.html', correct_pct=format_correct_percentage(current_score)))
    return response


def get_current_user(cookie_uuid, subreddit=None):
    current_user = User.query.get(cookie_uuid)
    if current_user is None:
        new_user = User(uuid=cookie_uuid)
        db.session.add(new_user)
        db.session.commit()    
        return new_user
    return current_user


def get_current_user_and_score(cookie_uuid):
    current_user = User.query.get(cookie_uuid)
    if current_user is None:
        new_user = User(uuid=cookie_uuid)
        db.session.add(new_user)
        db.session.commit()    
        return new_user
    

    query = UserScore.query.filter_by(uuid=current_user.uuid, subreddit=current_user.current_image_source)

    for x in query.order_by(UserScore.date_created.desc()).all():
        print x.date_created, x.num_correct, x.num_wrong
    current_score = query.order_by(UserScore.date_created.desc()).limit(1).first()

    # current_score = UserScore.query.filter_by(uuid=current_user.uuid, subreddit=current_user.current_image_source).order_by(UserScore.date_created).limit(1).first()
    if current_score is None:
        current_score = UserScore(uuid=current_user.uuid, subreddit=current_user.current_image_source)
        db.session.add(current_score)
        db.session.commit()


    return current_user, current_score

def make_new_score(current_user, subreddit):
    num_questions = 10 #eventually implement something random here
    new_score = UserScore(uuid=current_user.uuid, subreddit=subreddit, num_questions=10)
    db.session.add(new_score)
    db.session.commit()
    return new_score

def format_correct_percentage(current_score):

    num_answered = current_score.num_correct + current_score.num_wrong
    if num_answered == 0:
        return '--'
        # return 100

    percent_correct = current_score.num_correct / (1.0*num_answered)
    percent_correct *= 100
    percent_correct = int(percent_correct)
    return percent_correct

def get_uuid_from_cookie(cookie):
    if (UUID_NAME in cookie.keys()) == False:
        user_id = str(uuid.uuid4())
    else:
        user_id = request.cookies.get(UUID_NAME)
    return user_id



def update_article_source(current_uuid, article_source):
    current_user = get_current_user(current_uuid)
    current_user.current_image_source = article_source
    db.session.commit()


def update_images(current_uuid):
    current_user = get_current_user(current_uuid)
    month = None

    #Insert experiment logic here
    pic_1_filters, pic_2_filters = get_experimental_condition(current_user.current_image_source)

    query_1 = Post.query.filter(Post.year_posted==2014)
    if app.config['APPROVED_IMAGES_ONLY'] == True:
        query_1 = query_1.filter(Post.show_to_users == 't')
    if month is not None:
        query_1 = query_1.filter(Post.month_posted == month)
    if current_user.current_image_source is not None:
        query_1 = query_1.filter(Post.subreddit == current_user.current_image_source)
    if pic_1_filters['min_score'] is not None:
        query_1 = query_1.filter(Post.score >= pic_1_filters['min_score'])
    if pic_1_filters['max_score'] is not None:
        query_1 = query_1.filter(Post.score <= pic_1_filters['max_score'])

    random_offset = np.random.random_integers(0, int(query_1.count()) -1)
    image_1 = query_1.offset(random_offset).first()

    
    query_2 = Post.query.filter(Post.year_posted==2014)
    if app.config['APPROVED_IMAGES_ONLY'] == True:
        query_2 = query_2.filter(Post.show_to_users == 't')
    if month is not None:
        query_2 = query_2.filter(Post.month_posted == month)
    if current_user.current_image_source is not None:
        query_2 = query_2.filter(Post.subreddit == current_user.current_image_source)
    if pic_2_filters['min_score'] is not None:
        query_2 = query_2.filter(Post.score >= pic_2_filters['min_score'])
    if pic_2_filters['max_score'] is not None:
        query_2 = query_2.filter(Post.score <= pic_2_filters['max_score'])

    query_2 = query_2.filter(Post.id != image_1.id, Post.score != image_1.score)
    random_offset = np.random.random_integers(0, int(query_2.count()) -1)
    image_2 = query_2.offset(random_offset).first()


    current_user.current_image_1_id = image_1.id
    current_user.current_image_2_id = image_2.id

    db.session.commit()


def get_experimental_condition(subreddit):

    if subreddit is None:
        file_name = 'aww.json'
        experiment_name = 'experiment_configs_aww'
    else:
        file_name = subreddit + '.json'
        experiment_name = 'experiment_configs_' + subreddit


    mc = pylibmc.Client(["127.0.0.1"], binary=True, behaviors={"tcp_nodelay": True, "ketama": True})
    experiment_configs = mc.get(experiment_name)
    if experiment_configs is None:
        experiment_configs = json.load(open('app/experiment_configurations/'+ file_name))

        #update experiment config every hour
        mc.set(experiment_name, experiment_configs, time=60*60)

    weights = []
    for x in experiment_configs['conditions']:
        weights.append(x['weight']/100.0)

    experiment_condition =  choice(np.arange(len(weights)), p=weights)
    condition_1 = experiment_configs['conditions'][experiment_condition]['pic_1_filter']
    condition_2 = experiment_configs['conditions'][experiment_condition]['pic_2_filter']

    return condition_1, condition_2


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
    response.set_cookie(UUID_NAME, current_uuid, max_age = MAX_COOKIE_AGE)
    current_user = get_current_user(current_uuid)
    update_images(current_uuid)
    return response


@predict_game.route('/about')
def about():
    response = make_response(render_template('about.html'))
    return response



@predict_game.route('/reddit_description')
def reddit_description():
    response = make_response(render_template('reddit_description.html'))
    return response







