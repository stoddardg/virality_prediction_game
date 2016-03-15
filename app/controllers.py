import numpy as np
from numpy.random import choice

from flask import Blueprint, render_template, request, make_response, jsonify,url_for, redirect
import json
import os
import uuid
import md5
from scipy import stats


from models import Post, Vote, User, SurveyResult, UserScore, Quiz, Quiz_to_ImagePair, ImagePair, OpinionVote
from forms import SurveyForm
from app import db
from app import app


# import pylibmc

from app import MAX_COOKIE_AGE
# import app
predict_game = Blueprint("app",__name__)


UUID_NAME = 'guessit_uuid'


@predict_game.route('/record_survey_result')
def record_survey():
    current_uuid = get_uuid_from_cookie(request.cookies)
    subreddit = get_current_subreddit(request.cookies)
    q1 = json.loads(request.args['q1_answer'])
    q2 = json.loads(request.args['q2_answer'])
    q3 = json.loads(request.args['q3_answer'])
    q4 = json.loads(request.args['q4_answer'])
    q5 = json.loads(request.args['q5_answer'])


    s = SurveyResult(frequency_of_use = str(q1),
                        length_of_use = str(q2),
                        use_subreddit=str(q3),
                        vote_on_posts=str(q4),
                        browse_new_queue = str(q5),
                        user_id = current_uuid,
                        subreddit=str(subreddit)
                        )
    db.session.add(s)
    db.session.commit()


    # print current_uuid, q1, q2, q3
    return "ok"

@predict_game.route('/record_all_votes', methods=['POST', 'GET'])
def record_all_votes():
    current_uuid = get_uuid_from_cookie(request.cookies)
    

    current_subreddit = json.loads(request.args['current_subreddit'])

    user_choices = json.loads(request.args['votes'])
    user_opinions = json.loads(request.args['opinion_votes'])
    guess_times = json.loads(request.args['guess_times'])


    user_correct = json.loads(request.args['user_choice_correct'])
    image_1_reddit_ids = json.loads(request.args['image_1_reddit_ids'])
    image_2_reddit_ids = json.loads(request.args['image_2_reddit_ids'])



    # TODO: I should really do some better error checking here
    if len(user_choices) != len(user_correct) or len(user_correct) != len(image_1_reddit_ids) or len(image_1_reddit_ids) != len(image_2_reddit_ids):
        return 'ok'






    num_correct = 0
    num_wrong = 0



    for i in range(len(user_choices)):
        new_vote = Vote(current_uuid, image_1_reddit_ids[i], image_2_reddit_ids[i], user_choices[i], user_correct[i])
        new_vote.elapsed_time = int(np.round(guess_times[i]))
        new_vote.experiment_id = 2

        db.session.add(new_vote)
        db.session.commit()

        if i < len(user_opinions):
            new_opinion_vote = OpinionVote()
            new_opinion_vote.user_id = current_uuid
            new_opinion_vote.user_choice = user_opinions[i] 
            new_opinion_vote.post_id_1 = image_1_reddit_ids[i]
            new_opinion_vote.post_id_2 = image_2_reddit_ids[i]
            new_opinion_vote.vote_id = new_vote.id

            db.session.add(new_opinion_vote)

        if user_correct[i] == 1:
            num_correct += 1
        else:
            num_wrong += 1
    db.session.commit()

 
    # current_subreddit = get_current_subreddit(request.cookies)
    [current_subreddit, pic_source_url, pic_source_name] = get_subreddit_info(current_subreddit)
    new_score = UserScore(uuid=current_uuid,
        subreddit=current_subreddit,
        num_correct = num_correct,
        num_wrong= num_wrong,
        num_questions=len(user_correct),
        num_seen=len(user_correct),
        quiz_id=get_current_quiz(request.cookies)
        )
    db.session.add(new_score)
    db.session.commit()


    response_data = {}
    response_data['status'] = 'OK'


    print 'num_correct,num_wrong', num_correct, num_wrong

    response = jsonify(response_data)
    response.set_cookie('percent_correct', str(format_percentage(num_correct, num_wrong)))

    return response


def convert_imgur_url(url, size='m'):
    if size is None:
        return url
    pos = url.find('.jpg')
    if pos == -1:
        pos = url.find('.png')
    beginning = url[:pos]
    ending = url[pos:]
    print beginning + size + ending
    return beginning + size + ending


def get_current_subreddit(cookies):
    sub = cookies.get('subreddit')
    if sub is None:
        return 'aww'
    return sub

def get_current_quiz(cookies):
    return cookies.get("quiz_id")


@predict_game.route('/get_starting_data')
def get_game_start_data():
    print 'hi'
    current_uuid = get_uuid_from_cookie(request.cookies)
    subreddit = get_current_subreddit(request.cookies)

    quiz_id = get_current_quiz(request.cookies)

    print 'QUIZ ID IS ', quiz_id

    image_pairs = load_quiz(current_uuid, subreddit, quiz_id=quiz_id)
    
    image_pair_json_data = []
    for pair in image_pairs:
        temp_data = {}
        temp_data['image_1_url'] = convert_imgur_url(pair[0].url, size=None)
        

        temp_data['image_1_title'] = " "

        # temp_data['image_1_title'] = pair[0].title
        """ Change this to reddit_id for debugging only"""
        # temp_data['image_1_title'] = pair[0].title + ' ' + pair[0].reddit_id


        temp_data['image_1_score'] = pair[0].score
        temp_data['image_1_lightbox_src'] = pair[0].url
        temp_data['image_1_reddit_id'] = pair[0].reddit_id

        temp_data['image_2_url'] = convert_imgur_url(pair[1].url, size=None)
        temp_data['image_2_title'] = " "

        # temp_data['image_2_title'] = pair[1].title
        """ Change this to reddit_id for debugging only"""
        # temp_data['image_2_title'] = pair[1].title + ' ' + pair[1].reddit_id

        temp_data['image_2_score'] = pair[1].score
        temp_data['image_2_lightbox_src'] = pair[1].url
        temp_data['image_2_reddit_id'] = pair[1].reddit_id


        image_pair_json_data.append(temp_data)




    response_data = {}

    response_data['images'] = image_pair_json_data

    response_data['num_questions'] = len(image_pair_json_data)

    response_data['current_subreddit'] = subreddit


    return jsonify(response_data)
   


def get_new_quiz(uuid, subreddit):

    user_scores = UserScore.query.filter_by(uuid=uuid).all()
    completed_quiz_ids = []
    completed_quiz_clusters = []
    for score in user_scores:
        temp_quiz = Quiz.query.filter_by(id=score.quiz_id).first()
        completed_quiz_ids.append(temp_quiz.id)
        if temp_quiz.cluster_id is not None:
            completed_quiz_clusters.append(temp_quiz.cluster_id)

    query_1 = Quiz.query.filter_by(subreddit=subreddit).order_by(db.func.random())
    
    chosen_quiz = query_1.first()

    for quiz in query_1.all():
        if quiz.id not in completed_quiz_ids and quiz.cluster_id not in completed_quiz_clusters:
            chosen_quiz = quiz
            break
    return chosen_quiz.id, chosen_quiz.num_questions


# Generic class to get experiment assignment off of uuid by taking md5 of that value
# The hope here is that users will always be assigned to same treatment if they retain their cookie
def get_experimental_params(current_uuid):
    m = md5.new()
    m.update(current_uuid)

    ## Mod out by 100 to split the range... should be a better way to do this but ... 
    x = int(m.hexdigest(),16) % 100

    experiment_params = {}

    if x < 25:
        experiment_params['ask_opinion'] = False
    else:
        experiment_params['ask_opinion'] = True

    return experiment_params



@predict_game.route('/')
def start_game():


    current_uuid = get_uuid_from_cookie(request.cookies)

    if request.args.get('quiz_id') is None:
        sub_param = request.args.get('article_source')
        [subreddit, pic_source_url, pic_source_name] = get_subreddit_info(subreddit=sub_param)

        quiz_id, num_questions = get_new_quiz(current_uuid, subreddit)

    else:
        quiz_id = request.args.get('quiz_id')
        sub_param = get_quiz_subreddit(quiz_id)
        [subreddit, pic_source_url, pic_source_name] = get_subreddit_info(subreddit=sub_param)

        num_questions = 10

    # [subreddit, pic_source_url, pic_source_name] = get_subreddit_info(subreddit=sub_param)


    experiment_params = get_experimental_params(current_uuid)

    query_1 = User.query.filter_by(uuid=current_uuid).first()
    if query_1 is None:
        current_user = User()
        current_user.uuid = current_uuid
        current_user.original_referrer = str(request.referrer)
        current_user.browser = str(request.user_agent.browser)
        current_user.platform = str(request.user_agent.platform)
        current_user.user_agent_string = str(request.headers.get('User-Agent'))
        current_user.role = str(request.args.get('role'))
        current_user.ask_opinion_question = experiment_params['ask_opinion']
        current_user.full_url = str(request.url)
        db.session.add(current_user)
        db.session.commit()
    else:
        if request.args.get('role') is not None:
            query_1.role = str(request.args.get('role'))
            query_1.full_url = str(request.url)
            db.session.commit()
        elif request.args.get('special_url') is not None:
            query_1.full_url = str(request.url)
            db.session.commit()
        # query_1.role = str(request.args.get('role'))
        # query_1.full_url = str(request.url)
        # db.session.commit()




    experiment_params = get_experimental_params(current_uuid)

    ask_opinion = request.args.get('opinion')
    if ask_opinion is None:
        ask_opinion = True
    if ask_opinion == "False":
        ask_opinion = False


    response = make_response( render_template('pic_game_mobile.html', 
        pic_source_url = pic_source_url,
        pic_source_name = pic_source_name,
        ask_opinion = experiment_params['ask_opinion']
        )
    )

    
    response.set_cookie(UUID_NAME, current_uuid, max_age=MAX_COOKIE_AGE)
    response.set_cookie('num_questions',str(num_questions))
    response.set_cookie('subreddit',subreddit)
    response.set_cookie('quiz_id', str(quiz_id))
    response.set_cookie('percent_correct', '', expires=0)



    return response


@predict_game.route('/end_game')
def end_game():

    current_uuid = get_uuid_from_cookie(request.cookies)
    current_subreddit = get_current_subreddit(request.cookies)
    [current_subreddit, pic_source_url, pic_source_name] = get_subreddit_info(current_subreddit)
   
    try:
        user_score = float(request.cookies.get('percent_correct'))
    except:
        user_score = 0.0

    mean_score, user_percentile = get_score_distribution_mean(current_subreddit, user_score)


    sub_html = "<a href=%s> %s </a>" % (pic_source_url, 'r/'+current_subreddit)



    #check to see if a user has filled out a Survey
    num_user_surveys = SurveyResult.query.filter_by(user_id=current_uuid).count()
    print 'num_user_surveys',num_user_surveys
    if num_user_surveys == 0:
        #ask the survey question
        show_survey = ""
        show_score = "display:none"
    else:
        # Don't show survey
        show_survey = "display:none"
        show_score = ""

    if request.cookies.get('percent_correct') is None:
        correct_pct = 0
    else:
        correct_pct = request.cookies.get('percent_correct')


    response = make_response(render_template('end_game_text_only.html', 
        correct_pct=int(user_score),
        median_score=int(mean_score), 
        subreddit=sub_html,
        user_percentile=user_percentile,
        show_survey=show_survey,
        show_score=show_score,
        title="Reddit Use"))


    return response

def get_score_distribution_mean(subreddit, user_score=None):
    query = UserScore.query.filter_by(subreddit=subreddit)
    all_scores = []

    for x in query.all():
        if x.num_correct + x.num_wrong == 0:
            continue
        else:
            pct_correct = (x.num_correct*1.0) / (x.num_correct + x.num_wrong)
        pct_correct *= 100
        all_scores.append(pct_correct)
    
    if user_score is not None:
        return np.mean(all_scores), int(np.trunc(stats.percentileofscore(all_scores, user_score, kind='strict')))


    return np.mean(all_scores)


def make_new_score():
    num_questions = 10 # randomize this later
    score_dict = {
    'num_questions':num_questions,
    'num_correct':0,
    'num_wrong':0,
    'num_seen':0
    }
    return score_dict

def format_percentage(num_correct, num_wrong):

    num_answered = num_correct + num_wrong
    if num_answered == 0:
        return '--'

    percent_correct = num_correct / (1.0*num_answered)
    percent_correct *= 100
    percent_correct = int(percent_correct)
    return percent_correct


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


def get_quiz_subreddit(quiz_id):
    current_quiz = Quiz.query.filter_by(id=quiz_id).first()
    return current_quiz.subreddit

def load_quiz(current_uuid, subreddit, quiz_id=None):
    
    if quiz_id is not None:
        current_quiz = Quiz.query.filter_by(id=quiz_id).first()
    else:
        current_quiz = Quiz.query.filter_by(subreddit=subreddit).order_by(db.func.random()).first()

    print "quiz_id", current_quiz.id


    questions = Quiz_to_ImagePair.query.filter_by(quiz_id=current_quiz.id).order_by(db.func.random()).all()
    image_pairs = []
    for q in questions:
        if np.random.randint(2) == 0:
            image_pairs.append([q.image_pair.image_1, q.image_pair.image_2])
        else:
            image_pairs.append([q.image_pair.image_2, q.image_pair.image_1])

    return image_pairs



@predict_game.route('/survey', methods=['GET', 'POST'])
def survey():
    form = SurveyForm()
    current_uuid = get_uuid_from_cookie(request.cookies)
    if request.method == 'POST':
        s = SurveyResult(type_of_use = str(form.type_of_use.data),
                        frequency_of_use = str(form.use_frequency.data),
                        length_of_use = str(form.length_of_use.data),
                        user_id = current_uuid,
                        )
        db.session.add(s)
        db.session.commit()
        return render_template('survey_thanks.html')


    if request.method == 'GET':
        return render_template('survey.html', 
                               title='Reddit Use',
                               form=form)



def get_subreddit_info(subreddit=None):
    subreddits = ['pics','aww','OldSchoolCool','funny', 'itookapicture','EarthPorn','CrappyDesign','photocritique']

    if subreddit == 'aww':
        pic_source_url = "http://www.reddit.com/r/aww"
        pic_source_name = "reddit.com/r/aww"
    elif subreddit == 'pics':
        pic_source_url = "http://www.reddit.com/r/pics"
        pic_source_name = 'reddit.com/r/pics'
    elif subreddit == 'OldSchoolCool':
        pic_source_url = "https://www.reddit.com/r/oldschoolcool"
        pic_source_name = 'reddit.com/r/oldschoolcool'
    elif subreddit == 'funny':
        pic_source_url = 'https://www.reddit.com/r/funny'
        pic_source_name = 'reddit.com/r/funny'
    elif subreddit == 'itookapicture':
        pic_source_url = 'https://www.reddit.com/r/itookapicture'
        pic_source_name = 'reddit.com/r/itookapicture'
    elif subreddit == 'photocritique':
        pic_source_url = 'https://www.reddit.com/r/photocritique'
        pic_source_name = 'reddit.com/r/photocritique'
    elif subreddit == 'CrappyDesign':
        pic_source_url = 'https://www.reddit.com/r/crappydesign'
        pic_source_name = 'reddit.com/r/crappydesign'
    elif subreddit == 'EarthPorn':
        pic_source_url = 'https://www.reddit.com/r/earthporn'
        pic_source_name = 'reddit.com/r/earthporn'
    else:
        random_sub = choice(subreddits)
        return get_subreddit_info(subreddit=random_sub)

    return [subreddit, pic_source_url, pic_source_name]


# @predict_game.route('/')
# def index():
#     response = redirect(url_for('.start_game'))
#     current_uuid = get_uuid_from_cookie(request.cookies)
#     response.set_cookie(UUID_NAME, current_uuid, max_age = MAX_COOKIE_AGE)
#     return response
    # return "hi"

@predict_game.route('/about')
def about():
    response = make_response(render_template('about.html'))
    return response



@predict_game.route('/reddit_description')
def reddit_description():
    response = make_response(render_template('reddit_description.html'))
    return response







