import numpy as np
from numpy.random import choice

from flask import Blueprint, render_template, request, make_response, jsonify,url_for, redirect
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
    
    current_score = get_current_user_score(request.cookies)
    user_choice = int(request.args.get('choice'))


    [image_1, image_2] = get_current_images(request.cookies)

    if image_1.score > image_2.score:
        correct_answer = 1
    elif image_2.score > image_1.score:
        correct_answer = 2
    else:
        correct_answer = 0 

    if current_score['num_correct'] is None:
        current_score['num_correct'] = 0
    if current_score['num_wrong'] is None:
        current_score['num_wrong'] = 0


    if user_choice == correct_answer:
        user_correct = 1
        current_score['num_correct'] = current_score['num_correct'] + 1
    else:
        user_correct = 0
        current_score['num_wrong'] = current_score['num_wrong'] + 1

    # update_current_score(current_uuid, current_score)


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
    num_remaining = current_score['num_questions'] - (current_score['num_correct'] + current_score['num_wrong'])
    ret_vals = {
    'status':'OK',
    'image_1_karma':image_1_score,
    'image_2_karma':image_2_score,
    'correct':user_correct,
    'num_correct':current_score['num_correct'],
    'num_wrong':current_score['num_wrong'], 
    'num_remaining':num_remaining,
    'user_choice': user_choice
    }

    # print current_score.num_correct + current_score.num_wrong

    if current_score['num_correct'] + current_score['num_wrong'] >= current_score['num_questions']:
        ret_vals['end_of_game'] = 1

    print 'DUMPS'
    print json.dumps(ret_vals)

    print 'JSONIFY'
    print jsonify(ret_vals)


    response = jsonify(ret_vals)
    response.set_cookie('num_wrong',str(current_score['num_wrong']))
    response.set_cookie('num_correct',str(current_score['num_correct']))

    return response



@predict_game.route('/get_next_images', methods=['POST','GET'])
def get_next_images():

    current_uuid =  get_uuid_from_cookie(request.cookies)

    current_score = get_current_user_score(request.cookies)
    # current_score = get_score(current_uuid)

    current_score['num_seen'] = current_score['num_seen'] + 1
    
    # update_current_score(current_uuid, current_score)
    [current_image_1, current_image_2] = get_current_images(request.cookies)

    next_image_data = {}

    next_image_data['image_1_src'] = current_image_1.url
    next_image_data['image_1_title']  = current_image_1.title

    next_image_data['image_2_src'] = current_image_2.url
    next_image_data['image_2_title']  = current_image_2.title
    next_image_data['status'] = 'OK'

    num_remaining = current_score['num_questions'] - (current_score['num_correct'] + current_score['num_wrong'])
    next_image_data['num_remaining'] = num_remaining

    response = jsonify(next_image_data)


    response.set_cookie('num_seen',str(current_score['num_seen']))
    return response


def get_current_images(cookies, current_question=None):
    
    current_score = get_current_user_score(cookies)
    current_uuid =  get_uuid_from_cookie(cookies)
    subreddit = get_current_subreddit(cookies)

    mc = pylibmc.Client(["127.0.0.1"], binary=True, behaviors={"tcp_nodelay": True, "ketama": True})


    current_images = mc.get(current_uuid+'_images')
    if current_images is None:
        current_images = setup_images(current_uuid, subreddit, current_score['num_questions'])

    if current_question is None:
        current_question = current_score['num_seen']

    if current_question >= len(current_images):
        current_images = setup_images(current_uuid, subreddit, current_score['num_questions'])
        print "RESIZED"

    if current_question >= current_score['num_questions']:
        current_question = current_question % current_score['num_questions']

    return current_images[current_question]


def get_current_subreddit(cookies):
    sub = cookies.get('subreddit')
    if sub is None:
        return 'aww'
    return sub



@predict_game.route('/render_game')
def start_game():
    sub_param = request.args.get('article_source')
    [subreddit, pic_source_url, pic_source_name] = get_subreddit_info(subreddit=sub_param)


    current_uuid = get_uuid_from_cookie(request.cookies)
    current_score = make_new_score()

    setup_images(current_uuid, subreddit, current_score['num_questions'])
    [current_image_1, current_image_2] = get_current_images(request.cookies, current_question=0)


    response = make_response( render_template('pic_game_mobile.html', 
        pic_source_url = pic_source_url,
        pic_source_name = pic_source_name,
        image_1_title = current_image_1.title,
        image_1_src = current_image_1.url,
        image_2_title = current_image_2.title,
        image_2_src = current_image_2.url,
        num_correct = current_score['num_correct'],
        num_wrong = current_score['num_wrong'],
        num_remaining = current_score['num_questions'],
        num_questions = current_score['num_questions']
        )
    )
    
    response.set_cookie(UUID_NAME, current_uuid)
    response.set_cookie('num_wrong',str(current_score['num_wrong']))
    response.set_cookie('num_correct',str(current_score['num_correct']))
    response.set_cookie('num_seen',str(current_score['num_seen']))
    response.set_cookie('num_questions',str(current_score['num_questions']))
    response.set_cookie('subreddit',subreddit)


    return response


@predict_game.route('/end_game')
def end_game():
    current_uuid = get_uuid_from_cookie(request.cookies)
    current_score = get_current_user_score(request.cookies)
    current_subreddit = get_current_subreddit(request.cookies)
    
    new_score = UserScore(uuid=current_uuid,
        subreddit=current_subreddit,
        num_correct = current_score['num_correct'],
        num_wrong=current_score['num_wrong'],
        num_questions=current_score['num_questions'],
        num_seen=current_score['num_seen']
        )
    db.session.add(new_score)
    db.session.commit()

    num_bins = 10
    values = get_score_distributions(current_subreddit, num_bins)

    if current_score['num_correct'] + current_score['num_wrong'] == 0:
        current_pct = 0
    else:
        current_pct = (current_score['num_correct']*1.0) / (current_score['num_correct'] + current_score['num_wrong'])
    current_pct *= 100

    bin_size = 100/num_bins

    user_val = np.max(values)
    user_val *= 1.1



    response = make_response(render_template('end_game_thanks.html', 
        correct_pct=format_correct_percentage(current_score), 
        score_dist=values, 
        user_score=current_pct, 
        user_val = user_val , 
        bin_size=bin_size,
        subreddit=current_subreddit))

    print response
    return response


def get_score_distributions(subreddit, num_bins):
    query = UserScore.query.filter_by(subreddit=subreddit)

    all_scores = []

    for x in query.all():
        if x.num_correct + x.num_wrong == 0:
            continue
        else:
            pct_correct = (x.num_correct*1.0) / (x.num_correct + x.num_wrong)
        pct_correct *= 100
        all_scores.append(pct_correct)

    print all_scores

    bin_size = 100/num_bins

    hist, bin_edges = np.histogram(all_scores, bins=bin_size*np.arange(num_bins), density=False)
    hist = np.multiply(hist, 1.0)
    hist /= np.sum(hist)

    print 'sum is', np.sum(hist)
    print 'bin_edges',bin_edges
    return list(hist)

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

    if current_score is None:
        current_score = UserScore(uuid=current_user.uuid, subreddit=current_user.current_image_source)
        db.session.add(current_score)
        db.session.commit()


    return current_user, current_score


def make_new_score():
    num_questions = 10 # randomize this later
    score_dict = {
    'num_questions':num_questions,
    'num_correct':0,
    'num_wrong':0,
    'num_seen':1
    }
    return score_dict

def get_current_user_score(cookies):
    num_correct = cookies.get('num_correct')
    num_seen = cookies.get('num_seen')
    num_wrong = cookies.get('num_wrong')
    num_questions = cookies.get('num_questions')

    if num_correct is None:
        return make_new_score()
    if num_seen is None:
        return make_new_score()
    if num_wrong is None:
        return make_new_score()
    if num_questions is None:
        return make_new_score()


    score_dict = {
    'num_correct':int(num_correct),
    'num_seen':int(num_seen),
    'num_wrong':int(num_wrong),
    'num_questions':int(num_questions)
    }

    return score_dict

def format_correct_percentage(current_score):

    num_answered = current_score['num_correct'] + current_score['num_wrong']
    if num_answered == 0:
        return '--'
        # return 100

    percent_correct = current_score['num_correct'] / (1.0*num_answered)
    percent_correct *= 100
    percent_correct = int(percent_correct)
    return percent_correct

def get_uuid_from_cookie(cookie):
    if (UUID_NAME in cookie.keys()) == False:
        user_id = str(uuid.uuid4())
    else:
        user_id = cookie.get(UUID_NAME)
    return user_id



def update_article_source(current_uuid, article_source):
    current_user = get_current_user(current_uuid)
    current_user.current_image_source = article_source
    db.session.commit()



def setup_images(current_uuid, subreddit, num_questions):

    # subreddit = get_current_subreddit(current_uuid)
    score_threshold = 10 #change later by subreddit

    query_1 = Post.query.filter(Post.year_posted==2014, Post.show_to_users=='t', Post.subreddit==subreddit)

    low_score_images = query_1.filter(Post.score <= score_threshold).order_by(db.func.random())
    high_score_images = query_1.filter(Post.score > score_threshold).order_by(db.func.random())

    low_index = 0
    high_index = 0

    image_pairs = []
    weights = [.25,.25,.25,.25]
    experiment_condition =  choice(np.arange(len(weights)), p=weights)
    for i in np.arange(num_questions):

        #low low experiment 
        if experiment_condition == 0:
            first_image = low_score_images.offset(low_index).first()
            low_index += 1
            second_image = low_score_images.offset(low_index).first()
            while first_image.score == second_image.score:
                low_index += 1
                second_image = low_score_images.offset(low_index).first()
            low_index += 1

        if experiment_condition == 1:
            first_image = low_score_images.offset(low_index).first()
            low_index += 1
            second_image = low_score_images.offset(low_index).first()
            while first_image.score == second_image.score:
                low_index += 1
                second_image = low_score_images.offset(low_index).first()
            low_index += 1

        if experiment_condition == 2:
            first_image = high_score_images.offset(high_index).first()
            high_index += 1
            second_image = low_score_images.offset(low_index).first()
            low_index += 1

        if experiment_condition == 3:
            first_image = high_score_images.offset(high_index).first()
            high_index += 1
            second_image = high_score_images.offset(high_index).first()
            while first_image.score == second_image.score:
                high_index += 1
                second_image = high_score_images.offset(high_index).first()
            high_index += 1

        image_pairs.append([first_image, second_image])

    mc = pylibmc.Client(["127.0.0.1"], binary=True, behaviors={"tcp_nodelay": True, "ketama": True})
    mc.set(current_uuid + '_images',image_pairs, time=10*60)

    return image_pairs

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



def get_subreddit_info(subreddit=None):
    subreddits = ['pics','aww','OldSchoolCool']

    if subreddit == 'aww':
        pic_source_url = "http://www.reddit.com/r/aww"
        # pic_source_name = 'r/aww'
        pic_source_name = "reddit.com/r/aww"
    elif subreddit == 'pics':
        pic_source_url = "http://www.reddit.com/r/pics"
        pic_source_name = 'reddit.com/r/pics'
    elif subreddit == 'OldSchoolCool':
        pic_source_url = "https://www.reddit.com/r/oldschoolcool"
        pic_source_name = 'reddit.com/r/oldschoolcool'
    else:
        random_sub = choice(subreddits)

        return get_subreddit_info(subreddit=random_sub)



    return [subreddit, pic_source_url, pic_source_name]


@predict_game.route('/')
def index():
    response = redirect(url_for('.start_game'))
    current_uuid = get_uuid_from_cookie(request.cookies)
    response.set_cookie(UUID_NAME, current_uuid, max_age = MAX_COOKIE_AGE)
    return response


@predict_game.route('/about')
def about():
    response = make_response(render_template('about.html'))
    return response



@predict_game.route('/reddit_description')
def reddit_description():
    response = make_response(render_template('reddit_description.html'))
    return response







