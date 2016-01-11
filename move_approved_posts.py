import sys



from app import db
from app.models import Post,ImagePair, Quiz, Quiz_to_ImagePair
from sqlalchemy.exc import IntegrityError
import pandas
from sqlalchemy import create_engine




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


def export_images(file_name):
    engine = create_engine('postgresql://localhost/prediction_game')
    df = pandas.read_sql_table('post', engine)
    temp = df[df.show_to_users == True]
    temp = temp[temp.year_posted == 2014]
    temp.to_csv(file_name, index=False, encoding='utf-8')



def import_images(file_name):
    df = pandas.read_csv(file_name)
    print 'called'
    for row in df.iterrows():
        data = row[1]

        p = Post(score=data.score, url=data.url, title=data.title, reddit_id=data.reddit_id, subreddit=data.subreddit, 
            month_posted=data.month_posted, year_posted=data.year_posted, hand_validated=data.hand_validated, show_to_users=data.show_to_users)

        try:
            db.session.add(p)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            continue


if __name__ == '__main__':
    print sys.argv

    if sys.argv[1] == 'export_images':
        export_images(sys.argv[2])
    if sys.argv[1] == 'import_images':
        import_images(sys.argv[2])

    if sys.argv[1] == 'import_script':
        import_quiz(sys.argv[2])


