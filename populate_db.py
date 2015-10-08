import pandas
import imgurpython
from imgurpython.helpers.error import ImgurClientError

from app import db
from app.models import Post
from sqlalchemy.exc import IntegrityError


def check_image(image_url, client):
    
    pos = image_url.rfind('/')
    temp = image_url[pos+1:]
    
    #indicates the url has an extension
    if temp.find('.') != -1:
        image_id = temp[:temp.find('.')]
        has_extension = True
    else:
        image_id = temp
        has_extension = False
    
    if has_extension == True:
        try:
            image = client.get_image(image_id)
        except ImgurClientError as e:
            return 'bad_link' 
    else:
        try:
            album = client.get_album(image_id)
            is_gallery = True
        except:
            is_gallery = False

        if is_gallery == True:
            return 'bad_link'
        
        try:
            image = client.get_image(image_id)
        except ImgurClientError as e:
            return 'bad_link' 
    
    if image is None:
        return 'bad_link'
    
    if image.nsfw == True:
        return 'bad_link'
    
    if image.type == 'image/gif':
        return 'bad_link' 
    
    return image.link

def populate_table(datafile, sample_size=1000):
    imgur_client_id = '076efcf250d6c46'
    imgur_client_secret = '4994cb5d85b7530d64219337a9d56fe3c51491da'

    client = imgurpython.ImgurClient(imgur_client_id, imgur_client_secret)

    num_processed = 0 

    df = pandas.read_csv(datafile)


    for row in df.sample(sample_size).iterrows():
        data = row[1]
        new_link = check_image(data['url'], client)
        if new_link == 'bad_link':
            print 'bad link'
            continue
        p = Post(new_link, data.title, data.score, data.id, data.subreddit, data.year, data.month)
        try:
            db.session.add(p)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            continue
        


if __name__=='__main__':
    populate_table('pics_2014_random_sample.csv.gz', sample_size=500)












