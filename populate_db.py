import pandas
import imgurpython
from imgurpython.helpers.error import ImgurClientError


import config
from app import db
from app.models import Post,ImagePair, Quiz, Quiz_to_ImagePair
from sqlalchemy.exc import IntegrityError


def import_quiz(filename):
    quiz_df = pandas.read_csv(filename)
    for quiz_id, data in quiz_df.groupby('quiz_id'):
        print quiz_id

        subreddit = data.subreddit.min()
        num_questions = len(data) / 2
        #Create a new quiz

        new_quiz = Quiz(subreddit=subreddit, num_questions=10)
        db.session.add(new_quiz)
        db.session.commit()

        for pair_id, images in data.groupby('question_id'):
            image_dict = images.to_dict(orient='records')
            posts = []
            for image in image_dict:

                """ First check if the post is in the database already"""

                query_1 = Post.query.filter(Post.reddit_id==image['id'])

                if len(query_1.all()) > 0 :
                    p = query_1.first()
                else:
                    p = Post(image['url'], image['title'], image['score'], image['id'], subreddit, 
                             image['year'],image['month'])
                    db.session.add(p)
                    db.session.commit()
                posts.append(p)
            image_pair = ImagePair(image_1_id = posts[0].id, image_2_id = posts[1].id)
            db.session.add(image_pair)
            db.session.commit()


            quiz_to_image_pair = Quiz_to_ImagePair(quiz_id = new_quiz.id, image_pair_id = image_pair.id)
            db.session.add(quiz_to_image_pair)
            db.session.commit()
        


if __name__=='__main__':
    import_quiz('raw_script_data/script_data.csv.gz')












