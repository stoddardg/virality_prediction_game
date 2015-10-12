import sys



from app import db
from app.models import Post
from sqlalchemy.exc import IntegrityError
import pandas
from sqlalchemy import create_engine


def export_images(file_name):
    engine = create_engine('postgresql://localhost/prediction_game')
    df = pandas.read_sql_table('post', engine)
    temp = df[df.show_to_users == True]
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