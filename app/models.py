from app import db
from sqlalchemy.orm import relationship

from sqlalchemy import ForeignKey




db.create_all()
# Define a User model
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

    current_image_1_id = db.Column(db.Integer, ForeignKey("post.id"), default=None)
    current_image_2_id = db.Column(db.Integer, ForeignKey("post.id"), default=None)

    current_image_1 = relationship("Post", foreign_keys=[current_image_1_id])
    current_image_2 = relationship("Post", foreign_keys=[current_image_2_id])

    current_image_source = db.Column(db.String, default=None)

    num_correct = db.Column(db.Integer, default=0)
    num_wrong = db.Column(db.Integer, default=0)
    num_seen = db.Column(db.Integer, default=0)


class UserScore(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, index=True)
    subreddit = db.Column(db.String, index=True)
    num_correct = db.Column(db.Integer, default=0)
    num_wrong = db.Column(db.Integer, default=0)
    num_seen = db.Column(db.Integer, default=0)



class SurveyResult(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

    type_of_use = db.Column(db.String)
    frequency_of_use = db.Column(db.String)
    length_of_use = db.Column(db.String)

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

    def __init__(self, user_id, post_id_1, post_id_2, user_choice, correct_answer, experiment_condition=-1):
        self.user_id = user_id
        self.post_id_1 = post_id_1
        self.post_id_2 = post_id_2
        self.user_choice = user_choice
        self.correct_answer = correct_answer
        self.experiment_condition = experiment_condition

