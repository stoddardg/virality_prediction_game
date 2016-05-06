import pandas


import config
from app import db
from app.models import Post,ImagePair, Quiz, Quiz_to_ImagePair
from sqlalchemy.exc import IntegrityError

import glob

def import_quiz(filename):
    quiz_df = pandas.read_csv(filename)
    for quiz_id, data in quiz_df.groupby('quiz_id'):
        print quiz_id

        subreddit = data.subreddit.min()
        num_questions = len(data) // 2
        #Create a new quiz


        num_questions_added = 0

        new_quiz = Quiz(subreddit=subreddit, num_questions=num_questions)
        db.session.add(new_quiz)
        db.session.commit()

        for pair_id, images in data.groupby('question_id'):
            if len(images) < 2:
                continue
            image_dict = images.to_dict(orient='records')
            posts = []
            for image in image_dict:

                """ First check if the post is in the database already"""

                query_1 = Post.query.filter(Post.reddit_id==image['id'])

                if len(query_1.all()) > 0 :
                    p = query_1.first()
                else:
                    if 'year' in image:
                        image_year = image['year']
                    else:
                        image_year = -1
                    if 'month' in image:
                        image_month = image['month']
                    else:
                        image_month = -1
                    p = Post(image['url'], image['title'], image['score'], image['id'], subreddit, 
                             image_year,image_month)
                    db.session.add(p)
                    db.session.commit()
                posts.append(p)
            if posts[0].id == posts[1].id:
                continue
            if posts[0].url =='http://i.imgur.com/gooPC.png' or posts[1].url=='http://i.imgur.com/gooPC.png':
                continue

            if posts[0].score == posts[1].score:
                continue

            if posts[0].url.find('#') != -1 or posts[1].url.find('#') != -1:
                continue

            if posts[0].url.find('?') != -1 or posts[1].url.find('?') != -1:
                continue



            image_pair = ImagePair(image_1_id = posts[0].id, image_2_id = posts[1].id)
            db.session.add(image_pair)
            db.session.commit()
            num_questions_added += 1


            quiz_to_image_pair = Quiz_to_ImagePair(quiz_id = new_quiz.id, image_pair_id = image_pair.id)
            db.session.add(quiz_to_image_pair)
            db.session.commit()
        
        if num_questions_added < num_questions:
            new_quiz.num_questions = num_questions_added
            db.session.commit()


if __name__=='__main__':
    # import_quiz('raw_script_data/script_data_new.csv')
    for filename in glob.glob('raw_script_data/*.csv'):
        import_quiz(filename)
        # print filename












