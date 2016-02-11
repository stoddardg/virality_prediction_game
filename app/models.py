from app import db
from sqlalchemy.orm import relationship

from sqlalchemy import ForeignKey




db.create_all()


class Quiz(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

    subreddit = db.Column(db.String)
    num_questions = db.Column(db.Integer)

    cluster_id = db.Column(db.String)
    # image_pairs = db.Column(db.Array(db.Integer))    

class Quiz_to_ImagePair(db.Model):
    __tablename__ = 'quiz_to_image_pair'
    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

    quiz_id = db.Column(db.Integer, ForeignKey("quiz.id"))
    image_pair_id = db.Column(db.Integer, ForeignKey("image_pair.id"))    

    image_pair = relationship("ImagePair", foreign_keys=[image_pair_id])


class ImagePair(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

    image_1_id = db.Column(db.Integer, ForeignKey("post.id"), default=None)
    image_2_id = db.Column(db.Integer, ForeignKey("post.id"), default=None)


    image_1 = relationship("Post", foreign_keys=[image_1_id])
    image_2 = relationship("Post", foreign_keys=[image_2_id])    


class Post(db.Model):
    __tablename__ = 'post'
    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())


    score = db.Column(db.Integer)
    url = db.Column(db.String)
    title = db.Column(db.String)
    reddit_id = db.Column(db.String, unique=True)
    subreddit = db.Column(db.String)

    month_posted = db.Column(db.Integer)
    year_posted = db.Column(db.Integer)

    hand_validated = db.Column(db.Boolean, default=None)
    show_to_users = db.Column(db.Boolean, default=None)



    def __init__(self, url, title, score, reddit_id, subreddit, year_posted, month_posted, hand_validated=None, show_to_users=None):
        self.url = url
        self.title = title
        self.score = score
        self.reddit_id = reddit_id
        self.subreddit = subreddit
        self.year_posted = year_posted
        self.month_posted = month_posted
        self.hand_validated = hand_validated
        self.show_to_users = show_to_users



    def __repr__(self):
        return '[ %s]: score %s' % (self.title, self.score)



class User(db.Model):
    uuid = db.Column(db.String, primary_key=True)

    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

    original_referrer = db.Column(db.String)
    platform = db.Column(db.String)
    browser = db.Column(db.String)


class UserScore(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())


    uuid = db.Column(db.String, index=True)
    subreddit = db.Column(db.String, index=True)
    num_correct = db.Column(db.Integer, default=0)
    num_wrong = db.Column(db.Integer, default=0)
    num_seen = db.Column(db.Integer, default=0)

    num_questions = db.Column(db.Integer, default=10)

    quiz_id = db.Column(db.Integer)



class SurveyResult(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

    frequency_of_use = db.Column(db.String)
    length_of_use = db.Column(db.String)

    subreddit = db.Column(db.String)

    use_subreddit = db.Column(db.String)

    vote_on_posts = db.Column(db.String)

    browse_new_queue = db.Column(db.String)

    user_id = db.Column(db.String)

class Vote(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

    user_id = db.Column(db.String)

    user_choice = db.Column(db.Integer)
    correct_answer = db.Column(db.Integer)

    post_id_1 = db.Column(db.String)
    post_id_2 = db.Column(db.String)
    experiment_condition = db.Column(db.Integer)
    elapsed_time = db.Column(db.Integer)

    def __init__(self, user_id, post_id_1, post_id_2, user_choice, correct_answer, experiment_condition=-1):
        self.user_id = user_id
        self.post_id_1 = post_id_1
        self.post_id_2 = post_id_2
        self.user_choice = user_choice
        self.correct_answer = correct_answer
        self.experiment_condition = experiment_condition

class OpinionVote(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

    user_id = db.Column(db.String)

    user_choice = db.Column(db.Integer)

    post_id_1 = db.Column(db.String)
    post_id_2 = db.Column(db.String)
    
    vote_id = db.Column(db.Integer)

