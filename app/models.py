from app import db

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

    def __init__(self, url, title, score, reddit_id, subreddit):
        self.url = url
        self.title = title
        self.score = score
        self.reddit_id = reddit_id
        self.subreddit = subreddit

    def __repr__(self):
        return '[ %s]: score %s' % (self.title, self.score)


class Vote(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

    user_id = db.Column(db.String)

    user_choice = db.Column(db.Integer)
    correct_answer = db.Column(db.Integer)

    post_id_1 = db.Column(db.Integer)
    post_id_2 = db.Column(db.Integer)
    experiment_condition = db.Column(db.Integer)

    def __init__(self, user_id, post_id_1, post_id_2, user_choice, correct_answer, experiment_condition=-1):
        self.user_id = user_id
        self.post_id_1 = post_id_1
        self.post_id_2 = post_id_2
        self.user_choice = user_choice
        self.correct_answer = correct_answer
        self.experiment_condition = experiment_condition

